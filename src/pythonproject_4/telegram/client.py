from telethon import TelegramClient, connection
from pythonproject_4.config import get_settings
from telethon.sessions import StringSession
import os


def get_telegram_client():
    settings = get_settings()
    session_file = "session.session"
    session = StringSession()
    if os.path.exists(session_file):
        with open(session_file, 'r', encoding='utf-8') as f:
            session_string = f.read().strip()
        if session_string:
            session = StringSession(session_string)

    client = TelegramClient(
        session,
        settings.TELEGRAM_API_ID,
        settings.TELEGRAM_API_HASH,
        connection=connection.ConnectionTcpMTProxyRandomizedIntermediate,
        proxy=('a09.mtjlpoto.fit', 443, 'eebf7996394f73fa1002a1a074aa22f717786170692e6f7a6f6e2e7275')
    )
    return client
