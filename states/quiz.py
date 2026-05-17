from aiogram.fsm.state import StatesGroup, State

class QuizState(StatesGroup):
    choosing_time = State()  # Vaqt tanlash holati
    answering = State()      # Test ishlash holati