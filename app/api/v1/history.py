from datetime import date
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Query, Response

from app.api.deps import CurrentPatient, DbSession, LinkedPatient
from app.api.schemas import ErrorResponse, HistoryPage
from app.db.models import Patient
from app.services import history_service

router = APIRouter(tags=["Historial"])
ERRORS = {400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}}
Macro = Literal["ABD", "MUS", "BRA", "GLU"]
Format = Literal["pdf", "xlsx", "csv"]


def _page(
    db: Any,
    patient: Patient,
    cursor: str | None,
    limit: int,
    order: str,
    macro: str | None,
    date_from: date | None,
    date_to: date | None,
) -> dict[str, Any]:
    return history_service.page(db, patient, cursor, limit, order, macro, date_from, date_to)


def _export(db: Any, patient: Patient, fmt: str, date_from: date | None, date_to: date | None) -> Response:
    content, media_type, filename = history_service.export(db, patient, fmt, date_from, date_to)
    return Response(
        content, media_type=media_type, headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/history", response_model=HistoryPage, responses=ERRORS, summary="Consultar historial")
def get_history(
    patient: CurrentPatient,
    db: DbSession,
    cursor: str | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    order: Literal["desc", "asc"] = "desc",
    macro: Macro | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> dict[str, Any]:
    """HU-17, 18. Paginación por cursor sobre la lista doblemente enlazada (E5)."""
    return _page(db, patient, cursor, limit, order, macro, date_from, date_to)


@router.get(
    "/history/export",
    responses={200: {"content": {"application/pdf": {}, "text/csv": {}}}, 409: {"model": ErrorResponse}, **ERRORS},
    response_class=Response,
    summary="Exportar historial",
)
def export_history(
    patient: CurrentPatient,
    db: DbSession,
    format: Format = "pdf",
    date_from: date | None = None,
    date_to: date | None = None,
) -> Response:
    """HU-19. Archivo PDF, Excel o CSV con fecha, hora, microzona, zona macro y estado."""
    return _export(db, patient, format, date_from, date_to)


@router.get(
    "/doctor/patients/{patient_id}/history",
    response_model=HistoryPage,
    responses=ERRORS,
    tags=["Médico"],
    summary="Médico: historial del paciente",
)
def doctor_history(
    patient: LinkedPatient,
    db: DbSession,
    cursor: str | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    order: Literal["desc", "asc"] = "desc",
    macro: Macro | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> dict[str, Any]:
    """HU-26 / R26. Solo lectura y solo si hay un vínculo activo."""
    return _page(db, patient, cursor, limit, order, macro, date_from, date_to)


@router.get(
    "/doctor/patients/{patient_id}/history/export",
    responses={409: {"model": ErrorResponse}, **ERRORS},
    response_class=Response,
    tags=["Médico"],
    summary="Médico: exportar historial del paciente",
)
def doctor_export(
    patient: LinkedPatient,
    db: DbSession,
    format: Format = "pdf",
    date_from: date | None = None,
    date_to: date | None = None,
) -> Response:
    return _export(db, patient, format, date_from, date_to)
