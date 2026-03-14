import httpx
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()
API_URL = 'http://localhost:8000'


@router.message(Command('add_teacher'))
async def add_teacher(message: Message):
    parts = (message.text or '').split(maxsplit=2)
    if len(parts) < 3:
        await message.answer('Формат: /add_teacher <school_id> <ФИО>')
        return
    school_id, full_name = int(parts[1]), parts[2]
    payload = {'school_id': school_id, 'full_name': full_name, 'max_lessons_per_day': 6}
    async with httpx.AsyncClient() as client:
        resp = await client.post(f'{API_URL}/entities/teachers', json=payload)
    await message.answer('Учитель добавлен' if resp.is_success else f'Ошибка: {resp.text}')
