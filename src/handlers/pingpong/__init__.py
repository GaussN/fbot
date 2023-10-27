from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

router = Router()


@router.message(Command('ping'))
@router.message(F.text == 'ping')
async def ping(msg: Message):
    await msg.answer('pong')
