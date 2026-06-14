from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot.formatting import format_products
from app.bot.handlers.order import ask_phone_for_product
from app.bot.keyboards import (
    budget_keyboard,
    gender_keyboard,
    goal_keyboard,
    recommendation_keyboard,
    shape_keyboard,
    style_keyboard,
)
from app.bot.states import ConsultationStates
from app.services import ConsultationService, ProductService

router = Router()


async def start_consultation(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(ConsultationStates.goal)
    await message.answer(
        "Давайте подберём очки как стилист. Я задам несколько коротких вопросов и покажу лучшие варианты. "
        "Для чего в первую очередь нужны очки?",
        reply_markup=goal_keyboard(),
    )


@router.message(F.text.lower() == "подобрать очки")
async def consultation_button(message: Message, state: FSMContext) -> None:
    await start_consultation(message, state)


@router.callback_query(F.data.startswith("consult:goal:"))
async def goal_selected(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(goal=callback.data.rsplit(":", 1)[-1], message_count=2)
    await state.set_state(ConsultationStates.gender)
    await callback.message.answer("Кому подбираем посадку?", reply_markup=gender_keyboard())
    await callback.answer()


@router.callback_query(F.data.startswith("consult:gender:"))
async def gender_selected(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(gender=callback.data.rsplit(":", 1)[-1], message_count=3)
    await state.set_state(ConsultationStates.style)
    await callback.message.answer("Какой стиль ближе?", reply_markup=style_keyboard())
    await callback.answer()


@router.callback_query(F.data.startswith("consult:style:"))
async def style_selected(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(style=callback.data.rsplit(":", 1)[-1], message_count=4)
    await state.set_state(ConsultationStates.shape_preference)
    await callback.message.answer(
        "Есть предпочтение по форме? Если не уверены, нажмите «Не знаю» — подберу универсальный вариант.",
        reply_markup=shape_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("consult:shape:"))
async def shape_selected(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(shape_preference=callback.data.rsplit(":", 1)[-1], message_count=5)
    await state.set_state(ConsultationStates.budget)
    await callback.message.answer("Какой бюджет комфортен?", reply_markup=budget_keyboard())
    await callback.answer()


@router.callback_query(F.data.startswith("consult:budget:"))
async def budget_selected(
    callback: CallbackQuery,
    state: FSMContext,
    product_service: ProductService,
    consultation_service: ConsultationService,
) -> None:
    await state.update_data(budget=callback.data.rsplit(":", 1)[-1], page=1, message_count=6)
    await show_recommendations(callback, state, product_service, consultation_service, page=1)
    await callback.answer()


@router.callback_query(F.data == "consult:more")
async def show_more(
    callback: CallbackQuery,
    state: FSMContext,
    product_service: ProductService,
    consultation_service: ConsultationService,
) -> None:
    data = await state.get_data()
    page = int(data.get("page", 1)) + 1
    await state.update_data(page=page)
    await show_recommendations(callback, state, product_service, consultation_service, page=page)
    await callback.answer()


@router.callback_query(F.data == "consult:change_budget")
async def change_budget(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ConsultationStates.budget)
    await callback.message.answer("Хорошо, изменим бюджет. Какой диапазон выбрать?", reply_markup=budget_keyboard())
    await callback.answer()


@router.callback_query(F.data == "consult:restart")
async def restart(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(ConsultationStates.goal)
    await callback.message.answer("Начнём заново. Для чего выбираем очки?", reply_markup=goal_keyboard())
    await callback.answer()


@router.callback_query(F.data.startswith("consult:buy:"))
async def buy_recommended(callback: CallbackQuery, state: FSMContext, product_service: ProductService) -> None:
    product_id = int(callback.data.rsplit(":", 1)[-1])
    await ask_phone_for_product(callback.message, state, product_id, product_service)
    await callback.answer()


@router.message(ConsultationStates.budget)
async def budget_text_entered(
    message: Message,
    state: FSMContext,
    product_service: ProductService,
    consultation_service: ConsultationService,
) -> None:
    await state.update_data(budget=message.text or "any", page=1, message_count=6)
    fake_callback = type("MessageCarrier", (), {"message": message})()
    await show_recommendations(fake_callback, state, product_service, consultation_service, page=1)


async def show_recommendations(
    event,
    state: FSMContext,
    product_service: ProductService,
    consultation_service: ConsultationService,
    page: int,
) -> None:
    data = await state.get_data()
    recommendation = consultation_service.recommendation(data, page=page)
    products = await product_service.find_by_filters(recommendation.filters, page=page, limit=3)
    if not products:
        fallback_filters = {"type": "sunglasses", "gender": recommendation.filters.get("gender", "unisex")}
        products = await product_service.find_by_filters(fallback_filters, page=page, limit=3)
    await state.set_state(ConsultationStates.recommendation)
    await event.message.answer(
        f"{recommendation.explanation}\n\n{format_products(products)}\n\n"
        "Можно оформить заказ сейчас: нажмите кнопку «Купить» под понравившейся моделью.",
        parse_mode=ParseMode.HTML,
        reply_markup=recommendation_keyboard(products) if products else None,
    )
