from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def confirm_button():
    keyboards = [
        [
            KeyboardButton(text="Ha"),
            KeyboardButton(text="Yo`q"),
        ],
    ]
    kb = ReplyKeyboardMarkup(
        keyboard=keyboards,
        resize_keyboard=True,
        input_field_placeholder="Tugmadan foydalaning!"
    )
    return kb


def share_contact():
    keyboards = [
        [
            KeyboardButton(text="Share your contact", request_contact=True)
        ]
    ]
    kb = ReplyKeyboardMarkup(
        keyboard=keyboards,
        resize_keyboard=True,
        input_field_placeholder="Tugmadan foydalaning!"
    )
    return kb

def menu():
    keyboards = [
        [
            KeyboardButton(text="Testlar"),
            KeyboardButton(text="Natijalar")
        ],
        [
            KeyboardButton(text="Tilni o'zgartirish")
        ]
    ]
    kb = ReplyKeyboardMarkup(keyboard=keyboards, resize_keyboard=True)
    return kb
