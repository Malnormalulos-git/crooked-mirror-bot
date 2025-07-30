from aiogram.fsm.state import StatesGroup, State


class TweetRephrasing(StatesGroup):
    waiting_for_tweet_link_or_id = State()
    waiting_edit_manually = State()
    waiting_additional_instructions = State()