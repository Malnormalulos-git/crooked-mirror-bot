from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from src.services.gen_ai.gemini_gen_ai import GeminiGenAI


class DependencyInjectionMiddleware(BaseMiddleware):
    __gen_ai_service = GeminiGenAI()

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        data['gen_ai_service'] = DependencyInjectionMiddleware.__gen_ai_service

        return await handler(event, data)
