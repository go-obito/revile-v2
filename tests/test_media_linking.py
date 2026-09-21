import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.media_services import image_urls_from_body, link_media_to_post
from app.models import Media


class SqliteDb:
    def __init__(self, session: Session) -> None:
        self.session = session

    async def scalars(self, statement: object):
        return self.session.scalars(statement)  # type: ignore[arg-type]


@pytest.fixture
def media_db() -> SqliteDb:
    engine = create_engine("sqlite://")
    with engine.begin() as connection:
        connection.execute(text("""
            CREATE TABLE media (
                id INTEGER PRIMARY KEY,
                file_url VARCHAR(1000) NOT NULL,
                imagekit_file_id VARCHAR(255),
                alt_text VARCHAR(300) NOT NULL,
                uploaded_by INTEGER NOT NULL,
                post_id INTEGER,
                created_at DATETIME
            )
        """))
    session = Session(engine)
    session.add(Media(file_url="https://ik.imagekit.io/revile/story.avif", imagekit_file_id="file-1", alt_text="Story", uploaded_by=2, post_id=None))
    session.commit()
    try:
        yield SqliteDb(session)
    finally:
        session.close()


def test_image_urls_support_markdown_and_html() -> None:
    body = "![Story](https://ik.imagekit.io/revile/story.avif)\n<img src=\"https://ik.imagekit.io/revile/other.avif\">"
    assert image_urls_from_body(body) == {
        "https://ik.imagekit.io/revile/story.avif",
        "https://ik.imagekit.io/revile/other.avif",
    }


@pytest.mark.asyncio
async def test_uploaded_image_gets_real_post_id_when_post_is_saved(media_db: SqliteDb) -> None:
    linked = await link_media_to_post(
        media_db, post_id=42, body="![Story](https://ik.imagekit.io/revile/story.avif)", uploaded_by=2
    )
    media_db.session.commit()
    media = media_db.session.query(Media).one()
    assert linked == 1
    assert media.post_id == 42
