"""FastAPI application. Swagger UI: /docs · ReDoc: /redoc · OpenAPI: /openapi.json"""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.errors import register_error_handlers
from app.db.seed import seed
from app.db.session import SessionLocal
from app.services import reminder_service

log = logging.getLogger("insumap")

DESCRIPTION = """
API de **Insumap**: rotación de zonas de inyección de insulina.

**Cómo probar en Swagger**
1. Pulsa **Authorize** e inicia sesión con `paciente@demo.insumap` / `Insumap123`
   (o `medico@demo.insumap`). También puedes registrarte en `POST /api/v1/auth/register`.
2. Consulta `GET /api/v1/map` y `GET /api/v1/suggestions`.
3. Registra con `POST /api/v1/injections` y deshaz con `POST /api/v1/injections/undo`.

Errores: `{"error": {"code", "message", "detail"}}`. Documentación completa en `docs/`.

> Proyecto académico. No es un dispositivo médico; los parámetros de recuperación
> están pendientes de validación clínica.
"""


def _start_background_scheduler() -> object | None:
    from apscheduler.schedulers.background import BackgroundScheduler

    def job() -> None:
        with SessionLocal() as db:
            reminder_service.tick(db)

    bg = BackgroundScheduler(timezone="UTC")
    bg.add_job(job, "interval", seconds=60, id="reminders-tick", max_instances=1, coalesce=True)
    bg.start()
    return bg


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    bg = None
    try:
        with SessionLocal() as db:
            seed(db)
            loaded = reminder_service.load_scheduler(db)
            log.info("Reminder heap loaded with %d entries", loaded)
    except Exception as exc:  # database not migrated yet
        log.warning("Could not load reminders: %s", exc)
    if settings.scheduler_enabled:
        bg = _start_background_scheduler()
    yield
    if bg is not None:
        bg.shutdown(wait=False)  # type: ignore[attr-defined]


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description=DESCRIPTION,
        lifespan=lifespan,
        swagger_ui_parameters={"persistAuthorization": True, "displayRequestDuration": True},
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_error_handlers(app)
    app.include_router(api_router)

    @app.get("/health", tags=["Interno"], summary="Estado del servicio")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
