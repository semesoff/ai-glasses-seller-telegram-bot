from decimal import Decimal

from app.datasets.normalization import normalize_product_row


def test_normalize_product_row_fills_missing_fields() -> None:
    row = {
        "title": "Ray-Ban Black Aviator Sunglasses for Men",
        "brand": "Ray-Ban",
        "description": "",
        "price/value": "",
        "stars": "4.5",
        "reviewsCount": "100.0",
    }

    product = normalize_product_row(row, 1)

    assert product["name"] == row["title"]
    assert product["brand"] == "Ray-Ban"
    assert product["type"] == "sunglasses"
    assert product["gender"] == "male"
    assert product["shape"] == "aviator"
    assert product["color"] == "black"
    assert product["price"] >= Decimal("1500.00")
    assert product["description"]
    assert product["rating"] == Decimal("4.50")
    assert product["reviews_count"] == 100


def test_normalize_product_row_uses_explicit_price() -> None:
    row = {
        "title": "Round Sunglasses",
        "brand": "SOJOS",
        "description": "Round plastic frame.",
        "price/value": "7.35",
        "stars": "",
        "reviewsCount": "",
    }

    product = normalize_product_row(row, 2)

    assert product["price"] == Decimal("7.35")
    assert product["shape"] == "round"
    assert product["frame_material"] == "plastic"
    assert product["rating"] is None
    assert product["reviews_count"] == 0

