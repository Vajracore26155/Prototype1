"""Phase 10: Vendor OTP System

Revision ID: phase10_vendor_otp
Revises: 019b50d90edb
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'phase10_vendor_otp'
down_revision = '019b50d90edb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create vendor system tables"""
    
    # Create vendor_users table
    op.create_table(
        'vendor_users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('vendor_id', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('company_name', sa.String(length=255), nullable=False),
        sa.Column('contact_name', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('email_verified', sa.Boolean(), nullable=True, default=False),
        sa.Column('verification_token', sa.String(length=255), nullable=True),
        sa.Column('verified_at', sa.DateTime(), nullable=True),
        sa.Column('approval_status', sa.String(length=50), nullable=True, default='PENDING'),
        sa.Column('approved_by', sa.String(length=255), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('devices', sa.JSON(), nullable=True),
        sa.Column('vendor_metadata', sa.JSON(), nullable=True),
        sa.Column('last_otp_sent', sa.DateTime(), nullable=True),
        sa.Column('otp_attempts', sa.Integer(), nullable=True, default=0),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('vendor_id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_vendor_users_vendor_id'), 'vendor_users', ['vendor_id'], unique=True)
    op.create_index(op.f('ix_vendor_users_email'), 'vendor_users', ['email'], unique=True)
    
    # Create vendor_otps table
    op.create_table(
        'vendor_otps',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('otp_id', sa.String(length=50), nullable=False),
        sa.Column('vendor_id', sa.Integer(), nullable=False),
        sa.Column('otp_code', sa.String(length=10), nullable=False),
        sa.Column('otp_hash', sa.String(length=255), nullable=False),
        sa.Column('is_used', sa.Boolean(), nullable=True, default=False),
        sa.Column('used_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('verification_attempts', sa.Integer(), nullable=True, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendor_users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('otp_id')
    )
    op.create_index(op.f('ix_vendor_otps_otp_id'), 'vendor_otps', ['otp_id'], unique=True)
    
    # Create vendor_upload_sessions table
    op.create_table(
        'vendor_upload_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(length=50), nullable=False),
        sa.Column('vendor_id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('otp_id', sa.Integer(), nullable=False),
        sa.Column('session_token', sa.String(length=255), nullable=False),
        sa.Column('files_uploaded', sa.JSON(), nullable=True),
        sa.Column('upload_count', sa.Integer(), nullable=True, default=0),
        sa.Column('status', sa.String(length=50), nullable=True, default='ACTIVE'),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('last_activity', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendor_users.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['otp_id'], ['vendor_otps.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_id'),
        sa.UniqueConstraint('session_token')
    )
    op.create_index(op.f('ix_vendor_upload_sessions_session_id'), 'vendor_upload_sessions', ['session_id'], unique=True)
    
    # Create vendor_approval_requests table
    op.create_table(
        'vendor_approval_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('request_id', sa.String(length=50), nullable=False),
        sa.Column('vendor_id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('request_type', sa.String(length=50), nullable=True, default='NEW_VENDOR'),
        sa.Column('request_message', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True, default='PENDING'),
        sa.Column('reviewed_by', sa.String(length=255), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendor_users.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('request_id')
    )
    op.create_index(op.f('ix_vendor_approval_requests_request_id'), 'vendor_approval_requests', ['request_id'], unique=True)


def downgrade() -> None:
    """Drop vendor system tables"""
    op.drop_index(op.f('ix_vendor_approval_requests_request_id'), table_name='vendor_approval_requests')
    op.drop_table('vendor_approval_requests')
    
    op.drop_index(op.f('ix_vendor_upload_sessions_session_id'), table_name='vendor_upload_sessions')
    op.drop_table('vendor_upload_sessions')
    
    op.drop_index(op.f('ix_vendor_otps_otp_id'), table_name='vendor_otps')
    op.drop_table('vendor_otps')
    
    op.drop_index(op.f('ix_vendor_users_email'), table_name='vendor_users')
    op.drop_index(op.f('ix_vendor_users_vendor_id'), table_name='vendor_users')
    op.drop_table('vendor_users')
