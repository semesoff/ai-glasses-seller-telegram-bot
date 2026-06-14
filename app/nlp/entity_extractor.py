import re
from typing import Any

try:
    import spacy
except ImportError:  # pragma: no cover
    spacy = None

PATTERNS = {
    "gender": {
        "male": ("муж", "men", "mens"),
        "female": ("жен", "women", "womens"),
        "unisex": ("унисекс", "unisex"),
    },
    "shape": {
        "aviator": ("авиатор", "aviator"),
        "round": ("кругл", "round"),
        "square": ("квадрат", "square"),
        "rectangular": ("прямоуголь", "rectangular"),
        "cat-eye": ("кошач", "cat eye", "cat-eye"),
        "wayfarer": ("wayfarer", "вайфарер"),
    },
    "color": {
        "black": ("черн", "чёрн", "black"),
        "brown": ("корич", "brown"),
        "gold": ("золот", "gold"),
        "silver": ("сереб", "silver"),
        "blue": ("син", "blue"),
        "pink": ("роз", "pink"),
        "green": ("зелен", "зелён", "green"),
    },
    "frame_material": {
        "metal": ("металл", "metal"),
        "plastic": ("пласт", "plastic"),
        "acetate": ("ацетат", "acetate"),
        "tr90": ("tr90",),
    },
}
BRANDS = ("Ray-Ban", "Oakley", "Polaroid", "SOJOS", "Vogue", "Carrera", "Guess", "Prada", "WearMe Pro")


_SPACY_NLP = None


def _nlp():
    global _SPACY_NLP
    if spacy is None:
        return None
    if _SPACY_NLP is None:
        _SPACY_NLP = spacy.blank("ru")
    return _SPACY_NLP


def _extract_price(text: str) -> int | None:
    match = re.search(r"(?:до|меньше|дешевле|не дороже)\s*(\d{3,6})", text.lower())
    return int(match.group(1)) if match else None


def extract_entities(text: str) -> dict[str, Any]:
    nlp = _nlp()
    doc = nlp(text) if nlp else None
    normalized = " ".join(token.text.lower() for token in doc) if doc else text.lower()
    entities: dict[str, Any] = {"type": "sunglasses"}
    for field, values in PATTERNS.items():
        for value, needles in values.items():
            if any(needle in normalized for needle in needles):
                entities[field] = value
                break
    for brand in BRANDS:
        if brand.lower() in normalized:
            entities["brand"] = brand
            break
    if price := _extract_price(normalized):
        entities["max_price"] = price
    return entities
