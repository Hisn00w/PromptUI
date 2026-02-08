from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class FavoriteToggleResponse(BaseModel):
    prompt_id: UUID
    is_favorite: bool


class FavoritePromptItem(BaseModel):
    prompt_id: UUID
    title: str
    slug: str
    tags: list[str]
    status: str
    favorited_at: datetime


class FavoriteListResponse(BaseModel):
    page: int
    page_size: int
    total: int
    items: list[FavoritePromptItem]


class CopyRecordRequest(BaseModel):
    source: str = 'web'
