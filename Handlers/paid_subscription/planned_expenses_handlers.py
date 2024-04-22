from aiogram import Router, F
from aiogram.fsm.context import FSMContext

from aiogram.types import Message, CallbackQuery

router: Router = Router()


@router.callback_query(F.data.startswith('sub_'))
async def add_finance_user(message: Message, state: FSMContext):
    print('тут')
