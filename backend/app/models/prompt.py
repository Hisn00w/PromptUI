from enum import StrEnum
import uuid

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class PromptStatus(StrEnum):
    DRAFT = 'draft'
    PENDING_REVIEW = 'pending_review'
    PUBLISHED = 'published'
    OFFLINE = 'offline'


class Prompt(Base):
    __tablename__ = 'prompts'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    title_en: Mapped[str | None] = mapped_column(String(255), nullable=True)
    prompt_text: Mapped[str] = mapped_column(Text)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String(64)), default=list)
    tags_en: Mapped[list[str]] = mapped_column(ARRAY(String(64)), default=list)
    subcategory: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    preview_component: Mapped[str | None] = mapped_column(String(128), nullable=True)
    code_assets: Mapped[dict] = mapped_column(JSONB, default=dict)
    status: Mapped[PromptStatus] = mapped_column(
        Enum(PromptStatus, name='promptstatus', values_callable=lambda enum_cls: [member.value for member in enum_cls]),
        default=PromptStatus.DRAFT,
        index=True,
    )
    current_version: Mapped[int] = mapped_column(Integer, default=1)

    category_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('categories.id', ondelete='RESTRICT'), index=True)
    author_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), index=True)
    reviewer_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    review_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    published_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    category = relationship('Category', back_populates='prompts')
    author = relationship('User', back_populates='prompts', foreign_keys=[author_id])
    reviewer = relationship('User', back_populates='reviewed_prompts', foreign_keys=[reviewer_id])
    versions = relationship('PromptVersion', back_populates='prompt', cascade='all, delete-orphan', order_by='PromptVersion.version_number')
    favorites = relationship('PromptFavorite', back_populates='prompt', cascade='all, delete-orphan')
    copy_events = relationship('PromptCopyEvent', back_populates='prompt', cascade='all, delete-orphan')


class PromptVersion(Base):
    __tablename__ = 'prompt_versions'
    __table_args__ = (UniqueConstraint('prompt_id', 'version_number', name='uq_prompt_version_number'),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prompt_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('prompts.id', ondelete='CASCADE'), index=True)
    version_number: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(255))
    title_en: Mapped[str | None] = mapped_column(String(255), nullable=True)
    prompt_text: Mapped[str] = mapped_column(Text)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String(64)), default=list)
    tags_en: Mapped[list[str]] = mapped_column(ARRAY(String(64)), default=list)
    subcategory: Mapped[str | None] = mapped_column(String(64), nullable=True)
    preview_component: Mapped[str | None] = mapped_column(String(128), nullable=True)
    code_assets: Mapped[dict] = mapped_column(JSONB, default=dict)
    change_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True
    )
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    prompt = relationship('Prompt', back_populates='versions')
    creator = relationship('User', back_populates='prompt_versions')
