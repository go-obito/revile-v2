from fastapi import HTTPException, Request, status

from app.cache import rate_limit


def client_ip_from_request(request: Request) -> str:
    return request.headers.get("x-real-ip", "").strip() or (request.client.host if request.client else "unknown")


async def enforce_rate_limit(request: Request, bucket: str, limit: int, window_seconds: int) -> None:
    client_ip = client_ip_from_request(request)
    allowed = await rate_limit(f"ratelimit:{bucket}:{client_ip}", limit, window_seconds)
    if not allowed:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many requests")
