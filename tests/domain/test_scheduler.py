from datetime import UTC, datetime, timedelta

from app.domain.algorithms.scheduler import ReminderScheduler

T0 = datetime(2026, 10, 20, 7, 0, tzinfo=UTC)


def test_due_snooze_cancel():
    s = ReminderScheduler()
    s.schedule("a", T0)
    s.schedule("b", T0 + timedelta(hours=6))
    s.schedule("c", T0 + timedelta(hours=13))
    assert s.due(T0 - timedelta(minutes=1)) == []
    s.snooze("a", T0 + timedelta(minutes=15))
    assert s.due(T0) == []
    assert s.due(T0 + timedelta(minutes=15)) == ["a"]
    s.cancel("b")
    assert s.due(T0 + timedelta(days=1)) == ["c"]
    assert len(s) == 0
