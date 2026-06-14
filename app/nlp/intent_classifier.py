from enum import StrEnum


class Intent(StrEnum):
    GREETING = "GREETING"
    SHOW_CATALOG = "SHOW_CATALOG"
    SEARCH_PRODUCT = "SEARCH_PRODUCT"
    CREATE_ORDER = "CREATE_ORDER"
    VIEW_ORDERS = "VIEW_ORDERS"
    ASK_DELIVERY = "ASK_DELIVERY"
    ASK_PAYMENT = "ASK_PAYMENT"
    ASK_RETURN = "ASK_RETURN"
    UNKNOWN = "UNKNOWN"


PRODUCT_TERMS = (
    "очки",
    "очков",
    "очками",
    "солнцезащит",
    "авиатор",
    "вайфарер",
    "wayfarer",
    "aviator",
    "ray-ban",
    "oakley",
    "polaroid",
    "sojos",
)
SEARCH_ACTIONS = ("найди", "найти", "подбери", "подобрать", "посоветуй", "покажи", "хочу")
PRODUCT_ATTRIBUTES = (
    "мужские",
    "женские",
    "унисекс",
    "круглые",
    "квадратные",
    "прямоугольные",
    "черные",
    "чёрные",
    "золотые",
    "металл",
    "пластик",
)
VIEW_ORDER_TERMS = (
    "мои заказы",
    "мой заказ",
    "мои заказ",
    "статус заказа",
    "где заказ",
    "покажи заказы",
    "посмотреть заказы",
)


def _has_any(text: str, needles: tuple[str, ...]) -> bool:
    return any(needle in text for needle in needles)


def _looks_like_product_search(text: str) -> bool:
    has_product_term = _has_any(text, PRODUCT_TERMS)
    has_search_action = _has_any(text, SEARCH_ACTIONS)
    has_product_attribute = _has_any(text, PRODUCT_ATTRIBUTES)
    return has_product_term or (has_search_action and has_product_attribute)


def classify_intent(text: str) -> Intent:
    normalized = text.lower().strip()
    if _has_any(normalized, ("привет", "здравств", "добрый день", "доброе утро", "добрый вечер")):
        return Intent.GREETING
    if _has_any(normalized, ("каталог", "ассортимент", "покажи все")):
        return Intent.SHOW_CATALOG
    if _has_any(normalized, VIEW_ORDER_TERMS):
        return Intent.VIEW_ORDERS
    if _has_any(normalized, ("доставка", "доставить", "курьер")):
        return Intent.ASK_DELIVERY
    if _has_any(normalized, ("оплат", "картой", "налич")):
        return Intent.ASK_PAYMENT
    if _has_any(normalized, ("вернуть", "возврат", "обмен")):
        return Intent.ASK_RETURN
    if _has_any(normalized, ("оформить заказ", "сделать заказ", "заказать", "хочу купить")) or (
        "купить" in normalized and _looks_like_product_search(normalized)
    ):
        return Intent.CREATE_ORDER
    if _looks_like_product_search(normalized):
        return Intent.SEARCH_PRODUCT
    return Intent.UNKNOWN
