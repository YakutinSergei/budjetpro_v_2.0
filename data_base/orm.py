import json
from datetime import datetime
from difflib import SequenceMatcher

import redis

from data_base.database import async_session, engine_asinc, Base
from sqlalchemy import select, func, update, extract, delete
from sqlalchemy.exc import IntegrityError

from data_base.models import (IncomesORM, UsersOrm, IncCategoryORM, ExpCategoryORM, ExpensesORM, PiggyBankORM,
                              ActionsPiggyBankORM)


async def create_tables():
    # Начинаем асинхронную транзакцию с базой данных
    async with engine_asinc.begin() as conn:
        existing_tables = await conn.run_sync(Base.metadata.reflect)
        print(Base.metadata)
        # Проверяем, есть ли информация о существующих таблицах
        if existing_tables is not None:
            for table_name, table in Base.metadata.tables.items():
                # Проверяем, есть ли текущая таблица в списке существующих таблиц
                if table_name not in existing_tables:
                    await conn.run_sync(table.create)
        else:
            # Если информация о существующих таблицах отсутствует,
            # создаем все таблицы из метаданных
            await conn.run_sync(Base.metadata.create_all)


async def add_users_bd(tg_id: int):
    try:
        async with async_session() as session:
            user = await session.execute(
                select(UsersOrm).filter(UsersOrm.tg_id == tg_id)
            )
            existing_user = user.scalar()

            if existing_user is None:
                # Если tg_id не найден, добавляем его в таблицу
                new_user = UsersOrm(tg_id=tg_id)
                session.add(new_user)
                await session.commit()
                return True  # Возвращаем True, если tg_id был добавлен
            else:
                return False  # Возвращаем False, если tg_id уже существует
    except IntegrityError:
        # Обработка ошибки нарушения уникальности, если она возникнет
        return None  # Возвращаем None в случае ошибки


'''Функция добавления категорий расходов'''


async def add_exp_category_bd(tg_id: int, category):
    try:
        async with async_session() as session:

            user = await session.execute(select(UsersOrm.id).where(UsersOrm.tg_id == tg_id))
            user_id = user.scalar()

            # Получаем текущее максимальное значение position для данного пользователя
            max_position = await session.scalar(
                select(func.max(ExpCategoryORM.position))
                .where(ExpCategoryORM.user_id == user_id)
            )

            # Наращиваем значение position на 1
            next_position = max_position + 1 if max_position else 1

            categories_to_add = []
            for index, item in enumerate(category):

                name = item.split('-')
                limit = 0
                if len(name) > 1:
                    try:
                        limit = int(name[-1])
                    except:
                        limit = 0

                category_obj = ExpCategoryORM(user_id=user_id,
                                              name=name[0][:17],
                                              limit_summ=limit,
                                              position=next_position + index)
                categories_to_add.append(category_obj)

            session.add_all(categories_to_add)
            await session.commit()

        get_category = await get_exp_categories(tg_id=tg_id)


    except IntegrityError:
        # Обработка ошибки нарушения уникальности, если она возникнет
        print(IntegrityError)


'''Функция добавления категорий доходов'''


async def add_inc_category_bd(tg_id: int, category: list):
    try:
        async with async_session() as session:
            user = await session.execute(select(UsersOrm.id).where(UsersOrm.tg_id == tg_id))
            user_id = user.scalar()

            # Получаем текущее максимальное значение position для данного пользователя
            max_position = await session.scalar(
                select(func.max(IncCategoryORM.position))
                .where(IncCategoryORM.user_id == user_id)
            )

            # Наращиваем значение position на 1
            next_position = max_position + 1 if max_position else 1

            # Создаем список объектов категорий доходов
            categories_to_add = []
            for index, item in enumerate(category):
                name = item.split('-')
                limit = 0
                if len(name) > 1:
                    try:
                        limit = int(name[-1])
                    except:
                        limit = 0
                category_obj = IncCategoryORM(user_id=user_id,
                                              name=name[0][:17],
                                              limit_summ=limit,
                                              position=next_position + index)
                categories_to_add.append(category_obj)

            session.add_all(categories_to_add)
            await session.commit()

        get_category = await get_inc_categories(tg_id=tg_id)

    except IntegrityError:
        # Обработка ошибки нарушения уникальности, если она возникнет
        print(IntegrityError)


