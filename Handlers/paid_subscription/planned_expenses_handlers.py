from aiogram import Router, F
from aiogram.fsm.context import FSMContext

from aiogram.types import Message, CallbackQuery

from Lexicon.lexicon_ru import LEXICON_RU

router: Router = Router()


@router.callback_query(F.data.startswith(f'sub_{LEXICON_RU["planned_exp"]}'))
async def add_finance_user(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text='🧑🏼‍💻Находится в разработке')
    await callback.answer()
