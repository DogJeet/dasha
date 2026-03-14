from pydantic import BaseModel


class ScheduleGenerateRequest(BaseModel):
    school_id: int
    max_iterations: int = 500


class ScheduleEntryRead(BaseModel):
    class_id: int
    subject_id: int
    teacher_id: int
    day: int
    lesson_index: int


class ScheduleRead(BaseModel):
    schedule_id: int
    entries: list[ScheduleEntryRead]
    score: dict
