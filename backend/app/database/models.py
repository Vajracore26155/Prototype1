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
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    audits = relationship("Audit", back_populates="configuration", cascade="all, delete-orphan")


class Audit(Base):
    """Security audit execution record"""
    __tablename__ = "audits"
    
    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(String(50), unique=True, index=True, nullable=False)  # AUD-000001
    configuration_id = Column(Integer, ForeignKey("configurations.id"), nullable=False)
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
