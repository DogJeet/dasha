from dataclasses import dataclass


@dataclass(frozen=True)
class Slot:
    day: int
    lesson_index: int


@dataclass
class LessonTask:
    class_id: int
    subject_id: int
    teacher_id: int
    avoid_last_lesson: bool = False
    paired: bool = False


@dataclass
class ScheduledLesson:
    class_id: int
    subject_id: int
    teacher_id: int
    day: int
    lesson_index: int
