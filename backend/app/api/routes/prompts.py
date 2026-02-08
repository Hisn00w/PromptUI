import re
from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from redis.asyncio import Redis
from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_optional_user, get_user_or_anonymous, is_admin_or_editor
from app.core.redis import get_redis
from app.db.session import get_db
from app.models.category import Category
from app.models.prompt import Prompt, PromptStatus, PromptVersion
from app.models.user import User
from app.models.user_interaction import PromptCopyEvent, PromptFavorite
from app.schemas.prompt import (
    PromptCreate,
    PromptListItem,
    PromptListResponse,
    PromptPublishRequest,
    PromptRead,
    PromptStatusChangeRequest,
    PromptSubmitReview,
    PromptUpdate,
    PromptVersionRead,
)
from app.services.audit import write_audit_log
from app.services.cache import (
    build_prompt_list_cache_key,
    get_cached_prompt_list,
    invalidate_prompt_list_cache,
    set_cached_prompt_list,
)

router = APIRouter()


_slug_pattern = re.compile(r'[^a-z0-9]+')


def _slugify(text: str) -> str:
    value = text.strip().lower()
    value = _slug_pattern.sub('-', value).strip('-')
    return value or 'prompt'


async def _unique_slug(db: AsyncSession, title: str) -> str:
    base = _slugify(title)
    slug = base
    counter = 2
    while await db.scalar(select(Prompt.id).where(Prompt.slug == slug)):
        slug = f'{base}-{counter}'
        counter += 1
    return slug


def _can_view_prompt(prompt: Prompt, user: User | None) -> bool:
    if prompt.status == PromptStatus.PUBLISHED:
        return True
    if not user:
        return False
    if is_admin_or_editor(user):
        return True
    return prompt.author_id == user.id


def _can_edit_prompt(prompt: Prompt, user: User) -> bool:
    return is_admin_or_editor(user) or prompt.author_id == user.id


@router.get('', response_model=PromptListResponse)
async def list_prompts(
    q: str | None = Query(default=None, max_length=200),
    category_id: UUID | None = None,
    subcategory: str | None = Query(default=None, max_length=64),
    status_filter: PromptStatus | None = Query(default=None, alias='status'),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    sort_by: str = Query(default='updated_at'),
    sort_order: str = Query(default='desc', pattern='^(asc|desc)$'),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    current_user: User | None = Depends(get_optional_user),
) -> PromptListResponse:
    viewer_is_staff = is_admin_or_editor(current_user)

    cache_params = {
        'q': q,
        'category_id': str(category_id) if category_id else None,
        'status': status_filter.value if status_filter else None,
        'subcategory': subcategory,
        'page': page,
        'page_size': page_size,
        'sort_by': sort_by,
        'sort_order': sort_order,
        'viewer_role': current_user.role.value if current_user else 'anonymous',
    }

    use_cache = not viewer_is_staff and (not current_user or current_user.role.value == 'user')
    cache_key = build_prompt_list_cache_key(cache_params)

    if use_cache:
        cached = await get_cached_prompt_list(redis, cache_key)
        if cached:
            return PromptListResponse(**cached)

    favorite_count_subq = (
        select(func.count(PromptFavorite.id))
        .where(PromptFavorite.prompt_id == Prompt.id)
        .correlate(Prompt)
        .scalar_subquery()
    )
    copy_count_subq = (
        select(func.count(PromptCopyEvent.id))
        .where(PromptCopyEvent.prompt_id == Prompt.id)
        .correlate(Prompt)
        .scalar_subquery()
    )

    stmt = (
        select(
            Prompt, 
            favorite_count_subq.label('favorite_count'), 
            copy_count_subq.label('copy_count'),
            User.username.label('author_username'),
            Category.name.label('category_name')
        )
        .join(User, Prompt.author_id == User.id, isouter=True)
        .join(Category, Prompt.category_id == Category.id, isouter=True)
    )

    if q:
        q_like = f'%{q.strip()}%'
        stmt = stmt.where(or_(Prompt.title.ilike(q_like), Prompt.prompt_text.ilike(q_like)))

    if category_id:
        stmt = stmt.where(Prompt.category_id == category_id)
    if subcategory:
        stmt = stmt.where(Prompt.subcategory == subcategory)

    if viewer_is_staff:
        if status_filter:
            stmt = stmt.where(Prompt.status == status_filter)
    else:
        stmt = stmt.where(Prompt.status == PromptStatus.PUBLISHED)

    sort_mapping = {
        'created_at': Prompt.created_at,
        'updated_at': Prompt.updated_at,
        'published_at': Prompt.published_at,
        'title': Prompt.title,
    }
    sort_column = sort_mapping.get(sort_by, Prompt.updated_at)
    sort_direction = desc if sort_order == 'desc' else asc
    stmt = stmt.order_by(sort_direction(sort_column), desc(Prompt.created_at))

    total_stmt = select(func.count()).select_from(stmt.subquery())
    total = int((await db.scalar(total_stmt)) or 0)

    offset = (page - 1) * page_size
    rows = (await db.execute(stmt.offset(offset).limit(page_size))).all()

    items = [
        PromptListItem(
            id=row[0].id,
            slug=row[0].slug,
            title=row[0].title,
            title_en=row[0].title_en,
            prompt_text=row[0].prompt_text,
            tags=row[0].tags,
            tags_en=row[0].tags_en,
            subcategory=row[0].subcategory,
            preview_component=row[0].preview_component,
            code_assets=row[0].code_assets or {},
            has_code_assets=bool(row[0].code_assets),
            status=row[0].status,
            category_id=row[0].category_id,
            author_id=row[0].author_id,
            updated_at=row[0].updated_at,
            favorite_count=int(row[1] or 0),
            copy_count=int(row[2] or 0),
            author_username=row[3],
            category_name=row[4],
        )
        for row in rows
    ]

    response = PromptListResponse(page=page, page_size=page_size, total=total, items=items)

    if use_cache:
        await set_cached_prompt_list(redis, cache_key, response.model_dump(mode='json'))

    return response


