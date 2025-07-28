import re

from aiogram import types, Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.formatting import Text, Bold
from aiogram.utils.media_group import MediaGroupBuilder

from config_reader import config
from src.final_state_machines.tweet_rephrasing import TweetRephrasing
from src.keyboards.keyboards import tweet_preview_kb
from src.tweet import Tweet, MediaType

rephrasing_router = Router()


@rephrasing_router.message(F.text == "🔄 Rephrase tweet 🐦")
async def handle_rephrase_tweet_message(message: Message, state: FSMContext) -> None:
    await message.answer("🔎 Sure, please give me link to tweet or id!")
    await state.set_state(TweetRephrasing.waiting_for_tweet_link_or_id)


@rephrasing_router.callback_query(F.data == 'rephrase_tweet')
async def handle_rephrase_tweet_callback(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer("🔎 Sure, please give me link to tweet or id!")
    await state.set_state(TweetRephrasing.waiting_for_tweet_link_or_id)
    await callback.answer()


@rephrasing_router.message(TweetRephrasing.waiting_for_tweet_link_or_id)
async def process_waiting_for_tweet_link_or_id(message: Message, state: FSMContext) -> None:
    link_or_id = message.text

    pattern = r'(?:.*status/)?(\d+)'
    match = re.search(pattern, link_or_id)
    if match:
        tweet_id = match.group(1)

        await message.answer("✅ I see! Fetching tweet...")

        tweet = await Tweet.create(tweet_id)

        if tweet.ok:
            await state.update_data(post_text=tweet.text)
            await state.update_data(post_media=tweet.media)

            caption = Text(tweet.__repr__())

            if len(tweet.media) > 0:
                media_group = MediaGroupBuilder()
                for i, media in enumerate(tweet.media):
                    if media.type == MediaType.IMAGE:
                        media_group.add_photo(media=media.url)
                    elif media.type == MediaType.VIDEO:
                        media_group.add_video(media=media.url)

                await message.answer_media_group(media=media_group.build())

            await message.answer(**caption.as_kwargs(), reply_markup=tweet_preview_kb)
        else:
            await message.answer("❌ Could not extract tweet information. Maybe id is invalid")

        return

    await message.reply("❌ I think your input is invalid. Try again")


@rephrasing_router.callback_query(F.data == 'public_post')
async def handle_public_post_callback(callback: types.CallbackQuery, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()

    post_text = data["post_text"]
    post_media = data["post_media"]

    caption = Text(post_text)

    if len(post_media) > 0:
        media_group = MediaGroupBuilder()
        for i, media in enumerate(post_media):
            media_caption = caption.as_markdown() if i == 0 else None

            if media.type == MediaType.IMAGE:
                media_group.add_photo(media=media.url, caption=media_caption)
            elif media.type == MediaType.VIDEO:
                media_group.add_video(media=media.url, caption=media_caption)
        await bot.send_media_group(config.channel_id, media=media_group.build())
    else:
        await bot.send_message(config.channel_id, **caption.as_kwargs(),)

    await callback.message.answer("✅ Post has been published!")
    # await state.set_state(TweetRephrasing.waiting_for_tweet_link_or_id)
    await callback.answer()


@rephrasing_router.callback_query(F.data == 'edit_post_manually')
async def handle_edit_post_manually_callback(callback: types.CallbackQuery, state: FSMContext) -> None:
    pass


@rephrasing_router.callback_query(F.data == 'rephrase_with_llm')
async def handle_rephrase_with_llm_callback(callback: types.CallbackQuery, state: FSMContext) -> None:
    pass