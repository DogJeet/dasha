from collections import defaultdict
from app.scheduling.models import ScheduledLesson


def check_hard_constraints(entries: list[ScheduledLesson]) -> tuple[bool, list[str]]:
    errors: list[str] = []
    teacher_slots: dict[tuple[int, int, int], int] = defaultdict(int)
    class_slots: dict[tuple[int, int, int], int] = defaultdict(int)
    for e in entries:
        teacher_slots[(e.teacher_id, e.day, e.lesson_index)] += 1
        class_slots[(e.class_id, e.day, e.lesson_index)] += 1

    for key, count in teacher_slots.items():
        if count > 1:
            errors.append(f'Teacher conflict on slot={key}')
    for key, count in class_slots.items():
        if count > 1:
            errors.append(f'Class conflict on slot={key}')
    return (len(errors) == 0, errors)
