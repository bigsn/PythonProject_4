"""Telethon client singleton manager."""

from telethon import TelegramClient
from pythonproject_4.config import get_settings

_client = None


def get_telegram_client() -> TelegramClient:
    """Get or create a Telethon client. Must be called from within a task context."""
    global _client
    if _client is None:
        settings = get_settings()
        _client = TelegramClient(
            settings.TELEGRAM_SESSION_PATH,
            settings.TELEGRAM_API_ID,
            settings.TELEGRAM_API_HASH,
        )
        if not _client.is_user_authorized():
            raise RuntimeError(
                "Telegram session not authorized. Run: python -m pythonproject_4.telegram.authorize"
            )
    return _client


def close_telegram_client():
    """Close the Telethon client."""
    global _client
    if _client:
        _client.disconnect()
        _client = None
