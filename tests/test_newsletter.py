from app.models import NewsletterSubscriber
from app.routers.newsletter import issued_token, token_hash
from app.schemas import NewsletterSubscribe


def test_newsletter_tokens_are_hashed_and_unique() -> None:
    raw_first, hashed_first = issued_token()
    raw_second, hashed_second = issued_token()

    assert raw_first != raw_second
    assert hashed_first != hashed_second
    assert raw_first != hashed_first
    assert token_hash(raw_first) == hashed_first


def test_newsletter_subscriber_and_email_schema() -> None:
    payload = NewsletterSubscribe(email="READER@EXAMPLE.COM")
    subscriber = NewsletterSubscriber(email=str(payload.email).lower(), status="pending", unsubscribe_token_hash="a" * 64)

    assert subscriber.email == "reader@example.com"
    assert subscriber.status == "pending"
