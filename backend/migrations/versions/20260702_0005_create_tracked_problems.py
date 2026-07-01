"""create tracked problems

Revision ID: 20260702_0005
Revises: 20260701_0004
Create Date: 2026-07-02
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260702_0005"
down_revision: str | None = "20260701_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "tracked_problems",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(length=255), nullable=False),
        sa.Column("problem_id", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["problem_id"],
            ["problems.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "problem_id",
            name="uq_tracked_problems_user_problem",
        ),
    )
    op.create_index(
        "ix_tracked_problems_problem_id",
        "tracked_problems",
        ["problem_id"],
    )
    op.create_index("ix_tracked_problems_user_id", "tracked_problems", ["user_id"])
    op.create_index(
        "ix_tracked_problems_user_created_at",
        "tracked_problems",
        ["user_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_tracked_problems_user_created_at", table_name="tracked_problems")
    op.drop_index("ix_tracked_problems_user_id", table_name="tracked_problems")
    op.drop_index("ix_tracked_problems_problem_id", table_name="tracked_problems")
    op.drop_table("tracked_problems")
