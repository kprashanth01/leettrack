"""create email preferences

Revision ID: 20260702_0006
Revises: 20260702_0005
Create Date: 2026-07-02
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260702_0006"
down_revision: str | None = "20260702_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "email_preferences",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(length=255), nullable=False),
        sa.Column("weekly_summary_enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_email_preferences_user_id"),
    )
    op.create_index("ix_email_preferences_user_id", "email_preferences", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_email_preferences_user_id", table_name="email_preferences")
    op.drop_table("email_preferences")
