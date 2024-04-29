from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from Bot_menu.menu import create_inline_kb
from Lexicon.lexicon_ru import LEXICON_RU
from data_base.orm import get_finances_by_month
from module_functions.users_function import get_text_message
from create_bot import bot

router: Router = Router()


'''Листания отчетов за месяц'''


@router.callback_query(F.data.startswith('report_'))
async def process_month_choice(callback: CallbackQuery):
    tg_id = int(callback.from_user.id) if callback.message.chat.type == 'private' else int(callback.message.chat.id)

    month = int(callback.data.split('_')[1])
    year = int(callback.data.split('_')[2])

    operation = callback.data.split('_')[-1]

    if operation == LEXICON_RU['back_report']:  # Предыдущий месяц
        if month == 1:
            month = 12
            year -= 1
        else:
            month -= 1
    elif operation == LEXICON_RU['forward_report']:  # Следующий месяц
        if month == 12:
            month = 1
            year += 1
        else:
            month += 1

    report_month = await get_finances_by_month(tg_id=tg_id,
                                               month=month,
                                               year=year)

    text = get_text_message(report_month, month, year)

    await bot.edit_message_text(chat_id=tg_id,
                                message_id=callback.message.message_id,
                                text=text,
                                reply_markup=await create_inline_kb(2,
                                                                    f'report_{month}_'
                                                                    f'{year}_',
                                                                    LEXICON_RU['back_report'],
                                                                    LEXICON_RU['forward_report']))
    await callback.answer()
