import logging

from aiogram import types, Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.formatting import Text, Pre

from config_reader import config
from src.services.gen_ai.gen_ai import GenAI
from src.services.social_platform_scraper.social_platform_manager import SocialPlatformManager
from src.states.rephrasing import Rephrasing
from src.keyboards.keyboards import additional_instructions_kb
from src.utils.assemble_media_group import assemble_media_group
from src.utils.show_post_preview import show_post_preview

rephrasing_router = Router()


@rephrasing_router.message(F.text == "🔄 Rephrase post 📜")
async def handle_rephrase_post_message(message: Message, state: FSMContext) -> None:
    await message.answer("🔎 Sure, please give me link/id of the post!")
    await state.set_state(Rephrasing.waiting_for_link_or_id)


@rephrasing_router.callback_query(F.data == 'rephrase_post')
async def handle_rephrase_post_callback(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer("🔎 Sure, please give me link/id of the post!")
    await state.set_state(Rephrasing.waiting_for_link_or_id)
    await callback.answer()


@rephrasing_router.message(Rephrasing.waiting_for_link_or_id)
async def process_waiting_for_post_link_or_id(
        message: Message,
        state: FSMContext,
        social_platform_manager: SocialPlatformManager
) -> None:
    url_or_id = message.text.strip()

    await message.answer("✅ I see! Fetching post...")

    try:
        post = await social_platform_manager.get_post(url_or_id)

        if not post:
            await message.answer(
                "❌ Could not extract post information. Maybe the link/id is invalid or platform is not supported.")
            return

        await state.update_data(
            post_text=post.text,
            original_post=post.text,
            post_media=post.media,
            platform=post.platform.value
        )

        post_info = Text(social_platform_manager.format_post_info(post))

        await message.answer(text=post_info.as_html())
        await message.answer("Current post is: ")
        await show_post_preview(message, post.text, post.media, is_original=True)

    except Exception as e:
        await message.answer("❌ An error occurred while fetching the post. Please try again.")
        logging.error(f"Error fetching post from {url_or_id}: {e}")


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

    await state.set_state(Rephrasing.waiting_edit_manually)
    await callback.answer()


@rephrasing_router.message(Rephrasing.waiting_edit_manually)
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
    original_post = data.get("original_post", "")

    if not original_post:
        await callback.message.answer("❌ No original post found.")
        await callback.answer()
        return

    await state.update_data(post_text=original_post)
    post_media = data.get("post_media", set())

    await callback.message.answer("✅ Restored to original text:")
    await show_post_preview(callback, original_post, post_media, is_original=False)
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
    await state.set_state(Rephrasing.waiting_additional_instructions)
    await callback.answer()


@rephrasing_router.message(Rephrasing.waiting_additional_instructions)
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
