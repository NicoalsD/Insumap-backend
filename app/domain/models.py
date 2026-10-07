"""Domain models (no FastAPI / SQLAlchemy dependencies)."""

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

# Microzone codes are user-visible data (shown in the UI, exports and assistant answers),
# so they keep the documented Spanish abbreviations: ABD/MUS/BRA/GLU and I (left) / D (right).
MACROS: tuple[str, ...] = ("ABD", "MUS", "BRA", "GLU")
SIDES: tuple[str, ...] = ("I", "D")
GRID_SIZES: tuple[int, ...] = (2, 4, 6)

# User-facing labels (Spanish).
MACRO_LABELS: dict[str, str] = {"ABD": "Abdomen", "MUS": "Muslos", "BRA": "Brazos", "GLU": "Glúteos"}
SIDE_LABELS: dict[str, str] = {"I": "izquierdo", "D": "derecho"}

_ID_PATTERN = re.compile(r"^(ABD|MUS|BRA|GLU)-(I|D)-([1-6])-([1-6])$")


class Color(StrEnum):
    RED = "RED"
    YELLOW = "YELLOW"
    GREEN = "GREEN"


class InjectionStatus(StrEnum):
    REGISTERED = "REGISTERED"
    UNDONE = "UNDONE"


class InvalidMicrozoneId(ValueError):
    pass


def format_id(macro: str, side: str, row: int, col: int) -> str:
    return f"{macro}-{side}-{row}-{col}"


def parse_id(microzone_id: str, grid_size: int) -> tuple[str, str, int, int]:
    """Validate a ``MACRO-SIDE-ROW-COL`` id against the current grid size."""
    m = _ID_PATTERN.match(microzone_id)
    if not m:
        raise InvalidMicrozoneId(f"Invalid microzone id: {microzone_id!r}")
    macro, side, row, col = m.group(1), m.group(2), int(m.group(3)), int(m.group(4))
    if row > grid_size or col > grid_size:
        raise InvalidMicrozoneId(f"{microzone_id} does not exist in a {grid_size}x{grid_size} grid")
    return macro, side, row, col


@dataclass(frozen=True)
class Params:
    """Algorithm parameters. **Example values, pending clinical validation.**"""

    base_hours: dict[str, float] = field(
        default_factory=lambda: {"ABD": 72.0, "MUS": 96.0, "BRA": 96.0, "GLU": 96.0}
    )
    frequency_alpha: float = 0.10
    yellow_threshold: float = 0.50
    green_threshold: float = 1.00
    max_ratio: float = 2.00
    usage_window_days: int = 30
    forgotten_days: int = 15
    forgotten_beta: float = 0.50
    overuse_gamma: float = 0.50
    neighbor_delta: float = 0.20
    neighbor_hours: float = 48.0
    neighbor_radius: int = 1
    top_k: int = 3
    undo_window_hours: float = 24.0


@dataclass
class Microzone:
    id: str
    macro: str
    side: str
    row: int
    col: int
    last_used: datetime | None = None
    uses_30d: int = 0


@dataclass
class InjectionView:
    """Injection as seen by the domain (microzone projected to the current grid)."""

    id: str
    microzone_id: str
    macro: str
    side: str
    row: int
    col: int
    applied_at: datetime
    registered_at: datetime
    status: InjectionStatus
    undone_at: datetime | None = None
    original_microzone_id: str = ""


@dataclass(frozen=True)
class UndoAction:
    """Snapshot of the microzone before a registration: what the undo stack (E3) stores."""

    injection_id: str
    microzone_id: str
    macro: str
    registered_at: datetime
    previous_last_used: datetime | None
    previous_uses_30d: int
    counted_in_window: bool
