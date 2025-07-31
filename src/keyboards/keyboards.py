from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='ℹ️ Help ❓')],
    [KeyboardButton(text='🔄 Rephrase post 📜')]
], resize_keyboard=True)

help_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔄 Try to rephrase post 📜', callback_data='rephrase_post')],
])

original_post_preview_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📰 Public as it 📢', callback_data='public_post')],
    [InlineKeyboardButton(text='📝 Edit manually ✍️', callback_data='edit_post_manually')],
    [InlineKeyboardButton(text='🤖 Rephrase with LLM 👾', callback_data='rephrase_with_llm')],
])

post_preview_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📰 Public 📢', callback_data='public_post')],
    [InlineKeyboardButton(text='📝 Edit manually ✍️', callback_data='edit_post_manually')],
    [InlineKeyboardButton(text='🤖 Rephrase with LLM 👾', callback_data='rephrase_with_llm')],
    [InlineKeyboardButton(text='🔄 Recover original 📜', callback_data='recover_original')],
])

additional_instructions_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Yes', callback_data='additional_instructions_yes'),
     InlineKeyboardButton(text='No', callback_data='additional_instructions_no')]
])
