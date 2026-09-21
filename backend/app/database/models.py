"""
Database models for SIH26155 Network Security Auditor
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Configuration(Base):
    """Uploaded configuration file metadata"""
    __tablename__ = "configurations"
    
    id = Column(Integer, primary_key=True, index=True)
    config_id = Column(String(50), unique=True, index=True, nullable=False)  # CFG-000001
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(10), nullable=False)  # .cfg, .conf, .txt, .json
    status = Column(String(50), default="UPLOADED")  # UPLOADED, PROCESSING, COMPLETED, FAILED, NEEDS_REVIEW
    vendor = Column(String(50), nullable=True)  # Cisco, Fortinet, Unknown
    vendor_confidence = Column(Float, nullable=True)
    storage_path = Column(String(500), nullable=False)
    sanitized_path = Column(String(500), nullable=True)
    file_hash_sha256 = Column(String(64), nullable=True, index=True)  # SHA-256 hash for integrity/deduplication
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)  # Phase 4: Multi-tenancy
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    audits = relationship("Audit", back_populates="configuration", cascade="all, delete-orphan")


class Audit(Base):
    """Security audit execution record"""
    __tablename__ = "audits"
    
    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(String(50), unique=True, index=True, nullable=False)  # AUD-000001
    configuration_id = Column(Integer, ForeignKey("configurations.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)  # Phase 4: Multi-tenancy
    status = Column(String(50), default="PROCESSING")  # PROCESSING, COMPLETED, FAILED, NEEDS_REVIEW
    compliance_score = Column(Float, nullable=True)
    risk_score = Column(Float, nullable=True)
    risk_level = Column(String(20), nullable=True)  # LOW, MEDIUM, HIGH, CRITICAL
    passed_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    warning_count = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    normalized_data = Column(JSON, nullable=True)  # Store the unified security model
    
    # Unknown vendor parsing metadata
    requires_human_review = Column(Boolean, default=False)  # Flag for human intervention needed
    interpretation_confidence = Column(Float, nullable=True)  # Overall confidence in parsing
    uninterpreted_lines_count = Column(Integer, default=0)  # Lines that couldn't be parsed
    total_lines_count = Column(Integer, default=0)  # Total config lines
    pending_mappings_count = Column(Integer, default=0)  # AI suggestions awaiting approval
    review_reason = Column(Text, nullable=True)  # Why human review is needed
    
    # Relationships
    configuration = relationship("Configuration", back_populates="audits")
    findings = relationship("Finding", back_populates="audit", cascade="all, delete-orphan")


class Finding(Base):
    """Individual compliance finding/violation"""
    __tablename__ = "findings"
    
    id = Column(Integer, primary_key=True, index=True)
    finding_id = Column(String(50), unique=True, index=True, nullable=False)  # FND-000001
    audit_id = Column(Integer, ForeignKey("audits.id"), nullable=False)
    rule_id = Column(String(50), nullable=False)  # NET-001
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), nullable=False)  # PASS, FAIL, WARNING, NOT_APPLICABLE, UNKNOWN
    severity = Column(String(20), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    expected = Column(String(255), nullable=True)
    actual = Column(String(255), nullable=True)
    field_path = Column(String(255), nullable=True)  # remote_access.telnet_enabled
    evidence_file = Column(String(255), nullable=True)
    evidence_line = Column(Integer, nullable=True)
    evidence_text = Column(Text, nullable=True)
    risk_score = Column(Float, nullable=True)
    remediation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    audit = relationship("Audit", back_populates="findings")


class LearnedMapping(Base):
    """AI-learned configuration mappings"""
    __tablename__ = "learned_mappings"
    
    id = Column(Integer, primary_key=True, index=True)
    mapping_id = Column(String(50), unique=True, index=True, nullable=False)  # MAP-000001
    vendor = Column(String(50), default="Unknown")
    raw_pattern = Column(Text, nullable=False)  # management-access secure-shell
    normalized_field = Column(String(255), nullable=False)  # remote_access.ssh_enabled
    value = Column(String(255), nullable=False)  # true
    suggested_meaning = Column(String(255), nullable=True)  # SSH Remote Management
    confidence = Column(Float, nullable=False)
    approved = Column(Boolean, default=False)
    approved_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)
    usage_count = Column(Integer, default=0)  # How many times this mapping was reused


class ComplianceRule(Base):
    """Compliance rules metadata (optional, rules primarily in YAML)"""
    __tablename__ = "compliance_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(String(50), unique=True, index=True, nullable=False)  # NET-001
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String(20), nullable=False)
    field_path = Column(String(255), nullable=False)
    expected_value = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True)  # Remote Access, Management, Authentication
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================
# PHASE 4: AUTHENTICATION & RBAC MODELS
# ============================================================

class Organization(Base):
    """Multi-tenant organization"""
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(String(50), unique=True, index=True, nullable=False)  # ORG-000001
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)  # acme-corp
    status = Column(String(20), default="ACTIVE")  # ACTIVE, SUSPENDED, DELETED
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="organization")


class User(Base):
    """User accounts with RBAC"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), unique=True, index=True, nullable=False)  # USR-000001
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    role = Column(String(50), nullable=False)  # SUPER_ADMIN, ADMIN, ANALYST, AUDITOR, VIEWER
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    audit_logs = relationship("SecurityAuditLog", back_populates="user")


