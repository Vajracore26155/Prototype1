"""Phase 5: Device management, drift detection, posture scoring models

Revision ID: phase5_001
Revises: phase4_auth_rbac_001, c0b1201f4f27
Create Date: 2024-12-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'phase5_001'
down_revision = ('phase4_auth_rbac_001', 'c0b1201f4f27')
branch_labels = None
depends_on = None


def upgrade():
    # Update Device table - skip foreign keys for SQLite
    op.add_column('devices', sa.Column('ip_address', sa.String(45), nullable=True))
    op.add_column('devices', sa.Column('model', sa.String(100), nullable=True))
    op.add_column('devices', sa.Column('location', sa.String(255), nullable=True))
    op.add_column('devices', sa.Column('owner', sa.String(255), nullable=True))
    op.add_column('devices', sa.Column('status', sa.String(20), nullable=True, server_default='ACTIVE'))
    op.add_column('devices', sa.Column('baseline_config_id', sa.Integer(), nullable=True))
    op.add_column('devices', sa.Column('tags', sa.JSON(), nullable=True))
    op.add_column('devices', sa.Column('device_metadata', sa.JSON(), nullable=True))
    # Skip FK for SQLite - will work via ORM relationships
    
    # ConfigurationVersion table
    op.create_table(
        'configuration_versions',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('version_id', sa.String(50), unique=True, index=True, nullable=False),
        sa.Column('configuration_id', sa.Integer(), sa.ForeignKey('configurations.id'), nullable=False),
        sa.Column('device_id', sa.Integer(), sa.ForeignKey('devices.id'), nullable=True),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('content_hash', sa.String(64), nullable=False, index=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('uploaded_by', sa.String(255), nullable=True),
        sa.Column('change_summary', sa.Text(), nullable=True),
        sa.Column('is_baseline', sa.Boolean(), default=False, index=True),
        sa.Column('parent_version_id', sa.Integer(), sa.ForeignKey('configuration_versions.id'), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), server_default=sa.text('now()'), index=True)
    )
    
    # DriftAnalysis table
    op.create_table(
        'drift_analyses',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('drift_id', sa.String(50), unique=True, index=True, nullable=False),
        sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('device_id', sa.Integer(), sa.ForeignKey('devices.id'), nullable=False),
        sa.Column('baseline_version_id', sa.Integer(), sa.ForeignKey('configuration_versions.id'), nullable=False),
        sa.Column('current_version_id', sa.Integer(), sa.ForeignKey('configuration_versions.id'), nullable=False),
        sa.Column('drift_score', sa.Float(), nullable=False),
        sa.Column('drift_severity', sa.String(20), nullable=False),
        sa.Column('field_drifts', sa.JSON(), nullable=True),
        sa.Column('added_fields', sa.Integer(), default=0),
        sa.Column('removed_fields', sa.Integer(), default=0),
        sa.Column('modified_fields', sa.Integer(), default=0),
        sa.Column('security_impact', sa.String(20), nullable=True),
        sa.Column('detected_at', sa.DateTime(), server_default=sa.text('now()'), index=True),
        sa.Column('acknowledged', sa.Boolean(), default=False, index=True),
        sa.Column('acknowledged_by', sa.String(255), nullable=True),
        sa.Column('acknowledged_at', sa.DateTime(), nullable=True),
        sa.Column('remediation_plan_id', sa.Integer(), nullable=True)
    )
    
    # PostureScore table
    op.create_table(
        'posture_scores',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('score_id', sa.String(50), unique=True, index=True, nullable=False),
        sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('device_id', sa.Integer(), sa.ForeignKey('devices.id'), nullable=True),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('compliance_score', sa.Float(), nullable=False),
        sa.Column('drift_score', sa.Float(), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False),
        sa.Column('remediation_score', sa.Float(), nullable=False),
        sa.Column('config_age_score', sa.Float(), nullable=False),
        sa.Column('factor_breakdown', sa.JSON(), nullable=True),
        sa.Column('trend', sa.String(20), nullable=True),
        sa.Column('previous_score', sa.Float(), nullable=True),
        sa.Column('score_change', sa.Float(), nullable=True),
        sa.Column('calculated_at', sa.DateTime(), server_default=sa.text('now()'), index=True)
    )
    
    # PostureTrend table
    op.create_table(
        'posture_trends',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organizations.id'), nullable=False, index=True),
        sa.Column('device_id', sa.Integer(), sa.ForeignKey('devices.id'), nullable=True, index=True),
        sa.Column('date', sa.DateTime(), nullable=False, index=True),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('compliance_score', sa.Float(), nullable=False),
        sa.Column('drift_score', sa.Float(), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False),
        sa.Column('critical_findings', sa.Integer(), default=0),
        sa.Column('high_findings', sa.Integer(), default=0),
        sa.Column('medium_findings', sa.Integer(), default=0),
        sa.Column('low_findings', sa.Integer(), default=0),
        sa.Column('total_devices', sa.Integer(), nullable=True),
        sa.Column('compliant_devices', sa.Integer(), nullable=True)
    )
    
    # RemediationPlan table
    op.create_table(
        'remediation_plans',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('plan_id', sa.String(50), unique=True, index=True, nullable=False),
        sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('device_id', sa.Integer(), sa.ForeignKey('devices.id'), nullable=True),
        sa.Column('audit_id', sa.Integer(), sa.ForeignKey('audits.id'), nullable=True),
        sa.Column('drift_id', sa.Integer(), sa.ForeignKey('drift_analyses.id'), nullable=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('finding_ids', sa.JSON(), nullable=True),
        sa.Column('remediation_commands', sa.Text(), nullable=False),
        sa.Column('rollback_commands', sa.Text(), nullable=True),
        sa.Column('estimated_impact', sa.String(20), nullable=False),
        sa.Column('estimated_downtime', sa.String(100), nullable=True),
        sa.Column('requires_approval', sa.Boolean(), default=True, index=True),
        sa.Column('status', sa.String(50), server_default='DRAFT', index=True),
        sa.Column('created_by', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), index=True),
        sa.Column('approved_by', sa.String(255), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('rejected_by', sa.String(255), nullable=True),
        sa.Column('rejected_at', sa.DateTime(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('applied_by', sa.String(255), nullable=True),
        sa.Column('applied_at', sa.DateTime(), nullable=True),
        sa.Column('application_result', sa.Text(), nullable=True)
    )
    
    # RemediationApproval table
    op.create_table(
        'remediation_approvals',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('plan_id', sa.Integer(), sa.ForeignKey('remediation_plans.id'), nullable=False, index=True),
        sa.Column('approver_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('decision', sa.String(50), nullable=False),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'))
    )
    
    # ScheduledReport table
    op.create_table(
        'scheduled_reports',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('schedule_id', sa.String(50), unique=True, index=True, nullable=False),
        sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organizations.id'), nullable=False),
        sa.Column('report_type', sa.String(50), nullable=False),
        sa.Column('report_name', sa.String(255), nullable=False),
        sa.Column('frequency', sa.String(20), nullable=False),
        sa.Column('schedule_time', sa.String(10), nullable=False),
        sa.Column('recipients', sa.JSON(), nullable=False),
        sa.Column('parameters', sa.JSON(), nullable=True),
        sa.Column('format', sa.String(10), server_default='PDF'),
        sa.Column('is_active', sa.Boolean(), default=True, index=True),
        sa.Column('last_run_at', sa.DateTime(), nullable=True),
        sa.Column('next_run_at', sa.DateTime(), nullable=True, index=True),
        sa.Column('created_by', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()'))
    )
    
    # DeviceTag table
    op.create_table(
        'device_tags',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('device_id', sa.Integer(), sa.ForeignKey('devices.id'), nullable=False, index=True),
        sa.Column('tag_key', sa.String(100), nullable=False, index=True),
        sa.Column('tag_value', sa.String(255), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'))
    )
    
    # Skip FK for SQLite - will work via ORM relationships


def downgrade():
    # Drop tables in reverse order
    op.drop_table('device_tags')
    op.drop_table('scheduled_reports')
    op.drop_table('remediation_approvals')
    op.drop_table('remediation_plans')
    op.drop_table('posture_trends')
    op.drop_table('posture_scores')
    op.drop_table('drift_analyses')
    op.drop_table('configuration_versions')
    
    # Remove Device table columns
    op.drop_column('devices', 'device_metadata')
    op.drop_column('devices', 'tags')
    op.drop_column('devices', 'baseline_config_id')
    op.drop_column('devices', 'status')
    op.drop_column('devices', 'owner')
    op.drop_column('devices', 'location')
    op.drop_column('devices', 'model')
    op.drop_column('devices', 'ip_address')
