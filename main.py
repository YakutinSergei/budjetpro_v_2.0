import asyncio
import logging

from aiogram import Bot
from aiogram.types import BotCommand

from Handlers import start_handlers, financial_transactions_handlers, monthly_report_handlers, personal_account_handlers
from create_bot import bot, dp
from environs import Env

from data_base.orm import create_tables

env = Env()
env.read_env()

# Инициализируем логгер
logger = logging.getLogger(__name__)


async def set_main_menu(bot: Bot):

    # Создаем список с командами и их описанием для кнопки menu
    main_menu_commands = [
        BotCommand(command='/start', description='Перезапустить бота')]

    await bot.set_my_commands(main_menu_commands)

async def main():

    # Конфигурируем логирование
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')

    '''Подключаем базу данных'''
    await create_tables() # Создание таблиц

    # Регистриуем роутеры в диспетчере
    dp.include_router(start_handlers.router)
    dp.include_router(personal_account_handlers.router)
    dp.include_router(monthly_report_handlers.router)
    dp.include_router(financial_transactions_handlers.router)





    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    dp.startup.register(set_main_menu)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

