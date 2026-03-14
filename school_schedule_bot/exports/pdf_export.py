from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def export_pdf(schedule_id: int, data: dict) -> str:
    out_dir = Path('exports_artifacts')
    out_dir.mkdir(exist_ok=True)
    path = out_dir / f'schedule_{schedule_id}.pdf'

    c = canvas.Canvas(str(path), pagesize=A4)
    c.setFont('Helvetica', 10)
    y = 800
    c.drawString(30, y, f'Schedule #{schedule_id}')
    y -= 20
    for e in sorted(data['entries'], key=lambda x: (x.class_id, x.day, x.lesson_index)):
        c.drawString(30, y, f'class={e.class_id} subj={e.subject_id} teacher={e.teacher_id} d={e.day} l={e.lesson_index}')
        y -= 14
        if y < 40:
            c.showPage()
            c.setFont('Helvetica', 10)
            y = 800
    c.save()
    return str(path)
