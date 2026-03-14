from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.keyboards.common import main_menu

router = Router()


@router.message(Command('start'))
async def start(message: Message):
    await message.answer('Привет! Я помогу построить школьное расписание.', reply_markup=main_menu())


@router.message(Command('help'))
async def help_cmd(message: Message):
    await message.answer(
        '/new_project /add_teacher /add_class /add_subject /set_load /set_availability /generate /show_schedule /export /improve'
    )
