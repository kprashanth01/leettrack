"""create email delivery attempts

Revision ID: 20260702_0007
Revises: 20260702_0006
Create Date: 2026-07-02
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260702_0007"
down_revision: str | None = "20260702_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "email_preferences",
        sa.Column("recipient_email", sa.String(length=320), nullable=True),
    )
    op.create_index(
        "ix_email_preferences_recipient_email",
        "email_preferences",
        ["recipient_email"],
    )
    op.create_table(
        "email_delivery_attempts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(length=255), nullable=False),
        sa.Column("recipient_email", sa.String(length=320), nullable=False),
        sa.Column("email_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("provider_message_id", sa.String(length=255), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_email_delivery_attempts_email_type",
        "email_delivery_attempts",
        ["email_type"],
    )
    op.create_index(
        "ix_email_delivery_attempts_period_start",
        "email_delivery_attempts",
        ["period_start"],
    )
    op.create_index(
        "ix_email_delivery_attempts_recipient_email",
        "email_delivery_attempts",
        ["recipient_email"],
    )
    op.create_index(
        "ix_email_delivery_attempts_status",
        "email_delivery_attempts",
        ["status"],
    )
    op.create_index(
        "ix_email_delivery_attempts_user_id",
        "email_delivery_attempts",
        ["user_id"],
    )
    op.create_index(
        "ix_email_delivery_attempts_user_period",
        "email_delivery_attempts",
        ["user_id", "email_type", "period_start"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_email_delivery_attempts_user_period",
        table_name="email_delivery_attempts",
    )
    op.drop_index("ix_email_delivery_attempts_user_id", table_name="email_delivery_attempts")
    op.drop_index("ix_email_delivery_attempts_status", table_name="email_delivery_attempts")
    op.drop_index(
        "ix_email_delivery_attempts_recipient_email",
        table_name="email_delivery_attempts",
    )
    op.drop_index(
        "ix_email_delivery_attempts_period_start",
        table_name="email_delivery_attempts",
    )
    op.drop_index(
        "ix_email_delivery_attempts_email_type",
        table_name="email_delivery_attempts",
    )
    op.drop_table("email_delivery_attempts")
    op.drop_index("ix_email_preferences_recipient_email", table_name="email_preferences")
    op.drop_column("email_preferences", "recipient_email")
