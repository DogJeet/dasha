from collections import defaultdict
from sqlalchemy.orm import Session

from app.db.models import AvailabilitySlot, LessonRequirement, School, Teacher, TeacherClassAssignment, TeacherSubject


def feasibility_report(db: Session, school_id: int) -> dict:
    school = db.get(School, school_id)
    if school is None:
        return {'ok': False, 'errors': ['School not found']}

    teacher_subjects = {(x.teacher_id, x.subject_id) for x in db.query(TeacherSubject).all()}
    teacher_classes = {(x.teacher_id, x.class_id) for x in db.query(TeacherClassAssignment).all()}
    requirements: list[LessonRequirement] = db.query(LessonRequirement).filter_by(school_id=school_id).all()
    teachers: list[Teacher] = db.query(Teacher).filter_by(school_id=school_id).all()

    teacher_available = defaultdict(lambda: school.days_per_week * school.lessons_per_day)
    for slot in db.query(AvailabilitySlot).all():
        if not slot.is_available:
            teacher_available[slot.teacher_id] -= 1

    errors: list[str] = []
    total_required = 0
    for req in requirements:
        total_required += req.hours_per_week
        possible_teachers = [
            t for t in teachers if (t.id, req.subject_id) in teacher_subjects and (t.id, req.class_id) in teacher_classes
        ]
        if not possible_teachers:
            errors.append(f'No teacher for class={req.class_id} subject={req.subject_id}')

    if sum(teacher_available.values()) < total_required:
        errors.append('Not enough teacher slots to satisfy total load')

    return {'ok': len(errors) == 0, 'errors': errors, 'total_required': total_required}
