import io
import os
from sys import path_hooks

from aiogram.types import FSInputFile

from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from Bot_menu.menu import create_inline_kb
from Lexicon.lexicon_ru import LEXICON_RU
from data_base.orm import get_finances_by_month
from module_functions.users_function import get_text_message
from create_bot import bot

router: Router = Router()




@router.message(F.text == '/report')
@router.message(F.text == LEXICON_RU['report_month_user'])
async def add_finance_user(message: Message):
    tg_id = int(message.from_user.id) if message.chat.type == 'private' else int(message.chat.id)

    report_month = await get_finances_by_month(tg_id=tg_id,
                                               month=datetime.now().month,
                                               year=datetime.now().year)

    text = get_text_message(report_month, datetime.now().month, datetime.now().year)

    await message.answer(text=text,
                         reply_markup=await create_inline_kb(2,
                                                             f'report_{datetime.now().month}_'
                                                             f'{datetime.now().year}_',
                                                             LEXICON_RU['back_report'],
                                                             LEXICON_RU['forward_report']))


