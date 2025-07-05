import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from utils.states import Form

from keyboards import inline

import sqlite3


router = Router()


@router.message(Form.name)
async def form_name(message: Message, state: FSMContext):
    await state.update_data(name = message.text)
    await state.set_state(Form.age)
    await message.answer('Теперь введи свой возраст')

@router.message(Form.age)
async def form_age(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(age = message.text)
        await state.set_state(Form.gender)
        await message.answer('Теперь определимся с полом')
    else:
        await message.answer('Введи число')

@router.message(Form.gender, F.text.casefold().in_(['парень', 'девушка']))
async def form_gender(message: Message, state: FSMContext):
    await state.update_data(gender = message.text)
    await state.set_state(Form.about)
    await message.answer('расскажи о себе')

@router.message(Form.gender)
async def incorrect_form_gender(message: Message, state: FSMContext):
    await message.answer('Нажми на кнопку')

@router.message(Form.about)
async def form_about(message: Message, state: FSMContext):
    await state.update_data(about = message.text)
    await state.set_state(Form.photo)
    await message.answer('Теперь отправь свое фото')

@router.message(Form.photo)
async def form_photo(message: Message, state: FSMContext):
    photo_file_id = message.photo[-1].file_id
    data = await state.get_data()
    await state.clear()

    try:
        with sqlite3.connect("database.db") as db:
            cursor = db.cursor()

            cursor.execute('INSERT INTO users(id, name, age, gender, about, photo) VALUES(?, ?, ?, ?, ?, ?)', (message.from_user.id ,data['name'], data['age'], data['gender'], data['about'], photo_file_id))

            cursor.execute("SELECT * FROM users")

            logging.info(f"Создана анкета: ID: {message.from_user.id}, Name: {data['name']}, Age: {data['age']}, Gender: {data['gender']}, Description: {data['about']}, Photo: {photo_file_id}")
    except Exception as e:
        logging.error("Не удалось выполнить запрос к базе данных", exc_info=True)

    await message.answer_photo(photo=photo_file_id, caption=f"{data['name']}, {data['age']} - {data['about']}", reply_markup=inline.change_form_kb)