@router.post('', response_model=PromptRead, status_code=status.HTTP_201_CREATED)
async def create_prompt(
    payload: PromptCreate,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    current_user: User = Depends(get_user_or_anonymous),
) -> PromptRead:
    category = await db.get(Category, payload.category_id)
    if not category or not category.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid category')

    prompt = Prompt(
        slug=await _unique_slug(db, payload.title),
        title=payload.title,
        title_en=payload.title_en,
        prompt_text=payload.prompt_text,
        tags=payload.tags,
        tags_en=payload.tags_en,
        subcategory=payload.subcategory,
        preview_component=payload.preview_component,
        code_assets=payload.code_assets,
        category_id=payload.category_id,
        author_id=current_user.id,
        status=PromptStatus.DRAFT,
        current_version=1,
    )
    db.add(prompt)
    await db.flush()

    db.add(
        PromptVersion(
            prompt_id=prompt.id,
            version_number=1,
            title=payload.title,
            title_en=payload.title_en,
            prompt_text=payload.prompt_text,
            tags=payload.tags,
            tags_en=payload.tags_en,
            subcategory=payload.subcategory,
            preview_component=payload.preview_component,
            code_assets=payload.code_assets,
            change_note='Initial draft',
            created_by=current_user.id,
        )
    )

    await write_audit_log(
        db,
        actor_id=current_user.id,
        action='prompt.create',
        entity_type='prompt',
        entity_id=str(prompt.id),
        details={'title': prompt.title, 'status': prompt.status.value},
    )

    await db.commit()
    await db.refresh(prompt)
    await invalidate_prompt_list_cache(redis)

    return PromptRead.model_validate(prompt)


