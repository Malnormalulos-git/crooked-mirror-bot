from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from pathlib import Path


class Config(BaseSettings):
    bot_token: SecretStr
    admin_id: int
    twitter_auth_token: str
    twitter_ct0: str
    channel_id: str
    llm_api_key: str
    gemini_model: str = "gemini-2.5-flash"
    text_rephrasing_prompt: str = """
Rephrase the following text while preserving its original meaning, including all specific facts, names, numbers, terminology, and links if present.
Do not add or omit any important details.
Style and sentence structure may be changed only according to the additional instructions provided.

Output only the rephrased version. Do not include explanations, summaries, or formatting.

Additional instructions:
[{}]

Original text:
[{}]"""

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / '.env'
    )


config = Config()
