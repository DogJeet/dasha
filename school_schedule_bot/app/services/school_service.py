from sqlalchemy.orm import Session

from app.repositories.entities import SchoolRepository
from app.schemas.school import SchoolCreate


class SchoolService:
    def __init__(self, db: Session):
        self.repo = SchoolRepository(db)

    def create_school(self, data: SchoolCreate):
        return self.repo.create(**data.model_dump())
