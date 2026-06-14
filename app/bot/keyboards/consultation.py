from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.formatting import product_button_label
from app.database.models import Product


def _keyboard(rows: list[list[tuple[str, str]]]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=text, callback_data=data) for text, data in row]
            for row in rows
        ]
    )


def goal_keyboard() -> InlineKeyboardMarkup:
    return _keyboard([
        [("Каждый день", "consult:goal:everyday"), ("Вождение", "consult:goal:driving")],
        [("Пляж/отдых", "consult:goal:beach"), ("Подарок", "consult:goal:gift")],
        [("Стильный образ", "consult:goal:fashion")],
    ])


def gender_keyboard() -> InlineKeyboardMarkup:
    return _keyboard([
        [("Мужские", "consult:gender:male"), ("Женские", "consult:gender:female")],
        [("Унисекс", "consult:gender:unisex")],
    ])


def style_keyboard() -> InlineKeyboardMarkup:
    return _keyboard([
        [("Классика", "consult:style:classic"), ("Спорт", "consult:style:sport")],
        [("Премиум", "consult:style:premium"), ("Яркий образ", "consult:style:bright")],
        [("Минимализм", "consult:style:minimal")],
    ])


def shape_keyboard() -> InlineKeyboardMarkup:
    return _keyboard([
        [("Авиаторы", "consult:shape:aviator"), ("Круглые", "consult:shape:round")],
        [("Квадратные", "consult:shape:square"), ("Прямоугольные", "consult:shape:rectangular")],
        [("Не знаю", "consult:shape:any")],
    ])


def budget_keyboard() -> InlineKeyboardMarkup:
    return _keyboard([
        [("До 5000", "consult:budget:5000"), ("До 7000", "consult:budget:7000")],
        [("До 10000", "consult:budget:10000"), ("Без ограничения", "consult:budget:any")],
    ])


def recommendation_keyboard(products: list[Product]) -> InlineKeyboardMarkup:
    rows = [[(product_button_label(product), f"consult:buy:{product.id}")] for product in products]
    rows.append([("Показать ещё", "consult:more"), ("Изменить бюджет", "consult:change_budget")])
    rows.append([("Начать заново", "consult:restart")])
    return _keyboard(rows)
