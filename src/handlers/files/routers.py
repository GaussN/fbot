import os
from hashlib import md5
from io import BytesIO

import sqlalchemy.exc
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.types.input_file import FSInputFile
from aiogram.filters import Command
from aiogram.enums import ChatAction, ParseMode

from loguru import logger

from db import Session
from .models import File

from .states import FileStates
from .keyboards import get_del_files_list_keyboard, get_files_list_keyboard

router = Router()


@router.callback_query(F.data == 'cancel')
async def cancel(callbak: CallbackQuery, state: FSMContext):
    await state.clear()
    await callbak.message.delete()


@router.message(Command('files'))
async def get_files_list(msg: Message):
    await msg.delete()
    await msg.bot.send_chat_action(msg.chat.id, ChatAction.FIND_LOCATION)

    with Session() as db:
        files_set: list[File] = db.query(File).filter(File.user_id == msg.from_user.id).all()

    if not files_set:
        return await msg.answer(text='Кажется ты ещё не загружал файлы')

    await msg.answer(text='Файлы:', reply_markup=get_files_list_keyboard(files_set))


@router.message(F.document)
async def upload_file(msg: Message):
    user_id = msg.from_user.id
    filename = msg.document.file_name

    # FIXME: два раза вызывается download
    file_io = BytesIO()
    input_file = await msg.bot.get_file(msg.document.file_id)
    await msg.bot.download(input_file, file_io)

    file_path = File.DEFAULT_FOLDER / str(user_id)
    os.makedirs(file_path, exist_ok=True)

    await msg.bot.download(input_file, file_path / filename)

    with Session() as session:
        try:
            session.add(File(
                user_id=user_id,
                filename=filename,
                hash=md5(file_io.read()).hexdigest()
            ))
            session.commit()

            await msg.answer(text=f'файл добавлен в хранилище')
        except sqlalchemy.exc.IntegrityError:
            await msg.answer(text=f'Такой файл уже существует')


@router.callback_query(F.data.startswith('get:'))
async def get_file(callback: CallbackQuery):
    with Session() as db:
        try:
            file: File = db.query(File).filter(
                File.hash == callback.data[4:] and
                File.user_id == callback.from_user.id
            ).one()
        except sqlalchemy.exc.MultipleResultsFound as ex:
            logger.critical(ex)
            await callback.answer(text='Ой-ой! Произошла какая-то ошибка :o')
            raise SystemExit('Ошибка в БД') from ex
        except sqlalchemy.exc.NoResultFound:
            return await callback.answer(text='Ой ой кажется я не могу найти такой файл')

    input_file = FSInputFile(File.DEFAULT_FOLDER / str(file.user_id) / file.filename, file.filename)
    return await callback.bot.send_document(chat_id=file.user_id, document=input_file)


@router.message(Command('del'))
async def get_del_file_list(msg: Message, state: FSMContext):
    await msg.delete()
    with Session() as session:
        files: list[File] = session.query(File).filter(File.user_id == msg.from_user.id).all()

    if not files:
        return await msg.answer(text='У тебя ещё нет файлов :(')

    files_for_del = {file.hash: (False, file.filename) for file in files}
    await state.set_data(files_for_del)
    await msg.answer(
        text='Пометь файлы на удаление',
        reply_markup=get_del_files_list_keyboard(files_for_del),
        parse_mode=ParseMode.MARKDOWN_V2
    )
    await state.set_state(FileStates.select_files_for_del)


@router.callback_query(FileStates.select_files_for_del, F.data == 'delete')
async def del_files(callbak: CallbackQuery, state: FSMContext):
    # все файлы пользователя
    files: dict[str, tuple[bool, str]] = await state.get_data()
    # хэш файлов, помеченных на удаление
    files_to_delete = [file for file in files if files[file][0]]
    await state.clear()

    with Session() as session:
        count_del_files = session.query(File).filter(File.hash.in_(files_to_delete)).delete()
        session.commit()

    try:
        for flag, filename in files.values():
            if flag:
                os.remove(File.DEFAULT_FOLDER / str(callbak.from_user.id) / filename)
    except OSError as er:
        logger.error(er)

    await callbak.answer(text=f'Было удалено {count_del_files} файлов')
    await callbak.message.delete()


@router.callback_query(FileStates.select_files_for_del, F.data.len() == 32)
async def mark_file_for_del(callback: CallbackQuery, state: FSMContext):
    files: dict[str, list[bool, File]] = await state.get_data()
    files[callback.data] = not files[callback.data][0], files[callback.data][1]
    # NOTE: update_data не работате :(
    await state.set_data(files)
    return await callback.message.edit_reply_markup(
        callback.inline_message_id, reply_markup=get_del_files_list_keyboard(files=files)
    )