'''Функция проверки, есть ли такой пользователь в БД'''


async def check_user_exists(tg_id: int) -> bool:
    async with async_session() as session:
        # Выполняем запрос на проверку существования пользователя с заданным tg_id
        user = await session.execute(select(UsersOrm.id).where(UsersOrm.tg_id == tg_id))
        # Проверяем, был ли найден пользователь
        return bool(user.scalar())


'''Функция вывода всех категорий расходов'''


async def get_exp_categories(tg_id: int) -> list:
    try:
        async with (async_session() as session):

            # Получаем список объектов категорий расходов
            categories = await session.execute(
                select(ExpCategoryORM.id, ExpCategoryORM.name, ExpCategoryORM.position)
                .join(UsersOrm, UsersOrm.id == ExpCategoryORM.user_id)
                .where(UsersOrm.tg_id == tg_id)
                .order_by(ExpCategoryORM.position)
            )

            # Преобразуем объекты категорий в словари
            categories_data = [(categorys.id, categorys.name, categorys.position) for categorys in categories.all()]
            categories_data_name = [category[1] for category in categories_data]

            # Сериализуем список кортежей в JSON строку
            category_json = json.dumps(categories_data)

            # Сохраняем значения в Redis
            key = f'categories_exp:{tg_id}'
            r = redis.Redis(host='localhost', port=6379, db=0)
            r.set(key, category_json)
            # r = redis.Redis(host='localhost', port=6379, db=0)
            # r.set('categories_exp', category_json)
            # for category_data in categories_data:
            #     # Каждую категорию сохраняем под своим уникальным ключом
            #     r.set(f'exp_category', json.dumps(category_data))

            return categories_data_name

    except IntegrityError:
        # Обработка ошибки нарушения уникальности, если она возникнет
        print(IntegrityError)


'''Функция вывода всех категорий доходов'''


async def get_inc_categories(tg_id: int) -> list:
    try:
        async with (async_session() as session):

            # Получаем список объектов категорий расходов
            categories = await session.execute(
                select(IncCategoryORM.id, IncCategoryORM.name, IncCategoryORM.position)
                .join(UsersOrm, UsersOrm.id == IncCategoryORM.user_id)
                .where(UsersOrm.tg_id == tg_id)
                .order_by(IncCategoryORM.position)
            )

            # Преобразуем объекты категорий в словари
            categories_data = [(categorys.id, categorys.name, categorys.position) for categorys in categories.all()]
            categories_data_name = [category[1] for category in categories_data]

            # Сериализуем список кортежей в JSON строку
            category_json = json.dumps(categories_data)

            # Сохраняем значения в Redis
            key = f'categories_inc:{tg_id}'
            r = redis.Redis(host='localhost', port=6379, db=0)
            r.set(key, category_json)
            # for category_data in categories_data:
            #     # Каждую категорию сохраняем под своим уникальным ключом
            #     r.set(f'exp_category', json.dumps(category_data))

            return categories_data_name

    except IntegrityError:
        # Обработка ошибки нарушения уникальности, если она возникнет
        print(IntegrityError)


'''Проверка есть ли такая категория расходов и если есть то добавляем'''


async def check_and_add_user_category_exp(tg_id: int,
                                          amount: float,
                                          category: str,
                                          comment: str):
    try:
        async with async_session() as session:
            # Получаем список объектов категорий расходов
            categories = await session.execute(
                select(ExpCategoryORM.name)
                .join(UsersOrm, UsersOrm.id == ExpCategoryORM.user_id)
                .where(UsersOrm.tg_id == tg_id)
            )
            categorys = [category.name for category in categories.all()]

            if category:
                for item in categorys:
                    if (SequenceMatcher(None, category.lower(), item.lower()).ratio() * 100) > 80:
                        categories_id = await session.execute(
                            select(ExpCategoryORM.id)
                            .join(UsersOrm, UsersOrm.id == ExpCategoryORM.user_id)
                            .where(UsersOrm.tg_id == tg_id,
                                   ExpCategoryORM.name == item)
                        )
                        categories_id = int(categories_id.scalar())
                        category_obj = ExpensesORM(expense_id=categories_id,
                                                   summ=amount,
                                                   comment=comment)

                        session.add(category_obj)
                        await session.flush()
                        new_income_id = category_obj.id
                        await session.commit()

                        return f'{item}`{new_income_id}'
            else:
                return categorys

            return categorys

    except IntegrityError:
        # Обработка ошибки нарушения уникальности, если она возникнет
        print(IntegrityError)


