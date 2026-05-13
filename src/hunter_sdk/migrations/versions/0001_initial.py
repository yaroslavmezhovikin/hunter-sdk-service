"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-05-08

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "verifications",
        sa.Column("record_id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("operation", sa.String(length=64), nullable=False),
        sa.Column("query", JSONB(), nullable=False),
        sa.Column("response", JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_verifications_operation",
        "verifications",
        ["operation"],
    )
    op.create_index(
        "ix_verifications_created_at",
        "verifications",
        ["created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_verifications_created_at", table_name="verifications")
    op.drop_index("ix_verifications_operation", table_name="verifications")
    op.drop_table("verifications")
