from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import Comment, CommentModerationAudit, CommentReport, CommentStatus, User, UserRole
from app.schemas import (
    CommentAuditRead,
    CommentRead,
    CommentReportRead,
    ModerationCommentRead,
    ModerationUpdate,
    ReportedCommentRead,
)
from app.security import require_roles

router = APIRouter(prefix="/admin/comments", tags=["moderation"])


@router.get("/pending", response_model=list[ModerationCommentRead])
async def pending_comments(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.EDITOR)),
) -> list[Comment]:
    return list(
        (
            await db.scalars(
                select(Comment)
                .where(Comment.status.in_([CommentStatus.PENDING, CommentStatus.FLAGGED]))
                .order_by(Comment.created_at)
            )
        ).all()
    )


@router.get("/pending-count")
async def pending_comment_count(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.EDITOR)),
) -> dict[str, int]:
    comments = await db.scalars(select(Comment.id).where(Comment.status.in_([CommentStatus.PENDING, CommentStatus.FLAGGED])))
    return {"count": len(list(comments.all()))}


@router.get("/reported", response_model=list[ReportedCommentRead])
async def reported_comments(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.EDITOR)),
) -> list[ReportedCommentRead]:
    comments = list((await db.scalars(select(Comment).join(CommentReport).distinct().order_by(Comment.created_at))).all())
    if not comments:
        return []
    reports = list((await db.scalars(select(CommentReport).where(CommentReport.comment_id.in_([comment.id for comment in comments])).order_by(CommentReport.reported_at.desc()))).all())
    reports_by_comment: dict[int, list[CommentReport]] = {}
    for report in reports:
        reports_by_comment.setdefault(report.comment_id, []).append(report)
    return [
        ReportedCommentRead(
            **ModerationCommentRead.model_validate(comment).model_dump(),
            reports=[CommentReportRead.model_validate(report) for report in reports_by_comment.get(comment.id, [])],
        )
        for comment in comments
    ]


@router.get("/history", response_model=list[CommentAuditRead])
async def moderation_history(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.EDITOR)),
) -> list[CommentModerationAudit]:
    return list((await db.scalars(select(CommentModerationAudit).order_by(CommentModerationAudit.created_at.desc()).limit(100))).all())


@router.patch("/{comment_id}/moderate", response_model=CommentRead)
async def moderate_comment(
    comment_id: int,
    payload: ModerationUpdate,
    db: AsyncSession = Depends(get_db),
    actor: User = Depends(require_roles(UserRole.ADMIN, UserRole.EDITOR)),
) -> Comment:
    comment = await db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    comment.status = payload.status
    db.add(CommentModerationAudit(comment_id=comment.id, actor_id=actor.id, action=payload.status.value))
    await db.commit()
    await db.refresh(comment)
    return comment
