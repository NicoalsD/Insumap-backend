"""Registration, login, refresh-token rotation and password reset (R20-R23)."""

from datetime import timedelta

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core import clock
from app.core.config import get_settings
from app.core.errors import AppError, bad_request, conflict, unauthorized
from app.core.rate_limit import SlidingWindowCounter
from app.core.security import (
    create_access_token,
    hash_password,
    new_opaque_token,
    sha256,
    verify_password,
)
from app.db.models import Doctor, PasswordResetToken, Patient, RefreshToken, Role, User
from app.services import email_service

_settings = get_settings()
login_attempts = SlidingWindowCounter(_settings.login_max_attempts, timedelta(minutes=_settings.login_window_minutes))


def register(
    db: Session, *, name: str, email: str, password: str, role: Role, accept_terms: bool, license_number: str | None
) -> User:
    if not accept_terms:
        raise bad_request("TERMS_NOT_ACCEPTED", "Debes aceptar los términos y el tratamiento de datos de salud.")
    email = email.lower()
    if db.scalar(select(User).where(User.email == email)) is not None:
        raise conflict("EMAIL_IN_USE", "Este email ya está registrado.")
    user = User(name=name, email=email, password_hash=hash_password(password), role=role)
    db.add(user)
    db.flush()
    if role == Role.PATIENT:
        db.add(Patient(user_id=user.id))
    else:
        db.add(Doctor(user_id=user.id, license_number=license_number))
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, email: str, password: str, client_ip: str) -> User:
    email = email.lower()
    key = f"{email}|{client_ip}"
    if login_attempts.is_blocked(key):
        raise AppError(429, "RATE_LIMITED", "Demasiados intentos. Intenta de nuevo en 15 minutos.")
    user = db.scalar(select(User).where(User.email == email))
    if user is None or not user.is_active or not verify_password(password, user.password_hash):
        login_attempts.hit(key)
        raise unauthorized("INVALID_CREDENTIALS", "Email o contraseña incorrectos.")
    login_attempts.reset(key)
    return user


def issue_tokens(db: Session, user: User) -> tuple[str, str]:
    """Return (access_token, refresh_token). Only the refresh token hash is stored."""
    refresh = new_opaque_token()
    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=sha256(refresh),
            expires_at=clock.now() + timedelta(days=_settings.jwt_refresh_days),
        )
    )
    db.commit()
    return create_access_token(str(user.id), user.role.value), refresh


def rotate_refresh(db: Session, refresh: str | None) -> tuple[User, str, str]:
    if not refresh:
        raise unauthorized("INVALID_REFRESH", "Sesión no encontrada. Inicia sesión de nuevo.")
    row = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == sha256(refresh)))
    if row is None or row.revoked_at is not None or row.expires_at <= clock.now():
        raise unauthorized("INVALID_REFRESH", "Tu sesión expiró. Inicia sesión de nuevo.")
    user = db.get(User, row.user_id)
    if user is None or not user.is_active:
        raise unauthorized("INVALID_REFRESH", "Tu sesión expiró. Inicia sesión de nuevo.")
    row.revoked_at = clock.now()
    access, new_refresh = issue_tokens(db, user)
    return user, access, new_refresh


def logout(db: Session, refresh: str | None) -> None:
    if not refresh:
        return
    row = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == sha256(refresh)))
    if row is not None and row.revoked_at is None:
        row.revoked_at = clock.now()
        db.commit()


def request_password_reset(db: Session, email: str) -> None:
    """Always succeeds from the caller's view, so it never reveals whether an account exists."""
    user = db.scalar(select(User).where(User.email == email.lower()))
    if user is None:
        return
    token = new_opaque_token()
    db.add(
        PasswordResetToken(user_id=user.id, token_hash=sha256(token), expires_at=clock.now() + timedelta(minutes=30))
    )
    db.commit()
    link = f"{_settings.frontend_url}/restablecer-contrasena?token={token}"
    email_service.send(
        user.email,
        "Insumap - Restablecer contraseña",
        f"Hola {user.name},\n\nPara restablecer tu contraseña abre este enlace (válido 30 minutos):\n{link}\n\n"
        "Si no lo solicitaste, ignora este mensaje.",
    )


def reset_password(db: Session, token: str, new_password: str) -> None:
    row = db.scalar(select(PasswordResetToken).where(PasswordResetToken.token_hash == sha256(token)))
    if row is None or row.used_at is not None or row.expires_at <= clock.now():
        raise bad_request("INVALID_RESET_TOKEN", "El enlace venció o ya fue usado. Solicita uno nuevo.")
    user = db.get(User, row.user_id)
    assert user is not None
    user.password_hash = hash_password(new_password)
    row.used_at = clock.now()
    db.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user.id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=clock.now())
    )
    db.commit()
