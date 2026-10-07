"""Dose schedule, reminder generation, Web Push and the min-heap scheduler (R14-R16)."""

import json
import logging
import uuid
from datetime import datetime, time, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core import clock
from app.core.config import get_settings
from app.core.errors import bad_request, conflict, not_found
from app.db.models import DoseSchedule, Patient, PushSubscription, Reminder, ReminderStatus
from app.domain.algorithms.scheduler import ReminderScheduler

log = logging.getLogger("insumap.reminders")
scheduler = ReminderScheduler()  # process-wide min-heap (single instance deployment)

ACTIVE = (ReminderStatus.PENDING, ReminderStatus.SNOOZED)
HORIZON = timedelta(hours=24)


# --------------------------------------------------------------------------- schedule
def get_schedule(db: Session, patient: Patient) -> list[DoseSchedule]:
    stmt = (
        select(DoseSchedule)
        .where(DoseSchedule.patient_id == patient.user_id, DoseSchedule.is_active.is_(True))
        .order_by(DoseSchedule.time)
    )
    return list(db.scalars(stmt))


def save_schedule(db: Session, patient: Patient, doses: list[tuple[time, str | None]]) -> list[DoseSchedule]:
    times = [t.replace(second=0, microsecond=0) for t, _ in doses]
    if len(set(times)) != len(times):
        raise bad_request("DUPLICATED_DOSE_TIME", "Hay horas de dosis repetidas.")
    existing = {s.time: s for s in db.scalars(select(DoseSchedule).where(DoseSchedule.patient_id == patient.user_id))}
    wanted = dict(zip(times, (label for _, label in doses), strict=True))
    now = clock.now()
    for t, sched in existing.items():
        if t not in wanted and sched.is_active:
            sched.is_active = False
            for r in db.scalars(select(Reminder).where(Reminder.schedule_id == sched.id, Reminder.status.in_(ACTIVE))):
                scheduler.cancel(str(r.id))
            db.execute(
                delete(Reminder).where(
                    Reminder.schedule_id == sched.id, Reminder.status.in_(ACTIVE), Reminder.due_at > now
                )
            )
    for t, label in wanted.items():
        if t in existing:
            existing[t].is_active = True
            existing[t].label = label
        else:
            db.add(DoseSchedule(patient_id=patient.user_id, time=t, label=label))
    db.commit()
    ensure_upcoming(db, patient_ids=[patient.user_id])
    return get_schedule(db, patient)


# --------------------------------------------------------------------------- reminders
def _slots(sched: DoseSchedule, tz: ZoneInfo, now: datetime) -> list[datetime]:
    local_today = now.astimezone(tz).date()
    result = []
    for day in (local_today, local_today + timedelta(days=1)):
        slot = datetime.combine(day, sched.time, tzinfo=tz).astimezone(now.tzinfo)
        if now <= slot <= now + HORIZON:
            result.append(slot)
    return result


def ensure_upcoming(db: Session, patient_ids: list[uuid.UUID] | None = None) -> int:
    """Create reminders for the next 24 h (idempotent) and push them into the min-heap."""
    now = clock.now()
    stmt = select(DoseSchedule, Patient).join(Patient, Patient.user_id == DoseSchedule.patient_id)
    stmt = stmt.where(DoseSchedule.is_active.is_(True))
    if patient_ids is not None:
        stmt = stmt.where(DoseSchedule.patient_id.in_(patient_ids))
    created = 0
    for sched, patient in db.execute(stmt).all():
        tz = ZoneInfo(patient.timezone)
        for slot in _slots(sched, tz, now):
            exists = db.scalar(
                select(Reminder.id).where(Reminder.schedule_id == sched.id, Reminder.scheduled_for == slot)
            )
            if exists is None:
                r = Reminder(patient_id=patient.user_id, schedule_id=sched.id, scheduled_for=slot, due_at=slot)
                db.add(r)
                db.flush()
                scheduler.schedule(str(r.id), slot)
                created += 1
    db.commit()
    return created


def load_scheduler(db: Session) -> int:
    """Rebuild the in-memory heap from the database (process start)."""
    scheduler.clear()
    now = clock.now()
    rows = db.scalars(select(Reminder).where(Reminder.status.in_(ACTIVE), Reminder.due_at >= now - timedelta(hours=1)))
    count = 0
    for r in rows:
        scheduler.schedule(str(r.id), r.due_at)
        count += 1
    return count


