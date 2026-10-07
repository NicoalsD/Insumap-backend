from datetime import UTC, datetime, timedelta

from app.domain.models import Color, InjectionStatus, Params
from app.domain.patient_state import InjectionData, PatientState

NOW = datetime(2026, 10, 20, 8, 0, tzinfo=UTC)
P = Params()


def inj(i: int, mz: tuple[str, str, int, int], hours_ago: float, size: int = 4):
    t = NOW - timedelta(hours=hours_ago)
    return InjectionData(f"i{i}", *mz, size, t, t, InjectionStatus.REGISTERED)


def test_build_index_and_graph():
    s = PatientState(4, P)
    assert len(s.index) == 4 * 2 * 16
    assert s.neighborhood.degree("ABD-I-1-1") == 2
    assert s.neighborhood.degree("ABD-I-2-2") == 4


def test_register_turns_red_and_undo_restores():
    s = PatientState.build(4, [inj(1, ("MUS", "I", 1, 2), 120)], NOW, P)
    assert s.evaluate_microzone(s.microzone("MUS-I-1-2"), NOW)["color"] == Color.GREEN
    s.register(inj(2, ("MUS", "I", 1, 2), 0), NOW)
    assert s.evaluate_microzone(s.microzone("MUS-I-1-2"), NOW)["color"] == Color.RED
    assert s.macro_usage.get("MUS") == 2
    assert s.undoable(NOW).injection_id == "i2"
    s.apply_undo(NOW)
    mz = s.microzone("MUS-I-1-2")
    assert mz.last_used == NOW - timedelta(hours=120) and mz.uses_30d == 1
    assert s.macro_usage.get("MUS") == 1
    assert s.evaluate_microzone(mz, NOW)["color"] == Color.GREEN
    assert next(s.history.iter_forward()).status == InjectionStatus.UNDONE


def test_undo_window_24h():
    s = PatientState.build(4, [inj(1, ("ABD", "D", 1, 1), 30)], NOW, P)
    assert s.undoable(NOW) is None


def test_projection_on_grid_change():
    s = PatientState.build(2, [inj(1, ("GLU", "I", 4, 3), 1, size=4)], NOW, P)
    assert s.microzone("GLU-I-2-2").last_used is not None
    assert next(s.history.iter_forward()).original_microzone_id == "GLU-I-4-3"


def test_suggestion_avoids_recent_neighbors():
    s = PatientState.build(2, [inj(1, ("ABD", "I", 1, 1), 1)], NOW, P)
    sug = {x.microzone_id: x for x in s.suggestions(NOW, k=32)}
    assert sug["ABD-I-1-2"].neighbor_penalty == P.neighbor_delta
    assert sug["ABD-I-2-2"].neighbor_penalty == 0
