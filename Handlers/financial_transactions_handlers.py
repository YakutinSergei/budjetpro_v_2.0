import re
import calendar

from datetime import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from Bot_menu.menu import create_inline_kb, kb_date_order, kb_day_order, kb_month_order, kb_year_order
from Lexicon.lexicon_ru import LEXICON_RU
from data_base.orm import add_cetegory_exp, add_cetegory_inc, check_and_add_user_category_exp, \
    check_and_add_user_category_inc, delete_exp, delete_inc, get_exp_categories, get_inc_categories, update_dates_trans
from module_functions.users_function import message_inc, print_message_choice_category, user_check, message_exp, user_old_operations_check
from create_bot import bot

router: Router = Router()



#region Обработка сообщения от пользователя


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
                if category:
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
                            s = await state.get_data()
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
                    
                else: 
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
                    

'''Функция выбора категории ADD_e/i_amount_cat'''
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


'''Функция выбора котегорий Доходы/расходы  на вход: choiceCat_500.0_📉Расходы'''
@router.callback_query(F.data.startswith('choiceCat_'))
async def choice_global_category(callback: CallbackQuery, state: FSMContext):
    tg_id = int(callback.from_user.id) if callback.message.chat.type == 'private' else int(callback.message.chat.id)

    category = callback.data.split('_')[-1]
    amount = callback.data.split('_')[1]
    

    if category == LEXICON_RU['expenses_cat']: # Категории расходов
        categorys = await get_exp_categories(tg_id=tg_id)
        await bot.edit_message_text(chat_id=tg_id,
                                    message_id=callback.message.message_id,
                                    text=f'❔В какую категорию добавить {amount} ₽?',
                                    reply_markup=await create_inline_kb(1,
                                                            f'ADD_e_{amount}_',
                                                            *categorys,
                                                            LEXICON_RU['category_user']))
        
    elif category == LEXICON_RU['income_cat']: # Категории доходов
        categorys = await get_inc_categories(tg_id=tg_id)
        await bot.edit_message_text(chat_id=tg_id,
                                    message_id=callback.message.message_id,
                                    text=f'❔В какую категорию добавить {amount} ₽?',
                                    reply_markup=await create_inline_kb(1,
                                                            f'ADD_i_{amount}_',
                                                            *categorys,
                                                            LEXICON_RU['category_user']))

#endregion


#region Кнопки изменения транзакии
'''LEXICON_RU['date_fin'] - изменить дату,
     LEXICON_RU['comment'] - изменить коментарий,
     LEXICON_RU['change'] - кнопка изменить,
     LEXICON_RU['cancel_fin'] - отмена записи'''

'''Кнопки изменения транзакций'''


@router.callback_query(F.data.startswith('Edit_'))
async def edit_transaction(callback: CallbackQuery, state: FSMContext):
    action = callback.data.split('_')[-1] # выбор действия
    tg_id = int(callback.from_user.id) if callback.message.chat.type == 'private' else int(callback.message.chat.id)
    category = callback.data.split('_')[1] # Доход или расход (e/i)
    id_trans = callback.data.split('_')[2] # id транзакции в базе данных
    # Выбрано отмена записи
    if action == LEXICON_RU['cancel_fin']:
        text = callback.message.text
        if category == 'e':
            await delete_exp(tg_trans=int(id_trans)) # Удаляем запись
            await bot.edit_message_text(text=f'<s>{text}</s>',
                                        chat_id=tg_id,
                                        message_id=callback.message.message_id,
                                        reply_markup=None)
        elif category == 'i':
            await delete_inc(tg_trans=int(id_trans)) # Удаляем запись
            await bot.edit_message_text(text=f'<s>{text}</s>',
                                        chat_id=tg_id,
                                        message_id=callback.message.message_id,
                                        reply_markup=None)

    # Нажата кнопка изменить дату
    elif action == LEXICON_RU['date_fin']:
        current_datetime = str(datetime.now().date())
        await bot.edit_message_reply_markup(chat_id=tg_id,
                                            message_id=callback.message.message_id,
                                            reply_markup=await kb_date_order(order_datetime=current_datetime,
                                                                             id_trans=id_trans,
                                                                             cat=category)
                                            )

    await callback.answer()


'''Выбор даты  cur_e_1_14/4/2024_day'''


