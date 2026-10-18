"""Shared Telethon-based Telegram channel parser."""

import asyncio
from typing import List, Optional
import re
import logging

from pythonproject_4.news_parser.base import BaseParser, ParsedNews
from pythonproject_4.config import get_settings
from pythonproject_4.telegram.client import get_telegram_client
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class TelegramNewsParser(BaseParser):
    """Shared parser for all Telegram channels using a single Telethon client."""

    def parse(self, source_url: str) -> List[ParsedNews]:
        """Parse recent messages from the resolved Telegram channel."""
        channel_id = -1001544383662

        async def _fetch():
            results = []
            client = get_telegram_client()
            async with client:
                try:
                    async for msg in client.iter_messages(channel_id, limit=5):
                        if msg.text:
                            title = ""
                            match = re.search(r'\*\*(.*?)\*\*', msg.text)
                            if match:
                                title = match.group(1)
                            results.append(ParsedNews(
                                title=title,
                                raw_text=msg.text,
                                telegram_channel_id=channel_id,
                                telegram_message_id=msg.id,
                                published_at=msg.date if msg.date else None,
                            ))
                except Exception as e:
                    raise RuntimeError(f"Failed to fetch messages from channel: {e}")
            return results

        return asyncio.run(_fetch())