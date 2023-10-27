from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums import ParseMode

router = Router()


info_message = """
Бот *\<НАЗВАНИЕ БОТА\>*
Бот для хранения файлов
Список команд:
/ping \(pong\)
/files \(вернет список твоих файлов\)
/del \(выбрать файлы на удаление\)

Для добавления файла просто пришлите его боту
"""


@router.message(Command('start', 'help', 'info'))
async def info(msg: Message):
    return await msg.answer(info_message, parse_mode=ParseMode.MARKDOWN_V2)

