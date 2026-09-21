"""
Security Posture Scoring Engine
Phase 5: Calculate and track security posture scores
"""
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import Device, Audit, Finding, DriftAnalysis, Configuration


@dataclass
class PostureFactors:
    """Posture score factors"""
    compliance_score: float  # 0-100
    drift_score: float  # 0-100 (lower is better)
    risk_score: float  # 0-100 (lower is better)
    remediation_score: float  # 0-100
    config_age_score: float  # 0-100


@dataclass
class PostureScoreResult:
    """Posture score calculation result"""
    score: float  # Overall 0-100
    factors: PostureFactors
    factor_breakdown: Dict
    trend: str  # IMPROVING, DECLINING, STABLE
    previous_score: Optional[float]
    score_change: Optional[float]


def calculate_posture_score(
    compliance_score: float,
    drift_score: float,
    critical_findings: int,
    high_findings: int,
    remediation_velocity: float,
    config_age_days: int
) -> PostureScoreResult:
    """
    Calculate security posture score
    
    Scoring Formula:
    - Compliance Score: 40%
    - Drift Score (inverted): 20%
    - Risk Score (from findings): 25%
    - Remediation Velocity: 10%
    - Config Freshness: 5%
    
    Args:
        compliance_score: Compliance score (0-100)
        drift_score: Drift score (0-100, higher = more drift)
        critical_findings: Number of critical findings
        high_findings: Number of high findings
        remediation_velocity: Remediation rate (0-100)
        config_age_days: Days since last config update
        
    Returns:
        PostureScoreResult with overall score and breakdown
    """
    # Factor 1: Compliance (40%) - direct use
    compliance_factor = compliance_score * 0.4
    
    # Factor 2: Drift (20%) - inverted (less drift = better score)
    drift_inverted = 100 - drift_score
    drift_factor = drift_inverted * 0.2
    
    # Factor 3: Risk (25%) - based on findings
    risk_score = calculate_risk_score(critical_findings, high_findings)
    risk_inverted = 100 - risk_score
    risk_factor = risk_inverted * 0.25
    
    # Factor 4: Remediation (10%) - velocity of fixing issues
    remediation_factor = remediation_velocity * 0.1
    
    # Factor 5: Config Age (5%) - freshness bonus
    age_score = calculate_age_score(config_age_days)
    age_factor = age_score * 0.05
    
    # Calculate overall score
    overall_score = compliance_factor + drift_factor + risk_factor + remediation_factor + age_factor
    overall_score = round(min(max(overall_score, 0), 100), 2)
    
    factors = PostureFactors(
        compliance_score=round(compliance_score, 2),
        drift_score=round(drift_score, 2),
        risk_score=round(risk_score, 2),
        remediation_score=round(remediation_velocity, 2),
        config_age_score=round(age_score, 2)
    )
    
    breakdown = {
        "compliance": {
            "score": round(compliance_score, 2),
            "weight": 0.4,
            "contribution": round(compliance_factor, 2)
        },
        "drift": {
            "score": round(drift_inverted, 2),
            "raw_drift": round(drift_score, 2),
            "weight": 0.2,
            "contribution": round(drift_factor, 2)
        },
        "risk": {
            "score": round(risk_inverted, 2),
            "raw_risk": round(risk_score, 2),
            "critical_findings": critical_findings,
            "high_findings": high_findings,
            "weight": 0.25,
            "contribution": round(risk_factor, 2)
        },
        "remediation": {
            "score": round(remediation_velocity, 2),
            "weight": 0.1,
            "contribution": round(remediation_factor, 2)
        },
        "config_age": {
            "score": round(age_score, 2),
            "age_days": config_age_days,
            "weight": 0.05,
            "contribution": round(age_factor, 2)
        }
    }
    
    return PostureScoreResult(
        score=overall_score,
        factors=factors,
        factor_breakdown=breakdown,
        trend="STABLE",  # Will be calculated by comparing with previous
        previous_score=None,
        score_change=None
    )


def calculate_risk_score(critical_findings: int, high_findings: int) -> float:
    """
    Calculate risk score from findings
    
    Formula:
    - Each critical finding: 10 points
    - Each high finding: 5 points
    - Capped at 100
    """
    risk = (critical_findings * 10) + (high_findings * 5)
    return min(risk, 100)


def calculate_age_score(age_days: int) -> float:
    """
    Calculate configuration age score
    
    Scoring:
    - 0-7 days: 100 (excellent)
    - 7-30 days: 80 (good)
    - 30-90 days: 60 (acceptable)
    - 90-180 days: 40 (needs attention)
    - 180+ days: 20 (critical)
    """
    if age_days <= 7:
        return 100
    elif age_days <= 30:
        return 80
    elif age_days <= 90:
        return 60
    elif age_days <= 180:
        return 40
    else:
        return 20


