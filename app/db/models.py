"""ORM models. See docs/Modelo-de-datos.md."""

import uuid
from datetime import datetime, time
from enum import StrEnum
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import clock
from app.db.base import Base, JSONType, UTCDateTime


class Role(StrEnum):
    PATIENT = "PATIENT"
    DOCTOR = "DOCTOR"


class InjectionStatusDb(StrEnum):
    REGISTERED = "REGISTERED"
    UNDONE = "UNDONE"


class ColorDb(StrEnum):
    RED = "RED"
    YELLOW = "YELLOW"
    GREEN = "GREEN"


class InjectionOrigin(StrEnum):
    MAP = "MAP"
    SUGGESTION = "SUGGESTION"
    REMINDER = "REMINDER"
    ASSISTANT = "ASSISTANT"


class ReminderStatus(StrEnum):
    PENDING = "PENDING"
    SENT = "SENT"
    SNOOZED = "SNOOZED"
    CONFIRMED = "CONFIRMED"
    SKIPPED = "SKIPPED"


class MessageRole(StrEnum):
    USER = "USER"
    ASSISTANT = "ASSISTANT"
    TOOL = "TOOL"


def _enum(e: type[StrEnum], name: str) -> Enum:
    return Enum(e, name=name, native_enum=False, validate_strings=True, length=20)


def _uuid() -> uuid.UUID:
    return uuid.uuid4()


# --------------------------------------------------------------------------- identity
class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=_uuid)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(Text)
    role: Mapped[Role] = mapped_column(_enum(Role, "user_role"))
    name: Mapped[str] = mapped_column(String(120))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    accepted_terms_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=clock.now)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=clock.now)

    patient: Mapped["Patient | None"] = relationship(back_populates="user", uselist=False)
    doctor: Mapped["Doctor | None"] = relationship(back_populates="user", uselist=False)


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    expires_at: Mapped[datetime] = mapped_column(UTCDateTime())
    revoked_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=clock.now)


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    expires_at: Mapped[datetime] = mapped_column(UTCDateTime())
    used_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), nullable=True)


class Patient(Base):
    __tablename__ = "patients"
    __table_args__ = (CheckConstraint("grid_size IN (2, 4, 6)", name="grid_size"),)

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    grid_size: Mapped[int] = mapped_column(SmallInteger, default=4)
    timezone: Mapped[str] = mapped_column(String(40), default="America/Bogota")
    birth_date: Mapped[datetime | None] = mapped_column(UTCDateTime(), nullable=True)

    user: Mapped[User] = relationship(back_populates="patient")


class Doctor(Base):
    __tablename__ = "doctors"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    license_number: Mapped[str | None] = mapped_column(String(40), nullable=True)
    specialty: Mapped[str | None] = mapped_column(String(80), nullable=True)

    user: Mapped[User] = relationship(back_populates="doctor")


# --------------------------------------------------------------------------- doctor links
class LinkCode(Base):
    __tablename__ = "link_codes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=_uuid)
    patient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("patients.user_id", ondelete="CASCADE"), index=True)
    code: Mapped[str] = mapped_column(String(8), unique=True)
    expires_at: Mapped[datetime] = mapped_column(UTCDateTime())
    used_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), nullable=True)


class DoctorPatientLink(Base):
    __tablename__ = "doctor_patient_links"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=_uuid)
    doctor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("doctors.user_id", ondelete="CASCADE"), index=True)
    patient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("patients.user_id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=clock.now)
    revoked_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), nullable=True)


# --------------------------------------------------------------------------- clinical domain
class MacroZone(Base):
    __tablename__ = "macro_zones"

    code: Mapped[str] = mapped_column(String(3), primary_key=True)
    label: Mapped[str] = mapped_column(String(30))
    base_hours: Mapped[float] = mapped_column(Numeric(5, 1, asdecimal=False))
    display_order: Mapped[int] = mapped_column(SmallInteger)