'''Проверка есть ли такая статья доходов и если есть то добавляем'''


async def check_and_add_user_category_inc(tg_id: int,
                                          amount: float,
                                          category: str,
                                          comment: str):
    try:
        async with (async_session() as session):
            # Получаем список объектов категорий расходов
            categories = await session.execute(
                select(IncCategoryORM.name)
                .join(UsersOrm, UsersOrm.id == IncCategoryORM.user_id)
                .where(UsersOrm.tg_id == tg_id)
            )
            categorys = [category.name for category in categories.all()]

            if category:
                for item in categorys:
                    if (SequenceMatcher(None, category.lower(), item.lower()).ratio() * 100) > 80:
                        categories_id = await session.execute(
                            select(IncCategoryORM.id)
                            .join(UsersOrm, UsersOrm.id == IncCategoryORM.user_id)
                            .where(UsersOrm.tg_id == tg_id,
                                   IncCategoryORM.name == item)
                        )
                        categories_id = int(categories_id.scalar())
                        category_obj = IncomesORM(income_id=categories_id,
                                                  summ=amount,
                                                  comment=comment)

                        session.add(category_obj)
                        await session.flush()
                        new_income_id = category_obj.id
                        await session.commit()
                        return f'{item}`{new_income_id}'
            else:
                return categorys

            return categorys

    except IntegrityError:
        # Обработка ошибки нарушения уникальности, если она возникнет
        print(IntegrityError)


'''Функция добавления категории доходов, если указали сами'''


async def add_cetegory_inc(tg_id: int,
                           amount: float,
                           category: str):
    try:
        async with (async_session() as session):
            categories_id = await session.execute(
                select(IncCategoryORM.id)
                .join(UsersOrm, UsersOrm.id == IncCategoryORM.user_id)
                .where(UsersOrm.tg_id == tg_id,
                       IncCategoryORM.name == category)
            )
            categories_id = int(categories_id.scalar())
            category_obj = IncomesORM(income_id=categories_id,
                                      summ=amount,
                                      comment='')

            session.add(category_obj)
            await session.flush()
            new_income_id = category_obj.id
            await session.commit()
            return f'{category}`{new_income_id}'

    except IntegrityError:
        # Обработка ошибки нарушения уникальности, если она возникнет
        print(IntegrityError)


'''Функция добавления категории расходов, если указали сами'''


async def add_cetegory_exp(tg_id: int,
                           amount: float,
                           category: str):
    try:
        async with async_session() as session:
            categories_id = await session.execute(
                select(ExpCategoryORM.id)
                .join(UsersOrm, UsersOrm.id == ExpCategoryORM.user_id)
                .where(UsersOrm.tg_id == tg_id,
                       ExpCategoryORM.name == category)
            )
            categories_id = int(categories_id.scalar())
            category_obj = ExpensesORM(expense_id=categories_id,
                                       summ=amount,
                                       comment='')

            session.add(category_obj)
            await session.flush()
            new_expense_id = category_obj.id
            await session.commit()

            return f'{category}`{new_expense_id}'

    except IntegrityError:
        print(IntegrityError)


'''Функция удаления расхода'''


async def delete_exp(tg_trans: int):
    try:
        async with (async_session() as session):
            # Находим запись расхода по ключу id
            expense = await session.get(ExpensesORM, tg_trans)

            if expense:
                # Если запись найдена, удаляем её
                await session.delete(expense)
                await session.commit()
                return True
            else:
                return False

    except IntegrityError:
        # Обработка ошибки нарушения уникальности, если она возникнет
        print(IntegrityError)


'''Функция удаления доходов'''


async def delete_inc(tg_trans: int):
    try:
        async with (async_session() as session):
            # Находим запись расхода по ключу id
            expense = await session.get(IncomesORM, tg_trans)

            if expense:
                # Если запись найдена, удаляем её
                await session.delete(expense)
                await session.commit()
                return True
            else:
                return False

    except IntegrityError:
        # Обработка ошибки нарушения уникальности, если она возникнет
        print(IntegrityError)


