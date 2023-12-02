from aiogram.fsm.state import State, StatesGroup


class S(StatesGroup):
    set_file = State()
    set_ttl = State()
    set_counter = State()
