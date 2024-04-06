from data_base.database import async_session, engine_asinc, Base
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError

from data_base.models import UsersOrm, IncCategoryORM, ExpCategoryORM


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

            # Создаем список объектов категорий доходов
            categories_to_add = [
                ExpCategoryORM(user_id=user_id, name=name, position=next_position + index)
                for index, name in enumerate(category)
            ]

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
            categories_to_add = [
                IncCategoryORM(user_id=user_id, name=name, position=next_position + index)
                for index, name in enumerate(category)
            ]

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
        print(user)
        # Проверяем, был ли найден пользователь
        return bool(user.scalar())