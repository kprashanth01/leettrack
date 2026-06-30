"""create leetcode sync tables

Revision ID: 20260701_0001
Revises:
Create Date: 2026-07-01
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260701_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "leetcode_accounts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_leetcode_accounts_username"),
        "leetcode_accounts",
        ["username"],
        unique=True,
    )

    op.create_table(
        "problems",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("platform", sa.String(length=30), nullable=False),
        sa.Column("platform_slug", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "platform",
            "platform_slug",
            name="uq_problems_platform_slug",
        ),
    )
    op.create_index(op.f("ix_problems_platform"), "problems", ["platform"], unique=False)
    op.create_index(
        op.f("ix_problems_platform_slug"),
        "problems",
        ["platform_slug"],
        unique=False,
    )

    op.create_table(
        "submissions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("leetcode_account_id", sa.Integer(), nullable=False),
        sa.Column("problem_id", sa.Integer(), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("language", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["leetcode_account_id"],
            ["leetcode_accounts.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["problem_id"], ["problems.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "leetcode_account_id",
            "problem_id",
            "submitted_at",
            name="uq_submissions_account_problem_submitted_at",
        ),
    )
    op.create_index(
        "ix_submissions_account_submitted_at",
        "submissions",
        ["leetcode_account_id", "submitted_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_submissions_leetcode_account_id"),
        "submissions",
        ["leetcode_account_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_submissions_problem_id"),
        "submissions",
        ["problem_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_submissions_problem_id"), table_name="submissions")
    op.drop_index(op.f("ix_submissions_leetcode_account_id"), table_name="submissions")
    op.drop_index("ix_submissions_account_submitted_at", table_name="submissions")
    op.drop_table("submissions")
    op.drop_index(op.f("ix_problems_platform_slug"), table_name="problems")
    op.drop_index(op.f("ix_problems_platform"), table_name="problems")
    op.drop_table("problems")
    op.drop_index(op.f("ix_leetcode_accounts_username"), table_name="leetcode_accounts")
    op.drop_table("leetcode_accounts")
