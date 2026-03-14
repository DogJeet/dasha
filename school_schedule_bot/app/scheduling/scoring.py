from collections import defaultdict

from app.scheduling.models import ScheduledLesson


def score_schedule(entries: list[ScheduledLesson], lessons_per_day: int) -> dict:
    teacher_day_slots = defaultdict(list)
    class_day_slots = defaultdict(list)
    subject_runs_penalty = 0
    heavy_late = 0

    for e in entries:
        teacher_day_slots[(e.teacher_id, e.day)].append(e.lesson_index)
        class_day_slots[(e.class_id, e.day)].append((e.lesson_index, e.subject_id))
        if e.lesson_index > lessons_per_day // 2 and e.subject_id % 5 >= 3:
            heavy_late += 1

    teacher_gaps = 0
    for slots in teacher_day_slots.values():
        if len(slots) > 1:
            slots = sorted(slots)
            teacher_gaps += sum(max(0, b - a - 1) for a, b in zip(slots, slots[1:]))

    class_gaps = 0
    for slots in class_day_slots.values():
        ordered = sorted(slots)
        idx = [s for s, _ in ordered]
        if len(idx) > 1:
            class_gaps += sum(max(0, b - a - 1) for a, b in zip(idx, idx[1:]))
        run = 1
        for i in range(1, len(ordered)):
            if ordered[i][1] == ordered[i - 1][1]:
                run += 1
                if run > 2:
                    subject_runs_penalty += 1
            else:
                run = 1

    total = teacher_gaps * 3 + class_gaps * 3 + subject_runs_penalty * 2 + heavy_late
    grade = 'excellent' if total < 10 else 'good' if total < 25 else 'needs_improvement'
    return {
        'total_penalty': total,
        'teacher_gaps': teacher_gaps,
        'class_gaps': class_gaps,
        'subject_runs': subject_runs_penalty,
        'heavy_late': heavy_late,
        'quality': grade,
    }
