from __future__ import annotations

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db import get_db
from app.models import NewsletterSubscriber
from app.rate_limit import enforce_rate_limit
from app.schemas import NewsletterSubscribe
from app.services.newsletter import NewsletterDeliveryError, ResendNewsletter

router = APIRouter(prefix="/newsletter", tags=["newsletter"])
settings = get_settings()


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def issued_token() -> tuple[str, str]:
    raw_token = secrets.token_urlsafe(32)
    return raw_token, token_hash(raw_token)


def frontend_url(path: str, **query: str) -> str:
    base = settings.frontend_origin.rstrip("/")
    suffix = f"?{urlencode(query)}" if query else ""
    return f"{base}{path}{suffix}"


@router.post("/subscriptions", status_code=status.HTTP_202_ACCEPTED)
async def subscribe(payload: NewsletterSubscribe, request: Request, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    await enforce_rate_limit(request, "newsletter-subscribe", limit=5, window_seconds=3600)
    email = str(payload.email).strip().lower()
    subscriber = await db.scalar(select(NewsletterSubscriber).where(NewsletterSubscriber.email == email))
    if subscriber and subscriber.status == "subscribed":
        return {"message": "If that address is eligible, a confirmation email has been sent."}

    raw_confirmation, confirmation_hash = issued_token()
    _raw_unsubscribe, unsubscribe_hash = issued_token()
    now = datetime.now(UTC)
    if subscriber is None:
        subscriber = NewsletterSubscriber(
            email=email,
            status="pending",
            confirmation_token_hash=confirmation_hash,
            confirmation_expires_at=now + timedelta(hours=settings.newsletter_confirmation_hours),
            unsubscribe_token_hash=unsubscribe_hash,
        )
        db.add(subscriber)
    else:
        subscriber.status = "pending"
        subscriber.confirmation_token_hash = confirmation_hash
        subscriber.confirmation_expires_at = now + timedelta(hours=settings.newsletter_confirmation_hours)
        subscriber.unsubscribe_token_hash = unsubscribe_hash
        subscriber.unsubscribed_at = None

    await db.commit()
    try:
        await ResendNewsletter(settings).send_confirmation(email, frontend_url("/newsletter/confirm", token=raw_confirmation))
    except NewsletterDeliveryError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Newsletter signup is temporarily unavailable.") from exc
    return {"message": "If that address is eligible, a confirmation email has been sent."}


@router.get("/confirm")
async def confirm(token: str, db: AsyncSession = Depends(get_db)) -> RedirectResponse:
    now = datetime.now(UTC)
    subscriber = await db.scalar(
        select(NewsletterSubscriber).where(
            NewsletterSubscriber.confirmation_token_hash == token_hash(token),
            NewsletterSubscriber.confirmation_expires_at > now,
        )
    )
    if not subscriber:
        return RedirectResponse(frontend_url("/newsletter/confirmed", state="invalid"), status_code=status.HTTP_303_SEE_OTHER)
    if subscriber.status != "subscribed":
        try:
            delivery = ResendNewsletter(settings)
            if subscriber.resend_contact_id:
                await delivery.set_contact_subscription(subscriber.resend_contact_id, subscribed=True)
            else:
                subscriber.resend_contact_id = await delivery.subscribe_contact(subscriber.email)
        except NewsletterDeliveryError:
            return RedirectResponse(frontend_url("/newsletter/confirmed", state="retry"), status_code=status.HTTP_303_SEE_OTHER)
        subscriber.status = "subscribed"
        subscriber.consented_at = now
    subscriber.confirmation_token_hash = None
    subscriber.confirmation_expires_at = None
    await db.commit()
    return RedirectResponse(frontend_url("/newsletter/confirmed", state="confirmed"), status_code=status.HTTP_303_SEE_OTHER)


@router.get("/unsubscribe")
async def unsubscribe(token: str, db: AsyncSession = Depends(get_db)) -> RedirectResponse:
    subscriber = await db.scalar(select(NewsletterSubscriber).where(NewsletterSubscriber.unsubscribe_token_hash == token_hash(token)))
    if not subscriber:
        return RedirectResponse(frontend_url("/newsletter/unsubscribed", state="invalid"), status_code=status.HTTP_303_SEE_OTHER)
    if subscriber.resend_contact_id and subscriber.status == "subscribed":
        try:
            await ResendNewsletter(settings).unsubscribe_contact(subscriber.resend_contact_id)
        except NewsletterDeliveryError:
            return RedirectResponse(frontend_url("/newsletter/unsubscribed", state="retry"), status_code=status.HTTP_303_SEE_OTHER)
    subscriber.status = "unsubscribed"
    subscriber.unsubscribed_at = datetime.now(UTC)
    await db.commit()
    return RedirectResponse(frontend_url("/newsletter/unsubscribed", state="confirmed"), status_code=status.HTTP_303_SEE_OTHER)
