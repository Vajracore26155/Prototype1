"""add_file_hash_to_configuration

Revision ID: c0b1201f4f27
Revises: a281c81fb595
Create Date: 2026-09-17 15:42:01.535713

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c0b1201f4f27'
down_revision: Union[str, None] = 'a281c81fb595'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add file_hash_sha256 column to configurations table
    op.add_column('configurations', sa.Column('file_hash_sha256', sa.String(length=64), nullable=True))
    op.create_index(op.f('ix_configurations_file_hash_sha256'), 'configurations', ['file_hash_sha256'], unique=False)


def downgrade() -> None:
    # Remove file_hash_sha256 column and index
    op.drop_index(op.f('ix_configurations_file_hash_sha256'), table_name='configurations')
    op.drop_column('configurations', 'file_hash_sha256')
