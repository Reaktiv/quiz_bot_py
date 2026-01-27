from aiogram import Router, html
from aiogram.filters import CommandStart
from aiogram.types import Message

from utils.helper.decorator import check_register

start_router = Router()


@start_router.message(CommandStart())
@check_register
async def command_start_handler(message: Message):
    full_name = html.bold(message.from_user.full_name)

    text = "Salom, {name}!\n\nRo'yxatdan o'tish uchun 👉 /register kamandasini bosing".format(name=full_name)
    await message.answer(text)
