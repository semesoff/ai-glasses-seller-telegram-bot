import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, TelegramObject

logger = logging.getLogger(__name__)

SENSITIVE_STATE_PARTS = ("OrderStates:phone", "OrderStates:address")


def _shorten(value: str, limit: int = 500) -> str:
    value = " ".join(value.split())
    if len(value) <= limit:
        return value
    return f"{value[:limit]}..."


async def _state_name(data: dict[str, Any]) -> str | None:
    state: FSMContext | None = data.get("state")
    if state is None:
        return None
    return await state.get_state()


def _safe_text(text: str | None, state_name: str | None) -> str:
    if not text:
        return ""
    if state_name and any(part in state_name for part in SENSITIVE_STATE_PARTS):
        return "[redacted]"
    return _shorten(text)


class UserActivityLoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        state_name = await _state_name(data)

        if isinstance(event, Message):
            user = event.from_user
            logger.info(
                'user_message telegram_id=%s username=%s state=%s text="%s"',
                user.id if user else None,
                user.username if user else None,
                state_name,
                _safe_text(event.text or event.caption, state_name),
            )
        elif isinstance(event, CallbackQuery):
            user = event.from_user
            logger.info(
                'user_callback telegram_id=%s username=%s state=%s data="%s"',
                user.id if user else None,
                user.username if user else None,
                state_name,
                _shorten(event.data or ""),
            )

        return await handler(event, data)
