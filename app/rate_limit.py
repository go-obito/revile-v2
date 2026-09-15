from fastapi import HTTPException, Request, status

from app.cache import rate_limit


async def enforce_rate_limit(request: Request, bucket: str, limit: int, window_seconds: int) -> None:
    client_ip = request.client.host if request.client else "unknown"
    allowed = await rate_limit(f"ratelimit:{bucket}:{client_ip}", limit, window_seconds)
    if not allowed:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many requests")
