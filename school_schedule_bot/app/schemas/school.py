from pydantic import BaseModel, Field

from app.schemas.common import ORMBase


class SchoolCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    days_per_week: int = Field(ge=1, le=7)
    lessons_per_day: int = Field(ge=1, le=12)


class SchoolRead(ORMBase):
    id: int
    name: str
    days_per_week: int
    lessons_per_day: int