@router.callback_query(F.data.startswith('cur_'))
async def process_choice_date(callback: CallbackQuery, state: FSMContext):
    date_chance = callback.data.split('_')[-1]

    category = callback.data.split('_')[1]  # Доход или расход (e/i)
    id_trans = callback.data.split('_')[2]  # id транзакции в базе данных

    date = callback.data.split('_')[-2] # Дата
    month_order = int(date.split('/')[1]) # месяц
    year_order = int(date.split('/')[2]) # Год
    # Выбор изменения числа
    if date_chance == 'day':
        first_day_of_month_weekday_index = calendar.monthrange(year_order, month_order)[0]  # какой сейчас день недели
        count_day_month = calendar.monthrange(year_order, month_order)[1]  # Количество дней в месяце
        await bot.edit_message_reply_markup(chat_id=callback.from_user.id,
                                            message_id=callback.message.message_id,
                                            reply_markup=await kb_day_order(index_day=first_day_of_month_weekday_index,
                                                                            count_day_month=count_day_month,
                                                                            id_trans=id_trans,
                                                                            cat=category,
                                                                            date=date))
    elif date_chance == 'month':
        await bot.edit_message_reply_markup(chat_id=callback.from_user.id,
                                            message_id=callback.message.message_id,
                                            reply_markup=await kb_month_order(id_trans=id_trans,
                                                                              cat=category,
                                                                              date=date))

    else:
        await bot.edit_message_reply_markup( chat_id=callback.from_user.id,
                                             message_id=callback.message.message_id,
                                             reply_markup=await kb_year_order(id_trans=id_trans,
                                                                              cat=category,
                                                                              date=date))
    await callback.answer()


'''Запись нового числа chDay_i_2_14/4/2024_26'''


@router.callback_query(F.data.startswith('chDay_'))
async def process_day_choice(callback: CallbackQuery, state: FSMContext):
    day_order_new = callback.data.split('_')[-1] # День который выбрал пользователь

    tg_id = int(callback.from_user.id) if callback.message.chat.type == 'private' else int(callback.chat.id)

    data = callback.data.split('_')[-2]  # Дата
    month_order = data.split('/')[1]  # месяц
    year_order = data.split('/')[2] # Год

    new_date_order = "-".join([year_order,
                               month_order,
                               day_order_new]) # Новая дата заказа

    category = callback.data.split('_')[1]  # Доход или расход (e/i)
    id_trans = callback.data.split('_')[2]  # id транзакции в базе данных

    await bot.edit_message_reply_markup(chat_id=tg_id,
                                        message_id=callback.message.message_id,
                                        reply_markup=await kb_date_order(order_datetime=new_date_order,
                                                                         id_trans=id_trans,
                                                                         cat=category)
                                        )

    await callback.answer()


'''Запись нового месяца chMon_i_2_5/4/2024_12'''


@router.callback_query(F.data.startswith('chMon_'))
async def process_month_choice(callback: CallbackQuery, state: FSMContext):
    month_order_new = callback.data.split('_')[-1] #Месяц который выбрал пользователь
    tg_id = int(callback.from_user.id) if callback.message.chat.type == 'private' else int(callback.chat.id)

    data = callback.data.split('_')[-2]  # Дата
    year_order = data.split('/')[2]     # Год
    day_order = data.split('/')[0]      # День

    category = callback.data.split('_')[1]  # Доход или расход (e/i)
    id_trans = callback.data.split('_')[2]  # id транзакции в базе данных

    # Проверяем количество дней в месяце
    # если текущий день больше чем количество дней в месяце ставим последний день месяца
    count_day_month = calendar.monthrange(int(year_order), int(month_order_new))[1]
    if count_day_month < int(day_order):
        day_order = str(count_day_month)

    new_date_order = "-".join([year_order,
                               month_order_new,
                               day_order])  # Новая дата заказа

    await bot.edit_message_reply_markup(chat_id=tg_id,
                                        message_id=callback.message.message_id,
                                        reply_markup=await kb_date_order(order_datetime=new_date_order,
                                                                         id_trans=id_trans,
                                                                         cat=category)
                                        )

    await callback.answer()


'''Выбор года chYear_i_2_5/2/2024_2023'''


