from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message


from Handlers.start_handlers import process_start_command
from data_base.orm import check_user_exists

'''Функция проверки есть ли такой пользователь в базе'''
async def user_check(message: Message, state: FSMContext, tg_id: int):
    FSM_state = await state.get_data()  # Получаем данные из FSM
    if not 'user_check' in FSM_state:
        user = await check_user_exists(tg_id)
        if user:
            await state.update_data(user_check=True)
        else:
            await state.update_data(user_check=False)
            await message.answer(text="Вы не зарегистрированы, для продолжения введите команду '/start'")
    return FSM_state