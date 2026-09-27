"""SQLAlchemy ORM models for AINEWS."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


class Source(Base):
    """News source (website or Telegram channel)."""

    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String, nullable=False)  # 'site' or 'telegram'
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    enabled = Column(Boolean, default=True, nullable=False)

    news_items = relationship("NewsItem", back_populates="source", cascade="all, delete-orphan")


class NewsItem(Base):
    """Collected news item from a source."""

    __tablename__ = "news_items"
    __table_args__ = (
        UniqueConstraint("url", name="uq_news_items_url"),
        UniqueConstraint(
            "telegram_channel_id", "telegram_message_id",
            name="uq_news_items_telegram_pair"
        ),
        Index("ix_news_items_source_id", "source_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    url = Column(String, nullable=True)  # null for Telegram
    telegram_channel_id = Column(Integer, nullable=True)  # null for site
    telegram_message_id = Column(Integer, nullable=True)  # null for site
    summary = Column(String, nullable=True)
    raw_text = Column(Text, nullable=False)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=True)
    collected_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    source = relationship("Source", back_populates="news_items")
    posts = relationship("Post", back_populates="news_item")


class Post(Base):
    """Generated post awaiting or having been published."""

    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    news_item_id = Column(UUID(as_uuid=True), ForeignKey("news_items.id"), nullable=False)
    generated_text = Column(Text, nullable=True)
    generated_at = Column(DateTime(timezone=True), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, nullable=False, default="new")
    last_error = Column(String, nullable=True)

    news_item = relationship("NewsItem", back_populates="posts")
