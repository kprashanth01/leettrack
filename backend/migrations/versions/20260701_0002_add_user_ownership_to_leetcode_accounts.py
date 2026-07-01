"""add user ownership to leetcode accounts

Revision ID: 20260701_0002
Revises: 20260701_0001
Create Date: 2026-07-01
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260701_0002"
down_revision: str | None = "20260701_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("leetcode_accounts") as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.String(length=255), nullable=True))
        batch_op.drop_index("ix_leetcode_accounts_username")
        batch_op.create_index(
            op.f("ix_leetcode_accounts_username"),
            ["username"],
            unique=False,
        )
        batch_op.create_index(
            op.f("ix_leetcode_accounts_user_id"),
            ["user_id"],
            unique=False,
        )
        batch_op.create_unique_constraint(
            "uq_leetcode_accounts_user_username",
            ["user_id", "username"],
        )


def downgrade() -> None:
    with op.batch_alter_table("leetcode_accounts") as batch_op:
        batch_op.drop_constraint(
            "uq_leetcode_accounts_user_username",
            type_="unique",
        )
        batch_op.drop_index(op.f("ix_leetcode_accounts_user_id"))
        batch_op.drop_index(op.f("ix_leetcode_accounts_username"))
        batch_op.create_index(
            "ix_leetcode_accounts_username",
            ["username"],
            unique=True,
        )
        batch_op.drop_column("user_id")
