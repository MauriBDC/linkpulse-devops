"""Create the links table.

Revision ID: 0001
Revises:
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "links",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("original_url", sa.String(length=2048), nullable=False),
        sa.Column("short_code", sa.String(length=16), nullable=False),
        sa.Column("clicks", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_accessed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_links_short_code", "links", ["short_code"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_links_short_code", table_name="links")
    op.drop_table("links")