def tick(db: Session) -> dict[str, int]:
    created = ensure_upcoming(db)
    sent = 0
    for rid in scheduler.due(clock.now()):
        r = db.get(Reminder, uuid.UUID(rid))
        if r is None or r.status not in ACTIVE:
            continue
        _notify(db, r)
        r.status = ReminderStatus.SENT
        r.sent_at = clock.now()
        sent += 1
    db.commit()
    return {"reminders_created": created, "reminders_sent": sent}


def _own(db: Session, patient: Patient, reminder_id: uuid.UUID) -> Reminder:
    r = db.get(Reminder, reminder_id)
    if r is None or r.patient_id != patient.user_id:
        raise not_found("Recordatorio no encontrado.")
    return r


def upcoming(db: Session, patient: Patient) -> list[Reminder]:
    stmt = (
        select(Reminder)
        .where(
            Reminder.patient_id == patient.user_id,
            Reminder.status.in_((*ACTIVE, ReminderStatus.SENT)),
            Reminder.due_at >= clock.now() - timedelta(hours=2),
        )
        .order_by(Reminder.due_at)
        .limit(10)
    )
    return list(db.scalars(stmt))


def snooze(db: Session, patient: Patient, reminder_id: uuid.UUID, minutes: int) -> Reminder:
    r = _own(db, patient, reminder_id)
    if r.status not in (*ACTIVE, ReminderStatus.SENT):
        raise conflict("REMINDER_CLOSED", "Este recordatorio ya fue confirmado u omitido.")
    r.due_at = clock.now() + timedelta(minutes=minutes)
    r.status = ReminderStatus.SNOOZED
    r.snooze_count += 1
    db.commit()
    scheduler.snooze(str(r.id), r.due_at)
    return r


def confirm(db: Session, patient: Patient, reminder_id: uuid.UUID) -> Reminder:
    r = _own(db, patient, reminder_id)
    if r.status == ReminderStatus.SKIPPED:
        raise conflict("REMINDER_CLOSED", "Este recordatorio fue omitido.")
    r.status = ReminderStatus.CONFIRMED
    r.confirmed_at = clock.now()
    db.commit()
    scheduler.cancel(str(r.id))
    return r


# --------------------------------------------------------------------------- web push
def add_subscription(db: Session, user_id: uuid.UUID, data: dict[str, Any]) -> PushSubscription:
    sub = db.scalar(select(PushSubscription).where(PushSubscription.endpoint == data["endpoint"]))
    if sub is None:
        sub = PushSubscription(user_id=user_id, **data)
        db.add(sub)
    else:
        sub.user_id, sub.p256dh, sub.auth = user_id, data["p256dh"], data["auth"]
    db.commit()
    return sub


def remove_subscription(db: Session, user_id: uuid.UUID, sub_id: uuid.UUID) -> None:
    sub = db.get(PushSubscription, sub_id)
    if sub is None or sub.user_id != user_id:
        raise not_found("Suscripción no encontrada.")
    db.delete(sub)
    db.commit()


def _notify(db: Session, r: Reminder) -> None:
    s = get_settings()
    subs = list(db.scalars(select(PushSubscription).where(PushSubscription.user_id == r.patient_id)))
    payload = json.dumps(
        {
            "type": "dose_reminder",
            "reminder_id": str(r.id),
            "title": "Insumap",
            "body": "Es hora de tu dosis. Toca para ver la zona sugerida.",
        }
    )
    if not s.vapid_private_key:
        log.warning("VAPID not configured; reminder %s not pushed (%d subscriptions)", r.id, len(subs))
        return
    from pywebpush import WebPushException, webpush

    for sub in subs:
        try:
            webpush(
                subscription_info={"endpoint": sub.endpoint, "keys": {"p256dh": sub.p256dh, "auth": sub.auth}},
                data=payload,
                vapid_private_key=s.vapid_private_key,
                vapid_claims={"sub": s.vapid_subject},
            )
        except WebPushException as exc:
            status = getattr(exc.response, "status_code", None)
            if status in (404, 410):
                db.delete(sub)
            log.warning("Web Push failed for %s: %s", sub.endpoint[:40], exc)
