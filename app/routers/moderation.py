from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import Comment, CommentStatus, User, UserRole
from app.schemas import CommentRead, ModerationUpdate
from app.security import require_roles

router = APIRouter(prefix="/admin/comments", tags=["moderation"])


@router.get("/pending", response_model=list[CommentRead])
async def pending_comments(db: AsyncSession = Depends(get_db), _: User = Depends(require_roles(UserRole.ADMIN, UserRole.EDITOR))) -> list[Comment]:
    return list((await db.scalars(select(Comment).where(Comment.status == CommentStatus.PENDING).order_by(Comment.created_at))).all())


@router.patch("/{comment_id}/moderate", response_model=CommentRead)
async def moderate_comment(comment_id: int, payload: ModerationUpdate, db: AsyncSession = Depends(get_db), _: User = Depends(require_roles(UserRole.ADMIN, UserRole.EDITOR))) -> Comment:
    comment = await db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    comment.status = payload.status
    await db.commit()
    await db.refresh(comment)
    return comment
