from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State


class FSMfinance(StatesGroup):
    old_operations = State()
    user_check = State()


class FSMsettings(StatesGroup):
    add_category = State()
    name = State()
    summ = State()
    operators = State()
    id_category = State()
    id_message = State()