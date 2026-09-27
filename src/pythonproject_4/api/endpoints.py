"""REST API endpoints for AINEWS."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from pythonproject_4.db import get_db
from pythonproject_4.models import Source, NewsItem, Post
from pythonproject_4.schemas import (
    SourceCreate,
    SourceUpdate,
    SourceResponse,
    NewsItemResponse,
    PostResponse,
    GenerateRequest,
    PublishResponse,
)
from pythonproject_4.tasks import collect_all_enabled_sources, trigger_generation, publish_post_manual

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")


# --- Source endpoints ---

@router.get("/sources/", response_model=list[SourceResponse])
def list_sources(db: Session = Depends(get_db)):
    """List all news sources."""
    sources = db.query(Source).all()
    return sources


@router.post("/sources/", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
def create_source(source_data: SourceCreate, db: Session = Depends(get_db)):
    """Create a new news source."""
    # Validate URL format based on type
    if source_data.type == "telegram":
        username = source_data.url
        if source_data.url.startswith("https://t.me/"):
            username = source_data.url.split("/")[-1]
        if not __import__("re").match(r"^[a-zA-Z0-9_]{3,32}$", username):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid Telegram username or link format"
            )

    source = Source(
        type=source_data.type,
        name=source_data.name,
        url=source_data.url,
        enabled=source_data.enabled,
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


@router.get("/sources/{source_id}/", response_model=SourceResponse)
def get_source(source_id: int, db: Session = Depends(get_db)):
    """Get a source by ID."""
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")
    return source


@router.patch("/sources/{source_id}/", response_model=SourceResponse)
def update_source(source_id: int, source_data: SourceUpdate, db: Session = Depends(get_db)):
    """Update a source (including enabled status)."""
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")

    update_dict = source_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(source, field, value)

    db.commit()
    db.refresh(source)
    return source


@router.delete("/sources/{source_id}/", status_code=status.HTTP_204_NO_CONTENT)
def delete_source(source_id: int, db: Session = Depends(get_db)):
    """Delete a source (only if no news items exist)."""
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")

    if source.news_items:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete source with existing news items. Disable it instead."
        )

    db.delete(source)
    db.commit()


# --- News endpoints ---

@router.get("/news/", response_model=list[NewsItemResponse])
def list_news(db: Session = Depends(get_db)):
    """List all collected news items."""
    news = db.query(NewsItem).all()
    return news


# --- Post endpoints ---

@router.get("/posts/", response_model=list[PostResponse])
def list_posts(db: Session = Depends(get_db)):
    """List all posts with their status."""
    posts = db.query(Post).all()
    return posts


@router.get("/posts/{post_id}/", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """Get a post by ID with generated text and status."""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@router.post("/parse/", status_code=status.HTTP_202_ACCEPTED)
def trigger_parse():
    """Manually trigger news collection from all enabled sources."""
    task = collect_all_enabled_sources.delay()
    return {"task_id": task.id}


@router.post("/generate/", status_code=status.HTTP_202_ACCEPTED)
def trigger_generate(request: GenerateRequest, db: Session = Depends(get_db)):
    """Manually generate AI post for a news item."""
    news_item = db.query(NewsItem).filter(NewsItem.id == request.news_id).first()
    if not news_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="News item not found")

    # Check source is enabled
    source = db.query(Source).filter(Source.id == news_item.source_id).first()
    if not source or not source.enabled:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Source is disabled. Cannot generate post."
        )

    task = trigger_generation.delay(request.news_id)
    # Find the created post ID
    post = db.query(Post).filter(Post.news_item_id == request.news_id).order_by(Post.id.desc()).first()
    return {"post_id": post.id} if post else {"task_id": task.id}


@router.post("/posts/{post_id}/publish/", response_model=dict)
def trigger_publish(post_id: int, db: Session = Depends(get_db)):
    """Manually publish a post."""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if post.status == "published":
        return {"post_id": post.id, "status": "already_published"}

    if post.status in ("new", "generation_failed"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot publish post with status '{post.status}'. Generate it first."
        )

    task = publish_post_manual.delay(post_id)
    return {"post_id": post.id, "task_id": task.id}
