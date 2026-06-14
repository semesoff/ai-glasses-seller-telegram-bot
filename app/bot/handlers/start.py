from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.bot.keyboards import main_menu

router = Router()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.update_data(dialog_count=0, sales_offer_shown=False)
    await message.answer(
        "Здравствуйте! Я могу просто пообщаться, ответить на вопросы и помочь с выбором, когда это будет к месту. "
        "Расскажите, с чего начнём?",
        reply_markup=main_menu(),
    )