def calculate_organization_score(db: Session, organization_id: int) -> PostureScoreResult:
    """
    Calculate organization-level posture score
    
    Aggregates scores from all active devices
    """
    # Get all active devices
    devices = db.query(Device).filter(
        Device.organization_id == organization_id,
        Device.status == "ACTIVE"
    ).all()
    
    if not devices:
        # No devices, return default score
        return calculate_posture_score(0, 0, 0, 0, 0, 999)
    
    # Calculate average compliance score
    audits = db.query(Audit).join(
        Configuration, Audit.configuration_id == Configuration.id
    ).filter(
        Configuration.organization_id == organization_id,
        Audit.status == "COMPLETED"
    ).all()
    
    avg_compliance = sum(a.compliance_score or 0 for a in audits) / len(audits) if audits else 0
    
    # Calculate drift score
    drifts = db.query(DriftAnalysis).filter(
        DriftAnalysis.organization_id == organization_id
    ).order_by(DriftAnalysis.detected_at.desc()).limit(len(devices)).all()
    
    avg_drift = sum(d.drift_score for d in drifts) / len(drifts) if drifts else 0
    
    # Count findings
    critical_count = db.query(Finding).join(
        Audit, Finding.audit_id == Audit.id
    ).join(
        Configuration, Audit.configuration_id == Configuration.id
    ).filter(
        Configuration.organization_id == organization_id,
        Finding.severity == "CRITICAL",
        Finding.status == "FAIL"
    ).count()
    
    high_count = db.query(Finding).join(
        Audit, Finding.audit_id == Audit.id
    ).join(
        Configuration, Audit.configuration_id == Configuration.id
    ).filter(
        Configuration.organization_id == organization_id,
        Finding.severity == "HIGH",
        Finding.status == "FAIL"
    ).count()
    
    # Calculate remediation velocity (issues resolved in last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    total_findings = db.query(Finding).join(
        Audit, Finding.audit_id == Audit.id
    ).join(
        Configuration, Audit.configuration_id == Configuration.id
    ).filter(
        Configuration.organization_id == organization_id,
        Audit.started_at >= thirty_days_ago
    ).count()
    
    passed_findings = db.query(Finding).join(
        Audit, Finding.audit_id == Audit.id
    ).join(
        Configuration, Audit.configuration_id == Configuration.id
    ).filter(
        Configuration.organization_id == organization_id,
        Audit.started_at >= thirty_days_ago,
        Finding.status == "PASS"
    ).count()
    
    remediation_velocity = (passed_findings / total_findings * 100) if total_findings > 0 else 50
    
    # Calculate average config age
    configs = db.query(Configuration).filter(
        Configuration.organization_id == organization_id
    ).all()
    
    avg_age_days = 0
    if configs:
        total_age = sum((datetime.utcnow() - c.created_at).days for c in configs)
        avg_age_days = total_age // len(configs)
    
    return calculate_posture_score(
        compliance_score=avg_compliance,
        drift_score=avg_drift,
        critical_findings=critical_count,
        high_findings=high_count,
        remediation_velocity=remediation_velocity,
        config_age_days=avg_age_days
    )


def calculate_device_score(db: Session, device_id: int) -> PostureScoreResult:
    """
    Calculate device-level posture score
    """
    device = db.query(Device).filter(Device.id == device_id).first()
    
    if not device:
        raise ValueError(f"Device {device_id} not found")
    
    # Get latest audit for device
    latest_audit = None
    if device.current_config_id:
        latest_audit = db.query(Audit).filter(
            Audit.configuration_id == device.current_config_id,
            Audit.status == "COMPLETED"
        ).order_by(Audit.started_at.desc()).first()
    
    compliance_score = latest_audit.compliance_score if latest_audit else 0
    
    # Get latest drift
    latest_drift = db.query(DriftAnalysis).filter(
        DriftAnalysis.device_id == device_id
    ).order_by(DriftAnalysis.detected_at.desc()).first()
    
    drift_score = latest_drift.drift_score if latest_drift else 0
    
    # Count device findings
    critical_count = 0
    high_count = 0
    
    if latest_audit:
        critical_count = db.query(Finding).filter(
            Finding.audit_id == latest_audit.id,
            Finding.severity == "CRITICAL",
            Finding.status == "FAIL"
        ).count()
        
        high_count = db.query(Finding).filter(
            Finding.audit_id == latest_audit.id,
            Finding.severity == "HIGH",
            Finding.status == "FAIL"
        ).count()
    
    # Remediation velocity for device (last 30 days)
    remediation_velocity = 50  # Default
    
    # Config age
    config_age_days = 0
    if device.current_config_id:
        config = db.query(Configuration).filter(
            Configuration.id == device.current_config_id
        ).first()
        if config:
            config_age_days = (datetime.utcnow() - config.created_at).days
    
    return calculate_posture_score(
        compliance_score=compliance_score,
        drift_score=drift_score,
        critical_findings=critical_count,
        high_findings=high_count,
        remediation_velocity=remediation_velocity,
        config_age_days=config_age_days
    )
