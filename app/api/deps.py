"""FastAPI dependencies: database session and authenticated user / role guards."""

import uuid
from dataclasses import dataclass
from typing import Annotated

import jwt
from fastapi import Depends, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import forbidden, unauthorized
from app.core.security import ACCESS, ASSISTANT_READ_SCOPE, DELEGATED, decode_token
from app.db.models import Doctor, DoctorPatientLink, Patient, Role, User
from app.db.session import get_db

# tokenUrl points to the form-based endpoint so Swagger's "Authorize" button can log in.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)

DbSession = Annotated[Session, Depends(get_db)]


@dataclass
class Principal:
    user: User
    token_type: str


def _principal(db: Session, token: str | None, allow_delegated: bool) -> Principal:
    if not token:
        raise unauthorized()
    try:
        payload = decode_token(token)
    except jwt.ExpiredSignatureError as exc:
        raise unauthorized("TOKEN_EXPIRED", "Tu sesión expiró. Vuelve a iniciar sesión.") from exc
    except jwt.InvalidTokenError as exc:
        raise unauthorized("INVALID_TOKEN", "Token inválido.") from exc
    kind = payload.get("type")
    if kind == DELEGATED:
        if not allow_delegated or payload.get("scope") != ASSISTANT_READ_SCOPE:
            raise forbidden("Este token solo permite lecturas del asistente.")
    elif kind != ACCESS:
        raise unauthorized("INVALID_TOKEN", "Token inválido.")
    user = db.get(User, uuid.UUID(payload["sub"]))
    if user is None or not user.is_active:
        raise unauthorized("INVALID_TOKEN", "Usuario no encontrado o inactivo.")
    return Principal(user, kind)


def current_user(db: DbSession, token: Annotated[str | None, Depends(oauth2_scheme)]) -> User:
    return _principal(db, token, allow_delegated=False).user


CurrentUser = Annotated[User, Depends(current_user)]


def current_patient(user: CurrentUser) -> Patient:
    if user.role != Role.PATIENT or user.patient is None:
        raise forbidden("Esta acción es solo para pacientes.")
    return user.patient


def reading_patient(db: DbSession, token: Annotated[str | None, Depends(oauth2_scheme)]) -> Patient:
    """Patient for read endpoints: accepts access tokens and the assistant's delegated token."""
    user = _principal(db, token, allow_delegated=True).user
    if user.role != Role.PATIENT or user.patient is None:
        raise forbidden("Esta acción es solo para pacientes.")
    return user.patient


def current_doctor(user: CurrentUser) -> Doctor:
    if user.role != Role.DOCTOR or user.doctor is None:
        raise forbidden("Esta acción es solo para médicos.")
    return user.doctor


CurrentPatient = Annotated[Patient, Depends(current_patient)]
ReadingPatient = Annotated[Patient, Depends(reading_patient)]
CurrentDoctor = Annotated[Doctor, Depends(current_doctor)]


def linked_patient(patient_id: uuid.UUID, doctor: CurrentDoctor, db: DbSession) -> Patient:
    """The patient, only if the doctor has an active link with them (RNF-03)."""
    link = (
        db.query(DoctorPatientLink)
        .filter(
            DoctorPatientLink.doctor_id == doctor.user_id,
            DoctorPatientLink.patient_id == patient_id,
            DoctorPatientLink.revoked_at.is_(None),
        )
        .first()
    )
    patient = db.get(Patient, patient_id)
    if link is None or patient is None:
        raise forbidden("No estás vinculado con este paciente.")
    return patient


LinkedPatient = Annotated[Patient, Depends(linked_patient)]


def cron_guard(x_cron_token: Annotated[str | None, Header()] = None) -> None:
    if x_cron_token != get_settings().cron_token:
        raise unauthorized("INVALID_CRON_TOKEN", "Token de cron inválido.")
