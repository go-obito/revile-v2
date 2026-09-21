from fastapi import APIRouter, Depends, HTTPException
from imagekitio import ImageKit
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db import get_db
from app.models import Media, User
from app.schemas import ImageKitAuthResponse, MediaCreate, MediaRead
from app.security import get_current_user

router = APIRouter(prefix="/media", tags=["media"])
settings = get_settings()


@router.get("/imagekit-auth", response_model=ImageKitAuthResponse)
async def get_imagekit_authentication(_: User = Depends(get_current_user)) -> ImageKitAuthResponse:
    if not settings.imagekit_private_key:
        raise HTTPException(status_code=503, detail="ImageKit is not configured")
    auth_params = ImageKit(private_key=settings.imagekit_private_key).helper.get_authentication_parameters()
    return ImageKitAuthResponse(**auth_params)


@router.post("", response_model=MediaRead, status_code=201)
async def create_media_record(
    payload: MediaCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MediaRead:
    media = Media(
        file_url=payload.file_url,
        imagekit_file_id=payload.imagekit_file_id,
        alt_text=payload.alt_text,
        uploaded_by=user.id,
        post_id=payload.post_id,
    )
    db.add(media)
    await db.commit()
    await db.refresh(media)
    return MediaRead.model_validate(media)
