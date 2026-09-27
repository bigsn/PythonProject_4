"""Post publishing via Telethon."""

import asyncio
from telethon import TelegramClient
from pythonproject_4.config import get_settings


async def publish_post(client: TelegramClient, target_channel: str, text: str) -> None:
    """Send a post to the target Telegram channel."""
    entity = await client.get_entity(target_channel)
    await client.send_message(entity, text)
