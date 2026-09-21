import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Media

MARKDOWN_IMAGE_PATTERN = re.compile(r"!\[[^\]]*\]\((https?://[^\s)]+)")
HTML_IMAGE_PATTERN = re.compile(r'<img[^>]+src=["\'](https?://[^"\']+)', re.IGNORECASE)


def image_urls_from_body(body: str) -> set[str]:
    return set(MARKDOWN_IMAGE_PATTERN.findall(body)) | set(HTML_IMAGE_PATTERN.findall(body))


async def link_media_to_post(
    db: AsyncSession,
    *,
    post_id: int,
    body: str,
    uploaded_by: int | None = None,
) -> int:
    image_urls = image_urls_from_body(body)
    if not image_urls:
        return 0
    statement = select(Media).where(Media.post_id.is_(None), Media.file_url.in_(image_urls))
    if uploaded_by is not None:
        statement = statement.where(Media.uploaded_by == uploaded_by)
    media_rows = list((await db.scalars(statement)).all())
    for media in media_rows:
        media.post_id = post_id
    return len(media_rows)