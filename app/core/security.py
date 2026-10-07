"""Password hashing (Argon2id) and JWT helpers."""

import hashlib
import secrets
from datetime import timedelta
from typing import Any

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

from app.core import clock
from app.core.config import get_settings

_hasher = PasswordHasher()

ACCESS = "access"
DELEGATED = "delegated"
ASSISTANT_READ_SCOPE = "assistant:read"


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except (VerifyMismatchError, InvalidHashError):
        return False


def new_opaque_token() -> str:
    return secrets.token_urlsafe(48)


def sha256(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def create_token(subject: str, role: str, kind: str, minutes: int, scope: str | None = None) -> str:
    s = get_settings()
    issued = clock.now()
    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "type": kind,
        "iat": int(issued.timestamp()),
        "exp": int((issued + timedelta(minutes=minutes)).timestamp()),
    }
    if scope:
        payload["scope"] = scope
    return jwt.encode(payload, s.jwt_secret, algorithm=s.jwt_algorithm)


def create_access_token(user_id: str, role: str) -> str:
    return create_token(user_id, role, ACCESS, get_settings().jwt_access_minutes)


def create_delegated_token(user_id: str, role: str) -> str:
    s = get_settings()
    return create_token(user_id, role, DELEGATED, s.delegated_token_minutes, ASSISTANT_READ_SCOPE)


def decode_token(token: str) -> dict[str, Any]:
    """Raises ``jwt.ExpiredSignatureError`` / ``jwt.InvalidTokenError``."""
    s = get_settings()
    data: dict[str, Any] = jwt.decode(
        token,
        s.jwt_secret,
        algorithms=[s.jwt_algorithm],
        options={"verify_exp": False, "verify_iat": False, "verify_nbf": False},
    )
    if int(data.get("exp", 0)) < int(clock.now().timestamp()):
        raise jwt.ExpiredSignatureError("Token expired")
    return data
