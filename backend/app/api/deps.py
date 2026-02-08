from typing import Annotated, Callable
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import TokenPayloadError, decode_token
from app.db.session import get_db
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f'{settings.api_prefix}/auth/login')


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
    )
    try:
        payload = decode_token(token, expected_type='access')
        user_id = payload.get('sub')
    except TokenPayloadError as exc:
        raise credentials_exception from exc

    user = await db.get(User, UUID(user_id))
    if not user or not user.is_active:
        raise credentials_exception
    return user


async def get_optional_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    authorization: Annotated[str | None, Header(alias='Authorization')] = None,
) -> User | None:
    if not authorization:
        return None

    if not authorization.lower().startswith('bearer '):
        return None

    token = authorization.split(' ', 1)[1].strip()
    try:
        payload = decode_token(token, expected_type='access')
        user_id = payload.get('sub')
    except TokenPayloadError:
        return None

    try:
        user_uuid = UUID(user_id)
    except (ValueError, TypeError):
        return None

    user = await db.scalar(select(User).where(User.id == user_uuid, User.is_active.is_(True)))
    return user


def require_roles(*roles: UserRole) -> Callable:
    async def _dependency(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if current_user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Insufficient permissions')
        return current_user

    return _dependency


def is_admin_or_editor(user: User | None) -> bool:
    if not user:
        return False
    return user.role in {UserRole.ADMIN, UserRole.EDITOR}


# 匿名用户的固定 ID 和信息
ANONYMOUS_USER_EMAIL = 'anonymous@promptui.local'
ANONYMOUS_USER_NAME = 'anonymous'


async def get_or_create_anonymous_user(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """获取或创建匿名用户，用于无需登录的操作"""
    user = await db.scalar(select(User).where(User.email == ANONYMOUS_USER_EMAIL))
    if user:
        return user
    
    # 创建匿名用户
    user = User(
        email=ANONYMOUS_USER_EMAIL,
        username=ANONYMOUS_USER_NAME,
        hashed_password='$2b$12$anonymous.hash.not.usable',
        role=UserRole.EDITOR,  # 给予 Editor 权限以便发布
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_or_anonymous(
    db: Annotated[AsyncSession, Depends(get_db)],
    authorization: Annotated[str | None, Header(alias='Authorization')] = None,
) -> User:
    """尝试获取已登录用户，否则返回匿名用户"""
    if authorization and authorization.lower().startswith('bearer '):
        token = authorization.split(' ', 1)[1].strip()
        try:
            payload = decode_token(token, expected_type='access')
            user_id = payload.get('sub')
            user = await db.get(User, UUID(user_id))
            if user and user.is_active:
                return user
        except (TokenPayloadError, ValueError, TypeError):
            pass
    
    # 返回匿名用户
    return await get_or_create_anonymous_user(db)
