
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import async_session

from keyboards.reply.button import share_contact
from states.register import RegisterState
from utils.db.database import User

register_router = Router()

@register_router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("To'liq ismingizni kiriting:")
    await state.set_state(RegisterState.full_name)

@register_router.message(RegisterState.full_name)
async def get_full_name(message: Message, state:FSMContext):
    await state.update_data(full_name = message.text)
    await message.answer("Telefon raqamingizni kiriting:", reply_markup=share_contact())
    await state.set_state(RegisterState.phone)

@register_router.message(RegisterState.phone)
async def get_phone(message: Message, state: FSMContext):
    data = await state.get_data()

    async with async_session() as session:
        user = User(
            chat_id=message.from_user.id,
            full_name=data["full_name"],
            phone = message.text
        )
        session.add(user)
        await session.commit()
    await state.clear()
    await message.answer("Siz muvaffaqiyatli ro'yxatdan o'tdingiz✅")















