import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Injection
from app.domain.models import InjectionStatus
from app.domain.patient_state import InjectionData


def list_for_patient(db: Session, patient_id: uuid.UUID) -> list[Injection]:
    stmt = select(Injection).where(Injection.patient_id == patient_id).order_by(Injection.registered_at, Injection.id)
    return list(db.scalars(stmt))


def to_data(row: Injection) -> InjectionData:
    return InjectionData(
        id=str(row.id),
        macro=row.macro,
        side=row.side,
        row=row.row,
        col=row.col,
        grid_size=row.grid_size,
        applied_at=row.applied_at,
        registered_at=row.registered_at,
        status=InjectionStatus(row.status.value),
        undone_at=row.undone_at,
    )
