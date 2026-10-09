"""AI generation orchestration."""

from pythonproject_4.ai.client import generate_post


async def generate_post_for_news(news_item) -> str:
    """Generate text for a news item. Uses summary if available, else raw_text."""
    input_text = news_item.raw_text
    return await generate_post(input_text)
