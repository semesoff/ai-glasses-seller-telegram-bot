import logging
from dataclasses import dataclass

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.bot.formatting import format_products, format_sales_offer
from app.bot.handlers.consultation import start_consultation
from app.bot.handlers.faq import answer_faq
from app.bot.handlers.order import my_orders_command, order_command
from app.bot.handlers.search import run_search
from app.bot.keyboards import main_menu, recommendation_keyboard
from app.nlp import Intent
from app.services import (
    ConsultationService,
    ConversationService,
    DialogueService,
    LLMService,
    NLPService,
    OrderService,
    ProductService,
)

router = Router()
logger = logging.getLogger(__name__)

BUY_PHRASES = {"купить", "хочу купить", "покупаю", "беру", "заказать", "хочу заказать"}
YES_PHRASES = {"да", "давай", "конечно", "покажи", "покажи модели", "хочу посмотреть"}


@dataclass(slots=True)
class TextRouteResult:
    spoken_text: str | None = None
    visual_sent: bool = False


async def show_buyable_products(message: Message, product_service: ProductService, text: str | None = None) -> TextRouteResult:
    products = await product_service.search_products(text) if text else await product_service.get_catalog()
    await message.answer(
        format_products(products) + "\n\nВыберите модель кнопкой ниже, и я сразу оформлю бронь.",
        parse_mode=ParseMode.HTML,
        reply_markup=recommendation_keyboard(products) if products else None,
    )
    if products:
        return TextRouteResult(
            spoken_text="Я подобрал несколько вариантов очков и отправил карточки с кнопками покупки в чат.",
            visual_sent=True,
        )
    return TextRouteResult(spoken_text="По этому запросу я ничего не нашёл. Попробуйте назвать другой стиль или бюджет.")


