import json

import redis
from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from Bot_menu.menu import create_inline_kb
from FSMstate.FSMstate import FSMsettings
from Lexicon.lexicon_ru import LEXICON_RU
from create_bot import bot
from data_base.orm import get_data_personal_bd, get_exp_categories, get_inc_categories, edit_name_category, \
    add_inc_category_bd, add_exp_category_bd
from module_functions.users_function import get_redis_data, print_message_list_category, \
    print_message_setting_categoryes, user_old_operations_check

router: Router = Router()


@router.message(F.text == LEXICON_RU['settings_user'])
async def add_finance_user(message: Message):
    await message.answer(text=LEXICON_RU['settings_user'],
                         reply_markup=await create_inline_kb(1,
                                                             'set_',
                                                             LEXICON_RU['set_category'],
                                                             LEXICON_RU['set_help']))


''' Нажата кнопка в сообщении настроек'''


@router.callback_query(F.data.startswith('set_'))
async def set_category_user(callback: CallbackQuery):
    tg_id = int(callback.from_user.id) if callback.message.chat.type == 'private' else int(callback.message.chat.id)

    set_item = callback.data.split('_')[-1]  # Что выбрал пользователь

    if set_item == LEXICON_RU['set_category']:
        await print_message_setting_categoryes(tg_id=tg_id,
                                               callback=callback)

    await callback.answer()


'''Нажата кнопка на категории доходов/расходов'''


@router.callback_query(F.data.startswith('setCategory_'))
async def set_category_user(callback: CallbackQuery):
    tg_id = int(callback.from_user.id) if callback.message.chat.type == 'private' else int(callback.message.chat.id)

    category = callback.data.split('_')[-1]  # Что выбрал пользователь

    if category == LEXICON_RU['back_date_order']:  # Кнопка назад
        await bot.edit_message_text(text=LEXICON_RU['settings_user'],
                                    chat_id=tg_id,
                                    message_id=callback.message.message_id,
                                    reply_markup=await create_inline_kb(1,
                                                                        'set_',
                                                                        LEXICON_RU['set_category'],
                                                                        LEXICON_RU['set_help']))
    else:  # Если выбрал категорию расходов или доходов
        await print_message_list_category(category=category,
                                          tg_id=tg_id,
                                          callback=callback)
    await callback.answer()


'''настройка определенной категории '''


@router.callback_query(F.data.startswith('SAC_'))
async def set_category_all_user(callback: CallbackQuery, state: FSMContext):
    tg_id = int(callback.from_user.id) if callback.message.chat.type == 'private' else int(callback.message.chat.id)
    operation = callback.data.split('_')[1]  # E/I
    category = callback.data.split('_')[-1]

    if category == LEXICON_RU['back_date_order']:
        await print_message_setting_categoryes(tg_id=tg_id,
                                               callback=callback)
    elif category == LEXICON_RU['add']:
        if operation == 'e':
            category_user = await get_redis_data('categories_exp')  # Получаем категории расходов из Redis
            # Узнаем id категории
            category_id = 0

            for item in category_user:
                if item[1] == category:
                    category_id = item[0]
                    break

            await callback.message.answer(text=LEXICON_RU['add_expenses_cat'])
            await state.set_state(FSMsettings.add_category)
            await state.update_data(operators=operation)
            await state.update_data(id_category=category_id)
            await state.update_data(id_message=callback.message.message_id)
        elif operation == 'i':
            category_user = await get_redis_data('categories_inc')  # Получаем категории расходов из Redis
            # Узнаем id категории
            category_id = 0

            for item in category_user:
                if item[1] == category:
                    category_id = item[0]
                    break
            await callback.message.answer(text=LEXICON_RU['add_income_cat'])
            await state.set_state(FSMsettings.add_category)
            await state.update_data(operators=operation)
            await state.update_data(id_category=category_id)
            await state.update_data(id_message=callback.message.message_id)
    else:
        if operation == 'e':
            category_user = await get_redis_data('categories_exp')  # Получаем категории расходов из Redis
        elif operation == 'i':
            category_user = await get_redis_data('categories_inc')

        if category_user:
            categorys = [category[1] for category in category_user]
        else:  # Если в редис нет
            categorys = await get_exp_categories(tg_id)  # Получаем категории расходов
            category_user = await get_redis_data('categories_exp')  # Получаем категории расходов из Redis

        # Узнаем id категории
        category_id = 0

        for item in category_user:
            if item[1] == category:
                category_id = item[0]
                break

        await bot.edit_message_text(chat_id=tg_id,
                                    message_id=callback.message.message_id,
                                    text=f'Редактирование категории <b>"{category}"</b>',
                                    reply_markup=await create_inline_kb(1,
                                                                        f'eCat_{operation}_{category_id}_',
                                                                        LEXICON_RU['edit_name'],
                                                                        LEXICON_RU['edit_position'],
                                                                        LEXICON_RU['edit_summ'],
                                                                        LEXICON_RU['del_category'],
                                                                        LEXICON_RU['back_date_order']))
    await callback.answer()


'''Добавление новых категорий'''


