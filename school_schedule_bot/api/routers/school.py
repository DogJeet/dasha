from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.dependencies import get_db
from app.schemas.school import SchoolCreate, SchoolRead
from app.services.school_service import SchoolService

router = APIRouter(prefix='/schools', tags=['schools'])


@router.post('', response_model=SchoolRead)
def create_school(payload: SchoolCreate, db: Session = Depends(get_db)):
    return SchoolService(db).create_school(payload)
