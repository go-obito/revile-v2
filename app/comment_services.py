import logging
from dataclasses import dataclass

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SpamCheckResult:
    score: float | None
    reason: str | None
    suspected: bool


async def check_akismet(*, author_name: str, author_email: str, body: str, client_ip: str, user_agent: str, referrer: str | None) -> SpamCheckResult:
    settings = get_settings()
    if not settings.akismet_api_key or not settings.akismet_blog_url:
        return SpamCheckResult(score=None, reason="Akismet is not configured", suspected=False)
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                f"https://{settings.akismet_api_key}.rest.akismet.com/1.1/comment-check",
                data={
                    "blog": settings.akismet_blog_url,
                    "user_ip": client_ip,
                    "user_agent": user_agent,
                    "referrer": referrer or "",
                    "comment_type": "comment",
                    "comment_author": author_name,
                    "comment_author_email": author_email,
                    "comment_content": body,
                },
            )
            response.raise_for_status()
            suspected = response.text.strip().lower() == "true"
            return SpamCheckResult(score=1.0 if suspected else 0.0, reason="Akismet marked this as spam" if suspected else "Akismet passed", suspected=suspected)
    except httpx.HTTPError:
        # Akismet is advisory: retain the submission for human review instead
        # of treating an outage as a reason to discard a legitimate comment.
        logger.warning("Akismet check unavailable", exc_info=True)
        return SpamCheckResult(score=None, reason="Akismet check unavailable", suspected=False)


