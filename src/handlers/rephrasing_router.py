import re
import logging

from aiogram import types, Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.formatting import Text, Pre

from config_reader import config
from src.services.gen_ai.gen_ai import GenAI
from src.states.tweet_rephrasing import TweetRephrasing
from src.keyboards.keyboards import additional_instructions_kb
from src.tweet import Tweet
from src.utils.assemble_media_group import assemble_media_group
from src.utils.show_post_preview import show_post_preview

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
    if not match:
        await message.reply("❌ I think your input is invalid. Try again")
        return

    tweet_id = match.group(1)
    await message.answer("✅ I see! Fetching tweet...")

    try:
        tweet = await Tweet.create(tweet_id)

        if not tweet.ok:
            await message.answer("❌ Could not extract tweet information. Maybe id is invalid")
            return

        await state.update_data(
            post_text=tweet.text,
            original_tweet=tweet.text,
            post_media=tweet.media
        )

        tweet_info = Text(tweet.__repr__())
        await message.answer(text=tweet_info.as_html())

        await message.answer("Current post is: ")
        await show_post_preview(message, tweet.text, tweet.media, is_original=True)

    except Exception as e:
        await message.answer("❌ An error occurred while fetching the tweet. Please try again.")
        logging.error(f"Error fetching tweet {tweet_id}: {e}")


@rephrasing_router.callback_query(F.data == 'public_post')
async def handle_public_post_callback(callback: types.CallbackQuery, state: FSMContext, bot: Bot) -> None:
    try:
        data = await state.get_data()
        post_text = data.get("post_text", "")
        post_media = data.get("post_media", set())

        if not post_text:
            await callback.message.answer("❌ No post text found. Please try again.")
            await callback.answer()
            return

        caption = Text(post_text)

        if len(post_media) > 0:
            media_group = assemble_media_group(post_media, caption)
            await bot.send_media_group(config.channel_id, media=media_group)
        else:
            await bot.send_message(config.channel_id, text=caption.as_html(), parse_mode='HTML')

        await callback.message.answer("✅ Post has been published!")

        await state.clear()

    except Exception as e:
        await callback.message.answer("❌ An error occurred while publishing the post.")
        logging.error(f"Error publishing post: {e}")

    await callback.answer()


@rephrasing_router.callback_query(F.data == 'edit_post_manually')
async def handle_edit_post_manually_callback(callback: types.CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    post_text = data.get("post_text", "")

    if not post_text:
        await callback.message.answer("❌ No post text found. Please try again.")
        await callback.answer()
        return

    caption = Text("Current text:", Pre(post_text))
    await callback.message.answer("📝 Please send your new version of the text:")
    await callback.message.answer(text=caption.as_html())

    await state.set_state(TweetRephrasing.waiting_edit_manually)
    await callback.answer()


@rephrasing_router.message(TweetRephrasing.waiting_edit_manually)
async def process_waiting_edit_manually(message: Message, state: FSMContext) -> None:
    new_post_text = message.text.strip()

    if not new_post_text:
        await message.answer("❌ Please provide some text.")
        return

    await state.update_data(post_text=new_post_text)
    data = await state.get_data()
    post_media = data.get("post_media", set())

    await message.answer("✅ Text updated! Here's how your post looks like:")
    await show_post_preview(message, new_post_text, post_media, is_original=False)


@rephrasing_router.callback_query(F.data == 'recover_original')
async def handle_recover_original_callback(callback: types.CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    original_tweet = data.get("original_tweet", "")

    if not original_tweet:
        await callback.message.answer("❌ No original tweet found.")
        await callback.answer()
        return

    await state.update_data(post_text=original_tweet)
    post_media = data.get("post_media", set())

    await callback.message.answer("✅ Restored to original text:")
    await show_post_preview(callback, original_tweet, post_media, is_original=False)
    await callback.answer()


@rephrasing_router.callback_query(F.data == 'rephrase_with_llm')
async def handle_rephrase_with_llm_callback(callback: types.CallbackQuery) -> None:
    await callback.message.answer(
        "⚙️ Would you like to provide any additional instructions for rephrasing?",
        reply_markup=additional_instructions_kb
    )
    await callback.answer()


@rephrasing_router.callback_query(F.data == 'additional_instructions_yes')
async def handle_additional_instructions_yes_callback(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer("📝 Please provide your additional instructions:")
    await state.set_state(TweetRephrasing.waiting_additional_instructions)
    await callback.answer()


@rephrasing_router.message(TweetRephrasing.waiting_additional_instructions)
async def process_waiting_additional_instructions(message: Message, state: FSMContext, gen_ai_service: GenAI) -> None:
    additional_instructions = message.text.strip()

    if not additional_instructions:
        await message.answer("❌ Please provide some instructions.")
        return

    data = await state.get_data()
    post_text = data.get("post_text", "")

    if not post_text:
        await message.answer("❌ No post text found. Please try again.")
        return

    await message.answer('🤖 Rephrasing your text...')

    result = gen_ai_service.rephrase_post(post_text, additional_instructions)

    if not result:
        await message.answer("❌ Failed to rephrase the text. Please try again.")
        return

    await state.update_data(post_text=result)
    post_media = data.get("post_media", set())

    await message.answer("✅ Text rephrased! Here's the result:")
    await show_post_preview(message, result, post_media, is_original=False)


@rephrasing_router.callback_query(F.data == 'additional_instructions_no')
async def handle_additional_instructions_no_callback(callback: types.CallbackQuery, state: FSMContext,
                                                     gen_ai_service: GenAI) -> None:
    data = await state.get_data()
    post_text = data.get("post_text", "")

    if not post_text:
        await callback.message.answer("❌ No post text found. Please try again.")
        await callback.answer()
        return

    await callback.message.answer('🤖 Rephrasing your text...')
    await callback.answer()

    result = gen_ai_service.rephrase_post(post_text)

    if not result:
        await callback.message.answer("❌ Failed to rephrase the text. Please try again.")
        return

    await state.update_data(post_text=result)
    post_media = data.get("post_media", set())

    await callback.message.answer("✅ Text rephrased! Here's the result:")
    await show_post_preview(callback, result, post_media, is_original=False)
