import re

from aiogram import types, Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.formatting import Text, Pre

from config_reader import config
from src.services.gen_ai.gen_ai import GenAI
from src.states.tweet_rephrasing import TweetRephrasing
from src.keyboards.keyboards import tweet_preview_kb, post_preview_kb
from src.tweet import Tweet
from src.utils.assemble_media_group import assemble_media_group

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
                media_group = assemble_media_group(tweet.media)

                await message.answer_media_group(media=media_group)

            await message.answer(text=caption.as_html(), reply_markup=tweet_preview_kb)
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
        media_group = assemble_media_group(post_media, caption)
        await bot.send_media_group(config.channel_id, media=media_group)
    else:
        await bot.send_message(config.channel_id, text=caption.as_html(), parse_mode='HTML')

    await callback.message.answer("✅ Post has been published!")
    await callback.answer()


@rephrasing_router.callback_query(F.data == 'edit_post_manually')
async def handle_edit_post_manually_callback(callback: types.CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()

    post_text = data["post_text"]

    caption = Text(Pre(post_text))

    await callback.message.answer("Waiting for your variant of the text: ")
    await callback.message.answer(text=caption.as_html())

    await state.set_state(TweetRephrasing.waiting_edit_manually)

    await callback.answer()


@rephrasing_router.message(TweetRephrasing.waiting_edit_manually)
async def process_waiting_edit_manually(message: Message, state: FSMContext) -> None:
    new_post_text = message.text

    data = await state.update_data(post_text=new_post_text)
    post_media = data["post_media"]

    await message.answer("This how your post looks like: ")

    caption = Text(new_post_text)

    if len(post_media) > 0:
        media_group = assemble_media_group(post_media)
        await message.answer_media_group(media=media_group)

    await message.answer(text=caption.as_html(), reply_markup=post_preview_kb)


@rephrasing_router.callback_query(F.data == 'rephrase_with_llm')
async def handle_rephrase_with_llm_callback(callback: types.CallbackQuery, state: FSMContext, gen_ai_service: GenAI) -> None:
    data = await state.get_data()
    post_text = data["post_text"]

    await callback.message.answer('Rephrasing your text...')
    await callback.answer()

    result = gen_ai_service.rephrase_post(post_text)

    await callback.message.answer(result if result else "❌ Something went wrong")
