import logging
from aiogram import types, Router, Bot
from aiogram.filters import Command
from aiogram.utils.media_group import MediaGroupBuilder

from src.tweet import Tweet, MediaType

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello!")


@router.message(Command("tweet"))
async def cmd_tweet(message: types.Message):
    try:
        url = message.text
        tweet_id = url.split('/')[-1].split('?')[0]

        tweet = await Tweet.create(tweet_id)

        if tweet.ok:
            caption = tweet.__repr__()

            if len(tweet.media) > 0:
                media_group = MediaGroupBuilder()
                for i, media in enumerate(tweet.media):
                    media_caption = caption if i == 0 else None

                    if media.type == MediaType.IMAGE:
                        media_group.add_photo(media=media.url, caption=media_caption)
                    elif media.type == MediaType.VIDEO:
                        media_group.add_video(media=media.url, caption=media_caption)
                await message.reply_media_group(media=media_group.build())
            else:
                await message.reply(caption)
        else:
            await message.reply("❌ Could not extract tweet information")
    except Exception as e:
        logging.error(f"Error processing tweet: {e}")
        await message.reply("❌ Error processing the tweet URL")