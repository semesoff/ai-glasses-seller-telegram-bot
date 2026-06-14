from app.nlp import Intent, classify_intent, extract_entities
from app.nlp.ml_intent_classifier import MLIntentClassifier
from app.services import NLPService


def test_classify_core_intents() -> None:
    assert classify_intent("Привет") == Intent.GREETING
    assert classify_intent("Покажи каталог") == Intent.SHOW_CATALOG
    assert classify_intent("Есть доставка?") == Intent.ASK_DELIVERY
    assert classify_intent("Как оплатить?") == Intent.ASK_PAYMENT
    assert classify_intent("Можно вернуть товар?") == Intent.ASK_RETURN
    assert classify_intent("Хочу оформить заказ") == Intent.CREATE_ORDER
    assert classify_intent("Хочу купить") == Intent.CREATE_ORDER
    assert classify_intent("Хочу мужские авиаторы") == Intent.SEARCH_PRODUCT
    assert classify_intent("случайный текст") == Intent.UNKNOWN


def test_view_orders_is_not_create_order() -> None:
    assert classify_intent("Мои заказы") == Intent.VIEW_ORDERS
    assert classify_intent("Покажи мои заказы") == Intent.VIEW_ORDERS
    assert classify_intent("Какой статус заказа?") == Intent.VIEW_ORDERS


def test_non_glasses_wishes_are_not_product_search() -> None:
    assert classify_intent("Хочу хлеб") == Intent.UNKNOWN
    assert classify_intent("Хочу картошку") == Intent.UNKNOWN
    assert classify_intent("Хочу презервативы") == Intent.UNKNOWN


def test_extract_entities_from_russian_search_query() -> None:
    entities = extract_entities("Хочу мужские черные авиаторы Ray-Ban до 5000 рублей")

    assert entities["type"] == "sunglasses"
    assert entities["gender"] == "male"
    assert entities["shape"] == "aviator"
    assert entities["color"] == "black"
    assert entities["brand"] == "Ray-Ban"
    assert entities["max_price"] == 5000


def test_extract_material_and_shape() -> None:
    entities = extract_entities("Найди круглые очки с металлической оправой дешевле 7000")

    assert entities["shape"] == "round"
    assert entities["frame_material"] == "metal"
    assert entities["max_price"] == 7000


def test_ml_classifier_predicts_known_intents() -> None:
    classifier = MLIntentClassifier(dataset_path=NLPService().ml_classifier.dataset_path)

    assert classifier.predict("откройте пожалуйста каталог") == Intent.SHOW_CATALOG
    assert classifier.predict("расскажите про доставку") == Intent.ASK_DELIVERY
    assert classifier.predict("как можно оплатить покупку") == Intent.ASK_PAYMENT


def test_nlp_service_keeps_rule_priority_for_unknown_wishes() -> None:
    service = NLPService()

    assert service.analyze("Хочу хлеб").intent == Intent.UNKNOWN
