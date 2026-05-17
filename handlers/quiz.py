import asyncio
import random
import string
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from quiz_tests import QUESTIONS
from states.quiz import QuizState
from keyboards.inline.quiz_kb import (
    get_ranges_keyboard,
    get_time_keyboard,
    get_options_keyboard,
    get_answered_keyboard
)
from keyboards.reply.button import menu

quiz_router = Router()
user_timers = {}


def shuffle_options(q_id: int):
    """Javoblarni dinamik aralashtirish (variantlar soniga qarab)"""
    q_data = QUESTIONS.get(q_id)
    original_correct_text = q_data['variantlar'][q_data['javob']]

    options_text = list(q_data['variantlar'].values())
    random.shuffle(options_text)

    shuffled_variants = {}
    correct_letter = ""

    # Qancha variant bo'lsa shuncha harf olamiz (masalan 3 ta bo'lsa: A, B, C)
    letters = list(string.ascii_uppercase)[:len(options_text)]

    for i, letter in enumerate(letters):
        shuffled_variants[letter] = options_text[i]
        if options_text[i] == original_correct_text:
            correct_letter = letter

    return shuffled_variants, correct_letter


@quiz_router.message(F.text == "Testlar")
async def show_test_ranges(message: Message):
    total_questions = len(QUESTIONS)
    if total_questions == 0:
        await message.answer("Hozircha bazada testlar yo'q.")
        return
    kb = get_ranges_keyboard(total_questions)
    await message.answer("Qaysi oraliqdagi testlarni ishlamoqchisiz?", reply_markup=kb)


@quiz_router.callback_query(F.data.startswith("quizrange_"))
async def choose_time_limit(call: CallbackQuery, state: FSMContext):
    _, start_idx, end_idx = call.data.split("_")
    await state.update_data(start=int(start_idx), end=int(end_idx))

    await state.set_state(QuizState.choosing_time)
    await call.message.edit_text("Har bir savol uchun vaqtni tanlang:", reply_markup=get_time_keyboard())


@quiz_router.callback_query(QuizState.choosing_time, F.data.startswith("quiztime_"))
async def start_quiz_session(call: CallbackQuery, state: FSMContext, bot: Bot):
    time_limit = int(call.data.split("_")[1])
    data = await state.get_data()
    start_q = data.get("start")

    await state.update_data(current=start_q, score=0, time_limit=time_limit)
    await state.set_state(QuizState.answering)

    await call.message.delete()
    await send_next_question(call.message.chat.id, start_q, state, bot)


async def send_next_question(chat_id: int, q_id: int, state: FSMContext, bot: Bot):
    data = await state.get_data()
    time_limit = data.get("time_limit")

    q_data = QUESTIONS.get(q_id)
    shuffled_variants, correct_letter = shuffle_options(q_id)
    available_letters = list(shuffled_variants.keys())  # ['A', 'B', 'C', 'D']

    text_base = f"<b>{q_id}-savol:</b> {q_data['savol']}\n\n"
    for opt in available_letters:
        text_base += f"{opt}) {shuffled_variants[opt]}\n"

    await state.update_data(
        current_correct_ans=correct_letter,
        current_text_base=text_base,
        available_letters=available_letters
    )

    text = text_base + f"\n⏳ <b>Vaqt:</b> {time_limit} soniya"
    kb = get_options_keyboard(q_id, available_letters)

    msg = await bot.send_message(chat_id, text, reply_markup=kb, parse_mode="HTML")

    task = asyncio.create_task(question_timer(chat_id, q_id, msg.message_id, time_limit, state, bot))
    user_timers[chat_id] = task


