from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models import CommentStatus, PostStatus, UserRole
from app.sanitize import sanitize_comment, sanitize_markdown


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    name: str
    role: UserRole
    is_active: bool
    created_at: datetime


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(min_length=1, max_length=200)
    role: UserRole = UserRole.READER


class RoleUpdate(BaseModel):
    role: UserRole


class PostCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    slug: str = Field(min_length=1, max_length=320)
    dek: str | None = Field(default=None, max_length=500)
    body: str = Field(min_length=1)
    category_ids: list[int] = Field(default_factory=list)
    tag_ids: list[int] = Field(default_factory=list)
    is_breaking: bool = False

    @field_validator("body")
    @classmethod
    def clean_body(cls, value: str) -> str:
        return sanitize_markdown(value)


class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=300)
    slug: str | None = Field(default=None, min_length=1, max_length=320)
    dek: str | None = Field(default=None, max_length=500)
    body: str | None = None
    category_ids: list[int] | None = None
    tag_ids: list[int] | None = None
    is_breaking: bool | None = None

    @field_validator("body")
    @classmethod
    def clean_body(cls, value: str | None) -> str | None:
        return sanitize_markdown(value) if value is not None else None


class PostRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    slug: str
    dek: str | None
    body: str
    status: PostStatus
    is_breaking: bool
    author_id: int
    editor_id: int | None
    published_at: datetime | None
    updated_at: datetime
    created_at: datetime


class PostList(BaseModel):
    items: list[PostRead]
    next_cursor: str | None = None


class CommentCreate(BaseModel):
    author_name: str = Field(min_length=1, max_length=120)
    author_email: EmailStr
    body: str = Field(min_length=1, max_length=5000)
    parent_id: int | None = None

    @field_validator("body")
    @classmethod
    def clean_body(cls, value: str) -> str:
        return sanitize_comment(value)


class CommentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    post_id: int
    parent_id: int | None
    author_name: str
    body: str
    status: CommentStatus
    created_at: datetime


class ModerationUpdate(BaseModel):
    status: CommentStatus


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    slug: str = Field(min_length=1, max_length=120)


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    slug: str


class TagCreate(CategoryCreate):
    pass


class MediaUploadRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    content_type: str = Field(pattern=r"^[\w.-]+/[\w.+-]+$")
    alt_text: str = Field(min_length=1, max_length=300)
    post_id: int | None = None


class MediaUploadResponse(BaseModel):
    upload_url: str
    media_url: str
    media_id: int


class CursorPage(BaseModel):
    cursor: str | None = None
    limit: int = Field(default=20, ge=1, le=100)
