"""Tests for Pydantic schemas."""

import pytest
from pythonproject_4.schemas import SourceCreate


class TestSourceCreate:
    """Test SourceCreate schema validation."""

    def test_valid_site_source(self):
        source = SourceCreate(type="site", name="Habr", url="https://habr.com/", enabled=True)
        assert source.type == "site"
        assert source.name == "Habr"

    def test_valid_telegram_source(self):
        source = SourceCreate(type="telegram", name="Tech News", url="https://t.me/technews")
        assert source.type == "telegram"
        assert source.url == "https://t.me/technews"

    def test_invalid_telegram_username(self):
        with pytest.raises(ValueError):
            SourceCreate(type="telegram", name="Bad", url="ab")

    def test_invalid_type(self):
        with pytest.raises(ValueError):
            SourceCreate(type="invalid", name="Test", url="https://example.com")
