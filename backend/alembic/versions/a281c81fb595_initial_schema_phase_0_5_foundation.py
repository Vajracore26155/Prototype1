"""Initial schema - Phase 0.5 foundation

Revision ID: a281c81fb595
Revises: 
Create Date: 2026-09-16 17:31:31.446803

This migration creates the initial database schema for Vajra Core.
It defines tables for configurations, audits, findings, learned mappings, and compliance rules.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a281c81fb595'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial database schema"""
    
    # Create configurations table
    op.create_table(
        'configurations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('config_id', sa.String(length=50), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('file_type', sa.String(length=10), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('vendor', sa.String(length=50), nullable=True),
        sa.Column('vendor_confidence', sa.Float(), nullable=True),
        sa.Column('storage_path', sa.String(length=500), nullable=False),
        sa.Column('sanitized_path', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_configurations_config_id'), 'configurations', ['config_id'], unique=True)
    op.create_index(op.f('ix_configurations_id'), 'configurations', ['id'], unique=False)
    
    # Create audits table
    op.create_table(
        'audits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('audit_id', sa.String(length=50), nullable=False),
        sa.Column('configuration_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('compliance_score', sa.Float(), nullable=True),
        sa.Column('risk_score', sa.Float(), nullable=True),
        sa.Column('risk_level', sa.String(length=20), nullable=True),
        sa.Column('passed_count', sa.Integer(), nullable=True),
        sa.Column('failed_count', sa.Integer(), nullable=True),
        sa.Column('warning_count', sa.Integer(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('normalized_data', sa.JSON(), nullable=True),
        sa.Column('requires_human_review', sa.Boolean(), nullable=True),
        sa.Column('interpretation_confidence', sa.Float(), nullable=True),
        sa.Column('uninterpreted_lines_count', sa.Integer(), nullable=True),
        sa.Column('total_lines_count', sa.Integer(), nullable=True),
        sa.Column('pending_mappings_count', sa.Integer(), nullable=True),
        sa.Column('review_reason', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['configuration_id'], ['configurations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audits_audit_id'), 'audits', ['audit_id'], unique=True)
    op.create_index(op.f('ix_audits_id'), 'audits', ['id'], unique=False)
    
    # Create findings table
    op.create_table(
        'findings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('finding_id', sa.String(length=50), nullable=False),
        sa.Column('audit_id', sa.Integer(), nullable=False),
        sa.Column('rule_id', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('expected', sa.String(length=255), nullable=True),
        sa.Column('actual', sa.String(length=255), nullable=True),
        sa.Column('field_path', sa.String(length=255), nullable=True),
        sa.Column('evidence_file', sa.String(length=255), nullable=True),
        sa.Column('evidence_line', sa.Integer(), nullable=True),
        sa.Column('evidence_text', sa.Text(), nullable=True),
        sa.Column('risk_score', sa.Float(), nullable=True),
        sa.Column('remediation', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['audit_id'], ['audits.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_findings_finding_id'), 'findings', ['finding_id'], unique=True)
    op.create_index(op.f('ix_findings_id'), 'findings', ['id'], unique=False)
    
    # Create learned_mappings table
    op.create_table(
        'learned_mappings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('mapping_id', sa.String(length=50), nullable=False),
        sa.Column('vendor', sa.String(length=50), nullable=True),
        sa.Column('raw_pattern', sa.Text(), nullable=False),
        sa.Column('normalized_field', sa.String(length=255), nullable=False),
        sa.Column('value', sa.String(length=255), nullable=False),
        sa.Column('suggested_meaning', sa.String(length=255), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('approved', sa.Boolean(), nullable=True),
        sa.Column('approved_by', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_learned_mappings_id'), 'learned_mappings', ['id'], unique=False)
    op.create_index(op.f('ix_learned_mappings_mapping_id'), 'learned_mappings', ['mapping_id'], unique=True)
    
    # Create compliance_rules table
    op.create_table(
        'compliance_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('rule_id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('field_path', sa.String(length=255), nullable=False),
        sa.Column('expected_value', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_compliance_rules_id'), 'compliance_rules', ['id'], unique=False)
    op.create_index(op.f('ix_compliance_rules_rule_id'), 'compliance_rules', ['rule_id'], unique=True)


def downgrade() -> None:
    """Drop all tables"""
    op.drop_index(op.f('ix_compliance_rules_rule_id'), table_name='compliance_rules')
    op.drop_index(op.f('ix_compliance_rules_id'), table_name='compliance_rules')
    op.drop_table('compliance_rules')
    
    op.drop_index(op.f('ix_learned_mappings_mapping_id'), table_name='learned_mappings')
    op.drop_index(op.f('ix_learned_mappings_id'), table_name='learned_mappings')
    op.drop_table('learned_mappings')
    
    op.drop_index(op.f('ix_findings_id'), table_name='findings')
    op.drop_index(op.f('ix_findings_finding_id'), table_name='findings')
    op.drop_table('findings')
    
    op.drop_index(op.f('ix_audits_id'), table_name='audits')
    op.drop_index(op.f('ix_audits_audit_id'), table_name='audits')
    op.drop_table('audits')
    
    op.drop_index(op.f('ix_configurations_id'), table_name='configurations')
    op.drop_index(op.f('ix_configurations_config_id'), table_name='configurations')
    op.drop_table('configurations')
