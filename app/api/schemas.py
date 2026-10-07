"""Request/response schemas. Field descriptions are user-facing documentation (Spanish)."""

import uuid
from datetime import datetime
from datetime import time as TimeOfDay
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.db.models import InjectionOrigin, ReminderStatus, Role


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------------------------------- errors
class ErrorBody(BaseModel):
    code: str = Field(examples=["MICROZONE_NOT_RECOVERED"])
    message: str = Field(examples=["La microzona ABD-I-1-1 aún no se ha recuperado (RED)."])
    detail: dict[str, object] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    error: ErrorBody


# --------------------------------------------------------------------------- auth
class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120, description="Nombre visible del usuario")
    email: EmailStr
    password: str = Field(min_length=8, max_length=128, description="Mínimo 8 caracteres y al menos un número")
    role: Role = Field(description="PATIENT (paciente) o DOCTOR (médico)")
    accept_terms: bool = Field(description="Acepta términos y tratamiento de datos de salud (obligatorio)")
    license_number: str | None = Field(default=None, max_length=40, description="Registro profesional (médicos)")

    @field_validator("password")
    @classmethod
    def _has_digit(cls, v: str) -> str:
        if not any(ch.isdigit() for ch in v):
            raise ValueError("La contraseña debe contener al menos un número")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(ORMModel):
    id: uuid.UUID
    name: str
    email: str
    role: Role


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int = Field(description="Segundos de vigencia del access token")
    user: UserOut


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def _has_digit(cls, v: str) -> str:
        if not any(ch.isdigit() for ch in v):
            raise ValueError("La contraseña debe contener al menos un número")
        return v


class MessageResponse(BaseModel):
    message: str


# --------------------------------------------------------------------------- map
class CellOut(BaseModel):
    id: str = Field(examples=["ABD-I-2-3"])
    row: int
    col: int
    color: Literal["RED", "YELLOW", "GREEN"]
    ratio: float
    hours_remaining: float = Field(description="Horas estimadas hasta que la microzona vuelva a VERDE")
    last_used: datetime | None
    uses_30d: int


class SideOut(BaseModel):
    side: Literal["I", "D"]
    cells: list[CellOut]


class ZoneOut(BaseModel):
    macro: str
    label: str
    sides: list[SideOut]


class MapResponse(BaseModel):
    grid_size: int
    generated_at: datetime
    zones: list[ZoneOut]


class GridSettingsRequest(BaseModel):
    grid_size: Literal[2, 4, 6] = Field(description="Tamaño de la cuadrícula por lado (2x2, 4x4 o 6x6)")


class InjectionOut(BaseModel):
    id: str
    microzone_id: str
    macro: str
    side: str
    applied_at: datetime
    registered_at: datetime
    status: Literal["REGISTERED", "UNDONE"]
    undone_at: datetime | None = None


class MicrozoneDetail(BaseModel):
    microzone: CellOut
    latest: list[InjectionOut]


# --------------------------------------------------------------------------- injections
class InjectionCreate(BaseModel):
    microzone_id: str = Field(examples=["MUS-I-1-2"], description="ID de la microzona en la cuadrícula vigente")
    applied_at: datetime | None = Field(default=None, description="Momento de aplicación; por defecto, ahora")
    confirm_not_recovered: bool = Field(
        default=False, description="Confirmar el registro aunque la microzona no esté en VERDE (R04)"
    )
    origin: InjectionOrigin = InjectionOrigin.MAP
    reminder_id: uuid.UUID | None = None


class InjectionResult(BaseModel):
    injection: InjectionOut
    microzone: CellOut
    can_undo: bool


# --------------------------------------------------------------------------- suggestions
class SuggestionBreakdown(BaseModel):
    ratio: float
    forgotten_bonus: float
    overuse_penalty: float
    neighbor_penalty: float


class SuggestionOut(BaseModel):
    microzone_id: str
    score: float
    color: Literal["RED", "YELLOW", "GREEN"]
    breakdown: SuggestionBreakdown


class SuggestionsResponse(BaseModel):
    suggestions: list[SuggestionOut]


# --------------------------------------------------------------------------- history
class HistoryPage(BaseModel):
    items: list[InjectionOut]
    next_cursor: str | None = Field(description="Pasar como `cursor` para obtener la siguiente página")


# --------------------------------------------------------------------------- schedule / reminders
class DoseIn(BaseModel):
    time: TimeOfDay = Field(examples=["07:00"])
    label: str | None = Field(default=None, max_length=40, examples=["Antes del desayuno"])


class ScheduleRequest(BaseModel):
    doses: list[DoseIn] = Field(min_length=1, max_length=6)


class DoseOut(ORMModel):
    id: uuid.UUID
    time: TimeOfDay
    label: str | None
    is_active: bool


class ScheduleResponse(BaseModel):
    timezone: str
    doses: list[DoseOut]


class ReminderOut(ORMModel):
    id: uuid.UUID
    scheduled_for: datetime
    due_at: datetime
    status: ReminderStatus
    snooze_count: int


class SnoozeRequest(BaseModel):
    minutes: int = Field(ge=5, le=120, description="Minutos a posponer (5 a 120)")


class ConfirmResponse(BaseModel):
    reminder: ReminderOut
    suggested_microzone_id: str | None


class PushSubscriptionIn(BaseModel):
    endpoint: str
    p256dh: str
    auth: str
    user_agent: str | None = None


class PushSubscriptionOut(ORMModel):
    id: uuid.UUID
    endpoint: str
    created_at: datetime


class TickResponse(BaseModel):
    reminders_created: int
    reminders_sent: int


# --------------------------------------------------------------------------- links
class LinkCodeOut(ORMModel):
    code: str
    expires_at: datetime


class LinkCreate(BaseModel):
    code: str = Field(min_length=8, max_length=9, examples=["K7QX2M9A"], description="Código entregado por el paciente")


class LinkOut(BaseModel):
    id: uuid.UUID
    doctor_id: uuid.UUID
    doctor_name: str
    patient_id: uuid.UUID
    patient_name: str
    created_at: datetime


# --------------------------------------------------------------------------- assistant
class AssistantMessageIn(BaseModel):
    message: str = Field(min_length=1, max_length=500, examples=["¿Dónde me inyecto ahora?"])


class AssistantReply(BaseModel):
    reply: str
    referenced_microzones: list[str]
    source: str = Field(description="Modelo que respondió o `template` en modo degradado")
    degraded: bool


class AssistantMessageOut(ORMModel):
    id: uuid.UUID
    role: str
    content: str
    created_at: datetime
