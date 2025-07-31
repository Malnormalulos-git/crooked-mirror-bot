from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from src.services.gen_ai.gemini_gen_ai import GeminiGenAI
from src.services.social_platform_scraper.social_platform_manager import SocialPlatformManager


class DependencyInjectionMiddleware(BaseMiddleware):
    __gen_ai_service = GeminiGenAI()
    __social_platform_manager = SocialPlatformManager()

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        data['gen_ai_service'] = DependencyInjectionMiddleware.__gen_ai_service
        data['social_platform_manager'] = DependencyInjectionMiddleware.__social_platform_manager

        return await handler(event, data)
