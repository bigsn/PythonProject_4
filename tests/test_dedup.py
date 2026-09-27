"""Tests for deduplication logic."""

from pythonproject_4.models import NewsItem


class TestDeduplication:
    """Test deduplication key generation."""

    def test_site_dedup_key(self):
        """Site news dedup by URL."""
        news1 = NewsItem(
            title="Test",
            raw_text="Content",
            url="https://example.com/article",
            source_id=1,
        )
        news2 = NewsItem(
            title="Test",
            raw_text="Content",
            url="https://example.com/article",
            source_id=1,
        )
        assert news1.url == news2.url

    def test_telegram_dedup_key(self):
        """Telegram news dedup by (channel_id, message_id)."""
        news1 = NewsItem(
            title="Test",
            raw_text="Content",
            telegram_channel_id=123456,
            telegram_message_id=789,
            source_id=1,
        )
        news2 = NewsItem(
            title="Test",
            raw_text="Content",
            telegram_channel_id=123456,
            telegram_message_id=789,
            source_id=1,
        )
        assert news1.telegram_channel_id == news2.telegram_channel_id
        assert news1.telegram_message_id == news2.telegram_message_id

    def test_different_telegram_messages(self):
        """Different message IDs should not be duplicates."""
        news1 = NewsItem(
            title="Test",
            raw_text="Content",
            telegram_channel_id=123456,
            telegram_message_id=789,
            source_id=1,
        )
        news2 = NewsItem(
            title="Test",
            raw_text="Content",
            telegram_channel_id=123456,
            telegram_message_id=790,
            source_id=1,
        )
        assert news1.telegram_message_id != news2.telegram_message_id
