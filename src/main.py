import asyncio
import logging

from aiogram import Bot, Dispatcher

from config_reader import config
from src.handlers import router
from src.middlewares.access_middleware import AccessMiddleware

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.bot_token.get_secret_value())

async def main():
    dp = Dispatcher()

    dp.update.outer_middleware(AccessMiddleware())

    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
