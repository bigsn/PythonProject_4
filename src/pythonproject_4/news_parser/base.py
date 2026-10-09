"""Base parser interface and news dataclass."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class ParsedNews:
    """Parsed news item from any source."""
    title: str
    raw_text: str
    url: Optional[str] = None  # for sites
    telegram_channel_id: Optional[int] = None  # for Telegram
    telegram_message_id: Optional[int] = None  # for Telegram
    img_url: Optional[str] = None
    author: Optional[str] = None
    published_at: Optional[str] = None


class BaseParser(ABC):
    """Abstract base for all news parsers."""

    @abstractmethod
    def parse(self, source_url: str) -> List[ParsedNews]:
        """Parse and return list of news items from the given source."""
        ...
