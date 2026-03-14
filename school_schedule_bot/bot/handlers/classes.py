import httpx
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()
API_URL = 'http://localhost:8000'


@router.message(Command('add_class'))
async def add_class(message: Message):
    parts = (message.text or '').split(maxsplit=2)
    if len(parts) < 3:
        await message.answer('Формат: /add_class <school_id> <название>')
        return
    payload = {'school_id': int(parts[1]), 'name': parts[2]}
    async with httpx.AsyncClient() as client:
        resp = await client.post(f'{API_URL}/entities/classes', json=payload)
    await message.answer('Класс добавлен' if resp.is_success else f'Ошибка: {resp.text}')
