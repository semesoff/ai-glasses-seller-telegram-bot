from aiogram.fsm.state import State, StatesGroup


class OrderStates(StatesGroup):
    product_id = State()
    phone = State()
    address = State()
    confirmation = State()

