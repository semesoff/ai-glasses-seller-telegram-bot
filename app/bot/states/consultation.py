from aiogram.fsm.state import State, StatesGroup


class ConsultationStates(StatesGroup):
    goal = State()
    gender = State()
    style = State()
    shape_preference = State()
    budget = State()
    recommendation = State()

