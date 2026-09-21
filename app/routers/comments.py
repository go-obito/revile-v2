from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.comment_services import check_akismet
from app.db import get_db
from app.models import Comment, CommentReport, CommentStatus, Post
from app.rate_limit import client_ip_from_request, enforce_rate_limit
from app.schemas import CommentCreate, CommentRead, CommentReportCreate

router = APIRouter(tags=["comments"])


@router.get("/posts/{post_id}/comments", response_model=list[CommentRead])
async def list_approved_comments(post_id: int, db: AsyncSession = Depends(get_db)) -> list[Comment]:
    if not await db.get(Post, post_id):
        raise HTTPException(status_code=404, detail="Post not found")
    statement = (
        select(Comment)
        .where(Comment.post_id == post_id, Comment.status == CommentStatus.APPROVED)
        .order_by(Comment.created_at, Comment.id)
    )
    return list((await db.scalars(statement)).all())


@router.post("/posts/{post_id}/comments", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: int,
    payload: CommentCreate,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> Comment:
    idempotency_key = str(payload.idempotency_key)
    existing = await db.scalar(select(Comment).where(Comment.idempotency_key == idempotency_key))
    if existing:
        if existing.post_id != post_id:
            raise HTTPException(status_code=409, detail="Idempotency key was already used for another post")
        response.status_code = status.HTTP_200_OK
        response.headers["Idempotent-Replay"] = "true"
        return existing

    await enforce_rate_limit(request, "comments", 5, 60)
    if not await db.get(Post, post_id):
        raise HTTPException(status_code=404, detail="Post not found")
    if payload.parent_id is not None:
        parent = await db.get(Comment, payload.parent_id)
        if not parent:
            raise HTTPException(status_code=400, detail="Parent comment not found")
        if parent.post_id != post_id:
            raise HTTPException(status_code=400, detail="Parent comment must belong to the post being commented on")
        if parent.status != CommentStatus.APPROVED:
            raise HTTPException(status_code=400, detail="Replies are only allowed to publicly visible comments")

    client_ip = client_ip_from_request(request)
    spam = await check_akismet(
        author_name=payload.author_name,
        author_email=str(payload.author_email),
        body=payload.body,
        client_ip=client_ip,
        user_agent=request.headers.get("user-agent", ""),
        referrer=request.headers.get("referer"),
    )
    comment = Comment(
        post_id=post_id,
        parent_id=payload.parent_id,
        author_name=payload.author_name,
        author_email=str(payload.author_email),
        body=payload.body,
        idempotency_key=idempotency_key,
        spam_score=spam.score,
        spam_reason=spam.reason,
        status=CommentStatus.FLAGGED if spam.suspected else CommentStatus.PENDING,
    )
    db.add(comment)
    try:
        await db.commit()
    except IntegrityError:
        # A concurrent retry can win the unique-key race. Return the original.
        await db.rollback()
        existing = await db.scalar(select(Comment).where(Comment.idempotency_key == idempotency_key))
        if existing and existing.post_id == post_id:
            response.status_code = status.HTTP_200_OK
            response.headers["Idempotent-Replay"] = "true"
            return existing
        raise
    await db.refresh(comment)
    return comment


@router.post("/comments/{comment_id}/reports", status_code=status.HTTP_201_CREATED)
async def report_comment(
    comment_id: int,
    payload: CommentReportCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict[str, bool]:
    await enforce_rate_limit(request, "comment-reports", 5, 3600)
    comment = await db.get(Comment, comment_id)
    if not comment or comment.status != CommentStatus.APPROVED:
        raise HTTPException(status_code=404, detail="Public comment not found")
    db.add(CommentReport(comment_id=comment.id, reason=payload.reason))
    await db.commit()
    return {"reported": True}
