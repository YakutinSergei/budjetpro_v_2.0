from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from Bot_menu.menu import create_inline_kb
from FSMstate.FSMstate import FMSPiggyBank
from Lexicon.lexicon_ru import LEXICON_RU
from data_base.orm import get_data_bank, add_piggy_bank

router: Router = Router()


@router.callback_query(F.data.startswith(f'sub_{LEXICON_RU["piggy_bank"]}'))
async def add_finance_user(callback: CallbackQuery):
    tg_id = int(callback.from_user.id) if callback.message.chat.type == 'private' else int(callback.message.chat.id)
    data_bank_user = await get_data_bank(tg_id)
    text = (f'💰Баланс: {data_bank_user["balance"]}\n'
            f'🔄Автопополнение: {"Да" if data_bank_user["auto-renewal"] else "Нет"}')
    await callback.message.answer(text=text,
                                  reply_markup=await create_inline_kb(1,
                                                                      f'bank_',
                                                                      LEXICON_RU['replenish'],
                                                                      LEXICON_RU['bring_out'],
                                                                      LEXICON_RU['settings_user']))
    await callback.answer()


'''Кнопка отмены ввода'''

@router.callback_query(F.data.startswith(f'cancelFSM_'))
async def cancelFSM(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text=LEXICON_RU['cancel_text'])
    await callback.answer()
    await state.clear()

'''Выбор что мы хотим сделать'''

@router.callback_query(F.data.startswith(f'bank_'))
async def piggy_bank_process(callback: CallbackQuery, state: FSMContext):
    event = callback.data.split('_')[-1]
    if event == LEXICON_RU['replenish']:  # Пополнить
        await state.set_state(FMSPiggyBank.replenish)
        await callback.message.edit_text(text=LEXICON_RU['replenish_text'],
                                         reply_markup=await create_inline_kb(1,
                                                                             'cancelFSM_',
                                                                             LEXICON_RU['cancel']))

    elif event == LEXICON_RU['bring_out']:  # Вывести
        pass
    elif event == LEXICON_RU['settings_user']:  # Настройки
        pass
    print(callback.data)


'''Ввод суммы пополнения'''

@router.message(StateFilter(FMSPiggyBank.replenish))
async def process_enter_comment(message: Message, state: FSMContext):
    text = message.text.replace(',', '.')
    if can_convert_to_float(text):
        tg_id = int(message.from_user.id) if message.chat.type == 'private' else int(message.chat.id)

        await add_piggy_bank(tg_id=tg_id,
                             amount=float(text))

        await message.answer(text='✅ Копилка пополнена')
        await state.clear()
    else:
        await message.answer(text='🤦🏼‍♂️Вы ввели не число')


def can_convert_to_float(value):
    try:
        float(value)  # Попытка преобразовать строку в float
        return True  # Возвращаем True, если преобразование успешно
    except ValueError:
        return False  # Возвращаем False, если произошла ошибка
