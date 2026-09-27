"""Authorization entry point.

Run with:
    python -m pythonproject_4.telegram.authorize
"""

from telethon import TelegramClient
from pythonproject_4.config import get_settings


def main():
    settings = get_settings()
    client = TelegramClient(
        settings.TELEGRAM_SESSION_PATH,
        settings.TELEGRAM_API_ID,
        settings.TELEGRAM_API_HASH,
    )

    print("=== Telegram Authorization ===")
    print(f"Session file: {settings.TELEGRAM_SESSION_PATH}")
    print()

    if client.is_user_authorized():
        print("Already authorized. Disconnecting...")
        client.disconnect()
        return

    print("Enter your phone number (with country code):")
    phone = input("> ").strip()

    print("Sending confirmation code...")
    client.start(phone=phone)

    print("Authorization successful! Session saved.")
    client.disconnect()


if __name__ == "__main__":
    main()
