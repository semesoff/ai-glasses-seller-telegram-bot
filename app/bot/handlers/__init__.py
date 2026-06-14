from aiogram import Router

from app.bot.handlers import catalog, consultation, faq, order, search, start, text, voice


def setup_routers() -> Router:
    router = Router()
    router.include_router(start.router)
    router.include_router(catalog.router)
    router.include_router(search.router)
    router.include_router(faq.router)
    router.include_router(order.router)
    router.include_router(consultation.router)
    router.include_router(voice.router)
    router.include_router(text.router)
    return router
