import json
from datetime import datetime

import redis
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from Bot_menu.menu import create_inline_kb
from Lexicon.lexicon_ru import LEXICON_RU
from create_bot import bot
from data_base.orm import check_user_exists, get_inc_categories, get_exp_categories

'''Функция проверки есть ли такой пользователь в базе'''


async def user_check(message: Message, state: FSMContext, tg_id: int):
    FSM_state = await state.get_data()  # Получаем данные из FSM

    if not 'user_check' in FSM_state:
        user = await check_user_exists(tg_id)  # Проверяем есть ли такой пользователь
        if user:  # Если есть такой пользователь
            await state.update_data(user_check=True)  # Обновляем состояние
            return True
        else:
            await state.update_data(user_check=False)  # Обновляем состояние
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
    s = await state.get_data()
    if 'old_operations' in s:
        return s['old_operations']
    else:  # Если нет последних добавлений, то
        await state.update_data(old_operations=False)  # Обновляем FSM
        return False


'''Функция вывода сообщение о том что добавлена новая запись в расходы'''


async def message_exp(check_category: str,
                      amount: float,
                      message: Message,
                      state: FSMContext,
                      comment: str = ''):
    date_value = datetime.now()
    # Извлекаем день, месяц и год из значения даты
    day = date_value.day
    month = date_value.month
    year = date_value.year

    id_fin = check_category.split('`')[-1]
    name_cat = check_category.split('`')[0]

    text = (f'✅Добавлено {amount} ₽ в категорию расходов "{name_cat}" \n'
            f'Дата: <i>{day}/{month}/{year} г.</i>')

    if comment != '':
        comment = f'\n<i>{comment}</i>'

    await message.answer(text=text + comment,
                         reply_markup=await create_inline_kb(2,
                                                             f"Edit_e_{id_fin}_",
                                                             LEXICON_RU['date_fin'],
                                                             LEXICON_RU['comment'],
                                                             LEXICON_RU['change'],
                                                             LEXICON_RU['cancel_fin'],
                                                             ))
    await state.update_data(old_operations=False)


async def message_exp_edit(check_category: str,
                           amount: float,
                           message_id: int,
                           tg_id: int,
                           message: Message,
                           state: FSMContext,
                           comment: str = ''):
    date_value = datetime.now()
    # Извлекаем день, месяц и год из значения даты
    day = date_value.day
    month = date_value.month
    year = date_value.year

    id_fin = check_category.split('`')[-1]
    name_cat = check_category.split('`')[0]

    text = (f'✅Добавлено {amount} ₽ в категорию расходов "{name_cat}" \n'
            f'Дата: <i>{day}/{month}/{year} г.</i>')

    if comment != '':
        comment = f'\n<i>{comment}</i>'

    await bot.edit_message_text(chat_id=tg_id,
                                message_id=message_id,
                                text=text + comment,
                                reply_markup=await create_inline_kb(2,
                                                                    f"Edit_e_{id_fin}_",
                                                                    LEXICON_RU['date_fin'],
                                                                    LEXICON_RU['comment'],
                                                                    LEXICON_RU['change'],
                                                                    LEXICON_RU['cancel_fin'],
                                                                    ))

    await state.update_data(old_operations=False)


'''Функция вывода сообщение о том что добавлена новая запись в доходы'''


async def message_inc(check_category: str,
                      amount: float,
                      message: Message,
                      state: FSMContext,
                      comment: str = ''):
    date_value = datetime.now()
    # Извлекаем день, месяц и год из значения даты
    day = date_value.day
    month = date_value.month
    year = date_value.year

    id_fin = check_category.split('`')[-1]
    name_cat = check_category.split('`')[0]

    text = (f'✅Добавлено {amount} ₽ в источник доходов "{name_cat}" \n'
            f'Дата: <i>{day}/{month}/{year} г.</i>')

    if comment != '':
        comment = f'\n<i>{comment}</i>'

    await message.answer(text=text + comment,
                         reply_markup=await create_inline_kb(2,
                                                             f"Edit_i_{id_fin}_",
                                                             LEXICON_RU['date_fin'],
                                                             LEXICON_RU['comment'],
                                                             LEXICON_RU['change'],
                                                             LEXICON_RU['cancel_fin'],
                                                             ))

    await state.update_data(old_operations=True)


async def message_inc_edit(check_category: str,
                           amount: float,
                           message_id: int,
                           tg_id: int,
                           message: Message,
                           state: FSMContext,
                           comment: str = ''):

    date_value = datetime.now()
    # Извлекаем день, месяц и год из значения даты
    day = date_value.day
    month = date_value.month
    year = date_value.year

    id_fin = check_category.split('`')[-1]
    name_cat = check_category.split('`')[0]

    text = (f'✅Добавлено {amount} ₽ в источник доходов "{name_cat}" \n'
            f'Дата: <i>{day}/{month}/{year} г.</i>')

    if comment != '':
        comment = f'\n<i>{comment}</i>'

    await bot.edit_message_text(text=text + comment,
                                chat_id=tg_id,
                                message_id=message_id,
                                reply_markup=await create_inline_kb(2,
                                                                    f"Edit_i_{id_fin}_",
                                                                    LEXICON_RU['date_fin'],
                                                                    LEXICON_RU['comment'],
                                                                    LEXICON_RU['change'],
                                                                    LEXICON_RU['cancel_fin'],
                                                                    ))

    await state.update_data(old_operations=True)


'''Функиия выбора категорий'''


async def print_message_choice_category(operation: str,
                                        message: Message,
                                        amount: float,
                                        categorys: list):
    await message.answer(text=f'❔В какую категорию добавить {amount} ₽?',
                         reply_markup=await create_inline_kb(1,
                                                             f'ADD_{operation}_{amount}_',
                                                             *categorys,
                                                             LEXICON_RU['category_user']))


