import re
from hashlib import md5

from emoji import emojize

import sqlalchemy.exc
from loguru import logger
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from aiogram.types import Message

from db import Session as DbSession

from .states import AuthStates
from .utils import gen_verify_code, send_verify_code

from .models import User, UserSession


router = Router()

EMAIL_REGEX = re.compile(r'^[\w-]+@\w+\.com$')
VERIFY_CODE_REGEX = re.compile(r'^[0-9a-zA-Z]{5}$')
PASSWORD_REGEX = re.compile(r'^.{5,30}$')

ATTEMPS_NUMBER = 3


@router.message(StateFilter(AuthStates), Command('cancel'))
async def cancel(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer('Галя, отмена!')


@router.message(Command('auth'))
async def start_auth(msg: Message, state: FSMContext):
    with DbSession() as session:
        if session.query(UserSession).filter(UserSession.tg_id == msg.from_user.id).first():
            return await msg.answer(
                emojize('Для входа сначала надо выйти:wolf:')
            )

    await state.set_state(AuthStates.enter_email)
    await msg.answer('Пришли мне свой email')


@router.message(AuthStates.enter_email)
async def get_email(msg: Message, state: FSMContext):
    user_email = msg.text.strip()
    if not EMAIL_REGEX.fullmatch(user_email):
        return await msg.answer('Неверный адрес')
    
    with DbSession() as session:
        if user := session.query(User).filter(User.email == user_email).first():
            await state.set_data({'user': user})
            await state.set_state(AuthStates.enter_password)
            return await msg.answer('Введи пароль')

    verify_code = gen_verify_code()
    await state.set_data({'email': user_email, 'code': verify_code, 'attemps': ATTEMPS_NUMBER})
    await state.set_state(AuthStates.enter_code)
    await msg.answer('Я отправил тебе на почту код. Пришли мне его')
    # TODO: проверка отправки письма
    logger.debug(send_verify_code(user_email, verify_code))


@router.message(AuthStates.enter_code)
async def get_code(msg: Message, state: FSMContext):
    entered_code = msg.text.strip()
    data = await state.get_data()

    if not VERIFY_CODE_REGEX.fullmatch(entered_code):
        return await msg.answer('Неверный формат кода')

    data['attemps'] = data['attemps'] - 1
    if data['attemps'] < 0:
        await state.clear()
        return await msg.answer('У тебя закончились попытки. Попробуй заново')

    if data['code'] != entered_code:
        await state.set_data(data)
        return await msg.answer('Неверный код')

    await state.set_state(AuthStates.enter_new_password)
    await msg.answer('Придумай пароль(от 5 до 30 символов)')


@router.message(AuthStates.enter_new_password)
async def get_new_password(msg: Message, state: FSMContext):
    user_password = msg.text.strip()
    if not PASSWORD_REGEX.fullmatch(user_password):
        return await msg.answer('!от 5 до 30 символов!')
    # user = await state.get_data()
    try:
        data = await state.get_data()
        new_user = User(
            tg_id=msg.from_user.id,
            email=data['email'],
            password_hash=md5(user_password.encode()).hexdigest()
        )
        new_session = UserSession(
            user=new_user,
            tg_id=msg.from_user.id
        )
        with DbSession() as session:
            session.add(new_user)
            session.add(new_session)
            session.commit()
    except Exception as ex:
        logger.error(ex)
        logger.error(ex.__traceback__.tb_next)
    await state.clear()
    await msg.answer(f'Произошла регистрация{emojize(":tada:")}')
    await me(msg)


@router.message(AuthStates.enter_password)
async def get_password(msg: Message, state: FSMContext):
    password = msg.text.strip()
    password_hash = md5(password.encode()).hexdigest()

    data = await state.get_data()
    user: User = data['user']
    if password_hash != user.password_hash:
        return msg.answer(emojize('Неверный пароль:red_circle:'))

    with DbSession() as session:
        new_user_session = UserSession(user=user, tg_id=msg.from_user.id)
        session.add(new_user_session)
        session.commit()

    await msg.answer('Здарова!')
    await state.clear()


@router.message(Command('me'))
async def me(msg: Message):
    with DbSession() as session:
        user_session: UserSession = session.query(UserSession).filter(UserSession.tg_id == msg.from_user.id).first()
        if user_session:
            user_sessions = '\n'.join([str(s.tg_id) for s in user_session.user.sessions])
            return await msg.answer(f'''
{user_session.tg_id} авторизован как {user_session.user.tg_id}
Пользователь {user_session.user.email}
Cессий({user_session.user.sessions.__len__()}):
{user_sessions}
''')

        user: User = session.query(User).filter(User.tg_id == msg.from_user.id).first()
        if user:
            return await msg.answer(f'вы пользователь без сессии({user.email})')

        return await msg.answer(f'Незарегистрированный пользователь(tg:{msg.from_user.id})')


@router.message(Command('exit'))
async def exit_(msg: Message, state: FSMContext):
    with DbSession() as session:
        try:
            user_session = session.query(UserSession).filter(UserSession.tg_id == msg.from_user.id).one()
            session.delete(user_session)
            session.commit()
        except sqlalchemy.exc.NoResultFound:
            return await msg.answer(emojize('Для выхода надо сначала войти:wolf:'))
    await msg.answer(f'Произошол выход{emojize(":exploding_head:")}')
    await state.clear()
