"""Tests for models."""

from pythonproject_4.models import Source, NewsItem, Post


class TestModels:
    """Test SQLAlchemy model definitions."""

    def test_source_creation(self):
        source = Source(type="site", name="Test", url="https://example.com", enabled=True)
        assert source.type == "site"
        assert source.enabled is True

    def test_newsitem_creation(self):
        news = NewsItem(
            title="Test News",
            raw_text="Some content here",
            source_id=1,
        )
        assert news.title == "Test News"
        assert news.url is None  # Telegram news

    def test_post_creation(self):
        post = Post(news_item_id="00000000-0000-0000-0000-000000000001", status="new")
        assert post.status == "new"
        assert post.generated_text is None

    def test_post_status_transitions(self):
        """Test valid post status transitions."""
        post = Post(news_item_id="00000000-0000-0000-0000-000000000001", status="new")
        assert post.status == "new"

        post.status = "generated"
        post.generated_text = "Generated content"
        assert post.status == "generated"

        post.status = "published"
        assert post.status == "published"
