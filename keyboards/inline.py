from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_rating_kb(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👍", callback_data=f"like:{user_id}"),
                InlineKeyboardButton(text="📝", callback_data=f"message:{user_id}"),
                InlineKeyboardButton(text="👎", callback_data="dislike"),
            ]
        ]
    )

change_form_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="⚙️", callback_data="like"),
            InlineKeyboardButton(text="📝", callback_data="message"),
        ]
    ]
)