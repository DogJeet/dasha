import httpx
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.states.forms import NewProjectForm

router = Router()
API_URL = 'http://localhost:8000'


@router.message(Command('new_project'))
async def new_project(message: Message, state: FSMContext):
    await state.set_state(NewProjectForm.name)
    await message.answer('Введите название школы:')


@router.message(NewProjectForm.name)
async def project_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(NewProjectForm.days)
    await message.answer('Количество учебных дней (например, 5):')


@router.message(NewProjectForm.days)
async def project_days(message: Message, state: FSMContext):
    await state.update_data(days_per_week=int(message.text))
    await state.set_state(NewProjectForm.lessons)
    await message.answer('Количество уроков в день (например, 6):')


@router.message(NewProjectForm.lessons)
async def project_lessons(message: Message, state: FSMContext):
    data = await state.get_data()
    payload = {
        'name': data['name'],
        'days_per_week': data['days_per_week'],
        'lessons_per_day': int(message.text),
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(f'{API_URL}/schools', json=payload)
    if resp.is_success:
        school_id = resp.json()['id']
        await message.answer(f'Проект создан. school_id={school_id}')
    else:
        await message.answer(f'Ошибка: {resp.text}')
    await state.clear()
