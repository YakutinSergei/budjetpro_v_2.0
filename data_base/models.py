import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import BigInteger
from sqlalchemy import text, ForeignKey
from data_base.database import Base

# Объявляем классы таблиц
class UsersOrm(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int]
    subscription: Mapped[datetime.datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))

'''Таблица категории расходов'''
class ExpCategoryORM(Base):
    __tablename__ = 'exp_category'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str]
    position: Mapped[int] = mapped_column(default=1)
    limit_summ: Mapped[int | None]


'''Таблица категории доходов'''
class IncCategoryORM(Base):
    __tablename__ = 'inc_category'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str]
    position: Mapped[int] = mapped_column(default=1)
    limit_summ: Mapped[int | None]

'''Таблица доходов'''
class IncomesORM(Base):
    __tablename__ = 'incomes'
    id: Mapped[int] = mapped_column(primary_key=True)
    income_id: Mapped[int] = mapped_column(ForeignKey("inc_category.id", ondelete="CASCADE"))
    summ: Mapped[float] = mapped_column()
    date: Mapped[datetime.datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    comment: Mapped[str]

'''Таблица доходов'''
class ExpensesORM(Base):
    __tablename__ = 'expenses'
    id: Mapped[int] = mapped_column(primary_key=True)
    expense_id: Mapped[int] = mapped_column(ForeignKey("exp_category.id", ondelete="CASCADE"))
    summ: Mapped[float] = mapped_column()
    date: Mapped[datetime.datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    comment: Mapped[str]