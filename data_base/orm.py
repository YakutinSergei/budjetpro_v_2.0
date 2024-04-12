from difflib import SequenceMatcher

from data_base.database import async_session, engine_asinc, Base
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError

from data_base.models import IncomesORM, UsersOrm, IncCategoryORM, ExpCategoryORM, ExpensesORM


async def create_tables():
    # Начинаем асинхронную транзакцию с базой данных
    async with engine_asinc.begin() as conn:
        existing_tables = await conn.run_sync(Base.metadata.reflect)

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
async def add_exp_category_bd(tg_id:int, category):
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
                                              name=name[0],
                                              limit_summ=limit,
                                              position=next_position + index)
                categories_to_add.append(category_obj)

            session.add_all(categories_to_add)
            await session.commit()



    except IntegrityError:
        # Обработка ошибки нарушения уникальности, если она возникнет
        print(IntegrityError)

'''Функция добавления категорий доходов'''
async def add_inc_category_bd(tg_id:int, category: list):
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
                                              name=name[0],
                                              limit_summ=limit,
                                              position=next_position + index)
                categories_to_add.append(category_obj)

            session.add_all(categories_to_add)
            await session.commit()

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
                select(ExpCategoryORM.name)
                .join(UsersOrm, UsersOrm.id == ExpCategoryORM.user_id)
                .where(UsersOrm.tg_id == tg_id)
            )

            return [category.name for category in categories.all()]

    except IntegrityError:
        # Обработка ошибки нарушения уникальности, если она возникнет
        print(IntegrityError)

'''Функция вывода всех категорий доходов'''

async def get_inc_categories(tg_id: int) -> list:
    try:
        async with (async_session() as session):

            # Получаем список объектов категорий расходов
            categories = await session.execute(
                select(IncCategoryORM.name)
                .join(UsersOrm, UsersOrm.id == IncCategoryORM.user_id)
                .where(UsersOrm.tg_id == tg_id)
            )

            return [category.name for category in categories.all()]

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
                        categories_id=int(categories_id.scalar())
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
                        categories_id=int(categories_id.scalar())
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
            categories_id=int(categories_id.scalar())
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