class SecurityAuditLog(Base):
    """Immutable security audit log"""
    __tablename__ = "security_audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    log_id = Column(String(50), unique=True, index=True, nullable=False)  # LOG-000001
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    event_type = Column(String(50), nullable=False)  # LOGIN, LOGOUT, UPLOAD, AUDIT, etc.
    resource_type = Column(String(50), nullable=True)  # configuration, audit, finding
    resource_id = Column(String(50), nullable=True)
    action = Column(String(50), nullable=False)  # CREATE, READ, UPDATE, DELETE, EXECUTE
    result = Column(String(20), nullable=False)  # SUCCESS, FAILURE, DENIED
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")


class Job(Base):
    """Async job tracking"""
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(50), unique=True, index=True, nullable=False)  # JOB-000001
    task_id = Column(String(255), unique=True, nullable=True)  # Celery task ID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    job_type = Column(String(50), nullable=False)  # BULK_UPLOAD, AUDIT, REPORT, etc.
    status = Column(String(20), default="QUEUED")  # QUEUED, RUNNING, COMPLETED, FAILED, CANCELLED
    progress = Column(Integer, default=0)  # 0-100
    total_items = Column(Integer, nullable=True)
    processed_items = Column(Integer, default=0)
    failed_items = Column(Integer, default=0)
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)


class Device(Base):
    """Network device inventory"""
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(50), unique=True, index=True, nullable=False)  # DEV-000001
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    hostname = Column(String(255), nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)  # Support IPv6
    vendor = Column(String(50), nullable=True)
    model = Column(String(100), nullable=True)
    platform = Column(String(100), nullable=True)
    os_version = Column(String(100), nullable=True)
    device_type = Column(String(50), nullable=True)  # ROUTER, SWITCH, FIREWALL, WAF, IDS, IPS
    location = Column(String(255), nullable=True)  # Physical location
    site = Column(String(100), nullable=True)
    owner = Column(String(255), nullable=True)  # Team or person responsible
    criticality = Column(String(20), nullable=True)  # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String(20), default="ACTIVE")  # ACTIVE, MAINTENANCE, DECOMMISSIONED
    management_ip = Column(String(45), nullable=True)
    serial_number = Column(String(100), nullable=True)
    current_config_id = Column(Integer, ForeignKey("configurations.id"), nullable=True)
    baseline_config_id = Column(Integer, ForeignKey("configurations.id"), nullable=True)  # Phase 5: Baseline
    tags = Column(JSON, nullable=True)  # Phase 5: Tags for grouping
    device_metadata = Column(JSON, nullable=True)  # Phase 5: Custom metadata (renamed from metadata)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    current_config = relationship("Configuration", foreign_keys=[current_config_id])
    baseline_config = relationship("Configuration", foreign_keys=[baseline_config_id])


# ============================================================
# PHASE 5: ADVANCED SECURITY INTELLIGENCE & GOVERNANCE MODELS
# ============================================================

class ConfigurationVersion(Base):
    """Configuration version history for drift detection"""
    __tablename__ = "configuration_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(String(50), unique=True, index=True, nullable=False)  # VER-000001
    configuration_id = Column(Integer, ForeignKey("configurations.id"), nullable=False)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=True)
    version_number = Column(Integer, nullable=False)  # 1, 2, 3...
    content_hash = Column(String(64), nullable=False, index=True)  # SHA-256
    content = Column(Text, nullable=False)  # Full configuration content
    file_size = Column(Integer, nullable=False)
    uploaded_by = Column(String(255), nullable=True)  # User email
    change_summary = Column(Text, nullable=True)  # Human description of changes
    is_baseline = Column(Boolean, default=False, index=True)  # Is this the baseline version?
    parent_version_id = Column(Integer, ForeignKey("configuration_versions.id"), nullable=True)  # Previous version
    uploaded_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    configuration = relationship("Configuration", foreign_keys=[configuration_id])
    device = relationship("Device", foreign_keys=[device_id])


