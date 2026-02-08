from enum import StrEnum
import uuid

from sqlalchemy import Boolean, DateTime, Enum, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class UserRole(StrEnum):
    USER = 'user'
    EDITOR = 'editor'
    ADMIN = 'admin'


class User(Base):
    __tablename__ = 'users'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name='userrole', values_callable=lambda enum_cls: [member.value for member in enum_cls]),
        default=UserRole.USER,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    prompts = relationship('Prompt', back_populates='author', foreign_keys='Prompt.author_id')
    reviewed_prompts = relationship('Prompt', back_populates='reviewer', foreign_keys='Prompt.reviewer_id')
    prompt_versions = relationship('PromptVersion', back_populates='creator')
    favorites = relationship('PromptFavorite', back_populates='user', cascade='all, delete-orphan')
    copy_events = relationship('PromptCopyEvent', back_populates='user')
    refresh_tokens = relationship('RefreshToken', back_populates='user', cascade='all, delete-orphan')
    audit_logs = relationship('AuditLog', back_populates='actor')