@router.patch('/{prompt_id}', response_model=PromptRead)
async def update_prompt(
    prompt_id: UUID,
    payload: PromptUpdate,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user),
) -> PromptRead:
    prompt = await db.get(Prompt, prompt_id)
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Prompt not found')

    if not _can_edit_prompt(prompt, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not allowed to edit this prompt')

    data = payload.model_dump(exclude_unset=True)
    change_note = data.pop('change_note', None)

    if 'category_id' in data:
        category = await db.get(Category, data['category_id'])
        if not category or not category.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid category')

    changed = False
    for field, value in data.items():
        if getattr(prompt, field) != value:
            setattr(prompt, field, value)
            changed = True

    if changed:
        prompt.current_version += 1
        if not is_admin_or_editor(current_user) and prompt.status == PromptStatus.PUBLISHED:
            prompt.status = PromptStatus.PENDING_REVIEW

        db.add(
            PromptVersion(
                prompt_id=prompt.id,
                version_number=prompt.current_version,
                title=prompt.title,
                title_en=prompt.title_en,
                prompt_text=prompt.prompt_text,
                tags=prompt.tags,
                tags_en=prompt.tags_en,
                subcategory=prompt.subcategory,
                preview_component=prompt.preview_component,
                code_assets=prompt.code_assets,
                change_note=change_note or 'Content updated',
                created_by=current_user.id,
            )
        )

        await write_audit_log(
            db,
            actor_id=current_user.id,
            action='prompt.update',
            entity_type='prompt',
            entity_id=str(prompt.id),
            details={'changed_fields': list(data.keys()), 'status': prompt.status.value},
        )

        await db.commit()
        await db.refresh(prompt)
        await invalidate_prompt_list_cache(redis)

    return PromptRead.model_validate(prompt)


@router.post('/{prompt_id}/submit-review', response_model=PromptRead)
async def submit_prompt_for_review(
    prompt_id: UUID,
    payload: PromptSubmitReview,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PromptRead:
    prompt = await db.get(Prompt, prompt_id)
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Prompt not found')

    if not _can_edit_prompt(prompt, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not allowed')

    prompt.status = PromptStatus.PENDING_REVIEW
    prompt.review_comment = payload.comment

    await write_audit_log(
        db,
        actor_id=current_user.id,
        action='prompt.submit_review',
        entity_type='prompt',
        entity_id=str(prompt.id),
        details={'comment': payload.comment},
    )

    await db.commit()
    await db.refresh(prompt)
    return PromptRead.model_validate(prompt)


@router.post('/{prompt_id}/publish', response_model=PromptRead)
async def publish_prompt(
    prompt_id: UUID,
    payload: PromptPublishRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    current_user: User = Depends(get_user_or_anonymous),
) -> PromptRead:
    # 允许匿名用户发布（匿名用户已设置为 Editor 角色）

    prompt = await db.get(Prompt, prompt_id)
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Prompt not found')

    prompt.status = PromptStatus.PUBLISHED
    prompt.reviewer_id = current_user.id
    prompt.reviewed_at = datetime.now(UTC)
    prompt.published_at = datetime.now(UTC)
    prompt.review_comment = payload.comment

    await write_audit_log(
        db,
        actor_id=current_user.id,
        action='prompt.publish',
        entity_type='prompt',
        entity_id=str(prompt.id),
        details={'comment': payload.comment},
    )

    await db.commit()
    await db.refresh(prompt)
    await invalidate_prompt_list_cache(redis)

    return PromptRead.model_validate(prompt)


@router.post('/{prompt_id}/offline', response_model=PromptRead)
async def offline_prompt(
    prompt_id: UUID,
    payload: PromptStatusChangeRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user),
) -> PromptRead:
    if not is_admin_or_editor(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Editor/Admin only')

    prompt = await db.get(Prompt, prompt_id)
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Prompt not found')

    prompt.status = PromptStatus.OFFLINE
    prompt.reviewer_id = current_user.id
    prompt.reviewed_at = datetime.now(UTC)
    prompt.review_comment = payload.reason

    await write_audit_log(
        db,
        actor_id=current_user.id,
        action='prompt.offline',
        entity_type='prompt',
        entity_id=str(prompt.id),
        details={'reason': payload.reason},
    )

    await db.commit()
    await db.refresh(prompt)
    await invalidate_prompt_list_cache(redis)

    return PromptRead.model_validate(prompt)


@router.post('/{prompt_id}/rollback/{version_number}', response_model=PromptRead)
async def rollback_prompt_version(
    prompt_id: UUID,
    version_number: int,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user),
) -> PromptRead:
    prompt = await db.get(Prompt, prompt_id)
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Prompt not found')

    if not _can_edit_prompt(prompt, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not allowed')

    version = await db.scalar(
        select(PromptVersion).where(
            PromptVersion.prompt_id == prompt_id,
            PromptVersion.version_number == version_number,
        )
    )
    if not version:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Version not found')

    prompt.title = version.title
    prompt.title_en = version.title_en
    prompt.prompt_text = version.prompt_text
    prompt.tags = version.tags
    prompt.tags_en = version.tags_en
    prompt.subcategory = version.subcategory
    prompt.preview_component = version.preview_component
    prompt.code_assets = version.code_assets
    prompt.current_version += 1
    if not is_admin_or_editor(current_user):
        prompt.status = PromptStatus.PENDING_REVIEW

    db.add(
        PromptVersion(
            prompt_id=prompt.id,
            version_number=prompt.current_version,
            title=prompt.title,
            title_en=prompt.title_en,
            prompt_text=prompt.prompt_text,
            tags=prompt.tags,
            tags_en=prompt.tags_en,
            subcategory=prompt.subcategory,
            preview_component=prompt.preview_component,
            code_assets=prompt.code_assets,
            change_note=f'Rollback to version {version_number}',
            created_by=current_user.id,
        )
    )

    await write_audit_log(
        db,
        actor_id=current_user.id,
        action='prompt.rollback',
        entity_type='prompt',
        entity_id=str(prompt.id),
        details={'rollback_to': version_number, 'new_version': prompt.current_version},
    )

    await db.commit()
    await db.refresh(prompt)
    await invalidate_prompt_list_cache(redis)

    return PromptRead.model_validate(prompt)


@router.get('/{prompt_id}/versions', response_model=list[PromptVersionRead])
async def list_prompt_versions(
    prompt_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
) -> list[PromptVersionRead]:
    prompt = await db.get(Prompt, prompt_id)
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Prompt not found')

    if not _can_view_prompt(prompt, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not allowed to view versions')

    versions = (
        await db.scalars(
            select(PromptVersion)
            .where(PromptVersion.prompt_id == prompt_id)
            .order_by(PromptVersion.version_number.desc())
        )
    ).all()
    return [PromptVersionRead.model_validate(item) for item in versions]


@router.get('/{prompt_id}', response_model=PromptRead)
async def get_prompt(
    prompt_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
) -> PromptRead:
    prompt = await db.get(Prompt, prompt_id)
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Prompt not found')

    if not _can_view_prompt(prompt, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not allowed to view this prompt')

    return PromptRead.model_validate(prompt)
