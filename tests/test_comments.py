from uuid import uuid4

import pytest
from fastapi import HTTPException, Request, Response
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.comment_services import SpamCheckResult
from app.models import Comment, CommentModerationAudit, CommentReport, CommentStatus, User, UserRole
from app.routers.comments import create_comment, report_comment
from app.routers.moderation import moderate_comment
from app.schemas import CommentCreate, CommentReportCreate, ModerationUpdate


class SqliteDb:
    def __init__(self, session: Session) -> None:
        self.session = session

    async def get(self, model: type[object], identifier: int):
        return self.session.get(model, identifier)

    async def scalar(self, statement: object):
        return self.session.scalar(statement)  # type: ignore[arg-type]

    async def scalars(self, statement: object):
        return self.session.scalars(statement)  # type: ignore[arg-type]

    def add(self, row: object) -> None:
        self.session.add(row)

    async def commit(self) -> None:
        self.session.commit()

    async def rollback(self) -> None:
        self.session.rollback()

    async def refresh(self, row: object) -> None:
        self.session.refresh(row)


def make_db() -> SqliteDb:
    engine = create_engine("sqlite://")
    with engine.begin() as connection:
        connection.execute(text("""
            CREATE TABLE users (id INTEGER PRIMARY KEY, email VARCHAR(320), hashed_password VARCHAR(255),
              name VARCHAR(200), role VARCHAR(20), is_active BOOLEAN, created_at DATETIME)
        """))
        connection.execute(text("""
            CREATE TABLE posts (id INTEGER PRIMARY KEY, title VARCHAR(300), slug VARCHAR(320), dek VARCHAR(500),
              body TEXT, status VARCHAR(20), is_breaking BOOLEAN, author_id INTEGER, editor_id INTEGER,
              published_at DATETIME, updated_at DATETIME, created_at DATETIME, search_vector TEXT)
        """))
        connection.execute(text("""
            CREATE TABLE comments (id INTEGER PRIMARY KEY, post_id INTEGER, parent_id INTEGER, author_name VARCHAR(120),
                            author_email VARCHAR(320), body TEXT, idempotency_key VARCHAR(36), spam_score FLOAT, spam_reason TEXT,
              status VARCHAR(32), created_at DATETIME)
        """))
        connection.execute(text("CREATE TABLE comment_reports (id INTEGER PRIMARY KEY, comment_id INTEGER, reason VARCHAR(500), reported_at DATETIME)"))
        connection.execute(text("CREATE TABLE comment_moderation_audits (id INTEGER PRIMARY KEY, comment_id INTEGER, actor_id INTEGER, action VARCHAR(32), created_at DATETIME)"))
        for post_id in (42, 43):
            connection.execute(text("""INSERT INTO posts (id, title, slug, body, status, is_breaking, author_id, updated_at, created_at)
              VALUES (:id, 'Post', :slug, 'Body', 'published', 0, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"""), {"id": post_id, "slug": f"post-{post_id}"})
    return SqliteDb(Session(engine))


def request() -> Request:
    return Request({"type": "http", "method": "POST", "path": "/", "headers": [], "client": ("203.0.113.5", 9999)})


def payload(**overrides: object) -> CommentCreate:
    values = {
        "author_name": "Ada",
        "author_email": "ada@example.com",
        "body": "Useful comment",
        "idempotency_key": uuid4(),
    }
    values.update(overrides)
    return CommentCreate(
        **values,
    )


@pytest.fixture
def safe_services(monkeypatch: pytest.MonkeyPatch) -> None:

    async def skip_rate_limit(*_args: object) -> None:
        return None

    async def clean_spam(*_args: object, **_kwargs: object) -> SpamCheckResult:
        return SpamCheckResult(score=0.0, reason="Akismet passed", suspected=False)

    monkeypatch.setattr("app.routers.comments.enforce_rate_limit", skip_rate_limit)
    monkeypatch.setattr("app.routers.comments.check_akismet", clean_spam)


@pytest.mark.asyncio
async def test_duplicate_submission_returns_the_original_comment(safe_services: list[str]) -> None:
    db = make_db()
    try:
        submission = payload()
        first = await create_comment(42, submission, request(), Response(), db)  # type: ignore[arg-type]
        replay_response = Response()
        replay = await create_comment(42, submission, request(), replay_response, db)  # type: ignore[arg-type]
        assert replay.id == first.id
        assert replay_response.status_code == 200
        assert db.session.query(Comment).count() == 1
    finally:
        db.session.close()


@pytest.mark.asyncio
async def test_parent_from_another_post_is_rejected(safe_services: list[str]) -> None:
    db = make_db()
    try:
        parent = Comment(post_id=43, parent_id=None, author_name="Other", author_email="other@example.com", body="Parent", idempotency_key=str(uuid4()), status=CommentStatus.APPROVED)
        db.add(parent)
        await db.commit()
        with pytest.raises(HTTPException, match="Parent comment must belong") as error:
            await create_comment(42, payload(parent_id=parent.id), request(), Response(), db)  # type: ignore[arg-type]
        assert error.value.status_code == 400
    finally:
        db.session.close()


@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_akismet_spam_is_flagged_before_moderation(monkeypatch: pytest.MonkeyPatch, safe_services: None) -> None:
    db = make_db()
    async def spammy(*_args: object, **_kwargs: object) -> SpamCheckResult:
        return SpamCheckResult(score=1.0, reason="Akismet marked this as spam", suspected=True)
    monkeypatch.setattr("app.routers.comments.check_akismet", spammy)
    try:
        comment = await create_comment(42, payload(body="BUY CHEAP LINKS NOW"), request(), Response(), db)  # type: ignore[arg-type]
        assert comment.spam_score == 1.0
        assert comment.status == CommentStatus.FLAGGED
    finally:
        db.session.close()


@pytest.mark.asyncio
async def test_report_and_approval_audit_flow(monkeypatch: pytest.MonkeyPatch, safe_services: None) -> None:
    db = make_db()
    async def skip_rate_limit(*_args: object) -> None:
        return None
    monkeypatch.setattr("app.routers.comments.enforce_rate_limit", skip_rate_limit)
    try:
        comment = await create_comment(42, payload(), request(), Response(), db)  # type: ignore[arg-type]
        assert comment.status == CommentStatus.PENDING
        editor = User(id=9, email="editor@example.com", hashed_password="hash", name="Editor", role=UserRole.EDITOR, is_active=True)
        db.add(editor)
        await db.commit()
        approved = await moderate_comment(comment.id, ModerationUpdate(status=CommentStatus.APPROVED), db, editor)  # type: ignore[arg-type]
        assert approved.status == CommentStatus.APPROVED
        reported = await report_comment(comment.id, CommentReportCreate(reason="Off-topic"), request(), db)  # type: ignore[arg-type]
        assert reported == {"reported": True}
        assert db.session.query(CommentReport).one().reason == "Off-topic"
        audit = db.session.query(CommentModerationAudit).one()
        assert (audit.comment_id, audit.actor_id, audit.action) == (comment.id, editor.id, "approved")
    finally:
        db.session.close()
