from __future__ import annotations

import json
from pathlib import Path


def export_json(schedule_id: int, data: dict) -> str:
    out_dir = Path('exports_artifacts')
    out_dir.mkdir(exist_ok=True)
    path = out_dir / f'schedule_{schedule_id}.json'
    entries = [
        {
            'class_id': e.class_id,
            'subject_id': e.subject_id,
            'teacher_id': e.teacher_id,
            'day': e.day,
            'lesson_index': e.lesson_index,
        }
        for e in data['entries']
    ]
    score = data['score']
    payload = {
        'schedule_id': schedule_id,
        'entries': entries,
        'score': {
            'total_penalty': score.total_penalty if score else None,
            'teacher_gaps': score.teacher_gaps if score else None,
            'class_gaps': score.class_gaps if score else None,
            'subject_spread': score.subject_spread if score else None,
            'heavy_late': score.heavy_late if score else None,
        },
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    return str(path)
