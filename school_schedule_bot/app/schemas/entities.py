from pydantic import BaseModel, Field

from app.schemas.common import ORMBase


class ClassCreate(BaseModel):
    school_id: int
    name: str = Field(min_length=1, max_length=64)


class SubjectCreate(BaseModel):
    school_id: int
    name: str
    difficulty: int = Field(default=3, ge=1, le=5)


class TeacherCreate(BaseModel):
    school_id: int
    full_name: str
    max_lessons_per_day: int = Field(default=6, ge=1, le=12)


class RequirementCreate(BaseModel):
    school_id: int
    class_id: int
    subject_id: int
    hours_per_week: int = Field(ge=1, le=15)
    paired: bool = False
    avoid_last_lesson: bool = False


class AvailabilityCreate(BaseModel):
    teacher_id: int
    day: int
    lesson_index: int
    is_available: bool = True


class AssignmentCreate(BaseModel):
    teacher_id: int
    subject_id: int | None = None
    class_id: int | None = None


class GenericRead(ORMBase):
    id: int
