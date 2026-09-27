"""phase11_vendor_password_registration

Revision ID: phase11_vendor_password_registration
Revises: phase10_vendor_otp
Create Date: 2026-09-18 10:00:00.000000

Add username and password tracking fields to vendor_users table for optional password-based login.
This migration adds:
- username: Optional username field for vendors
- password_set_at: When vendor last set a password
- password_changed_at: When vendor changed their password
- last_login: When vendor last logged in
- last_login_method: How they logged in (PASSWORD, OTP)

Backward compatible - all fields are nullable/optional.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'phase11_vendor_password_registration'
down_revision = 'phase10_vendor_otp'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to vendor_users table
    op.add_column('vendor_users', sa.Column('username', sa.String(255), nullable=True, unique=True, index=True))
    op.add_column('vendor_users', sa.Column('password_set_at', sa.DateTime, nullable=True))
    op.add_column('vendor_users', sa.Column('password_changed_at', sa.DateTime, nullable=True))
    op.add_column('vendor_users', sa.Column('last_login', sa.DateTime, nullable=True))
    op.add_column('vendor_users', sa.Column('last_login_method', sa.String(50), nullable=True))  # PASSWORD or OTP


def downgrade() -> None:
    # Remove columns if migration is rolled back
    op.drop_column('vendor_users', 'last_login_method')
    op.drop_column('vendor_users', 'last_login')
    op.drop_column('vendor_users', 'password_changed_at')
    op.drop_column('vendor_users', 'password_set_at')
    op.drop_column('vendor_users', 'username')
