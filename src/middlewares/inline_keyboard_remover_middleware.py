from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton


class InlineKeyboardRemoverMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            callback_query: CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        if callback_query.message:
            message = callback_query.message

            original_text = message.html_text
            choice = callback_query.data

            inline_markup: InlineKeyboardMarkup = message.reply_markup

            choice_text: str | None = None

            for row in inline_markup.inline_keyboard:
                for button in row:
                    if isinstance(button, InlineKeyboardButton):
                        if button.callback_data == choice:
                            choice_text = button.text
                            break
                if choice_text is not None:
                    break

            text_with_choice = original_text + f"\n\nChoice: {choice_text or choice}"

            chat_id = message.chat.id
            message_id = message.message_id

            bot: Bot = data["bot"]

            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text_with_choice, reply_markup=None)

        return await handler(callback_query, data)