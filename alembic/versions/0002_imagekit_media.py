"""Migrate media metadata from S3-specific URLs to ImageKit metadata.

Revision ID: 0002_imagekit_media
Revises: 0001_initial_schema
Create Date: 2026-09-21
"""

import sqlalchemy as sa

from alembic import op

revision = "0002_imagekit_media"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("media", "s3_url", new_column_name="file_url")
    op.add_column("media", sa.Column("imagekit_file_id", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("media", "imagekit_file_id")
    op.alter_column("media", "file_url", new_column_name="s3_url")
