"""Shared Telethon-based Telegram channel parser."""

from typing import List, Optional

from telethon import TelegramClient
from telethon.tl.types import Channel

from pythonproject_4.news_parser.base import BaseParser, ParsedNews
from pythonproject_4.config import get_settings


class TelegramNewsParser(BaseParser):
    """Shared parser for all Telegram channels using a single Telethon client."""

    def __init__(self, client: Optional[TelegramClient] = None):
        self._client = client

    @property
    def client(self) -> TelegramClient:
        if self._client is None:
            settings = get_settings()
            self._client = TelegramClient(
                settings.TELEGRAM_SESSION_PATH,
                settings.TELEGRAM_API_ID,
                settings.TELEGRAM_API_HASH,
            )
            # Non-interactive: check if session is valid
            if not self._client.is_user_authorized():
                raise RuntimeError(
                    "Telegram session not authorized. Run: python -m pythonproject_4.telegram.authorize"
                )
        return self._client

    def resolve_channel(self, source_url: str) -> tuple:
        """Resolve source_url to (channel_id, channel_username)."""
        username = source_url
        if source_url.startswith("https://t.me/"):
            username = source_url.split("/")[-1]

        # Try to get entity
        entity = self.client.get_entity(username)
        if isinstance(entity, Channel):
            channel_id = entity.id
            return channel_id, username
        raise ValueError(f"Cannot resolve channel: {source_url}")

    def parse(self, source_url: str) -> List[ParsedNews]:
        """Parse recent messages from the resolved Telegram channel."""
        client = self.client
        channel_id, username = self.resolve_channel(source_url)

        messages = []
        try:
            # Get last 50 messages
            for msg in client.iter_messages(channel_id, limit=50):
                if msg.text:
                    messages.append(msg)
        except Exception as e:
            raise RuntimeError(f"Failed to fetch messages from channel {channel_id}: {e}")

        results = []
        for msg in messages:
            raw_text = msg.text.strip()
            if not raw_text:
                continue

            # Build message URL
            msg_url = f"https://t.me/{username}/{msg.id}" if msg.id else None

            results.append(ParsedNews(
                title=raw_text[:200],
                raw_text=raw_text,
                telegram_channel_id=channel_id,
                telegram_message_id=msg.id,
                published_at=msg.date if msg.date else None,
            ))

        return results
