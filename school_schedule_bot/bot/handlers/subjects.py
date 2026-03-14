import httpx
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()
API_URL = 'http://localhost:8000'


@router.message(Command('add_subject'))
async def add_subject(message: Message):
    parts = (message.text or '').split(maxsplit=2)
    if len(parts) < 3:
        await message.answer('Формат: /add_subject <school_id> <название>')
        return
    payload = {'school_id': int(parts[1]), 'name': parts[2], 'difficulty': 3}
    async with httpx.AsyncClient() as client:
        resp = await client.post(f'{API_URL}/entities/subjects', json=payload)
    await message.answer('Предмет добавлен' if resp.is_success else f'Ошибка: {resp.text}')
