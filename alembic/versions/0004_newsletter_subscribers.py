"""add newsletter subscribers

Revision ID: 0004_newsletter_subscribers
Revises: 0003_harden_comments
Create Date: 2026-09-21
"""

import sqlalchemy as sa

from alembic import op

revision = "0004_newsletter_subscribers"
down_revision = "0003_harden_comments"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "newsletter_subscribers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("confirmation_token_hash", sa.String(length=64), nullable=True),
        sa.Column("confirmation_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("unsubscribe_token_hash", sa.String(length=64), nullable=False),
        sa.Column("resend_contact_id", sa.String(length=255), nullable=True),
        sa.Column("consented_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("unsubscribed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_newsletter_subscribers_email", "newsletter_subscribers", ["email"], unique=True)
    op.create_index("ix_newsletter_subscribers_status", "newsletter_subscribers", ["status"])
    op.create_index("ix_newsletter_subscribers_confirmation_token_hash", "newsletter_subscribers", ["confirmation_token_hash"], unique=True)
    op.create_index("ix_newsletter_subscribers_unsubscribe_token_hash", "newsletter_subscribers", ["unsubscribe_token_hash"], unique=True)


def downgrade() -> None:
    op.drop_table("newsletter_subscribers")
