"""Uniform error format: {"error": {"code", "message", "detail"}}.

``code`` is a stable English identifier for clients; ``message`` is user-facing (Spanish).
"""

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppError(Exception):
    def __init__(self, status_code: int, code: str, message: str, detail: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.detail = detail or {}


def not_found(message: str = "Recurso no encontrado.") -> AppError:
    return AppError(status.HTTP_404_NOT_FOUND, "NOT_FOUND", message)


def forbidden(message: str = "No tienes permiso para realizar esta acción.") -> AppError:
    return AppError(status.HTTP_403_FORBIDDEN, "FORBIDDEN", message)


def unauthorized(code: str = "NOT_AUTHENTICATED", message: str = "Debes iniciar sesión.") -> AppError:
    return AppError(status.HTTP_401_UNAUTHORIZED, code, message)


def conflict(code: str, message: str, detail: dict[str, Any] | None = None) -> AppError:
    return AppError(status.HTTP_409_CONFLICT, code, message, detail)


def bad_request(code: str, message: str, detail: dict[str, Any] | None = None) -> AppError:
    return AppError(status.HTTP_400_BAD_REQUEST, code, message, detail)


def _body(code: str, message: str, detail: Any = None) -> dict[str, Any]:
    return {"error": {"code": code, "message": message, "detail": detail or {}}}


_STATUS_CODES = {
    401: ("NOT_AUTHENTICATED", "Debes iniciar sesión."),
    403: ("FORBIDDEN", "No tienes permiso para realizar esta acción."),
    404: ("NOT_FOUND", "Recurso no encontrado."),
    405: ("METHOD_NOT_ALLOWED", "Método no permitido."),
}


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error(_: Request, exc: AppError) -> JSONResponse:
        headers = {"WWW-Authenticate": "Bearer"} if exc.status_code == 401 else None
        return JSONResponse(_body(exc.code, exc.message, exc.detail), status_code=exc.status_code, headers=headers)

    @app.exception_handler(RequestValidationError)
    async def _validation(_: Request, exc: RequestValidationError) -> JSONResponse:
        errors = [{"field": ".".join(str(p) for p in e["loc"][1:]), "message": e["msg"]} for e in exc.errors()]
        return JSONResponse(
            _body("VALIDATION_ERROR", "Los datos enviados no son válidos.", {"errors": errors}), status_code=400
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        code, message = _STATUS_CODES.get(exc.status_code, ("HTTP_ERROR", str(exc.detail)))
        return JSONResponse(_body(code, message), status_code=exc.status_code, headers=exc.headers)
