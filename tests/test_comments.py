import pytest
from fastapi import Request
from sqlalchemy import create_engine, text
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Session

from app.models import Comment, CommentStatus, Post
from app.routers.comments import create_comment, list_approved_comments
from app.schemas import CommentCreate


class ScalarResult:
    def __init__(self, comments: list[Comment]) -> None:
        self.comments = comments

    def all(self) -> list[Comment]:
        return self.comments


class CommentsDb:
    def __init__(self, comments: list[Comment]) -> None:
        self.comments = comments
        self.statement = None

    async def get(self, _model: object, _post_id: int) -> object:
        return object()

    async def scalars(self, statement: object) -> ScalarResult:
        self.statement = statement
        return ScalarResult(self.comments)


class SqliteCommentsDb:
    def __init__(self, session: Session) -> None:
        self.session = session

    async def get(self, model: type[Post], post_id: int) -> Post | None:
        return self.session.get(model, post_id)

    async def scalars(self, statement: object):
        return self.session.scalars(statement)

    def add(self, comment: Comment) -> None:
        self.session.add(comment)

    async def commit(self) -> None:
        self.session.commit()

    async def refresh(self, comment: Comment) -> None:
        self.session.refresh(comment)


def create_comments_database() -> SqliteCommentsDb:
    engine = create_engine("sqlite://")
    with engine.begin() as connection:
        connection.execute(text("""
            CREATE TABLE posts (
                id INTEGER PRIMARY KEY, title VARCHAR(300), slug VARCHAR(320), dek VARCHAR(500),
                body TEXT, status VARCHAR(20), is_breaking BOOLEAN, author_id INTEGER, editor_id INTEGER,
                published_at DATETIME, updated_at DATETIME, created_at DATETIME, search_vector TEXT
            )
        """))
        connection.execute(text("""
            CREATE TABLE comments (
                id INTEGER PRIMARY KEY, post_id INTEGER, parent_id INTEGER, author_name VARCHAR(120),
                author_email VARCHAR(320), body TEXT, status VARCHAR(20), created_at DATETIME
            )
        """))
        for post_id in (42, 43, 44):
            connection.execute(text("""INSERT INTO posts
                (id, title, slug, dek, body, status, is_breaking, author_id, editor_id, published_at, updated_at, created_at, search_vector)
                VALUES (:id, 'Post', :slug, NULL, 'Body', 'published', 0, 1, NULL, NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, NULL)"""), {"id": post_id, "slug": f"post-{post_id}"})
    return SqliteCommentsDb(Session(engine))


@pytest.mark.asyncio
async def test_public_comments_query_is_scoped_to_approved_comments_for_the_post() -> None:
    approved_parent = Comment(id=1, post_id=42, parent_id=None, author_name="Ada", author_email="ada@example.com", body="Approved parent", status=CommentStatus.APPROVED)
    approved_reply = Comment(id=2, post_id=42, parent_id=1, author_name="Lin", author_email="lin@example.com", body="Approved reply", status=CommentStatus.APPROVED)
    db = CommentsDb([approved_parent, approved_reply])

    response = await list_approved_comments(42, db)  # type: ignore[arg-type]

    compiled = db.statement.compile(dialect=postgresql.dialect())
    assert response == [approved_parent, approved_reply]
    assert "comments.post_id = %(post_id_1)s" in str(compiled)
    assert "comments.status = %(status_1)s" in str(compiled)
    assert compiled.params == {"post_id_1": 42, "status_1": CommentStatus.APPROVED}


@pytest.mark.asyncio
async def test_public_comment_scenarios_use_persisted_approved_rows_only(monkeypatch: pytest.MonkeyPatch) -> None:
    db = create_comments_database()
    try:
        approved_parent = Comment(post_id=42, parent_id=None, author_name="Ada", author_email="ada@example.com", body="Approved parent", status=CommentStatus.APPROVED)
        db.add(approved_parent)
        await db.commit()
        approved_reply = Comment(post_id=42, parent_id=approved_parent.id, author_name="Lin", author_email="lin@example.com", body="Approved reply", status=CommentStatus.APPROVED)
        pending = Comment(post_id=42, parent_id=None, author_name="Pat", author_email="pat@example.com", body="Pending comment", status=CommentStatus.PENDING)
        pending_only = Comment(post_id=43, parent_id=None, author_name="Sam", author_email="sam@example.com", body="Not public", status=CommentStatus.PENDING)
        db.add(approved_reply)
        db.add(pending)
        db.add(pending_only)
        await db.commit()

        visible = await list_approved_comments(42, db)  # type: ignore[arg-type]
        pending_only_visible = await list_approved_comments(43, db)  # type: ignore[arg-type]

        async def skip_rate_limit(*_args: object) -> None:
            return None

        monkeypatch.setattr("app.routers.comments.enforce_rate_limit", skip_rate_limit)
        created = await create_comment(44, CommentCreate(author_name="New", author_email="new@example.com", body="Awaiting approval"), Request({"type": "http", "method": "POST", "path": "/"}), db)  # type: ignore[arg-type]
        newly_submitted_visible = await list_approved_comments(44, db)  # type: ignore[arg-type]

        assert [comment.body for comment in visible] == ["Approved parent", "Approved reply"]
        assert pending_only_visible == []
        assert created.status == CommentStatus.PENDING
        assert newly_submitted_visible == []
    finally:
        db.session.close()
