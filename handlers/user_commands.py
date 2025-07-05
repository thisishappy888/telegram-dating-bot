import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from utils.states import Form

from keyboards import inline

import sqlite3

router = Router()

@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    logging.info(f"Пользователь ID({message.from_user.id}) использует команду /start")
    try:
        with sqlite3.connect("database.db") as db:
            cursor = db.cursor()

            cursor.execute('SELECT * FROM users WHERE id=(?)', (message.from_user.id,))

            result = cursor.fetchone()
    except Exception as e:
        logging.error("Не удалось выполнить запрос к базе данных", exc_info=True)

    if result:
        try:
            with sqlite3.connect("database.db") as db:
                cursor = db.cursor()

                cursor.execute('SELECT * FROM users WHERE id=(?)', (message.from_user.id,))

        except Exception as e:
            logging.error("Не удалось выполнить запрос к базе данных", exc_info=True)

        question = cursor.fetchone()
        await message.answer_photo(photo=question[5], caption=f"{question[1]}, {question[2]} - {question[4]}", reply_markup=inline.change_form_kb)
    else:
        await state.set_state(Form.name)
        await message.answer('Введи свое имя')