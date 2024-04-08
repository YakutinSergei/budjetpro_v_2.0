from aiogram import Router, F
from aiogram.filters import StateFilter, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from Bot_menu.menu import create_inline_kb, kb_menu_user
from data_base.orm import add_users_bd, add_inc_category_bd, add_exp_category_bd
from Lexicon.lexicon_ru import LEXICON_RU


router: Router = Router()


class FSMcategory_add(StatesGroup):
    category = State()


@router.message(CommandStart())
async def process_start_command(message: Message):
    tg_id = int(message.from_user.id) if message.chat.type == 'private' else int(message.chat.id)

    user = await add_users_bd(tg_id=tg_id)

    if user:
        await message.answer(text=LEXICON_RU['start_text'])
        await message.answer(text=LEXICON_RU['setting_category'],
                             reply_markup=await create_inline_kb(2,
                                                                 'choiceCategory_',
                                                                 LEXICON_RU['expenses_cat'],
                                                                 LEXICON_RU['income_cat']))
    else:

        await message.answer(text="Привет",
                             reply_markup=await kb_menu_user())



'''Добавление категорий расходов или доходов'''
@router.callback_query(F.data.startswith('choiceCategory_'))
async def process_add_category_order(callback: CallbackQuery, state: FSMContext):
    category = callback.data.split('_')[-1]
    await state.set_state(FSMcategory_add.category)
    await state.update_data(category=category)  # Обновляем FSM

    if category == LEXICON_RU['expenses_cat']:
        await callback.message.edit_text(text=LEXICON_RU['add_expenses_cat'])
    else:
        await callback.message.edit_text(text=LEXICON_RU['add_income_cat'])


'''ВВод второй категории'''


@router.message(StateFilter(FSMcategory_add.category))
async def process_add_order_location(message: Message, state: FSMContext):
    tg_id = int(message.from_user.id) if message.chat.type == 'private' else int(message.chat.id)

    category = await state.get_data()  # Записывыем данные из FSM
    category = category['category']
    category_expenses: list[str] = []

    #Ввод расходов
    if category == LEXICON_RU['expenses_cat']:
        for text_category in message.text.split('\n'):
            category_expenses.append(text_category.replace('_', '').replace("'", ''))

        await add_exp_category_bd(tg_id=tg_id, category=category_expenses) # Добавляем категории расходов в базу данных
        await message.answer(text=f"✅Категории расходов успешно добавлены\n\n"
                                  f"{LEXICON_RU['add_income_cat']}")
        await state.update_data(category='ok_expenses')  # Обновляем FSM

    # Ввод источников доходов
    elif category == LEXICON_RU['income_cat']:
        for text_category in message.text.split('\n'):
            category_expenses.append(text_category.replace('_', '').replace("'", ''))
        await add_inc_category_bd(tg_id=tg_id, category=category_expenses) # Добавляем источники доходов
        await state.update_data(category='ok_income')  # Обновляем FSM
        await message.answer(text=f"✅Источники доходов успешно добавлены\n\n"
                                  f"{LEXICON_RU['add_expenses_cat']}")
    # Ввод расходов 2 этап
    elif category == 'ok_expenses':
        for text_category in message.text.split('\n'):
            category_expenses.append(text_category.replace('_', '').replace("'", ''))
        await add_inc_category_bd(tg_id=tg_id, category=category_expenses) # Добавляем источники доходов
        await state.clear() #Очищаем FSM


        await message.answer(text=LEXICON_RU['add_category_ok'],
                             reply_markup=await kb_menu_user())


    # Ввод источников доходов 2 этап
    else:
        for text_category in message.text.split('\n'):
            category_expenses.append(text_category.replace('_', '').replace("'", ''))
        await add_exp_category_bd(tg_id=tg_id, category=category_expenses) # Добавляем категории расходов в базу данных
        await state.clear() #Очищаем FSM

        await message.answer(text=LEXICON_RU['add_category_ok'],
                             reply_markup=await kb_menu_user())
