"""Create new StringSession for Telegram."""
import asyncio
import os

from telethon import TelegramClient, connection
from telethon.sessions import StringSession
from pythonproject_4.config import get_settings


async def create_session():
    """Create new StringSession and save to file."""
    settings = get_settings()

    session = StringSession()
    client = TelegramClient(
        session,
        settings.TELEGRAM_API_ID,
        settings.TELEGRAM_API_HASH,
        connection=connection.ConnectionTcpMTProxyRandomizedIntermediate,
        proxy=('a09.mtjlpoto.fit', 443, 'eebf7996394f73fa1002a1a074aa22f717786170692e6f7a6f6e2e7275')
    )
    
    try:
        await client.start()
        
        # Save session
        session_string = session.save()
        with open('session.session', 'w', encoding='utf-8') as f:
            f.write(session_string)
        
        print("\n✓ Session saved to session.session")
        print(f"Session length: {len(session_string)} characters")

    except Exception as e:
        print(f"\n✗ Error: {e}")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(create_session())
