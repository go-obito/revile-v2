from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import Comment, CommentStatus, Post
from app.rate_limit import enforce_rate_limit
from app.schemas import CommentCreate, CommentRead

router = APIRouter(prefix="/posts/{post_id}/comments", tags=["comments"])


@router.post("", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
async def create_comment(post_id: int, payload: CommentCreate, request: Request, db: AsyncSession = Depends(get_db)) -> Comment:
    await enforce_rate_limit(request, "comments", 5, 60)
    if not await db.get(Post, post_id):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Post not found")
    comment = Comment(post_id=post_id, parent_id=payload.parent_id, author_name=payload.author_name, author_email=str(payload.author_email), body=payload.body, status=CommentStatus.PENDING)
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment
