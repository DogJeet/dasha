from app.scheduling.models import ScheduledLesson
from app.scheduling.optimizer import optimize_schedule


def test_optimizer_returns_score():
    entries = [ScheduledLesson(1, 1, 1, 0, 0), ScheduledLesson(1, 2, 2, 0, 1)]
    optimized, score = optimize_schedule(entries, lessons_per_day=6, max_iterations=10)
    assert len(optimized) == len(entries)
    assert 'total_penalty' in score
