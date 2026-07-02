"""Add sync tracking fields to email delivery attempts.

Revision ID: 20260702_0008
Revises: 20260702_0007
Create Date: 2026-07-02
"""

from typing import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "20260702_0008"
down_revision: str | None = "20260702_0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "email_delivery_attempts",
        sa.Column("sync_status", sa.String(length=30), nullable=True),
    )
    op.add_column(
        "email_delivery_attempts",
        sa.Column("sync_fetched_count", sa.Integer(), nullable=True),
    )
    op.add_column(
        "email_delivery_attempts",
        sa.Column("sync_saved_count", sa.Integer(), nullable=True),
    )
    op.add_column(
        "email_delivery_attempts",
        sa.Column("sync_error_message", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("email_delivery_attempts", "sync_error_message")
    op.drop_column("email_delivery_attempts", "sync_saved_count")
    op.drop_column("email_delivery_attempts", "sync_fetched_count")
    op.drop_column("email_delivery_attempts", "sync_status")
