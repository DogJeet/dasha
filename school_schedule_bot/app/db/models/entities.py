from __future__ import annotations

from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class School(Base):
    __tablename__ = 'schools'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    days_per_week: Mapped[int] = mapped_column(Integer, default=5)
    lessons_per_day: Mapped[int] = mapped_column(Integer, default=6)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SchoolClass(Base):
    __tablename__ = 'school_classes'
    __table_args__ = (UniqueConstraint('school_id', 'name'),)

    id: Mapped[int] = mapped_column(primary_key=True)
    school_id: Mapped[int] = mapped_column(ForeignKey('schools.id'))
    name: Mapped[str] = mapped_column(String(64))


class Subject(Base):
    __tablename__ = 'subjects'
    __table_args__ = (UniqueConstraint('school_id', 'name'),)

    id: Mapped[int] = mapped_column(primary_key=True)
    school_id: Mapped[int] = mapped_column(ForeignKey('schools.id'))
    name: Mapped[str] = mapped_column(String(128))
    difficulty: Mapped[int] = mapped_column(Integer, default=3)


class Teacher(Base):
    __tablename__ = 'teachers'
    __table_args__ = (UniqueConstraint('school_id', 'full_name'),)

    id: Mapped[int] = mapped_column(primary_key=True)
    school_id: Mapped[int] = mapped_column(ForeignKey('schools.id'))
    full_name: Mapped[str] = mapped_column(String(255))
    max_lessons_per_day: Mapped[int] = mapped_column(Integer, default=6)


class TeacherSubject(Base):
    __tablename__ = 'teacher_subjects'
    __table_args__ = (UniqueConstraint('teacher_id', 'subject_id'),)

    id: Mapped[int] = mapped_column(primary_key=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey('teachers.id'))
    subject_id: Mapped[int] = mapped_column(ForeignKey('subjects.id'))


class TeacherClassAssignment(Base):
    __tablename__ = 'teacher_class_assignments'
    __table_args__ = (UniqueConstraint('teacher_id', 'class_id'),)

    id: Mapped[int] = mapped_column(primary_key=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey('teachers.id'))
    class_id: Mapped[int] = mapped_column(ForeignKey('school_classes.id'))


class LessonRequirement(Base):
    __tablename__ = 'lesson_requirements'
    __table_args__ = (UniqueConstraint('school_id', 'class_id', 'subject_id'),)

    id: Mapped[int] = mapped_column(primary_key=True)
    school_id: Mapped[int] = mapped_column(ForeignKey('schools.id'))
    class_id: Mapped[int] = mapped_column(ForeignKey('school_classes.id'))
    subject_id: Mapped[int] = mapped_column(ForeignKey('subjects.id'))
    hours_per_week: Mapped[int] = mapped_column(Integer)
    paired: Mapped[bool] = mapped_column(Boolean, default=False)
    avoid_last_lesson: Mapped[bool] = mapped_column(Boolean, default=False)


class AvailabilitySlot(Base):
    __tablename__ = 'availability_slots'
    __table_args__ = (UniqueConstraint('teacher_id', 'day', 'lesson_index'),)

    id: Mapped[int] = mapped_column(primary_key=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey('teachers.id'))
    day: Mapped[int] = mapped_column(Integer)
    lesson_index: Mapped[int] = mapped_column(Integer)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)


class FixedLesson(Base):
    __tablename__ = 'fixed_lessons'

    id: Mapped[int] = mapped_column(primary_key=True)
    school_id: Mapped[int] = mapped_column(ForeignKey('schools.id'))
    class_id: Mapped[int] = mapped_column(ForeignKey('school_classes.id'))
    subject_id: Mapped[int] = mapped_column(ForeignKey('subjects.id'))
    teacher_id: Mapped[int] = mapped_column(ForeignKey('teachers.id'))
    day: Mapped[int] = mapped_column(Integer)
    lesson_index: Mapped[int] = mapped_column(Integer)


class Schedule(Base):
    __tablename__ = 'schedules'

    id: Mapped[int] = mapped_column(primary_key=True)
    school_id: Mapped[int] = mapped_column(ForeignKey('schools.id'))
    version: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(32), default='generated')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ScheduleEntry(Base):
    __tablename__ = 'schedule_entries'
    __table_args__ = (UniqueConstraint('schedule_id', 'class_id', 'day', 'lesson_index'),)

    id: Mapped[int] = mapped_column(primary_key=True)
    schedule_id: Mapped[int] = mapped_column(ForeignKey('schedules.id'))
    class_id: Mapped[int] = mapped_column(ForeignKey('school_classes.id'))
    subject_id: Mapped[int] = mapped_column(ForeignKey('subjects.id'))
    teacher_id: Mapped[int] = mapped_column(ForeignKey('teachers.id'))
    day: Mapped[int] = mapped_column(Integer)
    lesson_index: Mapped[int] = mapped_column(Integer)


class ScheduleScore(Base):
    __tablename__ = 'schedule_scores'

    id: Mapped[int] = mapped_column(primary_key=True)
    schedule_id: Mapped[int] = mapped_column(ForeignKey('schedules.id'), unique=True)
    total_penalty: Mapped[int] = mapped_column(Integer)
    teacher_gaps: Mapped[int] = mapped_column(Integer, default=0)
    class_gaps: Mapped[int] = mapped_column(Integer, default=0)
    subject_spread: Mapped[int] = mapped_column(Integer, default=0)
    heavy_late: Mapped[int] = mapped_column(Integer, default=0)
