from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from FSMstate.FSMstate import FSMfinance
from Handlers.start_handlers import process_start_command
from data_base.orm import check_user_exists

'''Функция проверки есть ли такой пользователь в базе'''
async def user_check(message: Message, state: FSMContext, tg_id: int):
    FSM_state = await state.get_data()  # Получаем данные из FSM

    if not 'user_check' in FSM_state:
        user = await check_user_exists(tg_id)           # Проверяем есть ли такой пользователь
        if user:                                        # Если есть такой пользователь
            await state.update_data(user_check=True)    # Обновляем состояние
            return True
        else:
            await state.update_data(user_check=False)   # Обновляем состояние
            await message.answer(text="Вы не зарегистрированы, для продолжения введите команду '/start'")
            return False
    else:
        if FSM_state['user_check'] == False:
            user = await check_user_exists(tg_id)  # Проверяем есть ли такой пользователь
            if user:  # Если есть такой пользователь
                await state.update_data(user_check=True)  # Обновляем состояние
                return True
            else:
                await state.update_data(user_check=False)  # Обновляем состояние
                await message.answer(text="Вы не зарегистрированы, для продолжения введите команду '/start'")
                return False
        else:
            return True



'''Функция проверки что последнее добавляли'''
async def user_old_operations_check(state: FSMContext):
    if 'old_operations' in FSMfinance:
        return FSMfinance['old_operations']
    else:  # Если нет последних добавлений, то
        await state.update_data(old_operations=False)  # Обновляем FSM
        return False


'''Функция проверки на число'''


def is_number(s):
    try:
        float(s.replace(",", "."))  # Заменяем запятые на точки, чтобы правильно обработать дробные числа
        return True
    except ValueError:
        return False