from datetime import datetime
from uuid import UUID

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


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    slug: str


class TagRead(CategoryRead):
    pass


class PostRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    slug: str
    dek: str | None
    body: str
    featured_image_url: str | None = None
    featured_image_alt: str = ""
    status: PostStatus
    is_breaking: bool
    author_id: int
    author_name: str | None = None
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
    idempotency_key: UUID

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
    categories: list[CategoryRead] = Field(default_factory=list)
    tags: list[TagRead] = Field(default_factory=list)


class ModerationCommentRead(CommentRead):
    spam_score: float | None = None
    spam_reason: str | None = None


class CommentReportCreate(BaseModel):
    reason: str = Field(min_length=3, max_length=500)

    @field_validator("reason")
    @classmethod
    def clean_reason(cls, value: str) -> str:
        return sanitize_comment(value)


class CommentReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    comment_id: int
    reason: str
    reported_at: datetime


class ReportedCommentRead(ModerationCommentRead):
    reports: list[CommentReportRead]


class CommentAuditRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    comment_id: int
    actor_id: int
    action: str
    created_at: datetime


class ModerationUpdate(BaseModel):
    status: CommentStatus

    @field_validator("status")
    @classmethod
    def allow_only_moderation_outcomes(cls, value: CommentStatus) -> CommentStatus:
        if value not in {CommentStatus.APPROVED, CommentStatus.REJECTED, CommentStatus.SPAM, CommentStatus.FLAGGED}:
            raise ValueError("Status is not a moderation outcome")
        return value


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    slug: str = Field(min_length=1, max_length=120)


class TagCreate(CategoryCreate):
    pass


class NewsletterSubscribe(BaseModel):
    email: EmailStr


class ImageKitAuthResponse(BaseModel):
    token: str
    expire: int
    signature: str


class MediaCreate(BaseModel):
    file_url: str = Field(min_length=1, max_length=1000)
    imagekit_file_id: str = Field(min_length=1, max_length=255)
    alt_text: str = Field(min_length=1, max_length=300)
    post_id: int | None = None


class MediaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    file_url: str
    imagekit_file_id: str
    alt_text: str
    post_id: int | None


class CursorPage(BaseModel):
    cursor: str | None = None
    limit: int = Field(default=20, ge=1, le=100)
