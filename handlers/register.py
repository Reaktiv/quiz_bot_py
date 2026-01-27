
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import async_session

from keyboards.reply.button import share_contact, confirm_button, menu
from states.register import RegisterState
from utils.db.database import User, session
from utils.helper.decorator import check_register

register_router = Router()

@register_router.message(Command("register"))
@check_register
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("To'liq ismingizni kiriting:")
    await state.set_state(RegisterState.full_name)

@register_router.message(RegisterState.full_name)
async def get_full_name(message: Message, state:FSMContext):
    full_name = message.text
    await state.update_data(full_name=full_name)
    await message.answer("Telefon raqamingizni kiriting:", reply_markup=share_contact())
    await state.set_state(RegisterState.phone)

@register_router.message(RegisterState.phone)
async def get_phone(message: Message, state: FSMContext):
    phone_number = message.text
    if message.contact:
        phone_number = message.contact.phone_number

    await state.update_data(phone = phone_number)
    datas = await state.get_data()
    full_name = datas.get("full_name")
    phone = phone_number
    user_chat_id = message.from_user.id
    user_data = ("Ma'lumotlaringizni tasdiqlaysizmi!\n\n"
                 f"To'liq ism: {full_name}\n"
                 f"Telefon: {phone}\n"
                 f"Chat ID: {user_chat_id}\n")

    await message.answer(user_data, reply_markup=confirm_button())
    await state.set_state(RegisterState.confirm)

@register_router.message(RegisterState.confirm)
async def confirm_handler(message:Message, state: FSMContext):
    confirm = message.text
    if confirm.casefold() == "ha":
        datas = await state.get_data()
        full_name = datas.get("full_name")
        phone = datas.get("phone")
        user_chat_id = message.from_user.id

        user = User(full_name=full_name, phone=phone, chat_id=user_chat_id)
        user.save(session)

        await message.answer("""
Siz muvaffaqiyatli ro'yxatdan o'tdingiz✅
Botdan foydalanishga xush kelibsiz!!! 
""", reply_markup=menu())
    elif confirm.casefold() == "yo`q":
        await message.answer("Qayta ro'yxatdan o'tish uchun /register tugmasini bosing", reply_markup=ReplyKeyboardRemove())
        await state.clear()
    else:
        await message.reply('Ha yoki Yo`q bilan tasdiqlang iltimos!')















