from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command('export'))
async def export_schedule(message: Message):
    await message.answer('Экспорт доступен через API: /export/{schedule_id}/json|excel|pdf')
