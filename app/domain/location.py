"""Deterministic, user-facing (Spanish) description of where a microzone is on the body."""

from app.domain.models import SIDE_LABELS, parse_id

_REFERENCES: dict[str, str] = {
    "ABD": "a los lados del ombligo, dejando al menos 5 cm de distancia del ombligo",
    "MUS": "en la cara frontal y externa del muslo, entre la rodilla y la ingle",
    "BRA": "en la cara posterior del brazo, entre el hombro y el codo",
    "GLU": "en el cuadrante superior externo del glúteo",
}
_MACRO_NAMES: dict[str, str] = {"ABD": "abdomen", "MUS": "muslo", "BRA": "brazo", "GLU": "glúteo"}


def _band(index: int, size: int, labels: tuple[str, str, str]) -> str:
    """Map a 1-indexed position to a third of the grid."""
    third = (index - 1) * 3 // size
    return labels[third]


def describe_location(microzone_id: str, grid_size: int = 6) -> str:
    macro, side, row, col = parse_id(microzone_id, grid_size)
    vertical = _band(row, grid_size, ("parte superior", "parte media", "parte inferior"))
    horizontal = _band(col, grid_size, ("hacia adentro", "al centro", "hacia afuera"))
    return f"{_MACRO_NAMES[macro].capitalize()} {SIDE_LABELS[side]}, {vertical} y {horizontal} ({_REFERENCES[macro]})."
