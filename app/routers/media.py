from uuid import uuid4

import boto3
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db import get_db
from app.models import Media, User
from app.schemas import MediaUploadRequest, MediaUploadResponse
from app.security import get_current_user

router = APIRouter(prefix="/media", tags=["media"])
settings = get_settings()


@router.post("/upload-url", response_model=MediaUploadResponse)
async def create_upload_url(payload: MediaUploadRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)) -> MediaUploadResponse:
    if not settings.s3_bucket_name:
        raise HTTPException(status_code=503, detail="Media storage is not configured")
    key = f"media/{uuid4()}-{payload.filename}"
    client = boto3.client("s3", region_name=settings.aws_region, aws_access_key_id=settings.aws_access_key_id, aws_secret_access_key=settings.aws_secret_access_key)
    upload_url = client.generate_presigned_url("put_object", Params={"Bucket": settings.s3_bucket_name, "Key": key, "ContentType": payload.content_type}, ExpiresIn=900)
    media_url = f"https://{settings.s3_bucket_name}.s3.{settings.aws_region}.amazonaws.com/{key}"
    media = Media(s3_url=media_url, alt_text=payload.alt_text, uploaded_by=user.id, post_id=payload.post_id)
    db.add(media)
    await db.commit()
    await db.refresh(media)
    return MediaUploadResponse(upload_url=upload_url, media_url=media_url, media_id=media.id)
