"""Pydantic v2 request/response schemas."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
import re


# --- Source schemas ---

class SourceCreate(BaseModel):
    type: str = Field(..., pattern="^(site|telegram)$")
    name: str
    url: str
    enabled: bool = True

    @field_validator("url")
    @classmethod
    def validate_url_format(cls, v: str, info) -> str:
        if info.data.get("type") == "telegram":
            # Accept username or https://t.me/<username>
            username = v
            if v.startswith("https://t.me/"):
                username = v.split("/")[-1]
            if not re.match(r"^[a-zA-Z0-9_]{3,32}$", username):
                raise ValueError("Invalid Telegram username or link format")
        return v


class SourceUpdate(BaseModel):
    type: Optional[str] = None
    name: Optional[str] = None
    url: Optional[str] = None
    enabled: Optional[bool] = None


class SourceResponse(BaseModel):
    id: int
    type: str
    name: str
    url: str
    enabled: bool

    model_config = {"from_attributes": True}


# --- NewsItem schemas ---

class NewsItemResponse(BaseModel):
    id: UUID
    title: str
    url: Optional[str] = None
    telegram_channel_id: Optional[int] = None
    telegram_message_id: Optional[int] = None
    summary: Optional[str] = None
    raw_text: str
    source_id: int
    published_at: Optional[datetime] = None
    collected_at: datetime

    model_config = {"from_attributes": True}


# --- Post schemas ---

class PostResponse(BaseModel):
    id: int
    news_item_id: UUID
    generated_text: Optional[str] = None
    generated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    status: str
    last_error: Optional[str] = None

    model_config = {"from_attributes": True}


class GenerateRequest(BaseModel):
    news_id: UUID


class PublishResponse(BaseModel):
    post_id: int