'''Обновление записи'''


async def update_dates_trans(date: str,
                             id_trans: str,
                             category: str):
    try:
        async with async_session() as session:
            # Преобразуем строку в объект datetime
            input_date = datetime.strptime(date, '%d/%m/%Y')

            if category == 'e':
                expense = await session.execute(
                    update(ExpensesORM)
                    .where(ExpensesORM.id == int(id_trans))
                    .values(date=input_date)
                )
            elif category == 'i':
                income = await session.execute(
                    update(IncomesORM)
                    .where(IncomesORM.id == int(id_trans))
                    .values(date=input_date)
                )

            await session.commit()
            return True

    except IntegrityError as e:
        print(f"IntegrityError occurred: {e}")
        return False


'''Добавление комментария'''


async def edit_comment(id_record: int, comment: str, operation=str):
    try:
        async with async_session() as session:
            if operation == 'e':
                expense = await session.execute(
                    update(ExpensesORM)
                    .where(ExpensesORM.id == id_record)
                    .values(comment=comment)
                )
            elif operation == 'i':
                income = await session.execute(
                    update(IncomesORM)
                    .where(IncomesORM.id == id_record)
                    .values(comment=comment)
                )

            await session.commit()
            return True

    except IntegrityError as e:
        print(f"IntegrityError occurred: {e}")
        return False


'''Обновление категории'''


async def update_category_trans(operation: str,
                                id_trans: int,
                                new_category: str,
                                tg_id: int):
    try:
        async with async_session() as session:
            if operation == 'e':
                categories_id = await session.execute(
                    select(ExpCategoryORM.id)
                    .join(UsersOrm, UsersOrm.id == ExpCategoryORM.user_id)
                    .where(UsersOrm.tg_id == tg_id,
                           ExpCategoryORM.name == new_category)
                )
                categories_id = int(categories_id.scalar())
                expense = await session.execute(
                    update(ExpensesORM)
                    .where(ExpensesORM.id == id_trans)
                    .values(expense_id=categories_id)
                )
            elif operation == 'i':
                categories_id = await session.execute(
                    select(IncCategoryORM.id)
                    .join(UsersOrm, UsersOrm.id == IncCategoryORM.user_id)
                    .where(UsersOrm.tg_id == tg_id,
                           IncCategoryORM.name == new_category)
                )
                categories_id = int(categories_id.scalar())
                income = await session.execute(
                    update(IncomesORM)
                    .where(IncomesORM.id == id_trans)
                    .values(income_id=categories_id)
                )

            await session.commit()
            return True

    except IntegrityError as e:
        print(f"IntegrityError occurred: {e}")
        return False


'''Функция вывода отчета за месяц'''


async def get_finances_by_month(tg_id: int,
                                month: int,
                                year: int):
    try:
        async with async_session() as session:
            # Найти пользователя по tg_id
            user = await session.execute(
                select(UsersOrm.id).where(UsersOrm.tg_id == tg_id)
            )

            user_id = user.scalar()
            if not user_id:
                return "Пользователь не найден"

            # Получить все категории расходов и доходов пользователя
            expense_categories = await session.execute(
                select(ExpCategoryORM.id, ExpCategoryORM.name, ExpCategoryORM.limit_summ)
                .join(UsersOrm, UsersOrm.id == ExpCategoryORM.user_id)
                .where(UsersOrm.tg_id == tg_id)
            )
            expense_categories = [category for category in expense_categories.all()]

            income_categories = await session.execute(
                select(IncCategoryORM.id, IncCategoryORM.name, IncCategoryORM.limit_summ)
                .join(UsersOrm, UsersOrm.id == IncCategoryORM.user_id)
                .where(UsersOrm.tg_id == tg_id)
            )

            income_categories = [category for category in income_categories.all()]

            # Собрать результат для категорий расходов
            expense_result = {}

            for category in expense_categories:
                transactions = await session.execute(
                    select(func.sum(ExpensesORM.summ), func.sum(ExpCategoryORM.limit_summ))
                    .join(ExpCategoryORM)
                    .filter(
                        ExpensesORM.expense_id == category[0],
                        func.extract('month', ExpensesORM.date) == month,
                        func.extract('year', ExpensesORM.date) == year
                    )
                )
                transactions = transactions.first()
                expense_result[category[1]] = (transactions[0] or 0, category[2])
            # Собрать результат для категорий доходов
            income_result = {}
            for category in income_categories:
                transactions = await session.execute(
                    select(func.sum(IncomesORM.summ), func.sum(IncCategoryORM.limit_summ))
                    .join(IncCategoryORM)
                    .filter(
                        IncomesORM.income_id == category[0],
                        func.extract('month', IncomesORM.date) == month,
                        func.extract('year', IncomesORM.date) == year
                    )
                )
                transactions = transactions.first()
                income_result[category[1]] = (transactions[0] or 0, category[2])

            return income_result, expense_result

    except IntegrityError as e:
        print(f"IntegrityError occurred: {e}")
        return False


