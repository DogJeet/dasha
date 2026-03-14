from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from api.dependencies import get_db
from app.services.schedule_service import ScheduleService
from exports.excel_export import export_excel
from exports.json_export import export_json
from exports.pdf_export import export_pdf

router = APIRouter(prefix='/export', tags=['export'])


@router.get('/{schedule_id}/json')
def export_schedule_json(schedule_id: int, db: Session = Depends(get_db)):
    data = ScheduleService(db).get_schedule(schedule_id)
    path = export_json(schedule_id, data)
    return FileResponse(path)


@router.get('/{schedule_id}/excel')
def export_schedule_excel(schedule_id: int, db: Session = Depends(get_db)):
    data = ScheduleService(db).get_schedule(schedule_id)
    path = export_excel(schedule_id, data)
    return FileResponse(path)


@router.get('/{schedule_id}/pdf')
def export_schedule_pdf(schedule_id: int, db: Session = Depends(get_db)):
    data = ScheduleService(db).get_schedule(schedule_id)
    path = export_pdf(schedule_id, data)
    return FileResponse(path)
