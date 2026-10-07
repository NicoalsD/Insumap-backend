from typing import Any

from fastapi import APIRouter, status

from app.api.deps import CurrentPatient, DbSession
from app.api.schemas import ErrorResponse, InjectionCreate, InjectionResult
from app.services import injection_service

router = APIRouter(prefix="/injections", tags=["Inyecciones"])
ERRORS = {400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}, 409: {"model": ErrorResponse}}


@router.post(
    "",
    response_model=InjectionResult,
    status_code=status.HTTP_201_CREATED,
    responses=ERRORS,
    summary="Registrar inyección",
)
def register_injection(body: InjectionCreate, patient: CurrentPatient, db: DbSession) -> dict[str, Any]:
    """HU-03, 04, 08, 09. Si la microzona no está en GREEN responde **409 MICROZONE_NOT_RECOVERED**
    hasta que se envíe `confirm_not_recovered: true`."""
    return injection_service.register(
        db, patient, body.microzone_id, body.applied_at, body.confirm_not_recovered, body.origin, body.reminder_id
    )


@router.post("/undo", response_model=InjectionResult, responses=ERRORS, summary="Deshacer último registro")
def undo(patient: CurrentPatient, db: DbSession) -> dict[str, Any]:
    """HU-05, 06. Desapila el último registro (pila E3) y restaura el estado previo de la microzona."""
    return injection_service.undo_last(db, patient)
