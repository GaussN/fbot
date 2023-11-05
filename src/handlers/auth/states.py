from aiogram.fsm.state import State, StatesGroup


class AuthStates(StatesGroup):
    enter_email = State()
    enter_code = State()
    enter_new_password = State()
    enter_password = State()
