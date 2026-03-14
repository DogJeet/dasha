import asyncio

from aiogram import Bot, Dispatcher

from app.core.config import get_settings
from bot.handlers.classes import router as classes_router
from bot.handlers.export import router as export_router
from bot.handlers.project import router as project_router
from bot.handlers.schedule import router as schedule_router
from bot.handlers.start import router as start_router
from bot.handlers.subjects import router as subjects_router
from bot.handlers.teachers import router as teachers_router


async def main() -> None:
    settings = get_settings()
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    dp.include_router(start_router)
    dp.include_router(project_router)
    dp.include_router(teachers_router)
    dp.include_router(classes_router)
    dp.include_router(subjects_router)
    dp.include_router(schedule_router)
    dp.include_router(export_router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
