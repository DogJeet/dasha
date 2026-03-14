from __future__ import annotations

import math
import random
from copy import deepcopy

from app.scheduling.constraints import check_hard_constraints
from app.scheduling.models import ScheduledLesson
from app.scheduling.scoring import score_schedule


def _swap(entries: list[ScheduledLesson]) -> list[ScheduledLesson]:
    new = deepcopy(entries)
    if len(new) < 2:
        return new
    a, b = random.sample(range(len(new)), 2)
    new[a].day, new[b].day = new[b].day, new[a].day
    new[a].lesson_index, new[b].lesson_index = new[b].lesson_index, new[a].lesson_index
    return new


def optimize_schedule(
    entries: list[ScheduledLesson], lessons_per_day: int, max_iterations: int = 500
) -> tuple[list[ScheduledLesson], dict]:
    current = deepcopy(entries)
    current_score = score_schedule(current, lessons_per_day)
    best = deepcopy(current)
    best_score = current_score
    temp = 8.0

    for _ in range(max_iterations):
        candidate = _swap(current)
        ok, _ = check_hard_constraints(candidate)
        if not ok:
            continue
        cand_score = score_schedule(candidate, lessons_per_day)
        delta = cand_score['total_penalty'] - current_score['total_penalty']
        if delta < 0 or random.random() < math.exp(-delta / max(temp, 0.1)):
            current = candidate
            current_score = cand_score
            if cand_score['total_penalty'] < best_score['total_penalty']:
                best = deepcopy(candidate)
                best_score = cand_score
        temp *= 0.995

    return best, best_score
