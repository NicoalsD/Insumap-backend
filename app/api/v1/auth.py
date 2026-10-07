from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import CurrentUser, DbSession
from app.api.schemas import (
    ErrorResponse,
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserOut,
)
from app.core.config import get_settings
from app.db.models import User
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Autenticación"])
ERRORS = {400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}, 429: {"model": ErrorResponse}}


def _set_refresh_cookie(response: Response, refresh: str) -> None:
    s = get_settings()
    response.set_cookie(
        s.refresh_cookie_name,
        refresh,
        max_age=s.jwt_refresh_days * 86400,
        httponly=True,
        secure=s.cookie_secure,
        samesite=s.cookie_samesite,  # type: ignore[arg-type]
        path="/api/v1/auth",
    )


def _token_response(user: User, access: str) -> TokenResponse:
    return TokenResponse(
        access_token=access, expires_in=get_settings().jwt_access_minutes * 60, user=UserOut.model_validate(user)
    )


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"model": ErrorResponse}, **ERRORS},
    summary="Registrar cuenta (paciente o médico)",
)
def register(body: RegisterRequest, response: Response, db: DbSession) -> TokenResponse:
    """HU-20 / R20. Crea la cuenta e inicia sesión."""
    user = auth_service.register(
        db,
        name=body.name,
        email=body.email,
        password=body.password,
        role=body.role,
        accept_terms=body.accept_terms,
        license_number=body.license_number,
    )
    access, refresh = auth_service.issue_tokens(db, user)
    _set_refresh_cookie(response, refresh)
    return _token_response(user, access)


@router.post("/login", response_model=TokenResponse, responses=ERRORS, summary="Iniciar sesión")
def login(body: LoginRequest, request: Request, response: Response, db: DbSession) -> TokenResponse:
    """HU-21 / R21. Devuelve el access token y fija la cookie httpOnly de refresh."""
    user = auth_service.authenticate(db, body.email, body.password, request.client.host if request.client else "")
    access, refresh = auth_service.issue_tokens(db, user)
    _set_refresh_cookie(response, refresh)
    return _token_response(user, access)


@router.post("/token", response_model=TokenResponse, responses=ERRORS, summary="Login para Swagger (formulario)")
def token(
    form: Annotated[OAuth2PasswordRequestForm, Depends()], request: Request, response: Response, db: DbSession
) -> TokenResponse:
    """Mismo login en formato OAuth2 (`username` = email). Lo usa el botón **Authorize** de Swagger."""
    user = auth_service.authenticate(db, form.username, form.password, request.client.host if request.client else "")
    access, refresh = auth_service.issue_tokens(db, user)
    _set_refresh_cookie(response, refresh)
    return _token_response(user, access)


@router.post("/refresh", response_model=TokenResponse, responses=ERRORS, summary="Renovar sesión")
def refresh(response: Response, db: DbSession, insumap_rt: Annotated[str | None, Cookie()] = None) -> TokenResponse:
    """HU-22 / R22. Rota el refresh token de la cookie y emite un nuevo access token."""
    user, access, new_refresh = auth_service.rotate_refresh(db, insumap_rt)
    _set_refresh_cookie(response, new_refresh)
    return _token_response(user, access)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, summary="Cerrar sesión")
def logout(response: Response, db: DbSession, insumap_rt: Annotated[str | None, Cookie()] = None) -> Response:
    """HU-22 / R22. Revoca el refresh token y borra la cookie."""
    auth_service.logout(db, insumap_rt)
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.delete_cookie(get_settings().refresh_cookie_name, path="/api/v1/auth")
    return response


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Solicitar recuperación de contraseña",
)
def forgot_password(body: ForgotPasswordRequest, db: DbSession) -> MessageResponse:
    """HU-23 / R23. Responde igual exista o no el email."""
    auth_service.request_password_reset(db, body.email)
    return MessageResponse(message="Si el email existe, enviamos un enlace para restablecer la contraseña.")


@router.post("/reset-password", response_model=MessageResponse, responses=ERRORS, summary="Restablecer contraseña")
def reset_password(body: ResetPasswordRequest, db: DbSession) -> MessageResponse:
    """HU-23 / R23. Cambia la contraseña y cierra todas las sesiones."""
    auth_service.reset_password(db, body.token, body.new_password)
    return MessageResponse(message="Contraseña actualizada. Inicia sesión de nuevo.")


@router.get("/me", response_model=UserOut, responses=ERRORS, summary="Usuario actual")
def me(user: CurrentUser) -> User:
    return user
