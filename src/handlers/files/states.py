from aiogram.fsm.state import StatesGroup, State


class FileStates(StatesGroup):
    select_files_for_del = State()
