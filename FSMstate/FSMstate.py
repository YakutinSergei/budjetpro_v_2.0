from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State


class FSMfinance(StatesGroup):
    old_operations = State()
    user_check = State()


class FSMtest(StatesGroup):
    test = State()