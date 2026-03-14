from sqlalchemy.orm import Session

from app.repositories.entities import AssignmentRepository, AvailabilityRepository, TeacherRepository
from app.schemas.entities import AssignmentCreate, AvailabilityCreate, TeacherCreate


class TeacherService:
    def __init__(self, db: Session):
        self.repo = TeacherRepository(db)
        self.av_repo = AvailabilityRepository(db)
        self.assign_repo = AssignmentRepository(db)

    def create(self, data: TeacherCreate):
        return self.repo.create(**data.model_dump())

    def set_availability(self, data: AvailabilityCreate):
        return self.av_repo.upsert(**data.model_dump())

    def add_assignment(self, data: AssignmentCreate):
        if data.subject_id:
            return self.assign_repo.add_subject(data.teacher_id, data.subject_id)
        if data.class_id:
            return self.assign_repo.add_class(data.teacher_id, data.class_id)
        raise ValueError('subject_id or class_id must be provided')
