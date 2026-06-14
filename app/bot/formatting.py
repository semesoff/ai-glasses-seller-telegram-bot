from collections.abc import Iterable
from decimal import Decimal
from html import escape

from app.database.models import Product

SHAPE_LABELS = {
    "aviator": "авиаторы",
    "round": "круглая форма",
    "square": "квадратная форма",
    "rectangular": "прямоугольная форма",
    "cat-eye": "кошачий глаз",
    "wayfarer": "вайфареры",
}
COLOR_LABELS = {
    "black": "чёрный",
    "brown": "коричневый",
    "gold": "золотистый",
    "silver": "серебристый",
    "blue": "синий",
    "pink": "розовый",
    "green": "зелёный",
}
MATERIAL_LABELS = {
    "metal": "металлическая оправа",
    "plastic": "пластиковая оправа",
    "acetate": "ацетатная оправа",
    "tr90": "лёгкая TR90-оправа",
}
GENDER_LABELS = {
    "male": "мужские",
    "female": "женские",
    "unisex": "унисекс",
}


def _label(mapping: dict[str, str], value: str | None) -> str | None:
    if not value:
        return None
    return mapping.get(value.lower(), value)


def _money(value: Decimal | int | None) -> str:
    if not value:
        return "цена по запросу"
    decimal_value = Decimal(str(value))
    amount = int(decimal_value) if decimal_value == decimal_value.to_integral_value() else decimal_value
    return f"{amount:,}".replace(",", " ") + " руб."


def _short_name(product: Product, limit: int = 34) -> str:
    title = f"{product.brand} {product.name}".strip()
    title = " ".join(title.split())
    if len(title) <= limit:
        return title
    return title[: limit - 1].rstrip() + "…"


def product_button_label(product: Product) -> str:
    return f"Купить {_short_name(product, 42)}"


def _details(product: Product) -> list[str]:
    details = [
        _label(SHAPE_LABELS, product.shape),
        _label(COLOR_LABELS, product.color),
        _label(MATERIAL_LABELS, product.frame_material),
        _label(GENDER_LABELS, product.gender),
    ]
    return [detail for detail in details if detail]


def format_product(product: Product) -> str:
    details = _details(product)
    details_text = ", ".join(escape(detail) for detail in details) if details else "универсальная модель"
    rating = f"{product.rating:.1f}" if product.rating else "нет оценки"

    return (
        f"<b>{escape(product.brand)} — {escape(product.name)}</b>\n"
        f"Цена: <b>{escape(_money(product.price))}</b>\n"
        f"Особенности: {details_text}\n"
        f"Рейтинг: {escape(rating)}"
    )


def format_products(products: Iterable[Product]) -> str:
    items = list(products)
    if not items:
        return "Ничего не найдено. Попробуйте изменить запрос."
    return "\n\n".join(format_product(product) for product in items)


def format_sales_offer(products: Iterable[Product]) -> str:
    items = list(products)
    if not items:
        return ""

    cards = []
    for index, product in enumerate(items, start=1):
        details = _details(product)
        details_text = ", ".join(escape(detail) for detail in details[:3]) if details else "универсальная модель"
        cards.append(
            f"{index}. <b>{escape(product.brand)} — {escape(product.name)}</b>\n"
            f"   Цена: <b>{escape(_money(product.price))}</b>\n"
            f"   Подойдёт как: {details_text}"
        )

    return (
        "Кстати, раз уж мы разговорились, могу ненавязчиво предложить пару солнцезащитных очков. "
        "Не обязательно покупать прямо сейчас, но вдруг что-то подойдёт под лето, прогулки или поездки.\n\n"
        + "\n\n".join(cards)
        + "\n\nЕсли какая-то модель понравилась, нажмите кнопку с её названием ниже."
    )
