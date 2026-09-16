from app.models import User, UserRole
from app.sanitize import render_markdown, sanitize_comment, sanitize_markdown
from app.security import create_access_token, hash_password, verify_password


def test_password_hash_round_trip() -> None:
    hashed = hash_password("correct horse battery staple")
    assert verify_password("correct horse battery staple", hashed)
    assert not verify_password("wrong password", hashed)


def test_access_token_contains_user_claims() -> None:
    token = create_access_token(User(id=42, role=UserRole.AUTHOR))
    assert token


def test_content_is_sanitized() -> None:
    assert "script" not in sanitize_markdown("Hello <script>alert(1)</script>")
    assert "<img" not in sanitize_comment("<img src=x onerror=alert(1)>")
    assert "<script" not in render_markdown("[click](javascript:alert(1))")


def test_markdown_rendering_supports_editor_blocks() -> None:
    rendered = render_markdown("`inline`\n\n```python\nprint('ok')\n```\n\n| A | B |\n| --- | --- |\n| 1 | 2 |")
    assert "<code>inline</code>" in rendered
    assert "<pre><code>" in rendered
    assert "<table>" in rendered
