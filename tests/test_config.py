import pytest

from app.config import Settings


@pytest.mark.parametrize(
    ("database_url", "expected_url"),
    [
        (
            "postgresql://revile:revile@localhost:5432/revile",
            "postgresql+asyncpg://revile:revile@localhost:5432/revile",
        ),
        (
            "postgres://revile:revile@localhost:5432/revile",
            "postgresql+asyncpg://revile:revile@localhost:5432/revile",
        ),
        (
            "postgresql+asyncpg://revile:revile@localhost:5432/revile",
            "postgresql+asyncpg://revile:revile@localhost:5432/revile",
        ),
    ],
)
def test_database_url_is_normalized_for_async_sqlalchemy(database_url: str, expected_url: str) -> None:
    assert Settings(database_url=database_url).database_url == expected_url