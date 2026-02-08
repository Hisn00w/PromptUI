from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.prompt import PromptStatus


class PromptCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    title_en: str | None = Field(default=None, max_length=255)
    prompt_text: str = Field(min_length=1)
    tags: list[str] = Field(default_factory=list)
    tags_en: list[str] = Field(default_factory=list)
    subcategory: str | None = Field(default=None, max_length=64)
    preview_component: str | None = Field(default=None, max_length=128)
    code_assets: dict[str, Any] = Field(default_factory=dict)
    category_id: UUID


class PromptUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    title_en: str | None = Field(default=None, max_length=255)
    prompt_text: str | None = Field(default=None, min_length=1)
    tags: list[str] | None = None
    tags_en: list[str] | None = None
    subcategory: str | None = Field(default=None, max_length=64)
    preview_component: str | None = Field(default=None, max_length=128)
    code_assets: dict[str, Any] | None = None
    category_id: UUID | None = None
    change_note: str | None = None


class PromptSubmitReview(BaseModel):
    comment: str | None = None


class PromptPublishRequest(BaseModel):
    comment: str | None = None


class PromptStatusChangeRequest(BaseModel):
    reason: str | None = None


class PromptVersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    prompt_id: UUID
    version_number: int
    title: str
    title_en: str | None
    prompt_text: str
    tags: list[str]
    tags_en: list[str]
    subcategory: str | None
    preview_component: str | None
    code_assets: dict[str, Any]
    change_note: str | None
    created_by: UUID | None
    created_at: datetime


class PromptRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    title: str
    title_en: str | None
    prompt_text: str
    tags: list[str]
    tags_en: list[str]
    subcategory: str | None
    preview_component: str | None
    code_assets: dict[str, Any]
    status: PromptStatus
    current_version: int
    category_id: UUID
    author_id: UUID
    reviewer_id: UUID | None
    review_comment: str | None
    reviewed_at: datetime | None
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime


class PromptListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    title: str
    title_en: str | None
    prompt_text: str
    tags: list[str]
    tags_en: list[str]
    subcategory: str | None
    preview_component: str | None
    code_assets: dict[str, Any] = Field(default_factory=dict)
    has_code_assets: bool = False
    status: PromptStatus
    category_id: UUID
    author_id: UUID
    updated_at: datetime
    favorite_count: int = 0
    copy_count: int = 0
    
    # 关联数据
    author_username: str | None = None
    category_name: str | None = None


class PromptListResponse(BaseModel):
    page: int
    page_size: int
    total: int
    items: list[PromptListItem]
