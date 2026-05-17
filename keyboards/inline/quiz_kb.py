from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_ranges_keyboard(total_questions: int, step: int = 30) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for i in range(1, total_questions + 1, step):
        end = min(i + step - 1, total_questions)
        builder.button(text=f"{i} - {end}", callback_data=f"quizrange_{i}_{end}")
    builder.adjust(2)
    return builder.as_markup()


def get_time_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for t in [5, 10, 15, 20]:
        builder.button(text=f"⏱ {t} soniya", callback_data=f"quiztime_{t}")
    builder.adjust(2)
    return builder.as_markup()


def get_options_keyboard(q_id: int, available_letters: list) -> InlineKeyboardMarkup:
    """Endi faqat bor variantlar (masalan: A, B, C) uchun tugma yasaydi"""
    builder = InlineKeyboardBuilder()
    for opt in available_letters:
        builder.button(text=opt, callback_data=f"qans_{q_id}_{opt}")

    # Tugmalarni 2 tadan qatorga taxlash
    builder.adjust(2)
    # To'xtatish tugmasini alohida qatorga qo'shish
    builder.row(InlineKeyboardButton(text="🛑 Testni to'xtatish", callback_data="quiz_stop"))
    return builder.as_markup()


def get_answered_keyboard(correct_ans: str, available_letters: list, chosen_ans: str = None) -> InlineKeyboardMarkup:
    """Javob belgilangandan so'ng ✅/❌ ko'rsatish uchun"""
    builder = InlineKeyboardBuilder()
    for opt in available_letters:
        if opt == correct_ans:
            text = f"✅ {opt}"
        elif opt == chosen_ans:
            text = f"❌ {opt}"
        else:
            text = opt
        builder.button(text=text, callback_data="ignore")

    builder.adjust(2)
    return builder.as_markup()