class Injection(Base):
    __tablename__ = "injections"
    __table_args__ = (
        CheckConstraint("side IN ('I', 'D')", name="side"),
        Index("ix_injections_patient_registered", "patient_id", "registered_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=_uuid)
    patient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("patients.user_id", ondelete="CASCADE"), index=True)
    macro: Mapped[str] = mapped_column(ForeignKey("macro_zones.code"))
    side: Mapped[str] = mapped_column(String(1))
    row: Mapped[int] = mapped_column(SmallInteger)
    col: Mapped[int] = mapped_column(SmallInteger)
    grid_size: Mapped[int] = mapped_column(SmallInteger)
    microzone_id: Mapped[str] = mapped_column(String(12), index=True)
    applied_at: Mapped[datetime] = mapped_column(UTCDateTime())
    registered_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=clock.now)
    status: Mapped[InjectionStatusDb] = mapped_column(
        _enum(InjectionStatusDb, "injection_status"), default=InjectionStatusDb.REGISTERED
    )
    undone_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), nullable=True)
    color_at_registration: Mapped[ColorDb] = mapped_column(_enum(ColorDb, "color"))
    warning_accepted: Mapped[bool] = mapped_column(Boolean, default=False)
    previous_last_used: Mapped[datetime | None] = mapped_column(UTCDateTime(), nullable=True)
    origin: Mapped[InjectionOrigin] = mapped_column(_enum(InjectionOrigin, "injection_origin"))


class AlgorithmParam(Base):
    __tablename__ = "algorithm_params"

    key: Mapped[str] = mapped_column(String(40), primary_key=True)
    value: Mapped[Any] = mapped_column(JSONType)
    description: Mapped[str] = mapped_column(Text, default="")
    clinically_validated: Mapped[bool] = mapped_column(Boolean, default=False)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=clock.now, onupdate=clock.now)


# --------------------------------------------------------------------------- reminders
class DoseSchedule(Base):
    __tablename__ = "dose_schedules"
    __table_args__ = (UniqueConstraint("patient_id", "time", name="uq_dose_schedules_patient_time"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=_uuid)
    patient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("patients.user_id", ondelete="CASCADE"), index=True)
    time: Mapped[time] = mapped_column(Time())
    label: Mapped[str | None] = mapped_column(String(40), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Reminder(Base):
    __tablename__ = "reminders"
    __table_args__ = (UniqueConstraint("schedule_id", "scheduled_for", name="uq_reminders_schedule_slot"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=_uuid)
    patient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("patients.user_id", ondelete="CASCADE"), index=True)
    schedule_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("dose_schedules.id", ondelete="CASCADE"))
    scheduled_for: Mapped[datetime] = mapped_column(UTCDateTime(), index=True)
    due_at: Mapped[datetime] = mapped_column(UTCDateTime(), index=True)
    status: Mapped[ReminderStatus] = mapped_column(
        _enum(ReminderStatus, "reminder_status"), default=ReminderStatus.PENDING
    )
    sent_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), nullable=True)
    confirmed_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), nullable=True)
    snooze_count: Mapped[int] = mapped_column(SmallInteger, default=0)
    injection_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("injections.id", ondelete="SET NULL"), nullable=True
    )


class PushSubscription(Base):
    __tablename__ = "push_subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    endpoint: Mapped[str] = mapped_column(Text, unique=True)
    p256dh: Mapped[str] = mapped_column(Text)
    auth: Mapped[str] = mapped_column(Text)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=clock.now)


# --------------------------------------------------------------------------- assistant
class AssistantMessage(Base):
    __tablename__ = "assistant_messages"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=_uuid)
    patient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("patients.user_id", ondelete="CASCADE"), index=True)
    role: Mapped[MessageRole] = mapped_column(_enum(MessageRole, "message_role"))
    content: Mapped[str] = mapped_column(Text)
    tool_name: Mapped[str | None] = mapped_column(String(40), nullable=True)
    provider: Mapped[str | None] = mapped_column(String(40), nullable=True)
    model: Mapped[str | None] = mapped_column(String(60), nullable=True)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    blocked_by_guardrail: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=clock.now, index=True)
