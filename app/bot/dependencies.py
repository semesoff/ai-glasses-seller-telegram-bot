from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.database.repositories import OrderRepository, ProductRepository
from app.database.session import SessionFactory
from app.services import (
    ConsultationService,
    ConversationService,
    DialogueService,
    LLMService,
    NLPService,
    OrderService,
    ProductService,
    VoiceService,
)


class ServicesMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        async with SessionFactory() as session:
            products = ProductRepository(session)
            orders = OrderRepository(session)
            data["product_service"] = ProductService(products, NLPService())
            data["order_service"] = OrderService(orders, products)
            data["nlp_service"] = NLPService()
            data["consultation_service"] = ConsultationService()
            data["conversation_service"] = ConversationService()
            data["dialogue_service"] = DialogueService()
            data["llm_service"] = LLMService()
            data["voice_service"] = VoiceService()
            return await handler(event, data)
