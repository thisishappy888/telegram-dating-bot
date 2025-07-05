from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from keyboards import inline

import logging

import sqlite3

router = Router()

logger = logging.getLogger(__name__)

@router.callback_query(F.data == 'dislike')
async def dislike(callback: CallbackQuery, bot: Bot):
    message_id_to_delete = callback.message.message_id
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=message_id_to_delete)
    
    try:
        with sqlite3.connect("database.db") as db:
            cursor = db.cursor()

            cursor.execute('SELECT * FROM users WHERE id != ? ORDER BY RANDOM() LIMIT 1', (callback.message.from_user.id,))
        
            question = cursor.fetchone()

            await callback.message.answer_photo(photo=question[5], caption=f"{question[1]}, {question[2]} - {question[4]}", reply_markup=inline.get_rating_kb(question[0]))

    except Exception as e:
        logger.error("Не удалось выполнить запрос к базе данных", exc_info=True)




@router.callback_query(F.data.startswith('like:'))
async def like(callback: CallbackQuery, bot: Bot):
    print("like")

    from_user_id = callback.from_user.id
    to_user_id = int(callback.data.split(":")[1])
    print(from_user_id)
    print(to_user_id)

    