import re

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from Bot_menu.menu import create_inline_kb
from FSMstate.FSMstate import FSMfinance
from Handlers.start_handlers import process_start_command
from Lexicon.lexicon_ru import LEXICON_RU
from data_base.orm import check_user_exists, get_exp_categories, get_inc_categories
from module_functions.users_function import user_check, user_old_operations_check, is_number

router: Router = Router()




@router.message()
async def add_finance_user(message: Message, state: FSMContext):
    tg_id = int(message.from_user.id) if message.chat.type == 'private' else int(message.chat.id)



    FSM_state_check = await user_check(message=message, state=state, tg_id=tg_id)   # Проверяем был ли ранее зарегестрирован пользователь

    if FSM_state_check:
        if is_number(message.text):     # Если пользователь прислал только число
            price = message.text  # Сумма, которая была введена

            operations_check = await user_old_operations_check(state=state)         # проверка последнего действия (Расходы/Доходы)

            if not operations_check:    # Последнее действие расходы, или не было его

                category_user = await get_exp_categories(tg_id)  # Получаем категории доходов

                await message.answer(text=f'❔В какую категорию добавить {message.text} ₽?',
                                     reply_markup=await create_inline_kb(1,
                                                                         f'e_{price}_',
                                                                         *category_user,
                                                                         LEXICON_RU['category_user']))

            else:
                category_user = await get_inc_categories(tg_id)  # Получаем категории доходов
                await message.answer(text=f'❔В какую категорию добавить {message.text} ₽?',
                                     reply_markup=await create_inline_kb(1,
                                                                         f'i_{price}_',
                                                                         *category_user,
                                                                         LEXICON_RU['category_user']))

        elif message.text[0] == '+' or message.text[0] == '-': # Если пользователь прислал сообщение со знаком плюс или минус
            matches = re.match(r'([+-]?)\s*(\d+(?:[.,]\d+)?)\s*(?:на)?\s*([^\s]+)\s*(?:-\s*(.*))?', message.text)

        else: # Если прислал без знака
            pass


@router.callback_query()
async def test_callback(callback: CallbackQuery):
    print(callback.data)