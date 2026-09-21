import re

import pytest

from app.models import User
from app.routers.media import get_imagekit_authentication, settings


@pytest.mark.asyncio
async def test_imagekit_authentication_returns_signed_one_time_parameters(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "imagekit_private_key", "private_test_key")

    response = await get_imagekit_authentication(User())

    assert response.token
    assert response.expire > 0
    assert re.fullmatch(r"[0-9a-f]{40}", response.signature)
