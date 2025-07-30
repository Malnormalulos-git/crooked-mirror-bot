import logging
from aiogram import Router, types, F, Bot
from aiogram.enums import ChatMemberStatus
from aiogram.filters import Command
from aiogram.utils.formatting import Text, Bold

from config_reader import config
from src.keyboards.keyboards import main_kb, help_kb

common_router = Router()


@common_router.message(Command("start"))
async def cmd_start(message: types.Message) -> None:
    content = Text(
        "Hello, ",
        Bold(message.from_user.first_name),
        ", ready to serve you!"
    )
    await message.answer(**content.as_kwargs(), reply_markup=main_kb)


@common_router.message(F.text == "ℹ️ Help ❓")
async def help_btn_handler(message: types.Message) -> None:
    text = "With this bot you can rephrase tweet and public at the chanel!"
    await message.reply(text, reply_markup=help_kb)


@common_router.startup()
async def startup(bot: Bot) -> None:
    try:
        chat_member = await bot.get_chat_member(chat_id=config.channel_id, user_id=bot.id)
        is_admin = chat_member.status == ChatMemberStatus.ADMINISTRATOR
        if is_admin:
            logging.log(level=logging.INFO, msg="Bot is ready!")
            return
    except Exception as e:
        print(f"Error checking bot admin status: {e}")
        raise


@common_router.shutdown()
async def shutdown() -> None:
    logging.log(level=logging.INFO, msg="Shutting down...")