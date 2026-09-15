# Revile Backend

Production-oriented FastAPI backend for a news-first technology publication.

## Stack

- Python 3.12, FastAPI, Pydantic v2
- PostgreSQL with SQLAlchemy 2 async and Alembic
- Redis caching and IP rate limiting
- JWT access tokens plus rotated, hashed httpOnly refresh cookies
- AWS S3 presigned uploads
- APScheduler for scheduled publishing, sitemap, and RSS generation

## Local setup

1. Install Python 3.12 and `uv`.
2. Copy `.env.example` to `.env` and replace `JWT_SECRET` and `ADMIN_PASSWORD`.
3. Start local services:

```powershell
docker compose up -d postgres redis
uv sync
uv run alembic upgrade head
uv run python -m scripts.seed
uv run uvicorn main:app --reload
```

The API is available at `http://localhost:8000`; interactive docs are at `/docs` and the load-balancer check is `/healthz`.

## Docker development

```powershell
Copy-Item .env.example .env
docker compose up --build
```

The app container runs migrations before starting Uvicorn. PostgreSQL and Redis data persist in the `postgres_data` volume.

## Migrations

Create a migration after changing models:

```powershell
uv run alembic revision --autogenerate -m "describe change"
uv run alembic upgrade head
```

Never edit production schema manually. Review generated migrations before applying them.

## Authentication

`POST /api/v1/auth/login` returns a short-lived bearer access token and sets a rotated refresh token cookie. Send the access token as `Authorization: Bearer <token>`. `POST /api/v1/auth/refresh` rotates the cookie; `POST /api/v1/auth/logout` revokes it.

The first admin is created by `uv run python -m scripts.seed` using `ADMIN_EMAIL`, `ADMIN_PASSWORD`, and `ADMIN_NAME`.

## API areas

Public reads: `/api/v1/posts`, `/api/v1/posts/{slug}`, `/api/v1/posts/breaking`, `/api/v1/categories`, `/api/v1/categories/{slug}/posts`, and `/api/v1/search`.

Editorial and authenticated operations cover post creation/editing, publish/schedule/unpublish, breaking flags, moderation, users, and S3 upload URLs. Anonymous comments are accepted as pending and rate-limited per IP.

## Railway deployment

1. Create a Railway project and add a PostgreSQL service and Redis service.
2. Deploy this repository; Railway uses `railway.json` and the Dockerfile.
3. Set `DATABASE_URL` and `REDIS_URL` from the Railway service references.
4. Set `JWT_SECRET`, `FRONTEND_ORIGIN`, `S3_BUCKET_NAME`, AWS credentials, and admin seed variables in Railway Variables. Use a generated secret for `JWT_SECRET` and never commit it.
5. Railway runs `alembic upgrade head` before Uvicorn and checks `/healthz`.

For production, set `COOKIE_SECURE=true`, use HTTPS, restrict the frontend origin to the real site, and configure an S3 bucket policy appropriate for presigned uploads.

## Tests and checks

```powershell
uv run pytest
uv run ruff check .
uv run python -m compileall -q app alembic scripts main.py
```
