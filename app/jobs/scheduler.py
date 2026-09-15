from datetime import UTC, datetime
from pathlib import Path
from xml.sax.saxutils import escape

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from app.cache import invalidate_post
from app.db import SessionLocal
from app.logging import configure_logging
from app.models import Post, PostStatus

scheduler = AsyncIOScheduler(timezone="UTC")


async def publish_scheduled_posts() -> None:
    async with SessionLocal() as db:
        posts = list((await db.scalars(select(Post).where(Post.status == PostStatus.SCHEDULED, Post.published_at <= datetime.now(UTC)))).all())
        for post in posts:
            post.status = PostStatus.PUBLISHED
        if posts:
            await db.commit()
            for post in posts:
                await invalidate_post(post.id, post.slug)


async def regenerate_sitemap() -> None:
    async with SessionLocal() as db:
        posts = list((await db.scalars(select(Post).where(Post.status == PostStatus.PUBLISHED).order_by(Post.published_at.desc()))).all())
    public_dir = Path(__import__("app.config", fromlist=["get_settings"]).get_settings().public_dir)
    public_dir.mkdir(parents=True, exist_ok=True)
    urls = "".join(f"<url><loc>/posts/{escape(post.slug)}</loc><lastmod>{(post.updated_at or post.created_at).date().isoformat()}</lastmod></url>" for post in posts)
    sitemap = f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>'
    (public_dir / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    items = "".join(f"<item><title>{escape(post.title)}</title><link>/posts/{escape(post.slug)}</link><description>{escape(post.dek or '')}</description></item>" for post in posts[:50])
    rss = f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Revile</title><link>/</link>{items}</channel></rss>'
    (public_dir / "feed.xml").write_text(rss, encoding="utf-8")


def start_scheduler() -> None:
    configure_logging()
    scheduler.add_job(publish_scheduled_posts, "interval", seconds=30, id="publish-scheduled", replace_existing=True)
    scheduler.add_job(regenerate_sitemap, "interval", hours=1, id="regenerate-sitemap", replace_existing=True)
    scheduler.start()


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
