from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.audit_log import AuditLog
from app.models.prompt import Prompt, PromptStatus
from app.models.user import User, UserRole
from app.schemas.audit import AuditLogListResponse, AuditLogRead

router = APIRouter()


def _assert_admin(user: User) -> None:
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail='Admin only')


@router.get('/logs', response_model=AuditLogListResponse)
async def list_audit_logs(
    page: int = 1,
    page_size: int = 50,
    action: str | None = None,
    entity_type: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AuditLogListResponse:
    _assert_admin(current_user)

    page = max(1, page)
    page_size = max(1, min(page_size, 200))

    stmt = select(AuditLog)
    if action:
        stmt = stmt.where(AuditLog.action == action)
    if entity_type:
        stmt = stmt.where(AuditLog.entity_type == entity_type)

    stmt = stmt.order_by(desc(AuditLog.created_at))

    total_stmt = select(func.count()).select_from(stmt.subquery())
    total = int((await db.scalar(total_stmt)) or 0)

    items = (
        await db.scalars(stmt.offset((page - 1) * page_size).limit(page_size))
    ).all()

    return AuditLogListResponse(
        page=page,
        page_size=page_size,
        total=total,
        items=[AuditLogRead.model_validate(item) for item in items],
    )


@router.get('/review-queue')
async def review_queue(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    if current_user.role not in {UserRole.ADMIN, UserRole.EDITOR}:
        raise HTTPException(status_code=403, detail='Editor/Admin only')

    page = max(1, page)
    page_size = max(1, min(page_size, 100))

    stmt = (
        select(Prompt)
        .where(Prompt.status == PromptStatus.PENDING_REVIEW)
        .order_by(desc(Prompt.updated_at))
    )
    total_stmt = select(func.count()).select_from(stmt.subquery())
    total = int((await db.scalar(total_stmt)) or 0)

    rows = (await db.scalars(stmt.offset((page - 1) * page_size).limit(page_size))).all()

    return {
        'page': page,
        'page_size': page_size,
        'total': total,
        'items': [
            {
                'id': str(item.id),
                'title': item.title,
                'slug': item.slug,
                'author_id': str(item.author_id),
                'updated_at': item.updated_at,
            }
            for item in rows
        ],
    }
