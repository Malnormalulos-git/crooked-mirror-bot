from aiogram import Router, types, F
from aiogram.filters import Command

from src.keyboards.keyboards import main_kb, help_kb

common_router = Router()


@common_router.message(Command("start"))
async def cmd_start(message: types.Message) -> None:
    await message.answer(f"Hello, {message.from_user.first_name}, ready to serve you!", reply_markup=main_kb)


@common_router.message(F.text == "ℹ️ Help ❓")
async def help_btn_handler(message: types.Message) -> None:
    text = "With this bot you can rephrase tweet and public at the chanel!"
    await message.reply(text, reply_markup=help_kb)