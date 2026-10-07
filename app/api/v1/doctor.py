from typing import Any

from fastapi import APIRouter, status

from app.api.deps import CurrentDoctor, CurrentPatient, CurrentUser, DbSession, LinkedPatient
from app.api.schemas import ErrorResponse, LinkCodeOut, LinkCreate, LinkOut, MapResponse
from app.db.models import LinkCode
from app.services import injection_service, link_service

router = APIRouter(tags=["Médico"])
ERRORS = {400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}}


@router.post(
    "/links/codes",
    response_model=LinkCodeOut,
    status_code=status.HTTP_201_CREATED,
    responses=ERRORS,
    summary="Paciente: generar código de vínculo",
)
def create_code(patient: CurrentPatient, db: DbSession) -> LinkCode:
    """HU-24. Código de 8 caracteres, un solo uso, válido 48 h."""
    return link_service.create_code(db, patient)


@router.post(
    "/links",
    response_model=LinkOut,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"model": ErrorResponse}, **ERRORS},
    summary="Médico: vincularse con un código",
)
def redeem(body: LinkCreate, doctor: CurrentDoctor, user: CurrentUser, db: DbSession) -> dict[str, Any]:
    link = link_service.redeem(db, doctor, body.code)
    return next(x for x in link_service.list_links(db, user) if x["id"] == link.id)


@router.get("/links", response_model=list[LinkOut], responses=ERRORS, summary="Listar vínculos")
def list_links(user: CurrentUser, db: DbSession) -> list[dict[str, Any]]:
    """Paciente: sus médicos. Médico: sus pacientes (HU-24, 25)."""
    return link_service.list_links(db, user)


@router.delete(
    "/links/{link_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=ERRORS,
    summary="Paciente: revocar acceso de un médico",
)
def revoke(link_id: str, patient: CurrentPatient, db: DbSession) -> None:
    """HU-27 / R27. Revocación inmediata."""
    import uuid

    link_service.revoke(db, patient, uuid.UUID(link_id))


@router.get(
    "/doctor/patients/{patient_id}/map",
    response_model=MapResponse,
    responses=ERRORS,
    summary="Médico: mapa del paciente",
)
def patient_map(patient: LinkedPatient, db: DbSession) -> dict[str, Any]:
    """HU-25 / R25. Solo lectura."""
    return injection_service.body_map(db, patient)
