import csv
import json
import random
from pathlib import Path

from app.config import get_settings

BRANDS = ["Ray-Ban", "Oakley", "Polaroid", "SOJOS", "Vogue", "Carrera", "Guess", "Prada"]
GENDERS = [("male", "мужские"), ("female", "женские"), ("unisex", "унисекс")]
SHAPES = [("aviator", "авиаторы"), ("round", "круглые"), ("square", "квадратные"), ("rectangular", "прямоугольные"), ("cat-eye", "кошачий глаз")]
COLORS = [("black", "черные"), ("brown", "коричневые"), ("gold", "золотые"), ("silver", "серебристые"), ("blue", "синие")]
MATERIALS = [("metal", "металлическая"), ("plastic", "пластиковая"), ("acetate", "ацетатная")]


def _write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def generate_products(count: int = 1200) -> list[dict[str, object]]:
    random.seed(42)
    rows: list[dict[str, object]] = []
    for idx in range(1, count + 1):
        brand = random.choice(BRANDS)
        gender, gender_ru = random.choice(GENDERS)
        shape, shape_ru = random.choice(SHAPES)
        color, color_ru = random.choice(COLORS)
        material, material_ru = random.choice(MATERIALS)
        price = random.randint(1500, 15000)
        rows.append({
            "name": f"{brand} {shape.title()} Sunglasses {idx}",
            "brand": brand,
            "type": "sunglasses",
            "gender": gender,
            "shape": shape,
            "frame_material": material,
            "color": color,
            "price": price,
            "description": f"{color_ru.capitalize()} {gender_ru} очки формы {shape_ru}, {material_ru} оправа, UV400.",
            "rating": round(random.uniform(3.8, 5.0), 2),
            "reviews_count": random.randint(20, 30000),
        })
    return rows


def generate_intents(count: int = 1200) -> list[dict[str, str]]:
    templates = [
        ("Покажи каталог", "SHOW_CATALOG"),
        ("Открой каталог очков", "SHOW_CATALOG"),
        ("Хочу {gender} {shape} до {price} рублей", "SEARCH_PRODUCT"),
        ("Найди {color} очки {brand}", "SEARCH_PRODUCT"),
        ("Есть доставка?", "ASK_DELIVERY"),
        ("Сколько идет доставка?", "ASK_DELIVERY"),
        ("Как оплатить заказ?", "ASK_PAYMENT"),
        ("Можно оплатить картой?", "ASK_PAYMENT"),
        ("Можно вернуть товар?", "ASK_RETURN"),
        ("Хочу оформить заказ", "CREATE_ORDER"),
        ("Привет", "GREETING"),
    ]
    rows: list[dict[str, str]] = []
    for idx in range(count):
        text, intent = templates[idx % len(templates)]
        _, gender_ru = GENDERS[idx % len(GENDERS)]
        _, shape_ru = SHAPES[idx % len(SHAPES)]
        _, color_ru = COLORS[idx % len(COLORS)]
        brand = BRANDS[idx % len(BRANDS)]
        rows.append({
            "query": text.format(gender=gender_ru, shape=shape_ru, color=color_ru, brand=brand, price=2000 + idx % 12000),
            "intent": intent,
        })
    return rows


def _entity(text: str, value: str, label: str) -> tuple[int, int, str] | None:
    start = text.lower().find(value.lower())
    return (start, start + len(value), label) if start >= 0 else None


def generate_ner(count: int = 2400) -> list[tuple[str, dict[str, list[tuple[int, int, str]]]]]:
    rows = []
    for idx in range(count):
        brand = BRANDS[idx % len(BRANDS)]
        _, gender_ru = GENDERS[idx % len(GENDERS)]
        _, shape_ru = SHAPES[idx % len(SHAPES)]
        _, color_ru = COLORS[idx % len(COLORS)]
        _, material_ru = MATERIALS[idx % len(MATERIALS)]
        price = str(3000 + idx % 10000)
        text = f"Хочу {gender_ru} {color_ru} {shape_ru} очки {brand} с {material_ru} оправой до {price} рублей"
        entities = [
            item for item in (
                _entity(text, gender_ru, "GENDER"),
                _entity(text, color_ru, "COLOR"),
                _entity(text, shape_ru, "SHAPE"),
                _entity(text, brand, "BRAND"),
                _entity(text, material_ru, "FRAME_MATERIAL"),
                _entity(text, price, "PRICE"),
            )
            if item
        ]
        rows.append((text, {"entities": entities}))
    return rows


def main() -> None:
    settings = get_settings()
    product_rows = generate_products()
    _write_csv(settings.synthetic_products_csv, list(product_rows[0]), product_rows)
    _write_csv(settings.intents_csv, ["query", "intent"], generate_intents())
    settings.ner_dataset_json.parent.mkdir(parents=True, exist_ok=True)
    settings.ner_dataset_json.write_text(json.dumps(generate_ner(), ensure_ascii=False, indent=2), encoding="utf-8")
    print("Generated synthetic products, intents, and NER dataset")


if __name__ == "__main__":
    main()

