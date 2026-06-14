"""Bot middleware package."""
from app.bot.middlewares.logging import UserActivityLoggingMiddleware

__all__ = ["UserActivityLoggingMiddleware"]
