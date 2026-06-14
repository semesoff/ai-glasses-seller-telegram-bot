from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Подобрать очки")],
            [KeyboardButton(text="Каталог"), KeyboardButton(text="Поиск")],
            [KeyboardButton(text="Оформить заказ"), KeyboardButton(text="Мои заказы")],
            [KeyboardButton(text="Помощь")],
        ],
        resize_keyboard=True,
    )
