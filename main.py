import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.methods import DeleteWebhook

from config_reader import config
from src.handlers.common_router import common_router
from src.handlers.rephrasing_router import rephrasing_router
from src.middlewares.access_middleware import AccessMiddleware

logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=config.bot_token.get_secret_value(),
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML,
    ),
)


async def main():
    dp = Dispatcher(storage=MemoryStorage())

    dp.update.outer_middleware(AccessMiddleware())

    dp.include_router(common_router)
    dp.include_router(rephrasing_router)

    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
