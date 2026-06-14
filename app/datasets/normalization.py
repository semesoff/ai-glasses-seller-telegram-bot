import csv
import hashlib
from decimal import Decimal
from pathlib import Path
from typing import Any

SHAPES = {
    "aviator": ("aviator", "авиатор"),
    "round": ("round", "круг"),
    "square": ("square", "квадрат"),
    "rectangular": ("rectangular", "прямоуголь"),
    "cat-eye": ("cat eye", "cat-eye", "кошач"),
    "wayfarer": ("wayfarer",),
}
COLORS = {
    "black": ("black", "черн"),
    "brown": ("brown", "корич"),
    "gold": ("gold", "золот"),
    "silver": ("silver", "сереб"),
    "blue": ("blue", "син"),
    "pink": ("pink", "роз"),
    "green": ("green", "зелен"),
}
MATERIALS = {
    "metal": ("metal", "металл"),
    "plastic": ("plastic", "пласт"),
    "acetate": ("acetate", "ацетат"),
    "tr90": ("tr90",),
}


def _stable_number(text: str, min_value: int, max_value: int) -> int:
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return min_value + int(digest[:8], 16) % (max_value - min_value + 1)


def _match(text: str, mapping: dict[str, tuple[str, ...]], default: str) -> str:
    lowered = text.lower()
    for value, needles in mapping.items():
        if any(needle in lowered for needle in needles):
            return value
    return default


def derive_gender(text: str) -> str:
    lowered = text.lower()
    has_men = any(word in lowered for word in (" men", " men's", "mens", "муж"))
    has_women = any(word in lowered for word in ("women", "women's", "womens", "жен"))
    if has_men and not has_women:
        return "male"
    if has_women and not has_men:
        return "female"
    return "unisex"


def normalize_product_row(row: dict[str, str], index: int) -> dict[str, Any]:
    name = (row.get("title") or f"Sunglasses {index}").strip()
    brand = (row.get("brand") or "Generic").strip()[:120]
    raw_description = (row.get("description") or "").strip()
    text = f"{name} {raw_description}"
    price_raw = (row.get("price/value") or "").strip()
    price = Decimal(price_raw) if price_raw else Decimal(_stable_number(name, 1500, 12000))
    rating_raw = (row.get("stars") or "").strip()
    reviews_raw = (row.get("reviewsCount") or "0").strip()
    description = raw_description or f"{brand} sunglasses with UV protection, suitable for everyday wear."
    return {
        "name": name[:500],
        "brand": brand or "Generic",
        "type": "sunglasses",
        "gender": derive_gender(text),
        "shape": _match(text, SHAPES, "classic"),
        "frame_material": _match(text, MATERIALS, "plastic"),
        "color": _match(text, COLORS, "black"),
        "price": price.quantize(Decimal("0.01")),
        "description": description,
        "rating": Decimal(rating_raw).quantize(Decimal("0.01")) if rating_raw else None,
        "reviews_count": int(float(reviews_raw)) if reviews_raw else 0,
    }


def read_amazon_products(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return [normalize_product_row(row, idx) for idx, row in enumerate(csv.DictReader(file), start=1)]


def read_normalized_products(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        rows = []
        for row in csv.DictReader(file):
            rows.append({
                "name": row["name"],
                "brand": row["brand"],
                "type": row["type"],
                "gender": row["gender"],
                "shape": row["shape"],
                "frame_material": row["frame_material"],
                "color": row["color"],
                "price": Decimal(str(row["price"])).quantize(Decimal("0.01")),
                "description": row["description"],
                "rating": Decimal(str(row["rating"])).quantize(Decimal("0.01")) if row.get("rating") else None,
                "reviews_count": int(float(row["reviews_count"])) if row.get("reviews_count") else 0,
            })
        return rows


def read_products(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        fields = set(reader.fieldnames or [])
    if "title" in fields:
        return read_amazon_products(path)
    return read_normalized_products(path)


def write_products_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["name", "brand", "type", "gender", "shape", "frame_material", "color", "price", "description", "rating", "reviews_count"]
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