async def question_timer(chat_id: int, q_id: int, message_id: int, time_limit: int, state: FSMContext, bot: Bot):
    try:
        for remaining in range(time_limit, 0, -1):
            await asyncio.sleep(1)
            data = await state.get_data()

            if data.get("current") != q_id:
                return

            text_base = data.get("current_text_base")
            available_letters = data.get("available_letters", ["A", "B", "C", "D"])

            text = text_base + f"\n⏳ <b>Vaqt:</b> {remaining - 1} soniya"
            kb = get_options_keyboard(q_id, available_letters)

            try:
                await bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=kb,
                                            parse_mode="HTML")
            except TelegramBadRequest:
                pass

                # Vaqt tugadi
        data = await state.get_data()
        if data.get("current") == q_id:
            correct_ans = data.get("current_correct_ans")
            text_base = data.get("current_text_base")
            available_letters = data.get("available_letters", ["A", "B", "C", "D"])

            kb = get_answered_keyboard(correct_ans, available_letters)
            text = text_base + f"\n\n⏰ <b>Vaqt tugadi! To'g'ri javob: {correct_ans}</b>"

            await bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=kb,
                                        parse_mode="HTML")
            await proceed_to_next(chat_id, q_id, state, bot)

    except asyncio.CancelledError:
        pass


@quiz_router.callback_query(QuizState.answering, F.data == "quiz_stop")
async def stop_quiz(call: CallbackQuery, state: FSMContext, bot: Bot):
    chat_id = call.message.chat.id
    if chat_id in user_timers:
        user_timers[chat_id].cancel()

    data = await state.get_data()
    score = data.get("score", 0)
    start_q = data.get("start")
    current_q = data.get("current")

    attempted = current_q - start_q

    res = (
        f"🛑 <b>Test to'xtatildi!</b>\n\n"
        f"📊 <b>Ishlangan savollar:</b> {attempted} ta\n"
        f"✅ <b>To'g'ri:</b> {score} ta\n"
        f"❌ <b>Xato/Javobsiz:</b> {attempted - score} ta\n"
    )

    try:
        await call.message.edit_reply_markup(reply_markup=None)
    except:
        pass

    await bot.send_message(chat_id, res, parse_mode="HTML", reply_markup=menu())
    await state.clear()
    await call.answer()


@quiz_router.callback_query(QuizState.answering, F.data.startswith("qans_"))
async def process_answer(call: CallbackQuery, state: FSMContext, bot: Bot):
    _, q_id_str, selected_ans = call.data.split("_")
    q_id = int(q_id_str)

    data = await state.get_data()
    current_q = data.get("current")

    if q_id != current_q:
        await call.answer("Bu savolga javob berib bo'ldingiz yoki vaqt tugagan!", show_alert=True)
        return

    chat_id = call.message.chat.id
    if chat_id in user_timers:
        user_timers[chat_id].cancel()

    correct_ans = data.get("current_correct_ans")
    available_letters = data.get("available_letters", ["A", "B", "C", "D"])
    is_correct = (selected_ans == correct_ans)

    if is_correct:
        score = data.get("score", 0) + 1
        await state.update_data(score=score)
        result_msg = "✅ <b>To'g'ri!</b>"
    else:
        result_msg = f"❌ <b>Noto'g'ri! To'g'ri javob: {correct_ans}</b>"

    kb = get_answered_keyboard(correct_ans, available_letters, selected_ans)
    text_base = data.get("current_text_base")
    text = text_base + f"\n\n{result_msg}"

    await call.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await proceed_to_next(chat_id, q_id, state, bot)


@quiz_router.callback_query(F.data == "ignore")
async def ignore_old_clicks(call: CallbackQuery):
    await call.answer("Bu tugma endi faol emas!", show_alert=False)


async def proceed_to_next(chat_id: int, current_q: int, state: FSMContext, bot: Bot):
    data = await state.get_data()
    next_q = current_q + 1
    end_q = data.get("end")

    if next_q > end_q or next_q > len(QUESTIONS):
        score = data.get("score", 0)
        start_q = data.get("start")
        total = end_q - start_q + 1

        res = (
            f"🎯 <b>Test yakunlandi!</b>\n\n"
            f"📊 <b>Umumiy savollar:</b> {total} ta\n"
            f"✅ <b>To'g'ri:</b> {score} ta\n"
            f"❌ <b>Xato/Javobsiz:</b> {total - score} ta\n"
        )
        await bot.send_message(chat_id, res, parse_mode="HTML", reply_markup=menu())
        await state.clear()
    else:
        await state.update_data(current=next_q)
        await send_next_question(chat_id, next_q, state, bot)