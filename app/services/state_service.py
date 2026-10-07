"""Per-patient ``PatientState`` cache (E7 LRU) with the database as source of truth."""

import uuid
from datetime import datetime, timedelta
from threading import RLock

from sqlalchemy.orm import Session

from app.core import clock
from app.core.config import get_settings
from app.db.models import Patient
from app.domain.patient_state import PatientState
from app.domain.structures.lru_cache import LRUCache
from app.repositories import injections as injection_repo
from app.repositories.params import load_params

_settings = get_settings()
_cache: LRUCache[uuid.UUID, tuple[PatientState, datetime]] = LRUCache(_settings.state_cache_capacity)
# One lock for the whole cache: writes to a PatientState happen while holding it.
lock = RLock()


def build_state(db: Session, patient: Patient) -> PatientState:
    rows = injection_repo.list_for_patient(db, patient.user_id)
    return PatientState.build(
        patient.grid_size, (injection_repo.to_data(r) for r in rows), clock.now(), load_params(db)
    )


def get_state(db: Session, patient: Patient) -> PatientState:
    """Cached state; rebuilt when missing, expired (TTL) or the grid size changed."""
    with lock:
        cached = _cache.get(patient.user_id)
        ttl = timedelta(seconds=_settings.state_cache_ttl_seconds)
        if cached is not None:
            state, built_at = cached
            if state.grid_size == patient.grid_size and clock.now() - built_at < ttl:
                return state
        state = build_state(db, patient)
        _cache.put(patient.user_id, (state, clock.now()))
        return state


def invalidate(patient_id: uuid.UUID) -> None:
    with lock:
        _cache.invalidate(patient_id)


def clear() -> None:
    with lock:
        _cache.clear()
