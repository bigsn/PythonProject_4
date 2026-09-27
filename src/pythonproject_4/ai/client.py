"""Async OpenAI client wrapper."""

import openai
from pythonproject_4.config import get_settings

_settings = None


def get_openai_client():
    """Get or create OpenAI async client."""
    global _settings
    if _settings is None:
        _settings = get_settings()
    return openai.AsyncOpenAI(api_key=_settings.OPENAI_API_KEY)


async def generate_post(text: str) -> str:
    """Generate a Telegram post from news text using OpenAI."""
    client = get_openai_client()
    settings = get_settings()

    prompt = (
        "Сделай краткое, интересное описание новости для Telegram-канала, "
        "добавь emoji, call to action.\n\n"
        f"News text:\n{text}"
    )

    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are a professional Telegram content creator."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=500,
    )

    generated = response.choices[0].message.content.strip()
    if not generated:
        raise ValueError("AI returned empty response")
    return generated