'''Функция проверки на число'''


def is_number(s):
    try:
        float(s.replace(",", "."))  # Заменяем запятые на точки, чтобы правильно обработать дробные числа
        return True
    except ValueError:
        return False


'''Текст на отчет за месяц'''


def get_text_message(report_month, month, year):
    all_summary_income = 0  # Общая сумма доходов
    all_limit_income = 0  # Общий лимит дохожов
    all_summary_expense = 0  # Общая сумма расходов
    all_limit_expense = 0  # Общая сумма лимитов расходов

    report_income = report_month[0]  # Все доходы
    keys_income = report_income.keys()  # Категории доходов
    report_expense = report_month[1]  # Все расходы
    keys_expense = report_expense.keys()  # Категории расходов
    month_name = get_month_nam_full(month)
    text = f'{LEXICON_RU["income_cat"]} в {month_name} {year} года\n'
    for key in keys_income:
        all_summary_income += report_income[key][0]
        all_limit_income += report_income[key][1]

        summary = report_income[key][0]  # Сумма потраченных денег
        limit = report_income[key][1]  # Лимит
        percent_income_text = ''
        if limit > 0:
            percent = '{0:.2f}'.format(summary / limit * 100)
            percent_income_text = f'({percent}%)'

        text += f'{key}: {report_income[key][0]} Руб. {percent_income_text}\n'

    # Текст на доходы
    percent_income_text = ''
    if all_limit_income > 0:
        percent_income = '{0:.2f}'.format(all_summary_income / all_limit_income * 100)
        percent_income_text = f'({percent_income}%)'
    text += (f'-------------------\n'
             f'Итого: {all_summary_income} {percent_income_text}\n'
             f'\n{LEXICON_RU["expenses_cat"]} в {month_name} {year} года\n')

    # Текст на расходы
    for key in keys_expense:
        all_summary_expense += report_expense[key][0]
        all_limit_expense += report_expense[key][1]

        summary = report_expense[key][0]  # Сумма потраченных денег
        limit = report_expense[key][1]  # Лимит
        percent_expenses_text = ''
        if limit > 0:
            percent = '{0:.2f}'.format(summary / limit * 100)
            percent_expenses_text = f'({percent}%)'

        text += f'{key}: {report_expense[key][0]} Руб. {percent_expenses_text}\n'

    percent_expenses_text = ''
    if all_limit_income > 0:
        percent_income = '{0:.2f}'.format(all_summary_income / all_limit_income * 100)
        percent_expenses_text = f'({percent_income}%)'
    text += (f'-------------------\n'
             f'Итого: {all_summary_expense} {percent_expenses_text}\n\n')

    return text


def get_month_nam_full(month_number):
    months = {
        1: 'январе',
        2: 'феврале',
        3: 'марте',
        4: 'апреле',
        5: 'мае',
        6: 'июне',
        7: 'июле',
        8: 'августе',
        9: 'сентябре',
        10: 'октябре',
        11: 'ноябре',
        12: 'декабре'
    }
    return months.get(month_number, 'Некорректный номер месяца')


async def get_redis_data(keys: str):
    r = redis.Redis(host='localhost', port=6379, db=0)
    categories_str = r.get(f'{keys}')
    if categories_str:
        category_list = json.loads(categories_str)
        return category_list
    else:
        return False


'''Функция вывода на экран сообщения с категориями в настройках'''


async def print_message_list_category(category: str, tg_id: int, callback: CallbackQuery):
    if category == 'e':
        category = LEXICON_RU['expenses_cat']
    elif category == 'i':
        category = LEXICON_RU['income_cat']

    if category == LEXICON_RU['income_cat']:
        category_user = await get_redis_data(f'categories_inc:{tg_id}')  # Получаем категории доходов из Redis

        if category_user:
            categorys = [category[1] for category in category_user]
        else:  # Если в редис нет
            categorys = await get_inc_categories(tg_id)  # Получаем категории доходов

        await bot.edit_message_text(chat_id=tg_id,
                                    message_id=callback.message.message_id,
                                    text=f'Выберите категорию',
                                    reply_markup=await create_inline_kb(1,
                                                                        f'SAC_i_',
                                                                        *categorys,
                                                                        LEXICON_RU['add'],
                                                                        LEXICON_RU['back_date_order']))
    elif category == LEXICON_RU['expenses_cat']:  # Категории расходов
        category_user = await get_redis_data(f'categories_exp:{tg_id}')  # Получаем категории доходов из Redis
        if category_user:
            categorys = [category[1] for category in category_user]
        else:  # Если в редис нет
            categorys = await get_exp_categories(tg_id)  # Получаем категории расходов

        await bot.edit_message_text(chat_id=tg_id,
                                    message_id=callback.message.message_id,
                                    text=f'Выберите категорию',
                                    reply_markup=await create_inline_kb(1,
                                                                        f'SAC_e_',
                                                                        *categorys,
                                                                        LEXICON_RU['add'],
                                                                        LEXICON_RU['back_date_order']))


'''Функция печати сообщения с выбором категорий для редактирования'''


async def print_message_setting_categoryes(tg_id: int,
                                           callback: CallbackQuery):
    await bot.edit_message_text(text='📈Настройки категорий📉',
                                chat_id=tg_id,
                                message_id=callback.message.message_id,
                                reply_markup=await create_inline_kb(1,
                                                                    'setCategory_',
                                                                    LEXICON_RU['income_cat'],
                                                                    LEXICON_RU['expenses_cat'],
                                                                    LEXICON_RU['back_date_order']))
