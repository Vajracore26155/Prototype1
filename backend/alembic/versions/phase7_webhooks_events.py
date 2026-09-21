"""Phase 7: Webhooks and Events System

Revision ID: phase7_001
Revises: phase5_001
Create Date: 2024-12-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'phase7_001'
down_revision = 'phase5_001'
branch_labels = None
depends_on = None


def upgrade():
    # Webhooks table
    op.create_table(
        'webhooks',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('webhook_id', sa.String(50), unique=True, index=True, nullable=False),
        sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organizations.id'), nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('url', sa.String(500), nullable=False),
        sa.Column('secret', sa.String(255), nullable=False),
        sa.Column('event_types', sa.JSON(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True, index=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('headers', sa.JSON(), nullable=True),
        sa.Column('retry_count', sa.Integer(), default=3),
        sa.Column('timeout_seconds', sa.Integer(), default=30),
        sa.Column('created_by', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), index=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('last_triggered_at', sa.DateTime(), nullable=True),
        sa.Column('total_deliveries', sa.Integer(), default=0),
        sa.Column('successful_deliveries', sa.Integer(), default=0),
        sa.Column('failed_deliveries', sa.Integer(), default=0)
    )
    
    # Webhook Deliveries table (delivery tracking)
    op.create_table(
        'webhook_deliveries',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('delivery_id', sa.String(50), unique=True, index=True, nullable=False),
        sa.Column('webhook_id', sa.Integer(), sa.ForeignKey('webhooks.id'), nullable=False, index=True),
        sa.Column('event_id', sa.String(50), nullable=False, index=True),
        sa.Column('event_type', sa.String(100), nullable=False, index=True),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, index=True),
        sa.Column('http_status', sa.Integer(), nullable=True),
        sa.Column('response_body', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('attempt_count', sa.Integer(), default=0),
        sa.Column('next_retry_at', sa.DateTime(), nullable=True, index=True),
        sa.Column('delivered_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), index=True)
    )
    
    # Event Log table (persistent event storage)
    op.create_table(
        'event_log',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('event_id', sa.String(50), unique=True, index=True, nullable=False),
        sa.Column('event_type', sa.String(100), nullable=False, index=True),
        sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organizations.id'), nullable=False, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True, index=True),
        sa.Column('resource_type', sa.String(50), nullable=False, index=True),
        sa.Column('resource_id', sa.String(50), nullable=False, index=True),
        sa.Column('data', sa.JSON(), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), server_default=sa.text('now()'), index=True)
    )


def downgrade():
    op.drop_table('event_log')
    op.drop_table('webhook_deliveries')
    op.drop_table('webhooks')
