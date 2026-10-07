from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AlgorithmParam, MacroZone
from app.db.seed import PARAM_FIELDS
from app.domain.models import Params


def load_params(db: Session) -> Params:
    """Build ``Params`` from ``algorithm_params`` + ``macro_zones`` (falls back to defaults)."""
    defaults = Params()
    values: dict[str, object] = {}
    for row in db.scalars(select(AlgorithmParam)):
        if row.key in PARAM_FIELDS:
            values[PARAM_FIELDS[row.key][0]] = row.value
    base = dict(defaults.base_hours)
    for mz in db.scalars(select(MacroZone)):
        base[mz.code] = float(mz.base_hours)
    return Params(base_hours=base, **values)  # type: ignore[arg-type]
