from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

FAQ = {
    "delivery": "Доставка доступна по России. Обычно занимает 2-5 рабочих дней.",
    "payment": "Оплатить можно картой или наличными при получении, если этот способ доступен в вашем городе.",
    "return": "Возврат возможен в течение 14 дней при сохранении товарного вида.",
}


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    await message.answer(
        "Я умею подбирать очки как стилист, показывать /catalog, искать через /search, "
        "отвечать про доставку/оплату/возврат и оформлять /order."
    )


async def answer_faq(message: Message, topic: str) -> None:
    await message.answer(FAQ[topic])