class DriftAnalysis(Base):
    """Configuration drift detection results"""
    __tablename__ = "drift_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    drift_id = Column(String(50), unique=True, index=True, nullable=False)  # DRF-000001
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    baseline_version_id = Column(Integer, ForeignKey("configuration_versions.id"), nullable=False)
    current_version_id = Column(Integer, ForeignKey("configuration_versions.id"), nullable=False)
    drift_score = Column(Float, nullable=False)  # 0-100 (0 = no drift, 100 = complete drift)
    drift_severity = Column(String(20), nullable=False)  # NONE, LOW, MEDIUM, HIGH, CRITICAL
    field_drifts = Column(JSON, nullable=True)  # Array of field-level drifts
    added_fields = Column(Integer, default=0)
    removed_fields = Column(Integer, default=0)
    modified_fields = Column(Integer, default=0)
    security_impact = Column(String(20), nullable=True)  # LOW, MEDIUM, HIGH, CRITICAL
    detected_at = Column(DateTime, default=datetime.utcnow, index=True)
    acknowledged = Column(Boolean, default=False, index=True)
    acknowledged_by = Column(String(255), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    remediation_plan_id = Column(Integer, ForeignKey("remediation_plans.id"), nullable=True)
    
    # Relationships
    device = relationship("Device", foreign_keys=[device_id])
    baseline_version = relationship("ConfigurationVersion", foreign_keys=[baseline_version_id])
    current_version = relationship("ConfigurationVersion", foreign_keys=[current_version_id])


class PostureScore(Base):
    """Security posture score for organization or device"""
    __tablename__ = "posture_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    score_id = Column(String(50), unique=True, index=True, nullable=False)  # SCR-000001
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=True)  # NULL = organization-level score
    score = Column(Float, nullable=False)  # Overall score 0-100
    compliance_score = Column(Float, nullable=False)  # Compliance component
    drift_score = Column(Float, nullable=False)  # Drift component
    risk_score = Column(Float, nullable=False)  # Risk component
    remediation_score = Column(Float, nullable=False)  # Remediation velocity
    config_age_score = Column(Float, nullable=False)  # Configuration freshness
    factor_breakdown = Column(JSON, nullable=True)  # Detailed factor breakdown
    trend = Column(String(20), nullable=True)  # IMPROVING, DECLINING, STABLE
    previous_score = Column(Float, nullable=True)
    score_change = Column(Float, nullable=True)  # Change from previous
    calculated_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    device = relationship("Device", foreign_keys=[device_id])


class PostureTrend(Base):
    """Historical posture score trends"""
    __tablename__ = "posture_trends"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=True, index=True)  # NULL = organization-level
    date = Column(DateTime, nullable=False, index=True)
    score = Column(Float, nullable=False)
    compliance_score = Column(Float, nullable=False)
    drift_score = Column(Float, nullable=False)
    risk_score = Column(Float, nullable=False)
    critical_findings = Column(Integer, default=0)
    high_findings = Column(Integer, default=0)
    medium_findings = Column(Integer, default=0)
    low_findings = Column(Integer, default=0)
    total_devices = Column(Integer, nullable=True)  # For org-level only
    compliant_devices = Column(Integer, nullable=True)  # For org-level only
    
    # Relationships
    device = relationship("Device", foreign_keys=[device_id])


