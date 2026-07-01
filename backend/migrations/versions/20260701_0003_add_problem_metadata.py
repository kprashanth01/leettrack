"""add problem metadata

Revision ID: 20260701_0003
Revises: 20260701_0002
Create Date: 2026-07-01
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260701_0003"
down_revision: str | None = "20260701_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("problems") as batch_op:
        batch_op.add_column(sa.Column("difficulty", sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column("topic_tags", sa.JSON(), nullable=True))

    op.execute("UPDATE problems SET topic_tags = '[]' WHERE topic_tags IS NULL")


def downgrade() -> None:
    with op.batch_alter_table("problems") as batch_op:
        batch_op.drop_column("topic_tags")
        batch_op.drop_column("difficulty")
