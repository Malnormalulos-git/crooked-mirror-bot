from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='ℹ️ Help ❓')],
    [KeyboardButton(text='🔄 Rephrase tweet 🐦')]
], resize_keyboard=True)

help_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔄 Try to rephrase tweet 🐦', callback_data='rephrase_tweet')],
])

tweet_preview_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📰 Public as it 📢', callback_data='public_post')],
    [InlineKeyboardButton(text='📝 Edit manually ✍️', callback_data='edit_post_manually')],
    [InlineKeyboardButton(text='🤖 Rephrase with LLM 👾', callback_data='rephrase_with_llm')],
])