class RemediationPlan(Base):
    """Remediation plan for security findings"""
    __tablename__ = "remediation_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(String(50), unique=True, index=True, nullable=False)  # REM-000001
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=True)
    audit_id = Column(Integer, ForeignKey("audits.id"), nullable=True)
    drift_id = Column(Integer, ForeignKey("drift_analyses.id"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    finding_ids = Column(JSON, nullable=True)  # Array of finding IDs
    remediation_commands = Column(Text, nullable=False)  # Vendor-specific commands
    rollback_commands = Column(Text, nullable=True)  # Commands to rollback
    estimated_impact = Column(String(20), nullable=False)  # LOW, MEDIUM, HIGH
    estimated_downtime = Column(String(100), nullable=True)  # "5 minutes", "1 hour", etc.
    requires_approval = Column(Boolean, default=True, index=True)
    status = Column(String(50), default="DRAFT", index=True)  # DRAFT, PENDING_APPROVAL, APPROVED, REJECTED, APPLIED, FAILED, ROLLED_BACK
    created_by = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    approved_by = Column(String(255), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejected_by = Column(String(255), nullable=True)
    rejected_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    applied_by = Column(String(255), nullable=True)
    applied_at = Column(DateTime, nullable=True)
    application_result = Column(Text, nullable=True)  # Success/failure details
    
    # Relationships
    device = relationship("Device", foreign_keys=[device_id])
    audit = relationship("Audit", foreign_keys=[audit_id])


class RemediationApproval(Base):
    """Remediation plan approval tracking"""
    __tablename__ = "remediation_approvals"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("remediation_plans.id"), nullable=False, index=True)
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    decision = Column(String(50), nullable=False)  # APPROVE, REJECT, REQUEST_CHANGES
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    plan = relationship("RemediationPlan", foreign_keys=[plan_id])
    approver = relationship("User", foreign_keys=[approver_id])


class ScheduledReport(Base):
    """Scheduled report configuration"""
    __tablename__ = "scheduled_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(String(50), unique=True, index=True, nullable=False)  # SCH-000001
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    report_type = Column(String(50), nullable=False)  # EXECUTIVE, COMPLIANCE, DRIFT, RISK, etc.
    report_name = Column(String(255), nullable=False)
    frequency = Column(String(20), nullable=False)  # DAILY, WEEKLY, MONTHLY
    schedule_time = Column(String(10), nullable=False)  # HH:MM format
    recipients = Column(JSON, nullable=False)  # Array of email addresses
    parameters = Column(JSON, nullable=True)  # Report-specific parameters
    format = Column(String(10), default="PDF")  # PDF, CSV, JSON
    is_active = Column(Boolean, default=True, index=True)
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True, index=True)
    created_by = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DeviceTag(Base):
    """Device tagging for grouping and filtering"""
    __tablename__ = "device_tags"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True)
    tag_key = Column(String(100), nullable=False, index=True)  # e.g., "environment", "location", "owner"
    tag_value = Column(String(255), nullable=False, index=True)  # e.g., "production", "datacenter-1", "team-a"
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    device = relationship("Device", foreign_keys=[device_id])



# ============================================================
# PHASE 7: WEBHOOKS & EVENTS
# ============================================================

