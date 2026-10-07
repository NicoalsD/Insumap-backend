"""Map, microzones, injections and undo (R01-R10, R17) on top of the cached PatientState."""

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.core import clock
from app.core.errors import AppError, bad_request, conflict
from app.db.models import ColorDb, Injection, InjectionOrigin, InjectionStatusDb, Patient, Reminder, ReminderStatus
from app.domain.models import Color, InjectionStatus, InjectionView, InvalidMicrozoneId
from app.domain.patient_state import InjectionData, PatientState
from app.services import state_service
from app.services.reminder_service import scheduler


def view_out(v: InjectionView) -> dict[str, Any]:
    return {
        "id": v.id,
        "microzone_id": v.microzone_id,
        "macro": v.macro,
        "side": v.side,
        "applied_at": v.applied_at,
        "registered_at": v.registered_at,
        "status": v.status.value,
        "undone_at": v.undone_at,
    }


def _microzone_or_400(state: PatientState, microzone_id: str) -> Any:
    try:
        return state.microzone(microzone_id)
    except (InvalidMicrozoneId, KeyError) as exc:
        raise bad_request(
            "INVALID_MICROZONE",
            f"La microzona {microzone_id} no existe en tu cuadrícula {state.grid_size}x{state.grid_size}.",
        ) from exc


def body_map(db: Session, patient: Patient, macro: str | None = None) -> dict[str, Any]:
    with state_service.lock:
        state = state_service.get_state(db, patient)
        now = clock.now()
        return {"grid_size": state.grid_size, "generated_at": now, "zones": state.body_map(now, macro)}


def microzone_detail(db: Session, patient: Patient, microzone_id: str) -> dict[str, Any]:
    with state_service.lock:
        state = state_service.get_state(db, patient)
        mz = _microzone_or_400(state, microzone_id)
        return {
            "microzone": state.evaluate_microzone(mz, clock.now()),
            "latest": [view_out(v) for v in state.latest_for(microzone_id)],
        }


def set_grid_size(db: Session, patient: Patient, grid_size: int) -> dict[str, Any]:
    patient.grid_size = grid_size
    db.commit()
    state_service.invalidate(patient.user_id)
    return body_map(db, patient)


def suggestions(db: Session, patient: Patient, k: int | None) -> list[dict[str, Any]]:
    with state_service.lock:
        state = state_service.get_state(db, patient)
        return [
            {
                "microzone_id": s.microzone_id,
                "score": round(s.score, 4),
                "color": s.color.value,
                "breakdown": {
                    "ratio": round(s.ratio, 4),
                    "forgotten_bonus": s.forgotten_bonus,
                    "overuse_penalty": round(s.overuse_penalty, 4),
                    "neighbor_penalty": s.neighbor_penalty,
                },
            }
            for s in state.suggestions(clock.now(), k)
        ]


def register(
    db: Session,
    patient: Patient,
    microzone_id: str,
    applied_at: datetime | None,
    confirm_not_recovered: bool,
    origin: InjectionOrigin,
    reminder_id: uuid.UUID | None,
) -> dict[str, Any]:
    now = clock.now()
    applied = now if applied_at is None else (applied_at if applied_at.tzinfo else applied_at.replace(tzinfo=UTC))
    if applied > now + timedelta(minutes=5):
        raise bad_request("APPLIED_IN_FUTURE", "La hora de aplicación no puede estar en el futuro.")
    with state_service.lock:
        state = state_service.get_state(db, patient)
        mz = _microzone_or_400(state, microzone_id)
        current = state.evaluate_microzone(mz, now)
        color = Color(current["color"])
        if color != Color.GREEN and not confirm_not_recovered:
            best = state.suggestions(now, 1)
            raise conflict(
                "MICROZONE_NOT_RECOVERED",
                f"La microzona {microzone_id} aún no se ha recuperado. Confirma si deseas registrarla de todas formas.",
                {
                    "color": color.value,
                    "hours_remaining": current["hours_remaining"],
                    "suggested_microzone_id": best[0].microzone_id if best else None,
                },
            )
        reminder = None
        if reminder_id is not None:
            reminder = db.get(Reminder, reminder_id)
            if reminder is None or reminder.patient_id != patient.user_id:
                raise AppError(404, "NOT_FOUND", "Recordatorio no encontrado.")
        row = Injection(
            patient_id=patient.user_id,
            macro=mz.macro,
            side=mz.side,
            row=mz.row,
            col=mz.col,
            grid_size=state.grid_size,
            microzone_id=mz.id,
            applied_at=applied,
            registered_at=now,
            status=InjectionStatusDb.REGISTERED,
            color_at_registration=ColorDb(color.value),
            warning_accepted=color != Color.GREEN,
            previous_last_used=mz.last_used,
            origin=origin,
        )
        db.add(row)
        db.flush()
        if reminder is not None:
            reminder.status = ReminderStatus.CONFIRMED
            reminder.confirmed_at = now
            reminder.injection_id = row.id
            scheduler.cancel(str(reminder.id))
        db.commit()
        try:
            state.register(
                InjectionData(
                    str(row.id),
                    row.macro,
                    row.side,
                    row.row,
                    row.col,
                    row.grid_size,
                    applied,
                    now,
                    InjectionStatus.REGISTERED,
                ),
                now,
            )
        except Exception:
            state_service.invalidate(patient.user_id)
            raise
        view = state.history_nodes.get(str(row.id)).data()
        return {
            "injection": view_out(view),
            "microzone": state.evaluate_microzone(mz, now),
            "can_undo": state.undoable(now) is not None,
        }


def undo_last(db: Session, patient: Patient) -> dict[str, Any]:
    now = clock.now()
    with state_service.lock:
        state = state_service.get_state(db, patient)
        action = state.undoable(now)
        if action is None:
            raise conflict("NOTHING_TO_UNDO", "No hay registros recientes para deshacer.")
        row = db.get(Injection, uuid.UUID(action.injection_id))
        if row is None or row.status != InjectionStatusDb.REGISTERED:
            state_service.invalidate(patient.user_id)
            raise conflict("NOTHING_TO_UNDO", "El registro ya no se puede deshacer. Intenta de nuevo.")
        row.status = InjectionStatusDb.UNDONE
        row.undone_at = now
        db.commit()
        state.apply_undo(now)
        view = state.history_nodes.get(action.injection_id).data()
        return {
            "injection": view_out(view),
            "microzone": state.evaluate_microzone(state.microzone(action.microzone_id), now),
            "can_undo": state.undoable(now) is not None,
        }
