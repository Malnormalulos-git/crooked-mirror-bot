from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from pathlib import Path


class Config(BaseSettings):
    bot_token: SecretStr
    admin_id: int

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / '.env'
    )


config = Config()
