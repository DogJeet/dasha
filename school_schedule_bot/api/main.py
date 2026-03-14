from fastapi import FastAPI

from api.routers.entities import router as entities_router
from api.routers.export import router as export_router
from api.routers.schedule import router as schedule_router
from api.routers.school import router as school_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.base import Base
from app.db.session import engine

settings = get_settings()
configure_logging(settings.log_level)
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)
app.include_router(school_router)
app.include_router(entities_router)
app.include_router(schedule_router)
app.include_router(export_router)


@app.get('/health')
def health():
    return {'status': 'ok'}
