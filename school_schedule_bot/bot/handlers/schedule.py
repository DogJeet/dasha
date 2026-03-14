import httpx
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()
API_URL = 'http://localhost:8000'


@router.message(Command('generate'))
async def generate(message: Message):
    parts = (message.text or '').split()
    if len(parts) < 2:
        await message.answer('Формат: /generate <school_id>')
        return
    payload = {'school_id': int(parts[1]), 'max_iterations': 300}
    async with httpx.AsyncClient() as client:
        resp = await client.post(f'{API_URL}/schedules/generate', json=payload)
    await message.answer(resp.text)


@router.message(Command('show_schedule'))
async def show_schedule(message: Message):
    parts = (message.text or '').split()
    if len(parts) < 2:
        await message.answer('Формат: /show_schedule <schedule_id>')
        return
    async with httpx.AsyncClient() as client:
        resp = await client.get(f'{API_URL}/schedules/{int(parts[1])}')
    await message.answer(resp.text[:3800])


@router.message(Command('improve'))
async def improve(message: Message):
    await message.answer('Режим улучшения: используйте /generate с большим max_iterations через API.')
