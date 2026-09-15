from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import User, UserRole
from app.schemas import RoleUpdate, UserCreate, UserRead
from app.security import hash_password, require_roles

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, db: AsyncSession = Depends(get_db), _: User = Depends(require_roles(UserRole.ADMIN))) -> User:
    user = User(email=payload.email.lower(), hashed_password=hash_password(payload.password), name=payload.name, role=payload.role)
    db.add(user)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Email already exists") from exc
    await db.refresh(user)
    return user


@router.patch("/{user_id}/role", response_model=UserRead)
async def update_role(user_id: int, payload: RoleUpdate, db: AsyncSession = Depends(get_db), _: User = Depends(require_roles(UserRole.ADMIN))) -> User:
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = payload.role
    await db.commit()
    await db.refresh(user)
    return user
