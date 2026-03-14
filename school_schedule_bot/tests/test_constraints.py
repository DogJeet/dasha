from app.scheduling.constraints import check_hard_constraints
from app.scheduling.models import ScheduledLesson


def test_teacher_conflict_detected():
    entries = [
        ScheduledLesson(1, 1, 1, 0, 0),
        ScheduledLesson(2, 2, 1, 0, 0),
    ]
    ok, errors = check_hard_constraints(entries)
    assert not ok
    assert any('Teacher conflict' in e for e in errors)
