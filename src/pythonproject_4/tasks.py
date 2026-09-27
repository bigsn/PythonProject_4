"""Celery tasks for news collection, AI generation, and publication."""

import asyncio
import logging
from datetime import datetime, timezone
from uuid import UUID

from celery import shared_task
from sqlalchemy.orm import Session

from pythonproject_4.db import SessionLocal
from pythonproject_4.models import Source, NewsItem, Post
from pythonproject_4.news_parser.telegram import TelegramNewsParser
from pythonproject_4.news_parser.sites import get_parser_for_url
from pythonproject_4.ai.generator import generate_post_for_news
from pythonproject_4.telegram.publisher import publish_post
from pythonproject_4.telegram.client import get_telegram_client

logger = logging.getLogger(__name__)


def _get_db():
    """Get a new database session."""
    return SessionLocal()


def _is_duplicate(db: Session, parsed: dict) -> bool:
    """Check if a news item already exists."""
    if parsed.get("url"):
        return db.query(NewsItem).filter(NewsItem.url == parsed["url"]).first() is not None
    elif parsed.get("telegram_channel_id") is not None and parsed.get("telegram_message_id") is not None:
        return (
            db.query(NewsItem)
            .filter(
                NewsItem.telegram_channel_id == parsed["telegram_channel_id"],
                NewsItem.telegram_message_id == parsed["telegram_message_id"],
            )
            .first()
            is not None
        )
    return False


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def collect_news_from_source(self, source_id: int):
    """Collect news from a single enabled source."""
    db = _get_db()
    try:
        source = db.query(Source).filter(Source.id == source_id).first()
        if not source or not source.enabled:
            logger.info(f"Source {source_id} not found or disabled, skipping")
            return

        logger.info(f"Collecting news from source {source.name} ({source.type})")

        if source.type == "telegram":
            parser = TelegramNewsParser()
            news_list = parser.parse(source.url)
        elif source.type == "site":
            parser = get_parser_for_url(source.url)
            if not parser:
                logger.warning(f"No parser found for URL {source.url}")
                return
            news_list = parser.parse(source.url)
        else:
            logger.error(f"Unknown source type: {source.type}")
            return

        saved_count = 0
        new_news_items = []
        for parsed in news_list:
            if not parsed.raw_text:
                continue

            # Dedup check
            if _is_duplicate(db, {
                "url": parsed.url,
                "telegram_channel_id": parsed.telegram_channel_id,
                "telegram_message_id": parsed.telegram_message_id,
            }):
                logger.info(f"Duplicate news skipped for source {source_id}")
                continue

            # Create NewsItem
            title = parsed.title or parsed.raw_text[:200].strip()
            news = NewsItem(
                title=title,
                url=parsed.url,
                telegram_channel_id=parsed.telegram_channel_id,
                telegram_message_id=parsed.telegram_message_id,
                summary=parsed.summary,
                raw_text=parsed.raw_text,
                source_id=source.id,
                published_at=parsed.published_at,
                collected_at=datetime.now(timezone.utc),
            )
            db.add(news)
            db.flush()  # Get the ID
            saved_count += 1
            new_news_items.append(news)

        db.commit()
        logger.info(f"Saved {saved_count} new news items from source {source.name}")

        # Trigger AI generation for each new item
        for news in new_news_items:
            trigger_generation.delay(news.id)

    except Exception as exc:
        db.rollback()
        logger.error(f"Error collecting from source {source_id}: {exc}")
        raise self.retry(exc=exc, countdown=60)
    finally:
        db.close()


@shared_task
def collect_all_enabled_sources():
    """Celery Beat task: collect news from all enabled sources."""
    db = _get_db()
    try:
        sources = db.query(Source).filter(Source.enabled == True).all()  # noqa: E712
        logger.info(f"Found {len(sources)} enabled sources")
        for source in sources:
            collect_news_from_source.delay(source.id)
    finally:
        db.close()


@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def trigger_generation(self, news_item_id: UUID):
    """Generate AI post for a news item."""
    db = _get_db()
    try:
        news_item = db.query(NewsItem).filter(NewsItem.id == news_item_id).first()
        if not news_item:
            logger.error(f"News item {news_item_id} not found")
            return

        # Check source is still enabled
        source = db.query(Source).filter(Source.id == news_item.source_id).first()
        if not source or not source.enabled:
            logger.info(f"Source {news_item.source_id} is disabled, skipping generation")
            return

        # Create Post with status "new"
        post = Post(
            news_item_id=news_item.id,
            status="new",
        )
        db.add(post)
        db.commit()
        db.refresh(post)

        logger.info(f"Created Post {post.id} for news {news_item_id}")

        # Async generation
        async def _do_generate():
            generated_text = await generate_post_for_news(news_item)
            post.generated_text = generated_text
            post.generated_at = datetime.now(timezone.utc)
            post.status = "generated"
            db.commit()
            logger.info(f"Successfully generated post {post.id}")

        asyncio.get_event_loop().run_until_complete(_do_generate())

    except Exception as exc:
        db.rollback()
        # Mark as generation_failed
        if "post" in dir():
            post.status = "generation_failed"
            post.last_error = str(exc)
            db.commit()
        logger.error(f"Generation failed for news {news_item_id}: {exc}")
        raise self.retry(exc=exc, countdown=30)
    finally:
        db.close()


@shared_task
def schedule_publication():
    """Celery Beat task: publish one generated post (HH:00 and HH:30 UTC)."""
    db = _get_db()
    try:
        # Select oldest generated post
        post = (
            db.query(Post)
            .filter(Post.status == "generated")
            .order_by(Post.generated_at.asc(), Post.id.asc())
            .first()
        )

        if not post:
            logger.info("No generated posts to publish")
            return

        logger.info(f"Publishing post {post.id}")
        _do_publish(db, post)

    except Exception as exc:
        db.rollback()
        logger.error(f"Error in schedule_publication: {exc}")
    finally:
        db.close()


def _do_publish(db: Session, post: Post) -> None:
    """Publish a single post. Used by both scheduled and manual tasks."""
    if post.status == "published":
        logger.info(f"Post {post.id} already published, skipping")
        return

    if post.status not in ("generated", "publication_failed"):
        logger.error(f"Cannot publish post {post.id} with status '{post.status}'")
        return

    try:
        client = get_telegram_client()
        settings = __import__("pythonproject_4.config", fromlist=["get_settings"]).get_settings()
        asyncio.get_event_loop().run_until_complete(
            publish_post(client, settings.TELEGRAM_TARGET_CHANNEL, post.generated_text)
        )
        post.status = "published"
        post.published_at = datetime.now(timezone.utc)
        db.commit()
        logger.info(f"Successfully published post {post.id}")
    except Exception as exc:
        post.status = "publication_failed"
        post.last_error = str(exc)
        db.commit()
        logger.error(f"Publication failed for post {post.id}: {exc}")
        raise


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def publish_post_manual(self, post_id: int):
    """Manual publication trigger via API."""
    db = _get_db()
    try:
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            logger.error(f"Post {post_id} not found")
            return

        if post.status == "published":
            logger.info(f"Post {post_id} already published")
            return

        if post.status not in ("generated", "publication_failed"):
            logger.error(f"Cannot publish post {post_id} with status '{post.status}'")
            return

        _do_publish(db, post)
    except Exception as exc:
        db.rollback()
        logger.error(f"Manual publication failed for post {post_id}: {exc}")
        raise self.retry(exc=exc, countdown=60)
    finally:
        db.close()
