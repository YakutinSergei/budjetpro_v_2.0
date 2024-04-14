from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from datetime import datetime

from Lexicon.lexicon_ru import LEXICON_RU

'''генератор клавиатур'''


async def create_inline_kb(width: int,
                           pref: str,
                           *args: str,
                           **kwargs: str) -> InlineKeyboardMarkup:
    # Инициализируем билдер
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    # Инициализируем список для кнопок
    buttons: list[InlineKeyboardButton] = []

    # Заполняем список кнопками из аргументов args и kwargs
    if args:
        for button in args:
            buttons.append(InlineKeyboardButton(
                text=LEXICON_RU[button] if button in LEXICON_RU else button,
                callback_data=pref + button))

    if kwargs:
        for button, text in kwargs.items():
            buttons.append(InlineKeyboardButton(
                text=text,
                callback_data=pref + button))

    # Распаковываем список с кнопками в билдер методом row c параметром width
    kb_builder.row(*buttons, width=width)

    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()


'''Клавиатура на выбор даты'''


async def kb_date_order(order_datetime, id_trans: str, cat: str):
    # Получаем текущую дату и время
    current_datetime = datetime.strptime(order_datetime, "%Y-%m-%d")

    # Получаем текущий год, месяц и число
    current_year = current_datetime.year
    current_month = get_month_name(current_datetime.month)
    current_day = current_datetime.day
    # Инициализируем билдер
    inline_markup: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = [InlineKeyboardButton(
        text=str(current_day),
        callback_data=f'cur_{cat}_{id_trans}_{current_day}/{current_datetime.month}/{current_year}_day'
    ), InlineKeyboardButton(
        text=str(current_month),
        callback_data=f'cur_{cat}_{id_trans}_{current_day}/{current_datetime.month}/{current_year}_month'
    ), InlineKeyboardButton(
        text=str(current_year),
        callback_data=f'cur_{cat}_{id_trans}_{current_day}/{current_datetime.month}/{current_year}_year'
    )
    ]
    inline_markup.row(*buttons, width=3)

    # Инициализируем список для кнопок
    buttons: list[InlineKeyboardButton] = [InlineKeyboardButton(
        text=LEXICON_RU['done'],
        callback_data=f'done_{cat}_{id_trans}_{current_day}/{current_datetime.month}/{current_year}'
    ), InlineKeyboardButton(
        text=LEXICON_RU['cancel'],
        callback_data=f'ordCancel_{cat}_{id_trans}'
    )
    ]
    inline_markup.row(*buttons, width=1)
    return inline_markup.as_markup()


'''Клавиатура на изменение '''


async def kb_edit_message(id_exp: str, cat: int):
    if cat == 1:
        pref = 'exp'
    else:
        pref = 'inc'

    # Инициализируем билдер
    inline_markup: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = [InlineKeyboardButton(
        text=LEXICON_RU['edit_sum'],
        callback_data=f'editSum_{pref}_{id_exp}'
    ), InlineKeyboardButton(
        text=LEXICON_RU['edit_category'],
        callback_data=f'editCat_{pref}_{id_exp}'
    ), InlineKeyboardButton(
        text=LEXICON_RU['cancel'],
        callback_data=f'ordCancel_{pref}_{id_exp}'
    )
    ]
    inline_markup.row(*buttons, width=1)

    return inline_markup.as_markup()


'''Клавиатура на выбор дня заказа'''


async def kb_day_order(index_day: int, count_day_month: int, id_trans: str, cat: str, date: str):
    end_month = 7 - ((index_day + count_day_month + 1) % 7)
    # Инициализируем билдер
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    # Инициализируем список для кнопок
    buttons: list[InlineKeyboardButton] = []
    for i in range(1, index_day + count_day_month + 1 + end_month + 1):
        if i <= index_day or i > index_day + count_day_month:
            buttons.append(InlineKeyboardButton(
                text='.',
                callback_data='NoneDay'))
        else:
            buttons.append(InlineKeyboardButton(
                text=f'{i - index_day}',
                callback_data=f'chDay_{cat}_{id_trans}_{date}_{i - index_day}'))

    kb_builder.row(*buttons, width=7)

    buttons: list[InlineKeyboardButton] = [InlineKeyboardButton(
        text=LEXICON_RU['back_date_order'],
        callback_data=f'backDateOrder_{cat}_{id_trans}_{date}')
    ]
    kb_builder.row(*buttons, width=1)

    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()


'''Клавиатура для выбора месяца заказа'''


async def kb_month_order(id_trans: str, cat: str, date: str):
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    # Инициализируем список для кнопок
    buttons: list[InlineKeyboardButton] = []
    months = {
        1: 'Янв',
        2: 'Фев',
        3: 'Мар',
        4: 'Апр',
        5: 'Май',
        6: 'Июн',
        7: 'Июл',
        8: 'Авг',
        9: 'Сен',
        10: 'Окт',
        11: 'Ноя',
        12: 'Дек'
    }

    for i in range(1, len(months) + 1):
        buttons.append(InlineKeyboardButton(
            text=f'{months[i]}',
            callback_data=f'chMon_{cat}_{id_trans}_{date}_{i}'))

    kb_builder.row(*buttons, width=3)

    buttons: list[InlineKeyboardButton] = [InlineKeyboardButton(
        text=LEXICON_RU['back_date_order'],
        callback_data=f'backDateOrder_{cat}_{id_trans}_{date}')
    ]
    kb_builder.row(*buttons, width=1)

    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()


'''Клавиатура на выбор года заказа'''


async def kb_year_order(id_trans, cat: str, date: str):
    year_order = datetime.now().year
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    # Инициализируем список для кнопок
    buttons: list[InlineKeyboardButton] = []

    for i in range(year_order-2, year_order+1):
        buttons.append(InlineKeyboardButton(
            text=f'{i}',
            callback_data=f'chYear_{cat}_{id_trans}_{date}_{i}'))

    kb_builder.row(*buttons, width=3)

    buttons: list[InlineKeyboardButton] = [InlineKeyboardButton(
        text=LEXICON_RU['back_date_order'],
        callback_data=f'backDateOrder_{cat}_{id_trans}_{date}')
    ]
    kb_builder.row(*buttons, width=1)

    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()


'''Клавиатура на юзера'''


async def kb_menu_user():
    menu_user: ReplyKeyboardBuilder = ReplyKeyboardBuilder()

    btn_row_1: list[KeyboardButton] = [KeyboardButton(text=LEXICON_RU['report_month_user']),
                                       KeyboardButton(text=LEXICON_RU['personal_account_user']),
                                       KeyboardButton(text=LEXICON_RU['analysis_user']),
                                       KeyboardButton(text=LEXICON_RU['settings_user']),
                                       ]

    menu_user.row(*btn_row_1, width=2)

    return menu_user.as_markup(resize_keyboard=True)


def get_month_name(month_number):
    months = {
        1: 'Янв',
        2: 'Фев',
        3: 'Мар',
        4: 'Апр',
        5: 'Май',
        6: 'Июн',
        7: 'Июл',
        8: 'Авг',
        9: 'Сен',
        10: 'Окт',
        11: 'Ноя',
        12: 'Дек'
    }
    return months.get(month_number, 'Некорректный номер месяца')