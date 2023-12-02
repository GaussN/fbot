from typing import Iterable

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from handlers.files.models import File


def get_files_list_keyboard(files: Iterable[File]) -> InlineKeyboardMarkup:
    keyboard_builder = InlineKeyboardBuilder()
    for file in files:
        keyboard_builder.row(
            InlineKeyboardButton(text=file.filename, callback_data=file.hash)
        )
    keyboard_builder.row(
        InlineKeyboardButton(text='Отмена', callback_data='cancel')
    )
    return keyboard_builder.as_markup()
