"""remove module_path

Revision ID: 004
Revises: 003
Create Date: 2024-01-01 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if column exists before dropping
    conn = op.get_bind()
    inspector = inspect(conn)
    columns = [col["name"] for col in inspector.get_columns("problems")]
    
    if "module_path" in columns:
        op.drop_column("problems", "module_path")


def downgrade() -> None:
    op.add_column("problems", sa.Column("module_path", sa.String(), nullable=False, server_default=""))
