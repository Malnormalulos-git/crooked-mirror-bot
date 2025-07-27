from aiogram import Router, types
from aiogram.filters import Command

common_router = Router()


@common_router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello!")