from sqlalchemy.orm import Session

from app.repositories.entities import SubjectRepository
from app.schemas.entities import SubjectCreate


class SubjectService:
    def __init__(self, db: Session):
        self.repo = SubjectRepository(db)

    def create(self, data: SubjectCreate):
        return self.repo.create(**data.model_dump())
