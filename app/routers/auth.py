from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db import get_db
from app.models import RefreshToken, User
from app.schemas import LoginRequest, TokenResponse
from app.security import (
    create_access_token,
    create_refresh_token,
    hash_refresh_token,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


def set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie("refresh_token", token, httponly=True, secure=settings.cookie_secure, samesite="lax", max_age=settings.refresh_token_days * 86400, path="/")


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    user = await db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not user.is_active or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    raw_token, token_hash, expires_at = create_refresh_token()
    db.add(RefreshToken(user_id=user.id, token_hash=token_hash, expires_at=expires_at))
    await db.commit()
    set_refresh_cookie(response, raw_token)
    return TokenResponse(access_token=create_access_token(user), user=user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: Request, response: Response, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    raw_token = request.cookies.get("refresh_token")
    if not raw_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing")
    stored = await db.scalar(select(RefreshToken).where(RefreshToken.token_hash == hash_refresh_token(raw_token)))
    now = datetime.now(UTC)
    if not stored or stored.revoked_at or stored.expires_at <= now:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token invalid")
    user = await db.get(User, stored.user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User inactive")
    stored.revoked_at = now
    new_raw, new_hash, expires_at = create_refresh_token()
    db.add(RefreshToken(user_id=user.id, token_hash=new_hash, expires_at=expires_at))
    await db.commit()
    set_refresh_cookie(response, new_raw)
    return TokenResponse(access_token=create_access_token(user), user=user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(request: Request, response: Response, db: AsyncSession = Depends(get_db)) -> None:
    raw_token = request.cookies.get("refresh_token")
    if raw_token:
        stored = await db.scalar(select(RefreshToken).where(RefreshToken.token_hash == hash_refresh_token(raw_token)))
        if stored and not stored.revoked_at:
            stored.revoked_at = datetime.now(UTC)
            await db.commit()
    response.delete_cookie("refresh_token", path="/")
