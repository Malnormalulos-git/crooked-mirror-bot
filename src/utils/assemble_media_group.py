import logging

from aiogram.types import InputMediaAudio, InputMediaPhoto, InputMediaVideo, InputMediaDocument
from aiogram.utils.formatting import Text
from aiogram.utils.media_group import MediaGroupBuilder

from src.tweet import MediaItem, MediaType


def assemble_media_group(media: set[MediaItem], caption: Text | None = None) -> list[
    InputMediaAudio | InputMediaPhoto | InputMediaVideo | InputMediaDocument]:
    """
    Assemble a media group from MediaItem set with optional caption.

    Args:
        media: Set of MediaItem objects
        caption: Optional Text object for caption (will be added to first media item)

    Returns:
        List of InputMedia objects ready for sending
    """
    if not media:
        return []

    media_group = MediaGroupBuilder()

    for i, media_item in enumerate(media):
        media_caption = caption.as_html() if i == 0 and caption is not None else None

        try:
            if media_item.type == MediaType.IMAGE:
                media_group.add_photo(media=media_item.url, caption=media_caption, parse_mode='HTML')
            elif media_item.type == MediaType.VIDEO:
                media_group.add_video(media=media_item.url, caption=media_caption, parse_mode='HTML')
        except Exception as e:
            logging.warning(f"Failed to add media item {media_item.url}: {e}")

    return media_group.build()
