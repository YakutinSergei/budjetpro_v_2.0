from datetime import datetime
from aiogram.filters import BaseFilter

from aiogram.types import Message, CallbackQuery
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from data_base.database import async_session
from data_base.models import UsersOrm


class PaidFiltersMessage(BaseFilter):
    async def __call__(self, message: Message):
        try:
            tg_id = int(message.from_user.id) if message.chat.type == 'private' else int(message.chat.id)
            async with async_session() as session:

                # Получаем пользователя по tg_id
                user = await session.execute(select(UsersOrm).filter(UsersOrm.tg_id == tg_id))
                user = user.scalar_one_or_none()

                if not user:
                    return False

                # Проверяем подписку пользователя
                if user.subscription >= datetime.now():
                    return True
                else:
                    return False
        except IntegrityError as e:
            print(f"IntegrityError occurred: {e}")
            return False



class PaidFiltersCallback(BaseFilter):
    async def __call__(self, callback: CallbackQuery):
        try:
            tg_id = int(callback.from_user.id) if callback.message.chat.type == 'private' else int(
                callback.message.chat.id)
            async with async_session() as session:

                # Получаем пользователя по tg_id
                user = await session.execute(select(UsersOrm).filter(UsersOrm.tg_id == tg_id))
                user = user.scalar_one_or_none()
                if not user:
                    return False

                # Проверяем подписку пользователя
                if user.subscription >= datetime.now():
                    return True
                else:
                    return False
        except IntegrityError as e:
            print(f"IntegrityError occurred: {e}")

            return False