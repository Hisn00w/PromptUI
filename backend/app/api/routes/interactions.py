from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_optional_user, is_admin_or_editor
from app.db.session import get_db
from app.models.prompt import Prompt, PromptStatus
from app.models.user import User
from app.models.user_interaction import PromptCopyEvent, PromptFavorite
from app.schemas.interaction import (
    CopyRecordRequest,
    FavoriteListResponse,
    FavoritePromptItem,
    FavoriteToggleResponse,
)
from app.services.audit import write_audit_log

router = APIRouter()


def _can_view_prompt(prompt: Prompt, user: User | None) -> bool:
    if prompt.status == PromptStatus.PUBLISHED:
        return True
    if not user:
        return False
    if is_admin_or_editor(user):
        return True
    return prompt.author_id == user.id


@router.post('/prompts/{prompt_id}/favorite', response_model=FavoriteToggleResponse)
async def toggle_favorite(
    prompt_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FavoriteToggleResponse:
    prompt = await db.get(Prompt, prompt_id)
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Prompt not found')

    if not _can_view_prompt(prompt, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Cannot favorite this prompt')

    favorite = await db.scalar(
        select(PromptFavorite).where(
            PromptFavorite.user_id == current_user.id,
            PromptFavorite.prompt_id == prompt_id,
        )
    )

    if favorite:
        await db.delete(favorite)
        is_favorite = False
        action = 'interaction.unfavorite'
    else:
        db.add(PromptFavorite(user_id=current_user.id, prompt_id=prompt_id))
        is_favorite = True
        action = 'interaction.favorite'

    await write_audit_log(
        db,
        actor_id=current_user.id,
        action=action,
        entity_type='prompt',
        entity_id=str(prompt_id),
    )

    await db.commit()

    return FavoriteToggleResponse(prompt_id=prompt_id, is_favorite=is_favorite)


@router.get('/favorites', response_model=FavoriteListResponse)
async def list_my_favorites(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FavoriteListResponse:
    page = max(page, 1)
    page_size = max(1, min(page_size, 100))

    base = (
        select(PromptFavorite, Prompt)
        .join(Prompt, Prompt.id == PromptFavorite.prompt_id)
        .where(PromptFavorite.user_id == current_user.id)
        .order_by(desc(PromptFavorite.created_at))
    )

    total_stmt = select(func.count()).select_from(base.subquery())
    total = int((await db.scalar(total_stmt)) or 0)

    rows = (await db.execute(base.offset((page - 1) * page_size).limit(page_size))).all()
    items = [
        FavoritePromptItem(
            prompt_id=row[1].id,
            title=row[1].title,
            slug=row[1].slug,
            tags=row[1].tags,
            status=row[1].status.value,
            favorited_at=row[0].created_at,
        )
        for row in rows
    ]

    return FavoriteListResponse(page=page, page_size=page_size, total=total, items=items)


@router.post('/prompts/{prompt_id}/copy', status_code=status.HTTP_201_CREATED)
async def record_copy_event(
    prompt_id: UUID,
    payload: CopyRecordRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
) -> dict:
    prompt = await db.get(Prompt, prompt_id)
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Prompt not found')

    if not _can_view_prompt(prompt, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Cannot copy this prompt')

    db.add(
        PromptCopyEvent(
            user_id=current_user.id if current_user else None,
            prompt_id=prompt_id,
            source=payload.source,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get('user-agent'),
            created_at=datetime.now(UTC),
        )
    )

    await write_audit_log(
        db,
        actor_id=current_user.id if current_user else None,
        action='interaction.copy',
        entity_type='prompt',
        entity_id=str(prompt_id),
        details={'source': payload.source},
    )

    await db.commit()
    return {'ok': True}
