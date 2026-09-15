import asyncio
import os

from sqlalchemy import select

from app.db import SessionLocal
from app.models import Category, User, UserRole
from app.security import hash_password

STARTER_CATEGORIES = [("AI", "ai"), ("Hardware", "hardware"), ("Policy", "policy"), ("Startups", "startups")]


async def seed() -> None:
    email = os.environ.get("ADMIN_EMAIL", "admin@example.com").lower()
    password = os.environ.get("ADMIN_PASSWORD")
    if not password:
        raise RuntimeError("ADMIN_PASSWORD must be set")
    name = os.environ.get("ADMIN_NAME", "Revile Admin")
    async with SessionLocal() as db:
        admin = await db.scalar(select(User).where(User.email == email))
        if not admin:
            db.add(User(email=email, hashed_password=hash_password(password), name=name, role=UserRole.ADMIN))
        elif admin.role != UserRole.ADMIN:
            admin.role = UserRole.ADMIN
        for name, slug in STARTER_CATEGORIES:
            if not await db.scalar(select(Category).where(Category.slug == slug)):
                db.add(Category(name=name, slug=slug))
        await db.commit()


if __name__ == "__main__":
    asyncio.run(seed())
