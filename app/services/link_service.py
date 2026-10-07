"""Doctor-patient links through one-time codes (R24-R27)."""

import secrets
import uuid
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import clock
from app.core.errors import bad_request, conflict, not_found
from app.db.models import Doctor, DoctorPatientLink, LinkCode, Patient, Role, User

ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # no ambiguous characters (0/O, 1/I)
CODE_TTL = timedelta(hours=48)


def create_code(db: Session, patient: Patient) -> LinkCode:
    while True:
        code = "".join(secrets.choice(ALPHABET) for _ in range(8))
        if db.scalar(select(LinkCode.id).where(LinkCode.code == code)) is None:
            break
    row = LinkCode(patient_id=patient.user_id, code=code, expires_at=clock.now() + CODE_TTL)
    db.add(row)
    db.commit()
    return row


def redeem(db: Session, doctor: Doctor, code: str) -> DoctorPatientLink:
    normalized = code.replace("-", "").strip().upper()
    row = db.scalar(select(LinkCode).where(LinkCode.code == normalized))
    if row is None or row.used_at is not None or row.expires_at <= clock.now():
        raise bad_request("INVALID_LINK_CODE", "El código no es válido, ya fue usado o venció.")
    active = db.scalar(
        select(DoctorPatientLink).where(
            DoctorPatientLink.doctor_id == doctor.user_id,
            DoctorPatientLink.patient_id == row.patient_id,
            DoctorPatientLink.revoked_at.is_(None),
        )
    )
    if active is not None:
        raise conflict("ALREADY_LINKED", "Ya estás vinculado con este paciente.")
    row.used_at = clock.now()
    link = DoctorPatientLink(doctor_id=doctor.user_id, patient_id=row.patient_id)
    db.add(link)
    db.commit()
    return link


def list_links(db: Session, user: User) -> list[dict[str, object]]:
    col = DoctorPatientLink.patient_id if user.role == Role.PATIENT else DoctorPatientLink.doctor_id
    links = db.scalars(select(DoctorPatientLink).where(col == user.id, DoctorPatientLink.revoked_at.is_(None)))
    result = []
    for link in links:
        doctor_user = db.get(User, link.doctor_id)
        patient_user = db.get(User, link.patient_id)
        result.append(
            {
                "id": link.id,
                "doctor_id": link.doctor_id,
                "doctor_name": doctor_user.name if doctor_user else "",
                "patient_id": link.patient_id,
                "patient_name": patient_user.name if patient_user else "",
                "created_at": link.created_at,
            }
        )
    return result


def revoke(db: Session, patient: Patient, link_id: uuid.UUID) -> None:
    """Only the patient can revoke a doctor's access (R27)."""
    link = db.scalar(
        select(DoctorPatientLink).where(
            DoctorPatientLink.id == link_id, DoctorPatientLink.patient_id == patient.user_id
        )
    )
    if link is None or link.revoked_at is not None:
        raise not_found("Vínculo no encontrado.")
    link.revoked_at = clock.now()
    db.commit()
