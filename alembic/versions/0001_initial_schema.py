"""Initial Revile schema.

Revision ID: 0001_initial_schema
Revises:
"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    user_role = sa.Enum("admin", "editor", "author", "reader", name="userrole")
    post_status = sa.Enum("draft", "scheduled", "published", "archived", name="poststatus")
    comment_status = sa.Enum("pending", "approved", "spam", "rejected", name="commentstatus")

    op.create_table("users", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("email", sa.String(320), nullable=False), sa.Column("hashed_password", sa.String(255), nullable=False), sa.Column("name", sa.String(200), nullable=False), sa.Column("role", user_role, nullable=False, server_default="reader"), sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.UniqueConstraint("email"))
    op.create_index("ix_users_email", "users", ["email"], unique=False)
    op.create_index("ix_users_role", "users", ["role"], unique=False)
    op.create_table("categories", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(100), nullable=False), sa.Column("slug", sa.String(120), nullable=False), sa.UniqueConstraint("name"), sa.UniqueConstraint("slug"))
    op.create_index("ix_categories_slug", "categories", ["slug"], unique=False)
    op.create_table("tags", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(100), nullable=False), sa.Column("slug", sa.String(120), nullable=False), sa.UniqueConstraint("name"), sa.UniqueConstraint("slug"))
    op.create_index("ix_tags_slug", "tags", ["slug"], unique=False)
    op.create_table("refresh_tokens", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("token_hash", sa.String(128), nullable=False), sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False), sa.Column("revoked_at", sa.DateTime(timezone=True)), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.UniqueConstraint("token_hash"))
    op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"], unique=False)
    op.create_index("ix_refresh_tokens_token_hash", "refresh_tokens", ["token_hash"], unique=False)
    op.create_table("posts", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("title", sa.String(300), nullable=False), sa.Column("slug", sa.String(320), nullable=False), sa.Column("dek", sa.String(500)), sa.Column("body", sa.Text(), nullable=False), sa.Column("status", post_status, nullable=False, server_default="draft"), sa.Column("is_breaking", sa.Boolean(), nullable=False, server_default=sa.false()), sa.Column("author_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("editor_id", sa.Integer(), sa.ForeignKey("users.id")), sa.Column("published_at", sa.DateTime(timezone=True)), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("search_vector", postgresql.TSVECTOR()), sa.UniqueConstraint("slug"))
    op.create_index("ix_posts_slug", "posts", ["slug"], unique=False)
    op.create_index("ix_posts_status", "posts", ["status"], unique=False)
    op.create_index("ix_posts_is_breaking", "posts", ["is_breaking"], unique=False)
    op.create_index("ix_posts_author_id", "posts", ["author_id"], unique=False)
    op.create_index("ix_posts_editor_id", "posts", ["editor_id"], unique=False)
    op.create_index("ix_posts_published_at", "posts", ["published_at"], unique=False)
    op.create_index("ix_posts_published_feed", "posts", ["status", "published_at", "id"], unique=False)
    op.create_index("ix_posts_breaking", "posts", ["is_breaking", "status", "published_at"], unique=False)
    op.execute("CREATE INDEX ix_posts_search_vector ON posts USING GIN (search_vector)")
    op.create_table("post_revisions", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("post_id", sa.Integer(), sa.ForeignKey("posts.id", ondelete="CASCADE"), nullable=False), sa.Column("body_snapshot", sa.Text(), nullable=False), sa.Column("edited_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_post_revisions_post_id", "post_revisions", ["post_id"], unique=False)
    op.create_index("ix_post_revisions_edited_by", "post_revisions", ["edited_by"], unique=False)
    op.create_table("post_categories", sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True), sa.Column("post_id", sa.Integer(), sa.ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True))
    op.create_table("post_tags", sa.Column("tag_id", sa.Integer(), sa.ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True), sa.Column("post_id", sa.Integer(), sa.ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True))
    op.create_table("comments", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("post_id", sa.Integer(), sa.ForeignKey("posts.id", ondelete="CASCADE"), nullable=False), sa.Column("parent_id", sa.Integer(), sa.ForeignKey("comments.id", ondelete="CASCADE")), sa.Column("author_name", sa.String(120), nullable=False), sa.Column("author_email", sa.String(320), nullable=False), sa.Column("body", sa.Text(), nullable=False), sa.Column("status", comment_status, nullable=False, server_default="pending"), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_comments_post_id", "comments", ["post_id"], unique=False)
    op.create_index("ix_comments_status", "comments", ["status"], unique=False)
    op.create_index("ix_comments_post_status", "comments", ["post_id", "status", "created_at"], unique=False)
    op.create_table("media", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("s3_url", sa.String(1000), nullable=False), sa.Column("alt_text", sa.String(300), nullable=False), sa.Column("uploaded_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("post_id", sa.Integer(), sa.ForeignKey("posts.id", ondelete="SET NULL")), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_media_uploaded_by", "media", ["uploaded_by"], unique=False)
    op.create_index("ix_media_post_id", "media", ["post_id"], unique=False)
    op.execute("CREATE FUNCTION posts_search_vector_update() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN NEW.search_vector := to_tsvector('english', coalesce(NEW.title, '') || ' ' || coalesce(NEW.body, '')); RETURN NEW; END $$")
    op.execute("CREATE TRIGGER posts_search_vector_trigger BEFORE INSERT OR UPDATE OF title, body ON posts FOR EACH ROW EXECUTE FUNCTION posts_search_vector_update()")


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS posts_search_vector_trigger ON posts")
    op.execute("DROP FUNCTION IF EXISTS posts_search_vector_update()")
    for table in ("media", "comments", "post_tags", "post_categories", "post_revisions", "posts", "refresh_tokens", "tags", "categories", "users"):
        op.drop_table(table)
    for enum_name in ("commentstatus", "poststatus", "userrole"):
        sa.Enum(name=enum_name).drop(op.get_bind(), checkfirst=True)
