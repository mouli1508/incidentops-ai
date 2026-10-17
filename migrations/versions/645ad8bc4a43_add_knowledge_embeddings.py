"""add knowledge embeddings

Revision ID: 645ad8bc4a43
Revises: 611f8c0bcdab
Create Date: 2026-10-17 13:38:50.598239

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import VECTOR


# revision identifiers, used by Alembic.
revision: str = '645ad8bc4a43'
down_revision: Union[str, Sequence[str], None] = '611f8c0bcdab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.add_column(
        "knowledge_chunks",
        sa.Column(
            "embedding",
            VECTOR(384),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "knowledge_chunks",
        "embedding",
    )