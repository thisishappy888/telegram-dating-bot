import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards import inline

import sqlite3






from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import random

def get_best_match(current_user_id: int) -> int | None:
    with sqlite3.connect("database.db") as db:
        cursor = db.cursor()
        
        # Получаем анкету текущего пользователя
        cursor.execute("SELECT about FROM users WHERE id = ?", (current_user_id,))
        current_about = cursor.fetchone()
        if not current_about or not current_about[0].strip():
            return None

        current_about = current_about[0]

        # Получаем всех других пользователей
        cursor.execute("SELECT id, about FROM users WHERE id != ? AND about IS NOT NULL", (current_user_id,))
        users = cursor.fetchall()

    if not users:
        return None

    id_to_about = {uid: about for uid, about in users if about and about.strip()}

    if not id_to_about:
        return None

    # TF-IDF
    vectorizer = TfidfVectorizer(analyzer='word', token_pattern=r'\b\w+\b')
    all_texts = [current_about] + list(id_to_about.values())
    tfidf_matrix = vectorizer.fit_transform(all_texts)
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]

    # Сопоставим с ID
    user_ids = list(id_to_about.keys())
    scored_users = list(zip(user_ids, similarity))
    scored_users.sort(key=lambda x: x[1], reverse=True)

    best_score = scored_users[0][1] if scored_users else 0
    best_user_id = scored_users[0][0] if scored_users else None

    if best_score < 0.1:
        # Низкое сходство — лучше вернуть случайную анкету
        return None

    return best_user_id





router = Router()


@router.message(F.text == "смотреть анкеты")
async def look_question(message: Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        best_match_id = get_best_match(user_id)

        with sqlite3.connect("database.db") as db:
            cursor = db.cursor()

            cursor.execute("SELECT age FROM users WHERE id = ?", (message.from_user.id,))

            user_age = cursor.fetchone()[0]

            if best_match_id:
                cursor.execute("SELECT * FROM users WHERE id = ? AND age IN (?, ?, ?)", (best_match_id, user_age, user_age - 1, user_age + 1))
            else:
                cursor.execute('SELECT * FROM users WHERE id != ? AND age IN (?, ?, ?) ORDER BY RANDOM() LIMIT 1', (user_id, user_age, user_age - 1, user_age + 1))
           
        
            question = cursor.fetchone()

            if question:
                await message.answer_photo(photo=question[5], caption=f"{question[1]}, {question[2]} - {question[4]}", reply_markup=inline.get_rating_kb(question[0]))
            else:
                await message.answer("нету анкет")
            
    except Exception as e:
        logging.error("Не удалось выполнить запрос к базе данных", exc_info=True)