@router.callback_query(F.data.startswith('chYear_'))
async def process_year_choice(callback: CallbackQuery, state: FSMContext):

    year_order_new = callback.data.split('_')[-1] # Год который выбрал пользователь
    tg_id = int(callback.from_user.id) if callback.message.chat.type == 'private' else int(callback.chat.id)

    data = callback.data.split('_')[-2]  # Дата
    month_order = data.split('/')[1]  # месяц
    day_order = data.split('/')[0]  # День

    category = callback.data.split('_')[1]  # Доход или расход (e/i)
    id_trans = callback.data.split('_')[2]  # id транзакции в базе данных

    count_day_month = calendar.monthrange(int(year_order_new), int(month_order))[1]
    if count_day_month < int(day_order):
        day_order = str(count_day_month)

    new_date_order = "-".join([year_order_new,
                               month_order,
                               day_order])  # Новая дата заказа

    await bot.edit_message_reply_markup(chat_id=tg_id,
                                        message_id=callback.message.message_id,
                                        reply_markup=await kb_date_order(order_datetime=new_date_order,
                                                                         id_trans=id_trans,
                                                                         cat=category)
                                        )

    await callback.answer()


'''Кнопка назад в дате backDateOrder_i_1_14/4/2024'''


@router.callback_query(F.data.startswith('backDateOrder_'))
async def process_day_choice(callback: CallbackQuery, state: FSMContext):
    tg_id = int(callback.from_user.id) if callback.message.chat.type == 'private' else int(callback.chat.id)

    data = callback.data.split('_')[-1]  # Дата
    year_order = data.split('/')[2]     # Год
    month_order = data.split('/')[1]  # месяц
    day_order = data.split('/')[0]  # День

    category = callback.data.split('_')[1]  # Доход или расход (e/i)
    id_trans = callback.data.split('_')[2]  # id транзакции в базе данных


    new_date_order = "-".join([year_order,
                               month_order,
                               day_order])  # Новая дата заказа

    await bot.edit_message_reply_markup(chat_id=tg_id,
                                        message_id=callback.message.message_id,
                                        reply_markup=await kb_date_order(order_datetime=new_date_order,
                                                                         id_trans=id_trans,
                                                                         cat=category)
                                        )

    await callback.answer()


'''Кнопка отмены ordCancel_i_3'''


@router.callback_query(F.data.startswith('ordCancel_'))
async def process_cancel_date(callback: CallbackQuery, state: FSMContext):
    category = callback.data.split('_')[1]  # Доход или расход (e/i)
    id_trans = callback.data.split('_')[2]  # id транзакции в базе данных

    tg_id = int(callback.from_user.id) if callback.message.chat.type == 'private' else int(callback.chat.id)

    await bot.edit_message_reply_markup(chat_id=tg_id,
                                        message_id=callback.message.message_id,
                                        reply_markup=await create_inline_kb(2,
                                                                            f"Edit_{category}_{id_trans}_",
                                                                            LEXICON_RU['date_fin'],
                                                                            LEXICON_RU['comment'],
                                                                            LEXICON_RU['change'],
                                                                            LEXICON_RU['cancel_fin'],
                                                                            ))
    await callback.answer()


'''Кнопка готово на изменение даты done_i_3_9/4/2024'''


@router.callback_query(F.data.startswith('done'))
async def procces_done_date_expenses(callback: CallbackQuery, state: FSMContext):
    category = callback.data.split('_')[1]  # Доход или расход (e/i)
    id_trans = callback.data.split('_')[2]  # id транзакции в базе данных

    date = callback.data.split('_')[-1]  # Дата

    tg_id = int(callback.from_user.id) if callback.message.chat.type == 'private' else int(callback.chat.id)

    text_trans = callback.message.text.split("\n")[0]
    text_data = callback.message.text.split("\n")[1].split(':')[0]
    text_data = f'{text_data}: {date} г.'
    text_comment = callback.message.text.split("\n")[2] if len(callback.message.text.split("\n")) > 2 else ''

    await update_dates_trans(date=date,
                             id_trans=id_trans,
                             category=category)

    if update_dates_trans:
        await bot.edit_message_text(text=f'{text_trans}\n{text_data}\n{text_comment}',
                                    chat_id=tg_id,
                                    message_id=callback.message.message_id,
                                    reply_markup=await create_inline_kb(2,
                                                                        f"Edit_{category}_{id_trans}_",
                                                                        LEXICON_RU['date_fin'],
                                                                        LEXICON_RU['comment'],
                                                                        LEXICON_RU['change'],
                                                                        LEXICON_RU['cancel_fin'],
                                                                                ))
    else:
        await callback.message.answer(text='Запись не найдена')
    await callback.answer()




#endregion


@router.callback_query()
async def test_callback(callback: CallbackQuery):
    print(callback.data)
    await callback.answer()