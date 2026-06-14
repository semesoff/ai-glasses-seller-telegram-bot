import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.bot.dependencies import ServicesMiddleware
from app.bot.handlers import setup_routers
from app.bot.middlewares import UserActivityLoggingMiddleware
from app.config import get_settings


async def main() -> None:
    settings = get_settings()
    logging.basicConfig(level=settings.log_level)
    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN is empty. Set it in .env before running the bot.")
    bot = Bot(token=settings.bot_token)
    dispatcher = Dispatcher()
    services_middleware = ServicesMiddleware()
    activity_logging_middleware = UserActivityLoggingMiddleware()
    dispatcher.message.middleware(activity_logging_middleware)
    dispatcher.callback_query.middleware(activity_logging_middleware)
    dispatcher.message.middleware(services_middleware)
    dispatcher.callback_query.middleware(services_middleware)
    dispatcher.include_router(setup_routers())
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
