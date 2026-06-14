from decimal import Decimal

from app.bot.formatting import format_product, format_sales_offer, product_button_label
from app.database.models import Product


def _product() -> Product:
    return Product(
        id=42,
        name="Classic Aviator Sunglasses",
        brand="Ray-Ban",
        type="sunglasses",
        gender="unisex",
        shape="aviator",
        frame_material="metal",
        color="black",
        price=Decimal("5000.00"),
        description="Test product",
        rating=Decimal("4.80"),
        reviews_count=100,
    )


def test_product_card_has_html_and_readable_labels() -> None:
    text = format_product(_product())

    assert "<b>Ray-Ban — Classic Aviator Sunglasses</b>" in text
    assert "Цена: <b>5 000 руб.</b>" in text
    assert "авиаторы" in text
    assert "чёрный" in text
    assert "металлическая оправа" in text
    assert "classic, black" not in text.lower()


def test_sales_offer_has_bridge_and_compact_cards() -> None:
    text = format_sales_offer([_product()])

    assert "Кстати" in text
    assert "солнцезащитных очков" in text
    assert "кнопку с её названием" in text
    assert "<b>Ray-Ban — Classic Aviator Sunglasses</b>" in text


def test_buy_button_uses_product_name_not_raw_id() -> None:
    assert product_button_label(_product()) == "Купить Ray-Ban Classic Aviator Sunglasses"