'''Получение информации для личного кабинета'''


async def get_data_personal_bd(tg_id: int):
    try:
        async with async_session() as session:
            user_summary = {}

            # Получаем пользователя по tg_id
            user = await session.execute(select(UsersOrm).filter(UsersOrm.tg_id == tg_id))
            user = user.scalar_one_or_none()

            if not user:
                return "Пользователь не найден"

            # .join(UsersOrm, UsersOrm.id == ExpCategoryORM.user_id)
            # .where(UsersOrm.tg_id == tg_id)

            # Вычисляем баланс пользователя
            total_incomes = await session.execute(
                select(func.sum(IncomesORM.summ))
                .join(IncCategoryORM, IncomesORM.income_id == IncCategoryORM.id)
                .join(UsersOrm, UsersOrm.id == IncCategoryORM.user_id)
                .filter(UsersOrm.tg_id == tg_id)
            )
            total_incomes = total_incomes.scalar() or 0

            total_expenses = await session.execute(
                select(func.sum(ExpensesORM.summ))
                .join(ExpCategoryORM, ExpensesORM.expense_id == ExpCategoryORM.id)
                .join(UsersOrm, UsersOrm.id == ExpCategoryORM.user_id)
                .filter(UsersOrm.tg_id == tg_id)
            )

            total_expenses = total_expenses.scalar() or 0

            user_summary['balance'] = total_incomes - total_expenses

            # Вычисляем сумму всех доходов и расходов
            user_summary['total_incomes'] = total_incomes
            user_summary['total_expenses'] = total_expenses

            # Вычисляем суммы доходов и расходов за текущий месяц и предыдущий
            current_month = datetime.now().month
            current_year = datetime.now().year

            incomes_current_month = await session.execute(
                select(func.sum(IncomesORM.summ))
                .join(IncCategoryORM, IncomesORM.income_id == IncCategoryORM.id)
                .join(UsersOrm, UsersOrm.id == IncCategoryORM.user_id)
                .filter(extract('month', IncomesORM.date) == current_month,
                        extract('year', IncomesORM.date) == current_year,
                        UsersOrm.tg_id == tg_id)
            )

            user_summary['incomes_current_month'] = incomes_current_month.scalar() or 0

            expenses_current_month = await session.execute(
                select(func.sum(ExpensesORM.summ))
                .join(ExpCategoryORM, ExpensesORM.expense_id == ExpCategoryORM.id)
                .join(UsersOrm, UsersOrm.id == ExpCategoryORM.user_id)
                .filter(extract('month', ExpensesORM.date) == current_month,
                        extract('year', ExpensesORM.date) == current_year,
                        UsersOrm.tg_id == tg_id)
            )
            user_summary['expenses_current_month'] = expenses_current_month.scalar() or 0

            # Получаем количество категорий доходов и расходов
            income_categories_count = await session.execute(select(func.count(IncCategoryORM.id))
                                                            .join(UsersOrm,
                                                                  UsersOrm.id == IncCategoryORM.user_id)
                                                            .filter(UsersOrm.tg_id == tg_id)
                                                            )

            user_summary['income_categories_count'] = income_categories_count.scalar() or 0

            expense_categories_count = await session.execute(select(func.count(ExpCategoryORM.id))
                                                             .join(UsersOrm,
                                                                   UsersOrm.id == ExpCategoryORM.user_id)
                                                             .filter(UsersOrm.tg_id == tg_id)
                                                             )
            user_summary['expense_categories_count'] = expense_categories_count.scalar() or 0

            # Проверяем подписку пользователя
            if user.subscription >= datetime.now():
                user_summary['subscription'] = user.subscription.strftime("%d.%m.%Y %H:%M")
            else:
                user_summary['subscription'] = False

            return user_summary

    except IntegrityError as e:
        print(f"IntegrityError occurred: {e}")
        return False


