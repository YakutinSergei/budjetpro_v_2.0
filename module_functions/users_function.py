from datetime import datetime

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from Bot_menu.menu import create_inline_kb
from FSMstate.FSMstate import FSMfinance
from Handlers.start_handlers import process_start_command
from Lexicon.lexicon_ru import LEXICON_RU
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


'''Функция вывода сообщение о том что добавлена новая запись в расходы'''


async def message_exp(check_category: str,
                            amount: float,
                            comment: str,
                            message: Message):
    date_value = datetime.now()
    # Извлекаем день, месяц и год из значения даты
    day = date_value.day
    month = date_value.month
    year = date_value.year

    id_fin = check_category.split('`')[-1]

    text = (f'✅Добавлено {amount} ₽ в источник доходов "{check_category}" \n'
            f'Дата: <i>{day}/{month}/{year} г.</i>')

    if comment != '':
        comment = f'\n<i>{comment}</i>'

    await message.answer(text=text + comment,
                         reply_markup=await create_inline_kb(2,
                                                             f"e_{id_fin}_",
                                                             LEXICON_RU['date_fin'],
                                                             LEXICON_RU['comment'],
                                                             LEXICON_RU['change'],
                                                             LEXICON_RU['cancel_fin'],
                                                             ))


'''Функция проверки на число'''


def is_number(s):
    try:
        float(s.replace(",", "."))  # Заменяем запятые на точки, чтобы правильно обработать дробные числа
        return True
    except ValueError:
        return False