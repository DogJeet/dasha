from __future__ import annotations

from collections import defaultdict

from sqlalchemy.orm import Session

from app.db.models import AvailabilitySlot, FixedLesson, LessonRequirement, School, TeacherClassAssignment, TeacherSubject
from app.scheduling.constraints import check_hard_constraints
from app.scheduling.models import LessonTask, ScheduledLesson


def _teacher_allowed(db: Session) -> tuple[set[tuple[int, int]], set[tuple[int, int]]]:
    teacher_subjects = {(x.teacher_id, x.subject_id) for x in db.query(TeacherSubject).all()}
    teacher_classes = {(x.teacher_id, x.class_id) for x in db.query(TeacherClassAssignment).all()}
    return teacher_subjects, teacher_classes


def build_initial_schedule(db: Session, school_id: int) -> tuple[list[ScheduledLesson], list[str]]:
    school = db.get(School, school_id)
    if not school:
        return [], ['School not found']

    teacher_subjects, teacher_classes = _teacher_allowed(db)
    unavailable = {(x.teacher_id, x.day, x.lesson_index) for x in db.query(AvailabilitySlot).filter_by(is_available=False).all()}
    requirements: list[LessonRequirement] = db.query(LessonRequirement).filter_by(school_id=school_id).all()

    fixed = [
        ScheduledLesson(
            class_id=f.class_id,
            subject_id=f.subject_id,
            teacher_id=f.teacher_id,
            day=f.day,
            lesson_index=f.lesson_index,
        )
        for f in db.query(FixedLesson).filter_by(school_id=school_id).all()
    ]

    class_busy = {(x.class_id, x.day, x.lesson_index) for x in fixed}
    teacher_busy = {(x.teacher_id, x.day, x.lesson_index) for x in fixed}

    tasks: list[LessonTask] = []
    errors: list[str] = []
    for req in requirements:
        candidates = [
            teacher_id
            for teacher_id, subject_id in teacher_subjects
            if subject_id == req.subject_id and (teacher_id, req.class_id) in teacher_classes
        ]
        if not candidates:
            errors.append(f'No teacher candidates class={req.class_id} subject={req.subject_id}')
            continue
        teacher_id = min(candidates)
        for _ in range(req.hours_per_week):
            tasks.append(
                LessonTask(
                    class_id=req.class_id,
                    subject_id=req.subject_id,
                    teacher_id=teacher_id,
                    avoid_last_lesson=req.avoid_last_lesson,
                    paired=req.paired,
                )
            )

    def slot_score(task: LessonTask, day: int, lesson: int) -> int:
        s = 0
        if task.avoid_last_lesson and lesson == school.lessons_per_day - 1:
            s += 100
        s += abs((school.lessons_per_day // 2) - lesson)
        return s

    tasks.sort(key=lambda t: (t.avoid_last_lesson, t.paired), reverse=True)
    plan: list[ScheduledLesson] = fixed.copy()

    daily_teacher_count = defaultdict(int)
    for p in plan:
        daily_teacher_count[(p.teacher_id, p.day)] += 1

    for task in tasks:
        chosen = None
        all_slots = [
            (d, l)
            for d in range(school.days_per_week)
            for l in range(school.lessons_per_day)
            if (task.class_id, d, l) not in class_busy
            and (task.teacher_id, d, l) not in teacher_busy
            and (task.teacher_id, d, l) not in unavailable
        ]
        all_slots.sort(key=lambda x: slot_score(task, x[0], x[1]))

        for d, l in all_slots:
            if daily_teacher_count[(task.teacher_id, d)] >= school.lessons_per_day:
                continue
            if task.paired:
                next_slot = (d, l + 1)
                if l + 1 >= school.lessons_per_day:
                    continue
                if (task.class_id, next_slot[0], next_slot[1]) in class_busy:
                    continue
                if (task.teacher_id, next_slot[0], next_slot[1]) in teacher_busy:
                    continue
                if (task.teacher_id, next_slot[0], next_slot[1]) in unavailable:
                    continue
            chosen = (d, l)
            break

        if chosen is None:
            errors.append(f'Failed to place lesson class={task.class_id} subject={task.subject_id}')
            continue

        day, lesson = chosen
        lesson_entry = ScheduledLesson(task.class_id, task.subject_id, task.teacher_id, day, lesson)
        plan.append(lesson_entry)
        class_busy.add((task.class_id, day, lesson))
        teacher_busy.add((task.teacher_id, day, lesson))
        daily_teacher_count[(task.teacher_id, day)] += 1

        if task.paired:
            second = ScheduledLesson(task.class_id, task.subject_id, task.teacher_id, day, lesson + 1)
            plan.append(second)
            class_busy.add((task.class_id, day, lesson + 1))
            teacher_busy.add((task.teacher_id, day, lesson + 1))
            daily_teacher_count[(task.teacher_id, day)] += 1

    ok, hard_errors = check_hard_constraints(plan)
    if not ok:
        errors.extend(hard_errors)

    return plan, errors
