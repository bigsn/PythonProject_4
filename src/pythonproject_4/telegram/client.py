"""Telethon client singleton manager."""

import os

from telethon import TelegramClient, connection
from telethon.sessions import StringSession
from pythonproject_4.config import get_settings

_client = None
_session = None


def get_telegram_client() -> TelegramClient:
    """Get or create a Telethon client. Must be called from within a task context."""
    global _client, _session
    
    if _client is None:
        settings = get_settings()
        
        # Load StringSession from file
        session_file = "session.session"
        if os.path.exists(session_file):
            with open(session_file, 'r', encoding='utf-8') as f:
                session_string = f.read().strip()
            if session_string:
                _session = StringSession(session_string)
        else:
            _session = StringSession()
        
        _client = TelegramClient(
            _session,
            settings.TELEGRAM_API_ID,
            settings.TELEGRAM_API_HASH,
            connection=connection.ConnectionTcpMTProxyRandomizedIntermediate,
            proxy=('a09.mtjlpoto.fit', 443, 'eebf7996394f73fa1002a1a074aa22f717786170692e6f7a6f6e2e7275')
#            proxy = ('surf.suslik-cloud.homes', 443, 'eed7f61466f824eafe116a533553e01bca737572662e7375736c696b2d636c6f75642e686f6d6573')
        )
    return _client


def close_telegram_client():
    """Close the Telethon client."""
    global _client
    if _client:
        _client.disconnect()
        _client = None

