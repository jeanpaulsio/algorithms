"""add category

Revision ID: 003
Revises: 002
Create Date: 2024-01-01 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("problems", sa.Column("category", sa.String(), nullable=False, server_default="arrays-and-strings"))
    op.create_index(op.f("ix_problems_category"), "problems", ["category"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_problems_category"), table_name="problems")
    op.drop_column("problems", "category")
