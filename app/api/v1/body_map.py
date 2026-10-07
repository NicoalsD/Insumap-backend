from typing import Annotated, Any, Literal

from fastapi import APIRouter, Path, Query

from app.api.deps import CurrentPatient, DbSession, ReadingPatient
from app.api.schemas import ErrorResponse, GridSettingsRequest, MapResponse, MicrozoneDetail, SuggestionsResponse
from app.services import injection_service

router = APIRouter(tags=["Mapa y sugerencias"])
ERRORS = {400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}}


@router.get("/map", response_model=MapResponse, responses=ERRORS, summary="Mapa corporal con colores")
def get_map(
    patient: ReadingPatient,
    db: DbSession,
    macro: Annotated[Literal["ABD", "MUS", "BRA", "GLU"] | None, Query(description="Filtrar por zona macro")] = None,
) -> dict[str, Any]:
    """HU-01, 02, 07, 10. Estado de cada microzona: color, ratio y horas restantes."""
    return injection_service.body_map(db, patient, macro)


@router.get(
    "/microzones/{microzone_id}", response_model=MicrozoneDetail, responses=ERRORS, summary="Detalle de microzona"
)
def get_microzone(
    patient: ReadingPatient,
    db: DbSession,
    microzone_id: Annotated[str, Path(examples=["ABD-I-2-3"])],
) -> dict[str, Any]:
    """Estado de la microzona y sus últimas 5 aplicaciones."""
    return injection_service.microzone_detail(db, patient, microzone_id)


@router.put("/settings/grid", response_model=MapResponse, responses=ERRORS, summary="Cambiar tamaño de cuadrícula")
def set_grid(body: GridSettingsRequest, patient: CurrentPatient, db: DbSession) -> dict[str, Any]:
    """HU-02 / R02. El historial se proyecta a la nueva cuadrícula."""
    return injection_service.set_grid_size(db, patient, body.grid_size)


@router.get("/suggestions", response_model=SuggestionsResponse, responses=ERRORS, summary="Sugerir punto óptimo")
def get_suggestions(
    patient: ReadingPatient, db: DbSession, k: Annotated[int, Query(ge=1, le=10)] = 3
) -> dict[str, Any]:
    """HU-11, 12, 13. Top-k del max-heap con el desglose del score."""
    return {"suggestions": injection_service.suggestions(db, patient, k)}
