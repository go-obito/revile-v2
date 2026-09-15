from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()
if not settings.database_url.startswith("postgresql+asyncpg://"):
    database_scheme = settings.database_url.split("://", 1)[0]
    raise RuntimeError(
        "DATABASE_URL must use the postgresql+asyncpg:// scheme after normalization; "
        f"got {database_scheme!r}"
    )

engine = create_async_engine(settings.database_url, pool_pre_ping=True)
if engine.url.drivername != "postgresql+asyncpg":
    raise RuntimeError(f"SQLAlchemy engine must use postgresql+asyncpg, got {engine.url.drivername!r}")

SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


async def dispose_engine() -> None:
    await engine.dispose()
