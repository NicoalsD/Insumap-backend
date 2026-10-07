"""Idempotent seed data: macro zones, algorithm params and (optionally) demo users."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.models import AlgorithmParam, Doctor, MacroZone, Patient, Role, User
from app.domain.models import MACRO_LABELS, MACROS, Params

# key -> (attribute in Params, description shown in the docs / admin)
PARAM_FIELDS: dict[str, tuple[str, str]] = {
    "frequency_alpha": ("frequency_alpha", "Factor de frecuencia α en T_req"),
    "yellow_threshold": ("yellow_threshold", "Umbral u1: ratio < u1 es ROJO"),
    "green_threshold": ("green_threshold", "Umbral u2: ratio >= u2 es VERDE"),
    "max_ratio": ("max_ratio", "Tope del ratio de recuperación"),
    "usage_window_days": ("usage_window_days", "Ventana de uso en días (R12)"),
    "forgotten_days": ("forgotten_days", "Días sin uso para zona olvidada (R13)"),
    "forgotten_beta": ("forgotten_beta", "Bono β por zona olvidada"),
    "overuse_gamma": ("overuse_gamma", "Peso γ de penalización por sobreuso"),
    "neighbor_delta": ("neighbor_delta", "Penalización δ por vecina reciente"),
    "neighbor_hours": ("neighbor_hours", "Ventana en horas para vecinas recientes"),
    "neighbor_radius": ("neighbor_radius", "Radio del BFS de vecindad"),
    "top_k": ("top_k", "Número de sugerencias"),
    "undo_window_hours": ("undo_window_hours", "Ventana en horas para deshacer"),
}

DEMO_PASSWORD = "Insumap123"


def seed(db: Session) -> None:
    defaults = Params()
    for order, code in enumerate(MACROS):
        if db.get(MacroZone, code) is None:
            db.add(
                MacroZone(
                    code=code, label=MACRO_LABELS[code], base_hours=defaults.base_hours[code], display_order=order
                )
            )
    for key, (attr, description) in PARAM_FIELDS.items():
        if db.get(AlgorithmParam, key) is None:
            db.add(AlgorithmParam(key=key, value=getattr(defaults, attr), description=description))
    if get_settings().seed_demo_users:
        _demo_user(db, "paciente@demo.insumap", "Paciente Demo", Role.PATIENT)
        _demo_user(db, "medico@demo.insumap", "Médico Demo", Role.DOCTOR)
    db.commit()


def _demo_user(db: Session, email: str, name: str, role: Role) -> None:
    if db.scalar(select(User).where(User.email == email)) is not None:
        return
    user = User(email=email, name=name, role=role, password_hash=hash_password(DEMO_PASSWORD))
    db.add(user)
    db.flush()
    db.add(Patient(user_id=user.id) if role == Role.PATIENT else Doctor(user_id=user.id))


if __name__ == "__main__":
    from app.db.session import SessionLocal

    with SessionLocal() as session:
        seed(session)
    print("Seed OK")
