import base64
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import and_, desc, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.cache import cache_get, cache_set, invalidate_post
from app.db import get_db
from app.media_services import link_media_to_post
from app.models import Category, Post, PostRevision, PostStatus, Tag, User, UserRole
from app.schemas import PostCreate, PostList, PostRead, PostUpdate
from app.security import get_current_user, require_roles

router = APIRouter(prefix="/posts", tags=["posts"])


def encode_cursor(post: Post) -> str:
    value = f"{(post.published_at or post.created_at).isoformat()}|{post.id}"
    return base64.urlsafe_b64encode(value.encode()).decode()


def encode_manage_cursor(post: Post) -> str:
    value = f"{post.updated_at.isoformat()}|{post.id}"
    return base64.urlsafe_b64encode(value.encode()).decode()


def decode_cursor(cursor: str) -> tuple[datetime, int]:
    try:
        raw = base64.urlsafe_b64decode(cursor.encode()).decode()
        timestamp, post_id = raw.split("|", 1)
        return datetime.fromisoformat(timestamp), int(post_id)
    except (ValueError, TypeError, UnicodeDecodeError) as exc:
        raise HTTPException(status_code=400, detail="Invalid cursor") from exc


async def set_taxonomy(post: Post, category_ids: list[int], tag_ids: list[int], db: AsyncSession) -> None:
    post.categories = list((await db.scalars(select(Category).where(Category.id.in_(category_ids)))).all()) if category_ids else []
    post.tags = list((await db.scalars(select(Tag).where(Tag.id.in_(tag_ids)))).all()) if tag_ids else []


@router.get("", response_model=PostList)
async def list_posts(request: Request, cursor: str | None = None, limit: int = Query(20, ge=1, le=100), category: str | None = None, tag: str | None = None, db: AsyncSession = Depends(get_db)) -> PostList:
    cache_key = f"posts:list:{cursor}:{limit}:{category}:{tag}"
    cached = await cache_get(cache_key)
    if cached:
        return PostList.model_validate(cached)
    position = decode_cursor(cursor) if cursor else None
    query = select(Post).options(selectinload(Post.author), selectinload(Post.categories), selectinload(Post.tags)).where(Post.status == PostStatus.PUBLISHED)
    if category:
        query = query.join(Post.categories).where(Category.slug == category)
    if tag:
        query = query.join(Post.tags).where(Tag.slug == tag)
    if position:
        timestamp, post_id = position
        query = query.where(or_(Post.published_at < timestamp, and_(Post.published_at == timestamp, Post.id < post_id)))
    query = query.order_by(desc(Post.published_at), desc(Post.id)).limit(limit + 1)
    posts = list((await db.scalars(query)).unique().all())
    next_cursor = encode_cursor(posts.pop()) if len(posts) > limit else None
    result = PostList(items=posts, next_cursor=next_cursor)
    await cache_set(cache_key, result.model_dump(mode="json"), 75)
    return result


@router.get("/manage", response_model=PostList)
async def list_manage_posts(cursor: str | None = None, limit: int = Query(20, ge=1, le=100), post_status: PostStatus | None = Query(default=None, alias="status"), db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)) -> PostList:
    position = decode_cursor(cursor) if cursor else None
    query = select(Post).options(selectinload(Post.author), selectinload(Post.categories), selectinload(Post.tags))
    if user.role == UserRole.AUTHOR:
        query = query.where(Post.author_id == user.id)
    if post_status:
        query = query.where(Post.status == post_status)
    if position:
        timestamp, post_id = position
        query = query.where(or_(Post.updated_at < timestamp, and_(Post.updated_at == timestamp, Post.id < post_id)))
    query = query.order_by(desc(Post.updated_at), desc(Post.id)).limit(limit + 1)
    posts = list((await db.scalars(query)).unique().all())
    next_cursor = encode_manage_cursor(posts.pop()) if len(posts) > limit else None
    items = [PostRead.model_validate(post).model_copy(update={"author_name": post.author.name}) for post in posts]
    return PostList(items=items, next_cursor=next_cursor)


@router.get("/manage/{post_id}", response_model=PostRead)
async def get_manage_post(post_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(require_roles(UserRole.ADMIN, UserRole.EDITOR, UserRole.AUTHOR))) -> PostRead:
    post = await db.scalar(select(Post).options(selectinload(Post.author), selectinload(Post.categories), selectinload(Post.tags)).where(Post.id == post_id))
    if not post or (user.role == UserRole.AUTHOR and post.author_id != user.id):
        raise HTTPException(status_code=404, detail="Post not found")
    return PostRead.model_validate(post).model_copy(update={"author_name": post.author.name})


@router.get("/breaking", response_model=list[PostRead])
async def breaking_posts(db: AsyncSession = Depends(get_db)) -> list[Post]:
    cached = await cache_get("posts:breaking")
    if cached:
        return [PostRead.model_validate(item) for item in cached]
    posts = list((await db.scalars(select(Post).options(selectinload(Post.author), selectinload(Post.categories), selectinload(Post.tags)).where(Post.status == PostStatus.PUBLISHED, Post.is_breaking.is_(True)).order_by(desc(Post.published_at), desc(Post.id)))).all())
    await cache_set("posts:breaking", [PostRead.model_validate(post).model_dump(mode="json") for post in posts], 60)
    return posts


