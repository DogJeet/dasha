from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Новый проект', callback_data='new_project')],
            [InlineKeyboardButton(text='Сгенерировать', callback_data='generate')],
        ]
    )
