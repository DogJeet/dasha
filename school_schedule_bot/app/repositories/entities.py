from sqlalchemy import select

from app.db.models import (
    AvailabilitySlot,
    LessonRequirement,
    School,
    SchoolClass,
    Subject,
    Teacher,
    TeacherClassAssignment,
    TeacherSubject,
)
from app.repositories.base import BaseRepository


class SchoolRepository(BaseRepository):
    def create(self, **kwargs) -> School:
        obj = School(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get(self, school_id: int) -> School | None:
        return self.db.get(School, school_id)


class ClassRepository(BaseRepository):
    def create(self, **kwargs) -> SchoolClass:
        obj = SchoolClass(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def by_school(self, school_id: int) -> list[SchoolClass]:
        return list(self.db.scalars(select(SchoolClass).where(SchoolClass.school_id == school_id)))


class SubjectRepository(BaseRepository):
    def create(self, **kwargs) -> Subject:
        obj = Subject(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def by_school(self, school_id: int) -> list[Subject]:
        return list(self.db.scalars(select(Subject).where(Subject.school_id == school_id)))


class TeacherRepository(BaseRepository):
    def create(self, **kwargs) -> Teacher:
        obj = Teacher(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def by_school(self, school_id: int) -> list[Teacher]:
        return list(self.db.scalars(select(Teacher).where(Teacher.school_id == school_id)))


class RequirementRepository(BaseRepository):
    def create(self, **kwargs) -> LessonRequirement:
        obj = LessonRequirement(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def by_school(self, school_id: int) -> list[LessonRequirement]:
        return list(self.db.scalars(select(LessonRequirement).where(LessonRequirement.school_id == school_id)))


class AvailabilityRepository(BaseRepository):
    def upsert(self, **kwargs) -> AvailabilitySlot:
        stmt = select(AvailabilitySlot).where(
            AvailabilitySlot.teacher_id == kwargs['teacher_id'],
            AvailabilitySlot.day == kwargs['day'],
            AvailabilitySlot.lesson_index == kwargs['lesson_index'],
        )
        obj = self.db.scalar(stmt)
        if obj:
            obj.is_available = kwargs['is_available']
        else:
            obj = AvailabilitySlot(**kwargs)
            self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def by_teacher(self, teacher_id: int) -> list[AvailabilitySlot]:
        return list(self.db.scalars(select(AvailabilitySlot).where(AvailabilitySlot.teacher_id == teacher_id)))


class AssignmentRepository(BaseRepository):
    def add_subject(self, teacher_id: int, subject_id: int) -> TeacherSubject:
        obj = TeacherSubject(teacher_id=teacher_id, subject_id=subject_id)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def add_class(self, teacher_id: int, class_id: int) -> TeacherClassAssignment:
        obj = TeacherClassAssignment(teacher_id=teacher_id, class_id=class_id)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def teacher_subjects(self) -> list[TeacherSubject]:
        return list(self.db.scalars(select(TeacherSubject)))

    def teacher_classes(self) -> list[TeacherClassAssignment]:
        return list(self.db.scalars(select(TeacherClassAssignment)))
