"""phase7_3_reports_and_scheduling

Revision ID: 019b50d90edb
Revises: phase7_001
Create Date: 2026-09-18 01:44:36.618749

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '019b50d90edb'
down_revision: Union[str, None] = 'phase7_001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create reports table
    op.create_table(
        'reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('report_id', sa.String(50), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('audit_id', sa.Integer(), nullable=True),
        sa.Column('report_type', sa.String(50), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('format', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('generated_by', sa.String(255), nullable=False),
        sa.Column('generated_at', sa.DateTime(), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['audit_id'], ['audits.id'])
    )
    op.create_index('ix_reports_report_id', 'reports', ['report_id'], unique=True)
    op.create_index('ix_reports_organization_id', 'reports', ['organization_id'])


def downgrade() -> None:
    op.drop_index('ix_reports_organization_id', 'reports')
    op.drop_index('ix_reports_report_id', 'reports')
    op.drop_table('reports')