@router.message(StateFilter(FSMsettings.add_category))
async def process_enter_name_comment(message: Message, state: FSMContext):
    tg_id = int(message.from_user.id) if message.chat.type == 'private' else int(message.chat.id)
    info_cat = await state.get_data()  # Получаем данные из FSM
    message_id = info_cat['id_message']  # ID сообщения
    operator = info_cat['operators']  # e/i
    old_operations = await user_old_operations_check(state)  # Последнее действие

    category_expenses: list[str] = []
    if message.text:
        if operator == 'e':
            for text_category in message.text.split('\n'):
                category_expenses.append(text_category.replace('_', '').replace("'", '')
                                         .replace('"', ''))

            await add_exp_category_bd(tg_id=tg_id, category=category_expenses)  # Добавляем истоники расходов
        elif operator == 'i':
            for text_category in message.text.split('\n'):
                category_expenses.append(text_category.replace('_', '').replace("'", ''))
            await add_inc_category_bd(tg_id=tg_id, category=category_expenses)  # Добавляем источники доходов

        # Редакторивание сообщения
        if operator == 'e':
            category = LEXICON_RU['expenses_cat']
        elif operator == 'i':
            category = LEXICON_RU['income_cat']

        if category == LEXICON_RU['income_cat']:
            category_user = await get_redis_data('categories_inc')  # Получаем категории доходов из Redis

            if category_user:
                categorys = [category[1] for category in category_user]
            else:  # Если в редис нет
                categorys = await get_inc_categories(tg_id)  # Получаем категории доходов

            await bot.edit_message_text(chat_id=tg_id,
                                        message_id=message_id,
                                        text=f'Выберите категорию',
                                        reply_markup=await create_inline_kb(1,
                                                                            f'SAC_i_',
                                                                            *categorys,
                                                                            LEXICON_RU['add'],
                                                                            LEXICON_RU['back_date_order']))
        elif category == LEXICON_RU['expenses_cat']:  # Категории расходов
            category_user = await get_redis_data('categories_exp')  # Получаем категории расходов из Redis

            if category_user:
                categorys = [category[1] for category in category_user]
            else:  # Если в редис нет
                categorys = await get_exp_categories(tg_id)  # Получаем категории расходов

            await bot.edit_message_text(chat_id=tg_id,
                                        message_id=message_id,
                                        text=f'Выберите категорию',
                                        reply_markup=await create_inline_kb(1,
                                                                            f'SAC_e_',
                                                                            *categorys,
                                                                            LEXICON_RU['add'],
                                                                            LEXICON_RU['back_date_order']))

    else:
        await message.answer(text='УПС! Что то пошло не так')

    await state.clear()
    await state.update_data(user_check=True)
    await state.update_data(old_operations=old_operations)


'''Нажата кнопка на действие по редактированию'''


@router.callback_query(F.data.startswith('eCat_'))
async def set_edit_category_user(callback: CallbackQuery, state: FSMContext):
    tg_id = int(callback.from_user.id) if callback.message.chat.type == 'private' else int(callback.message.chat.id)

    operator = callback.data.split('_')[1]  # расходы или доходы e/i
    operations = callback.data.split('_')[-1]  # Действие выбрано какое
    category_id = callback.data.split('_')[2]  # id категории

    if operations == LEXICON_RU['edit_name']:  # Изменение имени
        await state.set_state(FSMsettings.name)
        await state.update_data(operators=operator)
        await state.update_data(id_category=category_id)
        await state.update_data(id_message=callback.message.message_id)
        await callback.message.answer(text='Введите новое название категории'
                                           '<i>Название не должно превышать 15 символов</i>')
    elif operations == LEXICON_RU['edit_position']:  # Изменение позиции
        pass
    elif operations == LEXICON_RU['edit_summ']:  # Изменение суммы
        pass
    elif operations == LEXICON_RU['del_category']:  # Удаление категории
        pass
    elif operations == LEXICON_RU['back_date_order']:  # Назад
        await print_message_list_category(category=operator,
                                          tg_id=tg_id,
                                          callback=callback)
    await callback.answer()


'''Установление нового имени'''


@router.message(StateFilter(FSMsettings.name))
async def process_enter_name_comment(message: Message, state: FSMContext):
    tg_id = int(message.from_user.id) if message.chat.type == 'private' else int(message.chat.id)
    info_cat = await state.get_data()  # Получаем данные из FSM
    id_cat = info_cat['id_category']  # Id записи
    message_id = info_cat['id_message']  # ID сообщения
    operator = info_cat['operators']  # e/i
    old_operations = info_cat['old_operations']  # Последнее действие
    edit_cat = await edit_name_category(id_cat=id_cat,
                                        operator=operator,
                                        tg_id=tg_id,
                                        new_name=message.text[:17])
    if edit_cat:
        await bot.edit_message_text(chat_id=tg_id,
                                    message_id=message_id,
                                    text=f'Редактирование категории <b>"{message.text[:17]}"</b>',
                                    reply_markup=await create_inline_kb(1,
                                                                        f'eCat_{operator}_{id_cat}_',
                                                                        LEXICON_RU['edit_name'],
                                                                        LEXICON_RU['edit_position'],
                                                                        LEXICON_RU['edit_summ'],
                                                                        LEXICON_RU['del_category'],
                                                                        LEXICON_RU['back_date_order']))

        await message.answer(text='✅Название успешно изменено')
        await state.clear()
        await state.update_data(user_check=True)
        await state.update_data(old_operations=old_operations)
    else:
        await message.answer(text=LEXICON_RU['edit_name_error'])


'''Установить новую позицию'''
