import redis
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from Bot_menu.menu import create_inline_kb
from Lexicon.lexicon_ru import LEXICON_RU
from create_bot import bot
from data_base.orm import get_data_personal_bd, get_exp_categories, get_inc_categories

router: Router = Router()


@router.message(F.text == LEXICON_RU['settings_user'])
async def add_finance_user(message: Message):
    r = redis.Redis(host='localhost', port=6379, db=0)

    categories_str = r.get('categories_inc')
    print(categories_str)
    if categories_str:
        inc_categories = categories_str.decode('utf-8').split(',')
        print(inc_categories)
    else:
        print('Нет такой ')
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
        await bot.edit_message_text(text='📈Настройки категорий📉',
                                    chat_id=tg_id,
                                    message_id=callback.message.message_id,
                                    reply_markup=await create_inline_kb(1,
                                                                        'setCategory_',
                                                                        LEXICON_RU['income_cat'],
                                                                        LEXICON_RU['expenses_cat'],
                                                                        LEXICON_RU['back_date_order']))

    await callback.answer()


'''Нажата кнопка на категории доходов/расходов'''


@router.callback_query(F.data.startswith('setCategory_'))
async def set_category_user(callback: CallbackQuery):
    tg_id = int(callback.from_user.id) if callback.message.chat.type == 'private' else int(callback.message.chat.id)

    category = callback.data.split('_')[-1]  # Что выбрал пользователь
    if category == LEXICON_RU['income_cat']:
        categorys = await get_inc_categories(tg_id=tg_id)
        await bot.edit_message_text(chat_id=tg_id,
                                    message_id=callback.message.message_id,
                                    text=f'Выберите категорию',
                                    reply_markup=await create_inline_kb(1,
                                                                        f'setAllCat_i_',
                                                                        *categorys,
                                                                        LEXICON_RU['add'],
                                                                        LEXICON_RU['back_date_order']))
    elif category == LEXICON_RU['expenses_cat']:
        categorys = await get_exp_categories(tg_id=tg_id)
        await bot.edit_message_text(chat_id=tg_id,
                                    message_id=callback.message.message_id,
                                    text=f'Выберите категорию',
                                    reply_markup=await create_inline_kb(1,
                                                                        f'setAllCat_e_',
                                                                        *categorys,
                                                                        LEXICON_RU['add'],
                                                                        LEXICON_RU['back_date_order']))
    elif category == LEXICON_RU['back_date_order']:
        await bot.edit_message_text(text=LEXICON_RU['settings_user'],
                                    chat_id=tg_id,
                                    message_id=callback.message.message_id,
                                    reply_markup=await create_inline_kb(1,
                                                                        'set_',
                                                                        LEXICON_RU['set_category'],
                                                                        LEXICON_RU['set_help']))
    await callback.answer()


'''настройка определенной категории'''


@router.callback_query(F.data.startswith('setAllCat_'))
async def set_category_all_user(callback: CallbackQuery):
    print('тут')
    tg_id = int(callback.from_user.id) if callback.message.chat.type == 'private' else int(callback.message.chat.id)
    operation = callback.data.split('_')[1]
    category = callback.data.split('_')[-1]

    await bot.edit_message_text(chat_id=tg_id,
                                message_id=callback.message.message_id,
                                text=f'Редактирование категории {category}',
                                reply_markup=await create_inline_kb(1,
                                                                    f'eCat_{operation}_{category}_',
                                                                    LEXICON_RU['edit_name'],
                                                                    LEXICON_RU['edit_position'],
                                                                    LEXICON_RU['del_category'],
                                                                    LEXICON_RU['del_category'],
                                                                    LEXICON_RU['back_date_order']))

