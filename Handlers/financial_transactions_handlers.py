import re

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from Bot_menu.menu import create_inline_kb
from Lexicon.lexicon_ru import LEXICON_RU
from data_base.orm import add_cetegory_exp, add_cetegory_inc, check_and_add_user_category_exp, check_and_add_user_category_inc, get_exp_categories, get_inc_categories
from module_functions.users_function import message_inc, print_message_choice_category, user_check, message_exp, user_old_operations_check
from create_bot import bot

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
                check_category = await check_and_add_user_category_exp(tg_id=tg_id,
                                                                       amount=amount,
                                                                       category=category,
                                                                       comment=comment)

                if isinstance(check_category, str): # Добавили в категорию
                    await message_exp(check_category=check_category,
                                      amount=amount,
                                      comment=comment,
                                      message=message,
                                      state=state)

                else:
                    # Печатаем сообщение с выбором категорий
                    await print_message_choice_category(operation='e',
                                                        message=message, 
                                                        amount=amount,
                                                        categorys=check_category)
                    
                

            elif sign == '+':       # Если прислали со знаком +
                check_category = await check_and_add_user_category_inc(tg_id=tg_id,
                                                                       amount=amount,
                                                                       category=category,
                                                                       comment=comment)

                if isinstance(check_category, str): # Добавили в категорию
                    await message_inc(check_category=check_category,
                                      amount=amount,
                                      comment=comment,
                                      message=message,
                                      state=state)

                else:
                    # Печатаем сообщение с выбором категорий
                    await print_message_choice_category(operation='i',
                                                        message=message, 
                                                        amount=amount,
                                                        categorys=check_category)
                    
            else:                   # Если прислали без знака
                print('Без знака')
                s = await state.get_data()
                print(s)
                operations_check = await user_old_operations_check(state=state)         # проверка последнего действия (Расходы/Доходы)
                
                if operations_check:    
                    category_user = await get_inc_categories(tg_id)  # Получаем категории доходов
                    operation = 'i'
                else:
                    category_user = await get_exp_categories(tg_id)  # Получаем категории расходов
                    operation = 'e'

                # Печатаем сообщение с выбором категорий
                await print_message_choice_category(operation=operation,
                                                    message=message, 
                                                    amount=amount,
                                                    categorys=category_user)
                    

'''Функция выбора категории'''
@router.callback_query(F.data.startswith('ADD_'))
async def choice_category(callback: CallbackQuery, state: FSMContext):
    tg_id = int(callback.from_user.id) if callback.message.chat.type == 'private' else int(callback.message.chat.id)
    
    category = callback.data.split('_')[-1]   # Имя категории
    amount = float(callback.data.split('_')[-2])       # Сумма платежа
    operation = callback.data.split('_')[1]     # Операция e/i
    if category == LEXICON_RU['category_user']:
        await bot.edit_message_reply_markup(chat_id=tg_id,
                                            message_id=callback.message.message_id,
                                            reply_markup=await create_inline_kb(1,
                                                                                f'choiceCat_{amount}_',
                                                                                LEXICON_RU['expenses_cat'],
                                                                                LEXICON_RU['income_cat'])
                                              )
    
    elif operation == 'i':   # Категории доходов

        check_add = await add_cetegory_inc(tg_id=tg_id,
                                           amount=amount,
                                           category=category)
        

        await bot.delete_message(chat_id=tg_id,
                                 message_id=callback.message.message_id)
        
        await message_inc(check_category=check_add,
                          amount=amount,
                          message=callback.message,
                          state=state)
        
    elif operation == 'e':   # Категории расходов
        check_add = await add_cetegory_exp(tg_id=tg_id,
                                           amount=amount,
                                           category=category)
        
        await bot.delete_message(chat_id=tg_id,
                                 message_id=callback.message.message_id)
        await message_exp(check_category=check_add,
                          amount=amount,
                          message=callback.message,
                          state=state)


    await callback.answer()



@router.callback_query()
async def test_callback(callback: CallbackQuery):
    print(callback.data)