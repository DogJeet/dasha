from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.dependencies import get_db
from app.schemas.entities import (
    AssignmentCreate,
    AvailabilityCreate,
    ClassCreate,
    GenericRead,
    RequirementCreate,
    SubjectCreate,
    TeacherCreate,
)
from app.services.class_service import ClassService
from app.services.schedule_service import ScheduleService
from app.services.subject_service import SubjectService
from app.services.teacher_service import TeacherService

router = APIRouter(prefix='/entities', tags=['entities'])


@router.post('/classes', response_model=GenericRead)
def add_class(payload: ClassCreate, db: Session = Depends(get_db)):
    return ClassService(db).create(payload)


@router.post('/subjects', response_model=GenericRead)
def add_subject(payload: SubjectCreate, db: Session = Depends(get_db)):
    return SubjectService(db).create(payload)


@router.post('/teachers', response_model=GenericRead)
def add_teacher(payload: TeacherCreate, db: Session = Depends(get_db)):
    return TeacherService(db).create(payload)


@router.post('/requirements', response_model=GenericRead)
def set_load(payload: RequirementCreate, db: Session = Depends(get_db)):
    return ScheduleService(db).set_requirement(**payload.model_dump())


@router.post('/availability', response_model=GenericRead)
def set_availability(payload: AvailabilityCreate, db: Session = Depends(get_db)):
    return TeacherService(db).set_availability(payload)


@router.post('/assignments', response_model=GenericRead)
def add_assignment(payload: AssignmentCreate, db: Session = Depends(get_db)):
    return TeacherService(db).add_assignment(payload)
