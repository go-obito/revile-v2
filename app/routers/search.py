from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import Post, PostStatus
from app.schemas import PostRead

router = APIRouter(tags=["search"])


@router.get("/search", response_model=list[PostRead])
async def search_posts(q: str = Query(min_length=2, max_length=200), db: AsyncSession = Depends(get_db)) -> list[Post]:
    query_vector = func.plainto_tsquery("english", q)
    return list((await db.scalars(select(Post).where(Post.status == PostStatus.PUBLISHED, Post.search_vector.op("@@")(query_vector)).order_by(func.ts_rank(Post.search_vector, query_vector).desc()).limit(50))).all())