'''Изменение названия категории'''


async def edit_name_category(id_cat: int,
                             tg_id: int,
                             operator: str,
                             new_name: str):
    try:
        async with async_session() as session:
            if operator == 'e':
                expense = await session.execute(
                    update(ExpCategoryORM)
                    .where(ExpCategoryORM.id == int(id_cat))
                    .values(name=new_name)
                )
                await session.commit()
                await get_exp_categories(tg_id)
            elif operator == 'i':
                income = await session.execute(
                    update(IncCategoryORM)
                    .where(IncCategoryORM.id == int(id_cat))
                    .values(name=new_name)
                )
                await session.commit()
                await get_inc_categories(tg_id)
            return True


    except IntegrityError as e:
        print(f"IntegrityError occurred: {e}")
        return False


'''Изменение позиции'''


async def update_position(id_trans: str,
                          operator: str,
                          new_position: int,
                          old_position: int,
                          tg_id: int):
    try:
        async with async_session() as session:
            if old_position == new_position:
                return True
            elif operator == 'e':
                id_user = await session.execute(select(UsersOrm.id)
                                                .where(UsersOrm.tg_id == tg_id))
                id_user = id_user.one()[0]
                if new_position > old_position:

                    expense = await session.execute(
                        update(ExpCategoryORM)
                        .where(
                            (ExpCategoryORM.user_id == id_user) &
                            (ExpCategoryORM.position.between(old_position + 1, new_position))
                        ).values(position=ExpCategoryORM.position - 1)
                    )
                else:
                    id_user = await session.execute(select(UsersOrm.id)
                                                    .where(UsersOrm.tg_id == tg_id))
                    id_user = id_user.one()[0]

                    if operator == 'e':
                        expense = await session.execute(
                            update(ExpCategoryORM)
                            .where(
                                (ExpCategoryORM.user_id == id_user) &
                                (ExpCategoryORM.position.between(new_position, old_position - 1))
                            ).values(position=ExpCategoryORM.position + 1)
                        )
                expense = await session.execute(
                    update(ExpCategoryORM)
                    .where(ExpCategoryORM.id == int(id_trans))
                    .values(position=new_position)
                )

                await session.commit()
                await get_exp_categories(tg_id)

            elif operator == 'i':
                id_user = await session.execute(select(UsersOrm.id)
                                                .where(UsersOrm.tg_id == tg_id))
                id_user = id_user.one()[0]
                if new_position > old_position:
                    income = await session.execute(
                        update(IncCategoryORM)
                        .where(
                            (IncCategoryORM.user_id == id_user) &
                            (IncCategoryORM.position.between(old_position + 1, new_position))
                        ).values(position=IncCategoryORM.position - 1)
                    )

                else:
                    income = await session.execute(
                        update(IncCategoryORM)
                        .where(
                            (IncCategoryORM.user_id == id_user) &
                            (IncCategoryORM.position.between(new_position, old_position - 1))
                        ).values(position=IncCategoryORM.position + 1)
                    )

                income = await session.execute(
                    update(IncCategoryORM)
                    .where(IncCategoryORM.id == int(id_trans))
                    .values(position=new_position)
                )

                await session.commit()
                await get_inc_categories(tg_id)

        return True

    except IntegrityError as e:
        print(f"IntegrityError occurred: {e}")
        return False


'''Установление нового лимита'''


async def update_limit(id_cat: int,
                       tg_id: int,
                       operator: str,
                       new_limit: str):
    try:
        async with async_session() as session:
            if operator == 'e':
                expense = await session.execute(
                    update(ExpCategoryORM)
                    .where(ExpCategoryORM.id == int(id_cat))
                    .values(limit_summ=new_limit)
                )
                await session.commit()
                await get_exp_categories(tg_id)
            elif operator == 'i':
                income = await session.execute(
                    update(IncCategoryORM)
                    .where(IncCategoryORM.id == int(id_cat))
                    .values(limit_summ=new_limit)
                )
                await session.commit()
                await get_inc_categories(tg_id)
            return True


    except IntegrityError as e:
        print(f"IntegrityError occurred: {e}")
        return False


