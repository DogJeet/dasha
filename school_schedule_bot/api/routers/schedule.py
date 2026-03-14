from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.dependencies import get_db
from app.db.models import ScheduleEntry
from app.schemas.schedule import ScheduleGenerateRequest
from app.services.schedule_service import ScheduleService

router = APIRouter(prefix='/schedules', tags=['schedule'])


@router.post('/generate')
def generate_schedule(payload: ScheduleGenerateRequest, db: Session = Depends(get_db)):
    result = ScheduleService(db).generate(payload.school_id, payload.max_iterations)
    if not result['ok']:
        raise HTTPException(status_code=400, detail=result['errors'])
    return result


@router.get('/{schedule_id}')
def get_schedule(schedule_id: int, db: Session = Depends(get_db)):
    return ScheduleService(db).get_schedule(schedule_id)


@router.get('/{schedule_id}/class/{class_id}')
def get_schedule_by_class(schedule_id: int, class_id: int, db: Session = Depends(get_db)):
    return db.query(ScheduleEntry).filter_by(schedule_id=schedule_id, class_id=class_id).all()


@router.get('/{schedule_id}/teacher/{teacher_id}')
def get_schedule_by_teacher(schedule_id: int, teacher_id: int, db: Session = Depends(get_db)):
    return db.query(ScheduleEntry).filter_by(schedule_id=schedule_id, teacher_id=teacher_id).all()