async def process_text_message(
    message: Message,
    state: FSMContext,
    text: str,
    product_service: ProductService,
    order_service: OrderService,
    nlp_service: NLPService,
    consultation_service: ConsultationService,
    conversation_service: ConversationService,
    dialogue_service: DialogueService,
    llm_service: LLMService,
    voice_mode: bool = False,
) -> TextRouteResult:
    lowered = text.lower().strip()
    telegram_id = message.from_user.id if message.from_user else None
    current_state = await state.get_state()

    if consultation_service.should_start(text) or lowered == "подобрать очки":
        logger.info("dialog_route telegram_id=%s route=consultation_start", telegram_id)
        await start_consultation(message, state)
        return TextRouteResult(
            spoken_text="Давайте подберём очки как стилист. Я задам несколько вопросов и предложу подходящие модели.",
            visual_sent=True,
        )

    result = nlp_service.analyze(text)
    if current_state and current_state.startswith("ConsultationStates:"):
        logger.info(
            "dialog_route telegram_id=%s route=consultation_cancel_to_free_chat previous_state=%s",
            telegram_id,
            current_state,
        )
        await state.clear()

    data = await state.get_data()
    last_bot_offer = bool(data.get("last_bot_offered_models"))
    if lowered in BUY_PHRASES or (last_bot_offer and lowered in YES_PHRASES):
        logger.info("dialog_route telegram_id=%s route=buyable_products", telegram_id)
        await state.update_data(last_bot_offered_models=False)
        return await show_buyable_products(message, product_service)

    if result.intent == Intent.SHOW_CATALOG or lowered == "каталог":
        logger.info("dialog_route telegram_id=%s route=catalog", telegram_id)
        return await show_buyable_products(message, product_service)
    if lowered == "поиск":
        logger.info("dialog_route telegram_id=%s route=search_prompt", telegram_id)
        reply_text = "Напишите запрос, например: Хочу мужские авиаторы до 5000 рублей"
        if not voice_mode:
            await message.answer(reply_text)
        return TextRouteResult(spoken_text=reply_text)
    if lowered == "помощь":
        logger.info("dialog_route telegram_id=%s route=help", telegram_id)
        reply_text = (
            "Можем просто поговорить, открыть каталог, найти модель через поиск, "
            "посмотреть заказы, обсудить доставку, оплату или оформить заказ."
        )
        if voice_mode:
            await message.answer("Выберите действие кнопкой ниже.", reply_markup=main_menu())
            return TextRouteResult(spoken_text=reply_text, visual_sent=True)
        await message.answer(reply_text, reply_markup=main_menu())
        return TextRouteResult(spoken_text=reply_text, visual_sent=True)
    if result.intent == Intent.VIEW_ORDERS:
        logger.info("dialog_route telegram_id=%s route=view_orders", telegram_id)
        await my_orders_command(message, state, order_service)
        return TextRouteResult(spoken_text="Я отправил ваши последние заказы в чат.", visual_sent=True)
    if result.intent == Intent.SEARCH_PRODUCT:
        logger.info("dialog_route telegram_id=%s route=product_search", telegram_id)
        await run_search(message, product_service, text)
        return TextRouteResult(
            spoken_text="Я нашёл подходящие модели и отправил карточки с кнопками покупки в чат.",
            visual_sent=True,
        )
    if result.intent == Intent.ASK_DELIVERY:
        logger.info("dialog_route telegram_id=%s route=faq_delivery", telegram_id)
        if not voice_mode:
            await answer_faq(message, "delivery")
        return TextRouteResult(spoken_text="Доставка доступна по России. Обычно занимает от двух до пяти рабочих дней.")
    if result.intent == Intent.ASK_PAYMENT:
        logger.info("dialog_route telegram_id=%s route=faq_payment", telegram_id)
        if not voice_mode:
            await answer_faq(message, "payment")
        return TextRouteResult(
            spoken_text="Оплатить можно картой или наличными при получении, если этот способ доступен в вашем городе."
        )
    if result.intent == Intent.ASK_RETURN:
        logger.info("dialog_route telegram_id=%s route=faq_return", telegram_id)
        if not voice_mode:
            await answer_faq(message, "return")
        return TextRouteResult(spoken_text="Возврат возможен в течение четырнадцати дней при сохранении товарного вида.")
    if result.intent == Intent.CREATE_ORDER:
        logger.info("dialog_route telegram_id=%s route=order_start", telegram_id)
        await order_command(message, state)
        return TextRouteResult(
            spoken_text="Хорошо, оформим заказ. Я написал в чат, какой номер товара нужно отправить.",
            visual_sent=True,
        )

    dialog_count = int(data.get("dialog_count", 0)) + 1
    history = list(data.get("dialog_history", []))

    llm_reply = await llm_service.chat(text, history, dialog_count)
    if llm_reply.available:
        reply_text = llm_reply.text
        should_offer_products = dialog_count >= 6 and not data.get("sales_offer_shown")
        logger.info("dialog_route telegram_id=%s route=llm dialog_count=%s", telegram_id, dialog_count)
    else:
        dialogue_answer = dialogue_service.find_answer(text)
        fallback = conversation_service.next_reply(text, dialog_count, dialogue_answer=dialogue_answer)
        reply_text = fallback.text
        should_offer_products = fallback.should_offer_products and not data.get("sales_offer_shown")
        logger.info("dialog_route telegram_id=%s route=fallback dialog_count=%s", telegram_id, dialog_count)

    history.extend(
        [
            {"role": "user", "content": text},
            {"role": "assistant", "content": reply_text},
        ]
    )

    if any(phrase in reply_text.lower() for phrase in ("хотите узнать о новых моделях", "показать модели", "предложить")):
        await state.update_data(last_bot_offered_models=True)

    await state.update_data(dialog_count=dialog_count, dialog_history=history[-12:])

    if should_offer_products:
        products = await product_service.find_by_filters({"type": "sunglasses"}, page=1, limit=3)
        await state.update_data(sales_offer_shown=True, page=1, last_bot_offered_models=False)
        logger.info(
            "sales_offer telegram_id=%s dialog_count=%s product_ids=%s",
            telegram_id,
            dialog_count,
            [product.id for product in products],
        )
        if not voice_mode:
            await message.answer(reply_text)
        await message.answer(
            format_sales_offer(products),
            parse_mode=ParseMode.HTML,
            reply_markup=recommendation_keyboard(products) if products else None,
        )
        return TextRouteResult(spoken_text=reply_text, visual_sent=True)

    if not voice_mode:
        await message.answer(reply_text)
    return TextRouteResult(spoken_text=reply_text)


@router.message()
async def free_text(
    message: Message,
    state: FSMContext,
    product_service: ProductService,
    order_service: OrderService,
    nlp_service: NLPService,
    consultation_service: ConsultationService,
    conversation_service: ConversationService,
    dialogue_service: DialogueService,
    llm_service: LLMService,
) -> None:
    await process_text_message(
        message=message,
        state=state,
        text=message.text or "",
        product_service=product_service,
        order_service=order_service,
        nlp_service=nlp_service,
        consultation_service=consultation_service,
        conversation_service=conversation_service,
        dialogue_service=dialogue_service,
        llm_service=llm_service,
    )
