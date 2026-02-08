import uuid

from sqlalchemy import DateTime, ForeignKey, Index, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class PromptFavorite(Base):
    __tablename__ = 'prompt_favorites'
    __table_args__ = (UniqueConstraint('user_id', 'prompt_id', name='uq_user_prompt_favorite'),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), index=True)
    prompt_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('prompts.id', ondelete='CASCADE'), index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship('User', back_populates='favorites')
    prompt = relationship('Prompt', back_populates='favorites')


class PromptCopyEvent(Base):
    __tablename__ = 'prompt_copy_events'
    __table_args__ = (Index('ix_prompt_copy_events_prompt_created', 'prompt_id', 'created_at'),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    prompt_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('prompts.id', ondelete='CASCADE'), index=True)
    source: Mapped[str] = mapped_column(String(32), default='web')
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship('User', back_populates='copy_events')
    prompt = relationship('Prompt', back_populates='copy_events')
