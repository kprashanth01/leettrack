"""create problem notes

Revision ID: 20260701_0004
Revises: 20260701_0003
Create Date: 2026-07-01
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260701_0004"
down_revision: str | None = "20260701_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "problem_notes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(length=255), nullable=False),
        sa.Column("problem_id", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["problem_id"],
            ["problems.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_problem_notes_problem_id",
        "problem_notes",
        ["problem_id"],
    )
    op.create_index("ix_problem_notes_user_id", "problem_notes", ["user_id"])
    op.create_index(
        "ix_problem_notes_user_problem",
        "problem_notes",
        ["user_id", "problem_id"],
    )
    op.create_index(
        "ix_problem_notes_user_updated_at",
        "problem_notes",
        ["user_id", "updated_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_problem_notes_user_updated_at", table_name="problem_notes")
    op.drop_index("ix_problem_notes_user_problem", table_name="problem_notes")
    op.drop_index("ix_problem_notes_user_id", table_name="problem_notes")
    op.drop_index("ix_problem_notes_problem_id", table_name="problem_notes")
    op.drop_table("problem_notes")
