from typing import Annotated, Any

from fastapi import APIRouter, Query

from app.api.deps import CurrentPatient, DbSession
from app.api.schemas import AssistantMessageIn, AssistantMessageOut, AssistantReply, ErrorResponse
from app.db.models import AssistantMessage
from app.services import assistant_service

router = APIRouter(prefix="/assistant", tags=["Asistente IA"])


@router.post(
    "/messages",
    response_model=AssistantReply,
    responses={401: {"model": ErrorResponse}, 429: {"model": ErrorResponse}},
    summary="Preguntar al asistente",
)
def send(body: AssistantMessageIn, patient: CurrentPatient, db: DbSession) -> dict[str, Any]:
    """HU-28, 29, 30. Si el servicio `Insumap-ai` no está configurado o falla, responde en modo degradado
    (`degraded: true`) con la sugerencia del algoritmo."""
    return assistant_service.send_message(db, patient, body.message)


@router.get("/messages", response_model=list[AssistantMessageOut], summary="Conversación reciente")
def list_messages(
    patient: CurrentPatient, db: DbSession, limit: Annotated[int, Query(ge=1, le=100)] = 30
) -> list[AssistantMessage]:
    return assistant_service.history(db, patient, limit)
