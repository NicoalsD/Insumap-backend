"""Patient assistant proxy (R28-R30).

The backend authenticates, rate-limits and stores messages, then forwards them to the
``Insumap-ai`` service with a short-lived delegated token. When the AI service is not
configured or fails, it answers in *degraded* mode with a template built from the
suggestion algorithm, so the patient always gets the suggested microzone.
"""

import logging
import re
from datetime import timedelta
from typing import Any

import httpx
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core import clock
from app.core.config import get_settings
from app.core.errors import AppError
from app.core.security import create_delegated_token
from app.db.models import AssistantMessage, MessageRole, Patient
from app.domain.location import describe_location
from app.services import state_service

log = logging.getLogger("insumap.assistant")

# Cheap pre-filter (the AI service applies the full guardrails). R30.
DOSE_PATTERN = re.compile(
    r"\b(\d+\s*(unidades|ui|u)\b|cu[aá]nta[s]?\s+(insulina|unidades)|dosis\s+de|cu[aá]nto\s+me\s+(pongo|inyecto))",
    re.IGNORECASE,
)
DOSE_REPLY = (
    "No puedo indicarte dosis ni cambios en tu medicación: eso lo define tu médico tratante. "
    "Sí puedo ayudarte a ubicar la zona donde aplicarte la próxima dosis."
)


def _count_last_hour(db: Session, patient: Patient) -> int:
    since = clock.now() - timedelta(hours=1)
    stmt = select(func.count(AssistantMessage.id)).where(
        AssistantMessage.patient_id == patient.user_id,
        AssistantMessage.role == MessageRole.USER,
        AssistantMessage.created_at >= since,
    )
    return int(db.scalar(stmt) or 0)


def history(db: Session, patient: Patient, limit: int) -> list[AssistantMessage]:
    stmt = (
        select(AssistantMessage)
        .where(AssistantMessage.patient_id == patient.user_id, AssistantMessage.role != MessageRole.TOOL)
        # Tie-break on equal timestamps so a question always precedes its answer once reversed.
        .order_by(AssistantMessage.created_at.desc(), AssistantMessage.role.asc())
        .limit(limit)
    )
    return list(reversed(list(db.scalars(stmt))))


def _degraded(db: Session, patient: Patient) -> dict[str, Any]:
    with state_service.lock:
        state = state_service.get_state(db, patient)
        best = state.suggestions(clock.now(), 1)
    if not best:
        return {"reply": "No pude calcular una sugerencia en este momento.", "referenced_microzones": []}
    mz = best[0].microzone_id
    return {
        "reply": (
            f"Te sugerimos aplicar la próxima dosis en {describe_location(mz, state.grid_size)} ({mz}). "
            "El asistente no está disponible en este momento; esta sugerencia la calculó Insumap."
        ),
        "referenced_microzones": [mz],
    }


def send_message(db: Session, patient: Patient, message: str) -> dict[str, Any]:
    s = get_settings()
    if _count_last_hour(db, patient) >= s.assistant_messages_per_hour:
        raise AppError(429, "RATE_LIMITED", "Alcanzaste el límite de mensajes por hora. Intenta más tarde.")
    db.add(AssistantMessage(patient_id=patient.user_id, role=MessageRole.USER, content=message))
    db.commit()

    if DOSE_PATTERN.search(message):
        result: dict[str, Any] = {"reply": DOSE_REPLY, "referenced_microzones": [], "source": "guardrail"}
        blocked, degraded = True, False
    else:
        blocked = False
        result, degraded = _call_ai(db, patient, message), False
        if result is None:
            result, degraded = {**_degraded(db, patient), "source": "template"}, True

    db.add(
        AssistantMessage(
            patient_id=patient.user_id,
            role=MessageRole.ASSISTANT,
            content=result["reply"],
            provider=result.get("provider"),
            model=result.get("model"),
            input_tokens=int(result.get("input_tokens", 0)),
            output_tokens=int(result.get("output_tokens", 0)),
            blocked_by_guardrail=blocked or bool(result.get("blocked_by_guardrail", False)),
        )
    )
    db.commit()
    return {
        "reply": result["reply"],
        "referenced_microzones": result.get("referenced_microzones", []),
        "source": result.get("source") or result.get("model") or "ai",
        "degraded": degraded,
    }


def _call_ai(db: Session, patient: Patient, message: str) -> dict[str, Any] | None:
    s = get_settings()
    if not s.ai_service_url:
        return None
    user = patient.user
    payload = {
        "patient_first_name": user.name.split()[0] if user and user.name else "",
        "message": message,
        "history": [{"role": m.role.value, "content": m.content} for m in history(db, patient, 10)[:-1]],
        "delegated_token": create_delegated_token(str(patient.user_id), "PATIENT"),
    }
    try:
        resp = httpx.post(
            f"{s.ai_service_url.rstrip('/')}/chat",
            json=payload,
            headers={"X-Service-Token": s.ai_service_token},
            timeout=s.ai_timeout_seconds,
        )
        resp.raise_for_status()
        data: dict[str, Any] = resp.json()
        if "reply" not in data:
            raise ValueError("AI response without 'reply'")
        return data
    except (httpx.HTTPError, ValueError) as exc:
        log.warning("AI service unavailable, using degraded mode: %s", exc)
        return None
