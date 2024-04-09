import re

from aiogram import Router,
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from Bot_menu.menu import create_inline_kb
from Lexicon.lexicon_ru import LEXICON_RU
from data_base.orm import check_and_add_user_category_exp
from module_functions.users_function import user_check

router: Router = Router()




@router.message()
async def add_finance_user(message: Message, state: FSMContext):
    tg_id = int(message.from_user.id) if message.chat.type == 'private' else int(message.chat.id)



    FSM_state_check = await user_check(message=message, state=state, tg_id=tg_id)   # Проверяем был ли ранее зарегестрирован пользователь

    if FSM_state_check:
        match = re.match(r'([+-]?)(\d+[.,]?\d*)(?:\s+([^\-]+?))?(?:\s+-\s*(.*))?$', message.text.strip())

        if match:
            sign, amount_str, category, comment = match.groups()
            comment = comment if comment else ''
            amount = float(amount_str.replace(',', '.')) # Преобразование цифры в тип float

            if sign == '-':         # Если прислали со знаком -
                print('Расходы')
                check_category = await check_and_add_user_category_exp(tg_id=tg_id,
                                                                       amount=amount,
                                                                       category=category,
                                                                       comment=comment)

                if isinstance(check_category, str): # Добавили в категорию

                    await print_mess_exp()
                    await message_exp(check_category=check_category,
                                                amount=amout,
                                                comment: str,
                                                message: Message)


                else:
                    await message.answer(text=f'❔В какую категорию добавить {amount_str} ₽?',
                                         reply_markup=await create_inline_kb(1,
                                                                             f'e_{amount}_',
                                                                             *check_category,
                                                                             LEXICON_RU['category_user']))





            elif sign == '+':       # Если прислали со знаком +
                print('Доходы')
                # check_category = await check_and_add_user_category_inc(tg_id=tg_id,
                #                                                        amount=amount,
                #                                                        category=category,
                #                                                        comment=comment)
            else:                   # Если прислали без знака
                print('Без знака')


        # if message.text[0] == '+' or message.text[0] == '-': # Если пользователь прислал сообщение со знаком плюс или минус
        #     matches = re.match(r'([+-]?)\s*(\d+(?:[.,]\d+)?)\s*(?:на)?\s*([^\s]+)\s*(?:-\s*(.*))?', message.text)
        #     print('Тут')
        #     # Проверяем, найдены ли совпадения
        #     if matches:
        #         print('ТТТТТТТ')
        #         # Группа 1 содержит знак, группа 2 содержит сумму, группа 3 содержит категорию
        #         sign = matches.group(1)
        #         amount = matches.group(2) # Сумма
        #         category = matches.group(3).strip()
        #         comment = matches.group(4).strip() if matches.group(4) else ""
        #
        #         amount = float(amount.replace(',', '.')) # Преобразование цифры в тип float
        #
        #
        #         if sign == '+':
        #             print('Доходы')
        #             # check_category = await check_and_add_user_category_inc(tg_id=tg_id,
        #             #                                                        amount=amount,
        #             #                                                        category=category,
        #             #                                                        comment=comment)
        #         elif sign == '-':
        #             print('Расходы')
        #             check_category = await check_and_add_user_category_exp(tg_id=tg_id,
        #                                                                amount=amount,
        #                                                                category=category,
        #                                                                comment=comment)
        #
        # elif is_number(message.text):     # Если пользователь прислал только число
        #     price = message.text  # Сумма, которая была введена
        #
        #     operations_check = await user_old_operations_check(state=state)         # проверка последнего действия (Расходы/Доходы)
        #
        #     if not operations_check:    # Последнее действие расходы, или не было его
        #
        #         category_user = await get_exp_categories(tg_id)  # Получаем категории доходов
        #
        #         await message.answer(text=f'❔В какую категорию добавить {message.text} ₽?',
        #                              reply_markup=await create_inline_kb(1,
        #                                                                  f'e_{price}_',
        #                                                                  *category_user,
        #                                                                  LEXICON_RU['category_user']))
        #
        #     else:
        #         category_user = await get_inc_categories(tg_id)  # Получаем категории доходов
        #         await message.answer(text=f'❔В какую категорию добавить {message.text} ₽?',
        #                              reply_markup=await create_inline_kb(1,
        #                                                                  f'i_{price}_',
        #                                                                  *category_user,
        #                                                                  LEXICON_RU['category_user']))
        # else: # Если прислал без знака
        #     pass


@router.callback_query()
async def test_callback(callback: CallbackQuery):
    print(callback.data)