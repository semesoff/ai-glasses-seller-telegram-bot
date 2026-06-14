from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

from app.bot.formatting import format_products
from app.bot.keyboards import recommendation_keyboard
from app.services import ProductService

router = Router()


@router.message(Command("catalog"))
async def catalog(message: Message, product_service: ProductService) -> None:
    products = await product_service.get_catalog()
    await message.answer(
        format_products(products) + "\n\nЧтобы оформить заказ, нажмите кнопку с названием модели ниже.",
        parse_mode=ParseMode.HTML,
        reply_markup=recommendation_keyboard(products) if products else None,
    )


@router.message(lambda message: message.text and message.text.lower() == "каталог")
async def catalog_button(message: Message, product_service: ProductService) -> None:
    await catalog(message, product_service)
