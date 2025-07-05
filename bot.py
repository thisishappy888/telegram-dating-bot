import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import CallbackQuery

from handlers import bot_messages, user_commands, question
from callbacks import callbacks

from keyboards import inline

import sqlite3
import os

from config_reader import config

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s",
                    handlers=[
                        logging.FileHandler("bot.log", encoding='utf-8'),
                        logging.StreamHandler()
                    ])

logger = logging.getLogger(__name__)

if not os.path.exists('database.db'):
    try:
        with sqlite3.connect('database.db') as db:
            cursor = db.cursor()

            cursor.execute("""CREATE TABLE users(
                          id INTEGER PRIMARY KEY,
                          name TEXT,
                          age INTEGER,
                          gender TEXT,
                          about TEXT,
                          photo TEXT)""")
    except Exception as e:
        logger.error("Не удалось выполнить запрос к базе данных", exc_info=True)

async def main():
    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher()
    
    logging.info('Бот запущен')

    dp.include_routers(
        user_commands.router,
        bot_messages.router, 
        question.router,
        callbacks.router,
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    


if __name__ == "__main__":
    asyncio.run(main())