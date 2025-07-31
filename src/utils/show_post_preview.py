from aiogram import types
from aiogram.types import Message
from aiogram.utils.formatting import Text

from src.keyboards.keyboards import original_post_preview_kb, post_preview_kb
from src.utils.assemble_media_group import assemble_media_group


async def show_post_preview(message_or_callback: Message | types.CallbackQuery, post_text: str, post_media: set, is_original: bool = True):
    """Unified function to show post preview with appropriate keyboard"""
    if isinstance(message_or_callback, Message):
        message = message_or_callback
    else:
        message = message_or_callback.message

    caption = Text(post_text)
    keyboard = original_post_preview_kb if is_original else post_preview_kb

    if len(post_media) > 0:
        media_group = assemble_media_group(post_media)
        await message.answer_media_group(media=media_group)

    await message.answer(text=caption.as_html(), reply_markup=keyboard)