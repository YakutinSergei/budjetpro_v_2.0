from aiogram import Router, F
from aiogram.types import CallbackQuery

from Bot_menu.menu import create_inline_kb
from Lexicon.lexicon_ru import LEXICON_RU
from data_base.orm import get_data_bank

router: Router = Router()


@router.callback_query(F.data.startswith(f'sub_{LEXICON_RU["piggy_bank"]}'))
async def add_finance_user(callback: CallbackQuery):
    tg_id = int(callback.from_user.id) if callback.message.chat.type == 'private' else int(callback.message.chat.id)
    data_bank_user = await get_data_bank(tg_id)
    print(data_bank_user)
    text = (f'💰Баланс: {data_bank_user["balance"]}\n'
            f'🔄Автопополнение: {"Да" if data_bank_user["auto-renewal"] else "Нет"}')
    await callback.message.answer(text=text,
                                  reply_markup=await create_inline_kb(1,
                                                                      f'bank_',
                                                                      LEXICON_RU['replenish'],
                                                                      LEXICON_RU['bring_out'],
                                                                      LEXICON_RU['settings_user']))
    await callback.answer()
