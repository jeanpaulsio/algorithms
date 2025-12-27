"""change id to uuid

Revision ID: 002
Revises: 001
Create Date: 2024-01-01 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the table if it exists with old schema, then recreate
    # This is safe for development - for production you'd want to migrate data
    op.drop_table("problems", if_exists=True)
    op.create_table(
        "problems",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("function_name", sa.String(), nullable=False),
        sa.Column("starter_code", sa.Text(), nullable=False),
        sa.Column("test_code", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_problems_id"), "problems", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_problems_id"), table_name="problems")
    op.drop_table("problems")
