from sqlalchemy.orm import Session

from app.repositories.entities import ClassRepository
from app.schemas.entities import ClassCreate


class ClassService:
    def __init__(self, db: Session):
        self.repo = ClassRepository(db)

    def create(self, data: ClassCreate):
        return self.repo.create(**data.model_dump())
