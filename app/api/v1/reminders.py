import uuid
from typing import Any

from fastapi import APIRouter, Depends, status

from app.api.deps import CurrentPatient, CurrentUser, DbSession, cron_guard
from app.api.schemas import (
    ConfirmResponse,
    ErrorResponse,
    PushSubscriptionIn,
    PushSubscriptionOut,
    ReminderOut,
    ScheduleRequest,
    ScheduleResponse,
    SnoozeRequest,
    TickResponse,
)
from app.core.config import get_settings
from app.db.models import PushSubscription, Reminder
from app.services import injection_service, reminder_service

router = APIRouter(tags=["Recordatorios"])
ERRORS = {400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}}


@router.get("/schedule", response_model=ScheduleResponse, responses=ERRORS, summary="Ver cronograma de dosis")
def get_schedule(patient: CurrentPatient, db: DbSession) -> dict[str, Any]:
    return {"timezone": patient.timezone, "doses": reminder_service.get_schedule(db, patient)}


@router.put("/schedule", response_model=ScheduleResponse, responses=ERRORS, summary="Configurar cronograma de dosis")
def put_schedule(body: ScheduleRequest, patient: CurrentPatient, db: DbSession) -> dict[str, Any]:
    """HU-14 / R14. Entre 1 y 6 horas diarias (en la zona horaria del paciente); reprograma el min-heap."""
    doses = reminder_service.save_schedule(db, patient, [(d.time, d.label) for d in body.doses])
    return {"timezone": patient.timezone, "doses": doses}


@router.get("/reminders/upcoming", response_model=list[ReminderOut], summary="Próximos recordatorios")
def upcoming(patient: CurrentPatient, db: DbSession) -> list[Reminder]:
    """Respaldo dentro de la app cuando no hay notificaciones push (p. ej. iPhone sin instalar la PWA)."""
    return reminder_service.upcoming(db, patient)


@router.post(
    "/reminders/{reminder_id}/snooze", response_model=ReminderOut, responses=ERRORS, summary="Posponer recordatorio"
)
def snooze(reminder_id: uuid.UUID, body: SnoozeRequest, patient: CurrentPatient, db: DbSession) -> Reminder:
    """HU-16. Actualiza la prioridad en el min-heap indexado en O(log n)."""
    return reminder_service.snooze(db, patient, reminder_id, body.minutes)


@router.post(
    "/reminders/{reminder_id}/confirm",
    response_model=ConfirmResponse,
    responses=ERRORS,
    summary="Confirmar recordatorio",
)
def confirm(reminder_id: uuid.UUID, patient: CurrentPatient, db: DbSession) -> dict[str, Any]:
    """HU-16. Devuelve la microzona sugerida para abrir el registro."""
    reminder = reminder_service.confirm(db, patient, reminder_id)
    best = injection_service.suggestions(db, patient, 1)
    return {"reminder": reminder, "suggested_microzone_id": best[0]["microzone_id"] if best else None}


@router.get("/push/vapid-public-key", summary="Llave pública VAPID para suscribirse a Web Push")
def vapid_key() -> dict[str, str]:
    return {"public_key": get_settings().vapid_public_key}


@router.post(
    "/push/subscriptions",
    response_model=PushSubscriptionOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar suscripción push",
)
def subscribe(body: PushSubscriptionIn, user: CurrentUser, db: DbSession) -> PushSubscription:
    """HU-15 / R15. Guarda la `PushSubscription` del navegador."""
    return reminder_service.add_subscription(db, user.id, body.model_dump())


@router.delete(
    "/push/subscriptions/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar suscripción"
)
def unsubscribe(subscription_id: uuid.UUID, user: CurrentUser, db: DbSession) -> None:
    reminder_service.remove_subscription(db, user.id, subscription_id)


@router.post(
    "/internal/reminders/tick",
    response_model=TickResponse,
    dependencies=[Depends(cron_guard)],
    tags=["Interno"],
    summary="Procesar recordatorios vencidos (cron)",
)
def tick(db: DbSession) -> dict[str, int]:
    """Requiere el header `X-Cron-Token`. Genera los recordatorios de las próximas 24 h y envía los vencidos."""
    return reminder_service.tick(db)
