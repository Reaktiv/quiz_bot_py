from functools import wraps
from aiogram.types import Message

from keyboards.reply.button import menu
from utils.db.database import User, session


def check_register(func):
    @wraps(func)  # Handler funksiyangizning asl nomi va ma'lumotlarini saqlab qoladi
    async def wrapper(*args, **kwargs):
        # args ichidan birinchi kelgan obyekt har doim Message (yoki CallbackQuery) bo'ladi
        message: Message = args[0]
        chat_id = message.chat.id

        # Foydalanuvchi bazada bormi yoki yo'qmi tekshiramiz
        if User.check_register(session, chat_id):
            await message.answer('Siz allaqachon ro‘yxatdan o‘tgansiz! Botdan foydalanishga xush kelibsiz!', reply_markup=menu())
            return  # Handler ishga tushmasligi uchun shu yerda to'xtatamiz

        # Agar ro'yxatdan o'tmagan bo'lsa, barcha argumentlarni (message, state va h.k.)
        # asl holicha handlerga uzatamiz
        return await func(*args, **kwargs)

    return wrapper