'''Удаление категории'''


async def del_category_bd(category_id: str,
                          operator: str,
                          tg_id):
    try:
        async with async_session() as session:
            if operator == 'e':
                id_user = await session.execute(select(UsersOrm.id)
                                                .where(UsersOrm.tg_id == tg_id))
                id_user = id_user.one()[0]

                position_category = await session.execute(select(ExpCategoryORM.position)
                                                          .where(ExpCategoryORM.id == int(category_id)))

                position_category = position_category.one()[0]

                expense_del = await session.execute(
                    delete(ExpCategoryORM)
                    .where(ExpCategoryORM.id == int(category_id))
                )

                expense = await session.execute(
                    update(ExpCategoryORM)
                    .where(
                        (ExpCategoryORM.user_id == id_user) &
                        (ExpCategoryORM.position > position_category)
                    ).values(position=ExpCategoryORM.position - 1)
                )

                await session.commit()
                await get_exp_categories(tg_id)
            elif operator == 'i':
                id_user = await session.execute(select(UsersOrm.id)
                                                .where(UsersOrm.tg_id == tg_id))
                id_user = id_user.one()[0]

                position_category = await session.execute(select(IncCategoryORM.position)
                                                          .where(IncCategoryORM.id == int(category_id)))
                position_category = position_category.one()[0]

                expense = await session.execute(
                    update(IncCategoryORM)
                    .where(
                        (IncCategoryORM.user_id == id_user) &
                        (IncCategoryORM.position > position_category)
                    ).values(position=IncCategoryORM.position - 1)
                )
                expense_del = await session.execute(
                    delete(IncCategoryORM)
                    .where(IncCategoryORM.id == int(category_id))
                )
                await session.commit()
                await get_inc_categories(tg_id)
            return True


    except IntegrityError as e:
        print(f"IntegrityError occurred: {e}")
        return False


'''Получаем данные по копилке'''


async def get_data_bank(tg_id: int):
    try:
        async with async_session() as session:
            user_bank = await session.execute(select(PiggyBankORM.id, PiggyBankORM.auto_completion)
                                              .join(UsersOrm, UsersOrm.id == PiggyBankORM.user_id)
                                              .where(UsersOrm.tg_id == tg_id)
                                              )
            bank_id = user_bank.all()  # Получаем id банка и автопополнение

            if bank_id:  # Если есть банк
                id_bank = bank_id[0][0]
                bank_auto_renewal = bank_id[0][1]

                bank_summ = await session.execute(select(func.sum(ActionsPiggyBankORM.summ))
                                                  .where(ActionsPiggyBankORM.bank_id == id_bank)
                                                  )

                # print(bank_summ.scalar())
                balance = bank_summ.scalar()
                balance = balance if balance else 0
                return {'balance': balance,
                        'auto-renewal': bank_auto_renewal}
            else:
                user_id = await session.execute(select(UsersOrm.id)
                                                .where(UsersOrm.tg_id == tg_id)
                                                )
                user_id = user_id.one()[0]
                new_bank = PiggyBankORM(user_id=user_id)
                session.add(new_bank)
                await session.commit()
                return {'balance': 0,
                        'auto-renewal': False}


    except IntegrityError as e:
        print(f"IntegrityError occurred: {e}")
        return False


# select(func.sum(ExpensesORM.summ), func.sum(ExpCategoryORM.limit_summ))
'''Пополнение копилки'''


async def add_piggy_bank(tg_id: int,
                         amount: float):
    try:
        async with async_session() as session:
            user_bank = await session.execute(select(PiggyBankORM.id, PiggyBankORM.auto_completion)
                                              .join(UsersOrm, UsersOrm.id == PiggyBankORM.user_id)
                                              .where(UsersOrm.tg_id == tg_id)
                                              )
            bank_id = user_bank.all()  # Получаем id банка и автопополнение

            if bank_id:
                id_bank = bank_id[0][0]

                new_action_bank = ActionsPiggyBankORM(bank_id=id_bank,
                                                      summ=amount)
                session.add(new_action_bank)

                await session.commit()

            else:
                return False


    except IntegrityError as e:
        print(f"IntegrityError occurred: {e}")
        return False
