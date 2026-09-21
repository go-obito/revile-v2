"""Link orphaned media records to posts whose body references their URLs."""

import asyncio

from sqlalchemy import select

from app.db import SessionLocal
from app.media_services import link_media_to_post
from app.models import Post


async def backfill() -> int:
    linked = 0
    async with SessionLocal() as db:
        posts = list((await db.scalars(select(Post))).all())
        for post in posts:
            linked += await link_media_to_post(db, post_id=post.id, body=post.body)
        await db.commit()
    return linked


if __name__ == "__main__":
    print(f"Linked {asyncio.run(backfill())} media record(s).")