@router.get("/{slug}", response_model=PostRead)
async def get_post(slug: str, db: AsyncSession = Depends(get_db)) -> Post:
    cached = await cache_get(f"post:{slug}")
    if cached:
        return PostRead.model_validate(cached)
    post = await db.scalar(select(Post).options(selectinload(Post.author), selectinload(Post.categories), selectinload(Post.tags)).where(Post.slug == slug, Post.status == PostStatus.PUBLISHED))
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    await cache_set(f"post:{slug}", PostRead.model_validate(post).model_dump(mode="json"), 120)
    return post


@router.post("", response_model=PostRead, status_code=status.HTTP_201_CREATED)
async def create_post(payload: PostCreate, db: AsyncSession = Depends(get_db), user: User = Depends(require_roles(UserRole.ADMIN, UserRole.EDITOR, UserRole.AUTHOR))) -> Post:
    existing = await db.scalar(select(Post.id).where(Post.slug == payload.slug))
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A post with this slug already exists")

    post = Post(title=payload.title, slug=payload.slug, dek=payload.dek, body=payload.body, is_breaking=payload.is_breaking, author_id=user.id)
    await set_taxonomy(post, payload.category_ids, payload.tag_ids, db)
    db.add(post)
    await db.flush()
    try:
        await link_media_to_post(db, post_id=post.id, body=post.body, uploaded_by=user.id)
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        if "posts_slug_key" in str(exc.orig):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A post with this slug already exists") from exc
        raise
    await db.refresh(post, attribute_names=["author", "categories", "tags", "updated_at"])
    return post


@router.patch("/{post_id}", response_model=PostRead)
async def update_post(post_id: int, payload: PostUpdate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)) -> Post:
    post = await db.scalar(
        select(Post)
        .options(selectinload(Post.categories), selectinload(Post.tags))
        .where(Post.id == post_id)
    )
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    can_edit = user.role in {UserRole.ADMIN, UserRole.EDITOR} or (user.role == UserRole.AUTHOR and post.author_id == user.id and post.status == PostStatus.DRAFT)
    if not can_edit:
        raise HTTPException(status_code=403, detail="You cannot edit this post")
    old_slug = post.slug
    db.add(PostRevision(post_id=post.id, body_snapshot=post.body, edited_by=user.id))
    changes = payload.model_dump(exclude_unset=True, exclude={"category_ids", "tag_ids"})
    for key, value in changes.items():
        setattr(post, key, value)
    if payload.category_ids is not None or payload.tag_ids is not None:
        await set_taxonomy(post, payload.category_ids or [], payload.tag_ids or [], db)
    post.editor_id = user.id
    await link_media_to_post(db, post_id=post.id, body=post.body, uploaded_by=user.id)
    await db.commit()
    await db.refresh(post, attribute_names=["author", "categories", "tags", "updated_at"])
    await invalidate_post(post.id, old_slug)
    return post


@router.post("/{post_id}/publish", response_model=PostRead)
async def publish_post(post_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(require_roles(UserRole.ADMIN, UserRole.EDITOR))) -> Post:
    if not (post := await db.get(Post, post_id)):
        raise HTTPException(status_code=404, detail="Post not found")
    post.status = PostStatus.PUBLISHED
    post.published_at = datetime.now(UTC)
    post.editor_id = user.id
    await db.commit()
    await db.refresh(post, attribute_names=["author", "categories", "tags", "updated_at"])
    await invalidate_post(post.id, post.slug)
    return post


@router.post("/{post_id}/schedule", response_model=PostRead)
async def schedule_post(post_id: int, published_at: datetime, db: AsyncSession = Depends(get_db), user: User = Depends(require_roles(UserRole.ADMIN, UserRole.EDITOR))) -> Post:
    if published_at.tzinfo is None:
        raise HTTPException(status_code=422, detail="published_at must include a timezone")
    if not (post := await db.get(Post, post_id)):
        raise HTTPException(status_code=404, detail="Post not found")
    post.status, post.published_at, post.editor_id = PostStatus.SCHEDULED, published_at, user.id
    await db.commit()
    await db.refresh(post, attribute_names=["author", "categories", "tags", "updated_at"])
    return post


@router.post("/{post_id}/unpublish", response_model=PostRead)
async def unpublish_post(post_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(require_roles(UserRole.ADMIN, UserRole.EDITOR))) -> Post:
    if not (post := await db.get(Post, post_id)):
        raise HTTPException(status_code=404, detail="Post not found")
    post.status, post.editor_id = PostStatus.DRAFT, user.id
    await db.commit()
    await db.refresh(post, attribute_names=["author", "categories", "tags", "updated_at"])
    await invalidate_post(post.id, post.slug)
    return post


@router.post("/{post_id}/flag-breaking", response_model=PostRead)
async def flag_breaking(post_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(require_roles(UserRole.ADMIN, UserRole.EDITOR))) -> Post:
    if not (post := await db.get(Post, post_id)):
        raise HTTPException(status_code=404, detail="Post not found")
    post.is_breaking = True
    await db.commit()
    await db.refresh(post, attribute_names=["author", "categories", "tags", "updated_at"])
    await invalidate_post(post.id, post.slug)
    return post
