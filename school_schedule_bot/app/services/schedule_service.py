from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import LessonRequirement, Schedule, ScheduleEntry, ScheduleScore, School
from app.repositories.entities import RequirementRepository
from app.scheduling.builder import build_initial_schedule
from app.scheduling.feasibility import feasibility_report
from app.scheduling.optimizer import optimize_schedule


class ScheduleService:
    def __init__(self, db: Session):
        self.db = db
        self.req_repo = RequirementRepository(db)

    def set_requirement(self, **kwargs):
        return self.req_repo.create(**kwargs)

    def generate(self, school_id: int, max_iterations: int = 500):
        report = feasibility_report(self.db, school_id)
        if not report['ok']:
            return {'ok': False, 'errors': report['errors']}

        initial, errors = build_initial_schedule(self.db, school_id)
        if errors:
            return {'ok': False, 'errors': errors}

        school = self.db.get(School, school_id)
        optimized, score = optimize_schedule(initial, school.lessons_per_day, max_iterations=max_iterations)

        version = (self.db.scalar(select(Schedule.version).where(Schedule.school_id == school_id).order_by(Schedule.version.desc())) or 0) + 1
        schedule = Schedule(school_id=school_id, version=version)
        self.db.add(schedule)
        self.db.flush()

        for e in optimized:
            self.db.add(
                ScheduleEntry(
                    schedule_id=schedule.id,
                    class_id=e.class_id,
                    subject_id=e.subject_id,
                    teacher_id=e.teacher_id,
                    day=e.day,
                    lesson_index=e.lesson_index,
                )
            )
        self.db.add(
            ScheduleScore(
                schedule_id=schedule.id,
                total_penalty=score['total_penalty'],
                teacher_gaps=score['teacher_gaps'],
                class_gaps=score['class_gaps'],
                subject_spread=score['subject_runs'],
                heavy_late=score['heavy_late'],
            )
        )
        self.db.commit()
        return {'ok': True, 'schedule_id': schedule.id, 'score': score}

    def get_schedule(self, schedule_id: int):
        entries = self.db.query(ScheduleEntry).filter_by(schedule_id=schedule_id).all()
        score = self.db.query(ScheduleScore).filter_by(schedule_id=schedule_id).first()
        return {'entries': entries, 'score': score}