class Webhook(Base):
    """Webhook configuration"""
    __tablename__ = "webhooks"
    
    id = Column(Integer, primary_key=True, index=True)
    webhook_id = Column(String(50), unique=True, index=True, nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    secret = Column(String(255), nullable=False)
    event_types = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    description = Column(Text, nullable=True)
    headers = Column(JSON, nullable=True)
    retry_count = Column(Integer, default=3)
    timeout_seconds = Column(Integer, default=30)
    created_by = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_triggered_at = Column(DateTime, nullable=True)
    total_deliveries = Column(Integer, default=0)
    successful_deliveries = Column(Integer, default=0)
    failed_deliveries = Column(Integer, default=0)


class WebhookDelivery(Base):
    """Webhook delivery tracking"""
    __tablename__ = "webhook_deliveries"
    
    id = Column(Integer, primary_key=True, index=True)
    delivery_id = Column(String(50), unique=True, index=True, nullable=False)
    webhook_id = Column(Integer, ForeignKey("webhooks.id"), nullable=False, index=True)
    event_id = Column(String(50), nullable=False, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    payload = Column(JSON, nullable=False)
    status = Column(String(20), nullable=False, index=True)
    http_status = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    attempt_count = Column(Integer, default=0)
    next_retry_at = Column(DateTime, nullable=True, index=True)
    delivered_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class EventLog(Base):
    """Persistent event storage"""
    __tablename__ = "event_log"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(50), unique=True, index=True, nullable=False)
    event_type = Column(String(100), nullable=False, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    resource_type = Column(String(50), nullable=False, index=True)
    resource_id = Column(String(50), nullable=False, index=True)
    data = Column(JSON, nullable=False)
    event_metadata = Column(JSON, nullable=True)  # Renamed from metadata to avoid SQLAlchemy reserved word
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class Report(Base):
    """Generated reports"""
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String(50), unique=True, index=True, nullable=False)  # RPT-00000001
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    audit_id = Column(Integer, ForeignKey("audits.id"), nullable=True)
    report_type = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    format = Column(String(20), nullable=False)  # PDF, HTML, JSON, CSV, EXCEL
    content = Column(Text, nullable=True)  # For HTML/JSON content
    report_metadata = Column(JSON, nullable=True)  # Renamed from metadata to avoid SQLAlchemy reserved word
    generated_by = Column(String(255), nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)
    file_path = Column(String(500), nullable=True)


# ============================================================
# PHASE 12: MOBILE QR SESSION
# ============================================================


# ============================================================
# VENDOR USER MODELS (Phase 10: Vendor OTP System)
# ============================================================

class VendorUser(Base):
    """
    Vendor users who upload device configurations
    NOT internal users - these are external vendors/partners
    """
    __tablename__ = "vendor_users"
    
    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(String(50), unique=True, index=True, nullable=False)  # VND-000001
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)  # Optional: for username/password login
    company_name = Column(String(255), nullable=False)
    contact_name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    
    # Verification status
    email_verified = Column(Boolean, default=False)
    verification_token = Column(String(255), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    
    # Approval status (admin must approve after email verification)
    approval_status = Column(String(50), default="PENDING")  # PENDING, APPROVED, REJECTED, SUSPENDED
    approved_by = Column(String(255), nullable=True)  # Admin email who approved
    approved_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Associated organization (which org they're uploading for)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Metadata
    devices = Column(JSON, default=list)  # List of device IDs they manage
    vendor_metadata = Column(JSON, default=dict)  # Additional vendor info
    
    # Security
    last_otp_sent = Column(DateTime, nullable=True)
    otp_attempts = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    otp_codes = relationship("VendorOTP", back_populates="vendor", cascade="all, delete-orphan")
    upload_sessions = relationship("VendorUploadSession", back_populates="vendor", cascade="all, delete-orphan")


class VendorOTP(Base):
    """
    One-time passwords for vendor authentication
    OTPs sent via email for each upload session
    """
    __tablename__ = "vendor_otps"
    
    id = Column(Integer, primary_key=True, index=True)
    otp_id = Column(String(50), unique=True, index=True, nullable=False)  # OTP-000001
    vendor_id = Column(Integer, ForeignKey("vendor_users.id"), nullable=False)
    
    # OTP details
    otp_code = Column(String(10), nullable=False)  # 6-digit code
    otp_hash = Column(String(255), nullable=False)  # Hashed OTP for storage
    
    # Validation
    is_used = Column(Boolean, default=False)
    used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=False)  # 10 minutes from creation
    
    # Security
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    verification_attempts = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    vendor = relationship("VendorUser", back_populates="otp_codes")


class VendorUploadSession(Base):
    """
    Upload session after OTP verification
    Tracks what vendor uploaded and when
    """
    __tablename__ = "vendor_upload_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), unique=True, index=True, nullable=False)  # VUS-000001
    vendor_id = Column(Integer, ForeignKey("vendor_users.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Session details
    otp_id = Column(Integer, ForeignKey("vendor_otps.id"), nullable=True)  # Can be null for password login
    session_token = Column(String(255), unique=True, nullable=False)  # JWT-like token
    
    # Upload tracking
    files_uploaded = Column(JSON, default=list)  # List of config_ids uploaded
    upload_count = Column(Integer, default=0)
    
    # Status
    status = Column(String(50), default="ACTIVE")  # ACTIVE, EXPIRED, REVOKED
    expires_at = Column(DateTime, nullable=False)  # 24 hours from creation
    
    # Security
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    vendor = relationship("VendorUser", back_populates="upload_sessions")


class VendorApprovalRequest(Base):
    """
    Admin approval requests for vendor access
    Creates notification for admins to approve/reject
    """
    __tablename__ = "vendor_approval_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(50), unique=True, index=True, nullable=False)  # VAR-000001
    vendor_id = Column(Integer, ForeignKey("vendor_users.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Request details
    request_type = Column(String(50), default="NEW_VENDOR")  # NEW_VENDOR, REACTIVATION
    request_message = Column(Text, nullable=True)
    
    # Status
    status = Column(String(50), default="PENDING")  # PENDING, APPROVED, REJECTED
    reviewed_by = Column(String(255), nullable=True)  # Admin email
    reviewed_at = Column(DateTime, nullable=True)
    review_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
