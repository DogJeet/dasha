from app.scheduling.models import ScheduledLesson
from app.scheduling.scoring import score_schedule


def test_score_schedule_has_penalty_keys():
    entries = [
        ScheduledLesson(1, 1, 1, 0, 0),
        ScheduledLesson(1, 1, 1, 0, 2),
        ScheduledLesson(1, 2, 2, 0, 3),
    ]
    score = score_schedule(entries, 6)
    assert 'total_penalty' in score
    assert score['teacher_gaps'] >= 0
