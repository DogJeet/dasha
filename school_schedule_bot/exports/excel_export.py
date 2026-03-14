from pathlib import Path

from openpyxl import Workbook


def export_excel(schedule_id: int, data: dict) -> str:
    out_dir = Path('exports_artifacts')
    out_dir.mkdir(exist_ok=True)
    path = out_dir / f'schedule_{schedule_id}.xlsx'

    wb = Workbook()
    ws = wb.active
    ws.title = 'Schedule'
    ws.append(['class_id', 'subject_id', 'teacher_id', 'day', 'lesson_index'])
    for e in sorted(data['entries'], key=lambda x: (x.class_id, x.day, x.lesson_index)):
        ws.append([e.class_id, e.subject_id, e.teacher_id, e.day, e.lesson_index])
    wb.save(path)
    return str(path)
