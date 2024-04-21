from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from Bot_menu.menu import create_inline_kb
from Lexicon.lexicon_ru import LEXICON_RU
from data_base.orm import get_data_personal_bd

router: Router = Router()


@router.message(F.text == 'personal_account')
@router.message(F.text == LEXICON_RU['personal_account_user'])
async def add_finance_user(message: Message):
    tg_id = int(message.from_user.id) if message.chat.type == 'private' else int(message.chat.id)

    data_personal = await get_data_personal_bd(tg_id=tg_id)

    balance = '{:,}'.format(data_personal["balance"]).replace(',', ' ')  # Баланс
    total_incomes = '{:,}'.format(data_personal["total_incomes"]).replace(',', ' ')  # Сумма доходов
    total_expenses = '{:,}'.format(data_personal["total_expenses"]).replace(',', ' ')  # Сумма расходов
    income_categories_count = data_personal["income_categories_count"]  # Количество категорий доходов
    expense_categories_count = data_personal["expense_categories_count"]  # Количество категорий расходов
    incomes_current_month = '{:,}'.format(data_personal["incomes_current_month"]).replace(',',
                                                                                          ' ')  # Сумма доходов в текущем месяце
    expenses_current_month = '{:,}'.format(data_personal["expenses_current_month"]).replace(',',
                                                                                            ' ')  # Сумма расходов в текущем месяце

    subscription = f'<b>🗓️ Подписка действует до:</b> <code>{data_personal["subscription"]}</code>' \
        if data_personal["subscription"] else '😔Подписка не активна🤦🏼‍♂️'
    text = (f'<b><u>👤 Личный Кабинет</u></b>\n\n'
            f'<b>💰 Общий баланс:</b> <code>{balance} руб.</code>\n\n'
            f'<b>📈 Доходы</b>\n'
            f'  - <b>Категорий:</b> <code>{income_categories_count}</code>\n'
            f'  - <b>Общая сумма:</b> <code>{total_incomes} руб.</code>\n'
            f'  - <b>За текущий месяц:</b> <code>{incomes_current_month} руб.</code>\n\n'
            f'<b>📉 Расходы</b>\n'
            f'  - <b>Категорий:</b> <code>{expense_categories_count}</code>\n'
            f'  - <b>Общая сумма:</b> <code>{total_expenses} руб.</code>\n'
            f'  - <b>За текущий месяц:</b> <code>{expenses_current_month} руб.</code>\n\n'
            f'{subscription}')

    await message.answer(text=text,
                         reply_markup= await create_inline_kb(1,
                                                              'sub_',
                                                              LEXICON_RU['planned_exp'],
                                                              LEXICON_RU['subscription'],
                                                              ))
