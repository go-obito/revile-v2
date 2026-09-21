"""harden comments with idempotency, abuse records, and moderation audit history

Revision ID: 0003_harden_comments
Revises: 0002_imagekit_media
Create Date: 2026-09-21
"""

import sqlalchemy as sa

from alembic import op

revision = "0003_harden_comments"
down_revision = "0002_imagekit_media"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE commentstatus ADD VALUE IF NOT EXISTS 'flagged'")
    op.add_column("comments", sa.Column("idempotency_key", sa.String(length=36), nullable=True))
    op.add_column("comments", sa.Column("spam_score", sa.Float(), nullable=True))
    op.add_column("comments", sa.Column("spam_reason", sa.Text(), nullable=True))
    # Preserve every existing comment; these legacy keys are never supplied by
    # clients, but make the new uniqueness invariant valid immediately.
    op.execute(
        """
        UPDATE comments
        SET idempotency_key = substr(md5(id::text || clock_timestamp()::text), 1, 8) || '-' ||
                              substr(md5(id::text || clock_timestamp()::text), 9, 4) || '-' ||
                              substr(md5(id::text || clock_timestamp()::text), 13, 4) || '-' ||
                              substr(md5(id::text || clock_timestamp()::text), 17, 4) || '-' ||
                              substr(md5(id::text || clock_timestamp()::text), 21, 12)
        WHERE idempotency_key IS NULL
        """
    )
    op.alter_column("comments", "idempotency_key", nullable=False)
    op.create_index("ix_comments_idempotency_key", "comments", ["idempotency_key"], unique=True)
    op.create_table(
        "comment_reports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("comment_id", sa.Integer(), sa.ForeignKey("comments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reason", sa.String(length=500), nullable=False),
        sa.Column("reported_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_comment_reports_comment_id", "comment_reports", ["comment_id"])
    op.create_table(
        "comment_moderation_audits",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("comment_id", sa.Integer(), sa.ForeignKey("comments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("actor_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("action", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_comment_moderation_audits_comment_id", "comment_moderation_audits", ["comment_id"])
    op.create_index("ix_comment_moderation_audits_actor_id", "comment_moderation_audits", ["actor_id"])


def downgrade() -> None:
    op.drop_index("ix_comment_moderation_audits_actor_id", table_name="comment_moderation_audits")
    op.drop_index("ix_comment_moderation_audits_comment_id", table_name="comment_moderation_audits")
    op.drop_table("comment_moderation_audits")
    op.drop_index("ix_comment_reports_comment_id", table_name="comment_reports")
    op.drop_table("comment_reports")
    op.drop_index("ix_comments_idempotency_key", table_name="comments")
    op.drop_column("comments", "spam_reason")
    op.drop_column("comments", "spam_score")
    op.drop_column("comments", "idempotency_key")
    # PostgreSQL does not support dropping enum values; the two unused values
    # are intentionally retained on downgrade.
