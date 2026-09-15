from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import Category, Post, PostStatus, Tag, User, UserRole
from app.routers.posts import encode_cursor
from app.schemas import CategoryCreate, CategoryRead, PostList
from app.security import require_roles

router = APIRouter(tags=["taxonomy"])


@router.get("/categories", response_model=list[CategoryRead])
async def list_categories(db: AsyncSession = Depends(get_db)) -> list[Category]:
    return list((await db.scalars(select(Category).order_by(Category.name))).all())


@router.post("/categories", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(payload: CategoryCreate, db: AsyncSession = Depends(get_db), _: User = Depends(require_roles(UserRole.ADMIN, UserRole.EDITOR))) -> Category:
    category = Category(name=payload.name, slug=payload.slug)
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


@router.get("/categories/{slug}/posts", response_model=PostList)
async def category_posts(slug: str, limit: int = 20, db: AsyncSession = Depends(get_db)) -> PostList:
    category = await db.scalar(select(Category).where(Category.slug == slug))
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    posts = list((await db.scalars(select(Post).join(Post.categories).where(Category.id == category.id, Post.status == PostStatus.PUBLISHED).order_by(Post.published_at.desc(), Post.id.desc()).limit(limit))).unique().all())
    return PostList(items=posts, next_cursor=encode_cursor(posts[-1]) if len(posts) == limit else None)


@router.get("/tags", response_model=list[CategoryRead])
async def list_tags(db: AsyncSession = Depends(get_db)) -> list[Tag]:
    return list((await db.scalars(select(Tag).order_by(Tag.name))).all())
