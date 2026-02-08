from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_optional_user, is_admin_or_editor
from app.db.session import get_db
from app.models.category import Category
from app.models.prompt import Prompt
from app.models.user import User, UserRole
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.services.audit import write_audit_log

router = APIRouter()


@router.get('', response_model=list[CategoryRead])
async def list_categories(
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
) -> list[CategoryRead]:
    stmt = select(Category).order_by(Category.name.asc())
    if not is_admin_or_editor(current_user):
        stmt = stmt.where(Category.is_active.is_(True))
    rows = (await db.scalars(stmt)).all()
    return [CategoryRead.model_validate(item) for item in rows]


@router.post('', response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CategoryRead:
    if current_user.role not in {UserRole.ADMIN, UserRole.EDITOR}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Insufficient permissions')

    exists = await db.scalar(select(Category).where((Category.key == payload.key) | (Category.name == payload.name)))
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Category key or name already exists')

    category = Category(**payload.model_dump())
    db.add(category)
    await db.flush()
    await write_audit_log(
        db,
        actor_id=current_user.id,
        action='category.create',
        entity_type='category',
        entity_id=str(category.id),
        details=payload.model_dump(),
    )
    await db.commit()
    await db.refresh(category)
    return CategoryRead.model_validate(category)


@router.patch('/{category_id}', response_model=CategoryRead)
async def update_category(
    category_id: UUID,
    payload: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CategoryRead:
    if current_user.role not in {UserRole.ADMIN, UserRole.EDITOR}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Insufficient permissions')

    category = await db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Category not found')

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(category, key, value)

    await write_audit_log(
        db,
        actor_id=current_user.id,
        action='category.update',
        entity_type='category',
        entity_id=str(category.id),
        details=data,
    )
    await db.commit()
    await db.refresh(category)
    return CategoryRead.model_validate(category)


@router.delete('/{category_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Admin only')

    category = await db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Category not found')

    prompt_count = await db.scalar(select(func.count()).select_from(Prompt).where(Prompt.category_id == category.id))
    if prompt_count:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Category is still used by prompts. Deactivate it instead.',
        )

    await write_audit_log(
        db,
        actor_id=current_user.id,
        action='category.delete',
        entity_type='category',
        entity_id=str(category.id),
        details={'name': category.name, 'key': category.key},
    )

    await db.delete(category)
    await db.commit()
