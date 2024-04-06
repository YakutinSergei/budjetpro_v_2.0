import re

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from Handlers.start_handlers import process_start_command
from Lexicon.lexicon_ru import LEXICON_RU
from data_base.orm import check_user_exists
from module_functions.users_function import user_check

router: Router = Router()




@router.message()
async def add_finance_user(message: Message, state: FSMContext):
    tg_id = int(message.from_user.id) if message.chat.type == 'private' else int(message.chat.id)

    FSM_state =await user_check(message=message, state=state, tg_id=tg_id)

    print(FSM_state['user_check'])

    if is_number(message.text):     # Если пользователь прислал только число
                                    # Функция проверки состояния FSM что последнее добавлял

        if 'old_operations' in FSM_state:
            print('Есть')
        else: # Если нет последних добавлений, то
            await state.update_data(old_operations=False)  # Обновляем FSM

            #operation = FSM_state['old_operations'] # True - доходы, False - расходы
        print('Продолжаем работу')

    elif message.text[0] == '+' or message.text[0] == '-': # Если пользователь прислал сообщение со знаком плюс или минус
        matches = re.match(r'([+-]?)\s*(\d+(?:[.,]\d+)?)\s*(?:на)?\s*([^\s]+)\s*(?:-\s*(.*))?', message.text)



    else: #Если пользователя нет в БД
        await process_start_command(message)


'''Функция проверки на число'''


def is_number(s):
    try:
        float(s.replace(",", "."))  # Заменяем запятые на точки, чтобы правильно обработать дробные числа
        return True
    except ValueError:
        return False