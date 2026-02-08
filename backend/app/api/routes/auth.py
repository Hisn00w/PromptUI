from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.security import (
    TokenPayloadError,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.db.session import get_db
from app.models.refresh_token import RefreshToken
from app.models.user import User, UserRole
from app.schemas.auth import AuthResponse, RefreshRequest, TokenPair, UserLogin, UserRead, UserRegister
from app.services.audit import write_audit_log

router = APIRouter()


def _build_tokens(user: User) -> TokenPair:
    access = create_access_token(subject=str(user.id), role=user.role.value)
    refresh, _ = create_refresh_token(subject=str(user.id))
    return TokenPair(
        access_token=access,
        refresh_token=refresh,
        expires_in=settings.access_token_expire_minutes * 60,
    )


async def _has_admin(db: AsyncSession) -> bool:
    """检查是否存在管理员账号"""
    admin_count = await db.scalar(
        select(func.count()).select_from(User).where(User.role == UserRole.ADMIN)
    )
    return admin_count > 0


@router.get('/status')
async def auth_status(db: AsyncSession = Depends(get_db)) -> dict:
    """返回系统状态，包括是否需要初始化管理员"""
    has_admin = await _has_admin(db)
    return {
        'needs_admin_setup': not has_admin,
        'has_admin': has_admin,
    }


@router.post('/register', response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: UserRegister,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    # 如果没有提供邮箱，自动生成一个
    email = payload.email.lower() if payload.email else f"{payload.username}@example.com"
    
    existing = await db.scalar(
        select(User).where(or_(User.email == email, User.username == payload.username))
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Email or username already in use')

    # 如果没有管理员，新用户自动成为管理员
    has_admin = await _has_admin(db)
    user_role = UserRole.USER if has_admin else UserRole.ADMIN

    user = User(
        email=email,
        username=payload.username,
        hashed_password=get_password_hash(payload.password),
        role=user_role,
    )
    db.add(user)
    await db.flush()

    refresh_token, jti = create_refresh_token(subject=str(user.id))
    expires_at = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
    db.add(
        RefreshToken(
            user_id=user.id,
            jti=jti,
            expires_at=expires_at,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get('user-agent'),
        )
    )

    await write_audit_log(
        db,
        actor_id=user.id,
        action='auth.register',
        entity_type='user',
        entity_id=str(user.id),
        details={'email': user.email},
    )

    await db.commit()
    await db.refresh(user)

    access_token = create_access_token(subject=str(user.id), role=user.role.value)
    return AuthResponse(
        user=UserRead.model_validate(user),
        tokens=TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.access_token_expire_minutes * 60,
        ),
    )


@router.post('/login', response_model=AuthResponse)
async def login(payload: UserLogin, request: Request, db: AsyncSession = Depends(get_db)) -> AuthResponse:
    account = payload.username.strip()
    user = await db.scalar(
        select(User).where(
            or_(
                User.username == account,
                User.email == account.lower(),
            )
        )
    )
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid account or password')

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User is inactive')

    access_token = create_access_token(subject=str(user.id), role=user.role.value)
    refresh_token, jti = create_refresh_token(subject=str(user.id))

    db.add(
        RefreshToken(
            user_id=user.id,
            jti=jti,
            expires_at=datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get('user-agent'),
        )
    )

    await write_audit_log(
        db,
        actor_id=user.id,
        action='auth.login',
        entity_type='user',
        entity_id=str(user.id),
    )
    await db.commit()

    return AuthResponse(
        user=UserRead.model_validate(user),
        tokens=TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.access_token_expire_minutes * 60,
        ),
    )


@router.post('/refresh', response_model=TokenPair)
async def refresh_tokens(payload: RefreshRequest, db: AsyncSession = Depends(get_db)) -> TokenPair:
    try:
        token_payload = decode_token(payload.refresh_token, expected_type='refresh')
    except TokenPayloadError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid refresh token') from exc

    jti = token_payload.get('jti')
    user_id = token_payload.get('sub')

    if not jti or not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid refresh token payload')

    user_uuid = UUID(user_id)

    token_row = await db.scalar(
        select(RefreshToken).where(
            RefreshToken.jti == jti,
            RefreshToken.user_id == user_uuid,
            RefreshToken.revoked_at.is_(None),
            RefreshToken.expires_at > datetime.now(UTC),
        )
    )
    if not token_row:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Refresh token revoked or expired')

    user = await db.get(User, user_uuid)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not available')

    token_row.revoked_at = datetime.now(UTC)

    new_access = create_access_token(subject=str(user.id), role=user.role.value)
    new_refresh, new_jti = create_refresh_token(subject=str(user.id))
    db.add(
        RefreshToken(
            user_id=user.id,
            jti=new_jti,
            expires_at=datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days),
        )
    )

    await write_audit_log(
        db,
        actor_id=user.id,
        action='auth.refresh',
        entity_type='user',
        entity_id=str(user.id),
    )
    await db.commit()

    return TokenPair(
        access_token=new_access,
        refresh_token=new_refresh,
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post('/logout')
async def logout(payload: RefreshRequest, db: AsyncSession = Depends(get_db)) -> dict:
    try:
        token_payload = decode_token(payload.refresh_token, expected_type='refresh')
    except TokenPayloadError:
        return {'message': 'ok'}

    jti = token_payload.get('jti')
    if jti:
        token_row = await db.scalar(select(RefreshToken).where(RefreshToken.jti == jti))
        if token_row and token_row.revoked_at is None:
            token_row.revoked_at = datetime.now(UTC)
            await db.commit()

    return {'message': 'ok'}


@router.get('/me', response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)
