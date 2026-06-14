from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

from app.bot.formatting import format_products
from app.bot.keyboards import recommendation_keyboard
from app.services import ProductService

router = Router()


@router.message(Command("search"))
async def search_command(message: Message) -> None:
    await message.answer("Напишите запрос, например: Хочу мужские авиаторы до 5000 рублей")


@router.message(F.text.lower() == "поиск")
async def search_button(message: Message) -> None:
    await search_command(message)


async def run_search(message: Message, product_service: ProductService, query: str) -> None:
    products = await product_service.search_products(query)
    await message.answer(
        format_products(products) + "\n\nЕсли модель понравилась, нажмите кнопку с её названием ниже.",
        parse_mode=ParseMode.HTML,
        reply_markup=recommendation_keyboard(products) if products else None,
    )
