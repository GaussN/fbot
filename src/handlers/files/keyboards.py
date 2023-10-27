from emoji import emojize
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from handlers.files.models import File


def get_del_files_list_keyboard(files: dict[str, tuple[bool, str]]) -> InlineKeyboardMarkup:
    """
    dict[str, tuple[bool, str]]
    file_hash: (mark_for_del, file_name)
    """
    del_markup = InlineKeyboardBuilder()
    for hash_, (mark, filename) in files.items():
        del_markup.row(
            InlineKeyboardButton(
                text=f'{emojize(":red_circle:") if mark else emojize(":radio_button:")}{filename}',
                callback_data=hash_
            )
        )

    del_markup.row(
        InlineKeyboardButton(text='Отмена', callback_data='cancel'),
        InlineKeyboardButton(text='Удалить', callback_data='delete'),
    )

    return del_markup.as_markup()


def get_files_list_keyboard(files: list[File]) -> InlineKeyboardMarkup:
    markup_builder = InlineKeyboardBuilder()
    for file in files:
        markup_builder.row(
            InlineKeyboardButton(
                text=file.filename,
                callback_data=f'get:{file.hash}'
            )
        )
    markup_builder.row(InlineKeyboardButton(text='Отмена', callback_data='cancel'))
    return markup_builder.as_markup()
