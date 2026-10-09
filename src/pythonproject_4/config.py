"""Application configuration via pydantic-settings."""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+psycopg2://user:pass@localhost:5432/ainews"

    # OpenAI
    OPENAI_API_KEY: str = "default_key"
    OPENAI_MODEL: str = "gpt-4"
    PROXY: str = 'https://openai.javarush.com/v1 '

    # Telegram
    TELEGRAM_API_ID: int = 0
    TELEGRAM_API_HASH: str = "default_hash"
    TELEGRAM_SESSION_PATH: str = "session"
    TELEGRAM_TARGET_CHANNEL: str = "default_channel"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # App
    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8000

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
