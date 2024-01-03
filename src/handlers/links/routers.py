"""
Deus salvare animas nostras
"""
import logging
from datetime import datetime, timedelta
from uuid import uuid4

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.enums.parse_mode import ParseMode

from sqlalchemy.orm import sessionmaker

from handlers.files.models import File

from .models import Link
from .states import S
from .keyboards import get_files_list_keyboard

router = Router()

# datetime regex
DT_REGEX = r'^\d{1,2}\.\d{1,2}\.\d{4} \d{1,2}:\d{1,2}$'
DT_FORMAT = '%d.%m.%Y %H:%M'
# timedelta regex
TD_REGEX = r'^\d{1,3}:\d{1,2}$'

logger = logging.getLogger('app.links')


@router.message(StateFilter(S), Command('cancel'))
@router.callback_query(StateFilter(S), F.data == 'cancel')
async def cancel(msg: Message, state: FSMContext):
    logger.debug('[%d] cancel %s', msg.from_user.id, await state.get_state())
    await state.clear()
    await msg.answer('Отмена')


@router.message(Command('create_link'))
async def start_create_link(msg: Message, state: FSMContext, db_session: sessionmaker):
    logger.debug('[%d] start create link', msg.from_user.id)
    await state.clear()
    await state.set_state(S.set_file)
    with db_session() as session:  # TODO: reg us
        files = session.query(File).filter(File.user_tg_id == msg.from_user.id)
    await msg.answer('Выберите файл:', reply_markup=get_files_list_keyboard(files))


@router.callback_query(StateFilter(S.set_file), F.data.len() == 32)
async def set_ttl_prompt(callback: CallbackQuery, state: FSMContext):
    logger.debug('[%d] choose file %s', callback.from_user.id, callback.data)
    await callback.message.delete()
    await state.update_data(file_hash=callback.data)
    await state.set_state(S.set_ttl)

    await callback.bot.send_message(
        callback.from_user.id,
        '''
        Введите время жизни ссылки в формате:
          <b>dd.mm.yyyy hh:mm</b> - для указания точной даты и времени(UTC)
          <b>hh:mm</b> - для указания времени от создания ссылки(таймер)
          <b>/skip</b> для пропуска
        ''',
        parse_mode=ParseMode.HTML
    )


@router.message(StateFilter(S.set_ttl, S.set_counter), Command('skip'))
async def skip(msg: Message, state: FSMContext, db_session: sessionmaker):
    # FIXME: kurda🤔
    cur_state = await state.get_state()
    logger.debug('[%d] skip %s', msg.from_user.id, cur_state)
    match cur_state:
        case S.set_ttl:
            await state.set_state(S.set_counter)
            await set_counter_prompt(msg.bot, msg.from_user.id)
        case S.set_counter:
            await create_link(msg.bot, msg.from_user.id, state, db_session)


@router.message(StateFilter(S.set_ttl), F.text.regexp(TD_REGEX))
async def set_ttl_as_timedelta(msg: Message, state: FSMContext):
    logger.debug('[%d] set ttl %s', msg.from_user.id, msg.text)
    await state.set_state(S.set_counter)
    await state.update_data(td=msg.text)
    await set_counter_prompt(msg.bot, msg.from_user.id)


@router.message(StateFilter(S.set_ttl), F.text.regexp(DT_REGEX))
async def set_ttl_as_datetime(msg: Message, state: FSMContext):
    logger.debug('[%d] set ttl %s', msg.from_user.id, msg.text)
    try:
        # валидация🤔🤔🤔🤔
        ttl = datetime.strptime(msg.text, DT_FORMAT)
        if ttl <= datetime.utcnow():
            # 🤔🤔🤔🤔🤔
            raise ValueError('Invalid datetime')
    except ValueError as ve:
        await msg.answer('Неправильная дата')
        logger.debug('[%d] invalid ttl %s', msg.from_user.id, msg.text)
    else:
        await state.set_state(S.set_counter)
        await state.update_data(ttl=msg.text)
        await set_counter_prompt(msg.bot, msg.from_user.id)


async def set_counter_prompt(bot: Bot, user_id: int):
    return await bot.send_message(user_id, 'Введите количество переходов по ссылке или /skip')


@router.message(StateFilter(S.set_counter), F.text.isdigit())
async def set_counter(msg: Message, state: FSMContext, db_session: sessionmaker):
    logger.debug('[%d] set count %s', msg.from_user.id, msg.text)
    await state.update_data(number_uses=int(msg.text))
    await create_link(msg.bot, msg.from_user.id, state, db_session)


async def create_link(bot: Bot, user_id: int, state: FSMContext, db_session: sessionmaker):
    data = await state.get_data()
    await state.clear()

    link = Link()

    if 'ttl' in data:
        link.live_until = datetime.strptime(data['ttl'], DT_FORMAT)
    elif 'td' in data:
        h, m = data['td'].split(':')
        link.live_until = datetime.utcnow() + timedelta(hours=int(h), minutes=int(m))
    if 'number_uses' in data:
        link.number_uses = data['number_uses']

    link.urn = uuid4().hex
    link.user_tg_id = user_id

    with db_session() as session:
        file = session.query(File).filter(File.hash == data['file_hash']).first()
        link.file = file

        session.add(link)
        session.commit()
        session.refresh(link)

        logger.info('[%d] create links for file %s', user_id, file.filename)

    await bot.send_message(
        user_id,
        f'ссылка на файл: `{link.urn}`',
        parse_mode=ParseMode.MARKDOWN
    )


@router.message(Command('get'))
async def get_file(msg: Message, db_session: sessionmaker):
    try:
        urn = msg.text.split(' ')[1]
        logger.info('[%d] request file by link %s', msg.from_user.id, urn)
    except IndexError:
        logger.debug('[%d] invalid input format', msg.from_user.id)
        return msg.answer('надо указать urn ссылки /get <urn>')

    with db_session() as session:
        link = session.query(Link).filter(Link.urn == urn).first()
        if not link:
            logger.debug('[%d] link on file dont exist', msg.from_user.id)
            return await msg.answer('Такого файла не существует')

        if not link.check():
            logger.info('%s isnt longer valid', link.urn)
            await msg.answer('Ссылка больше не действительна')
            session.delete(link)
            session.commit()
            return

        if link.number_uses:
            link.number_uses -= 1

        file = link.file
        input_file = FSInputFile(File.DEFAULT_FOLDER / str(file.user_tg_id) / file.filename, file.filename)
        _cor = msg.bot.send_document(chat_id=msg.from_user.id, document=input_file)

        session.commit()
        session.refresh(link)

        logger.debug('link %s refresh(ttl: %s, uses: %d)', link.urn, link.live_until or '-', link.number_uses or -1)
        logger.info('[%d] got file %s', msg.from_user.id, file.filename)

        return await _cor
