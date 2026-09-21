"""
System Administration API
Phase 11: System-level administration, statistics, analytics, audit logs
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timedelta

from app.database import (
    get_db, User, Organization, Device, Configuration,
    Audit, Finding, Report, SecurityAuditLog, Webhook,
    WebhookDelivery, EventLog, DriftAnalysis, PostureScore,
    RemediationPlan
)
from app.auth.dependencies import require_permission
from app.auth.permissions import Permission

router = APIRouter()


# ============================================================
# SYSTEM ADMIN AUTHORIZATION
# ============================================================

async def require_system_admin(current_user: User = Depends(require_permission(Permission.SYSTEM_ADMIN))):
    """
    Verify user is system administrator
    
    System admin has access to platform-wide data
    """
    # In a real system, you might have a specific system_admin flag
    # For now, we use the ADMIN permission
    return current_user


# ============================================================
# PLATFORM STATISTICS
# ============================================================

@router.get("/admin/statistics/platform")
async def get_platform_statistics(
    current_user: User = Depends(require_system_admin),
    db: Session = Depends(get_db)
):
    """
    Get platform-wide statistics
    
    System admin only
    """
    try:
        # Organization stats
        total_orgs = db.query(Organization).count()
        active_orgs = db.query(Organization).filter(Organization.is_active == True).count()
        
        # User stats
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        
        # Device stats
        total_devices = db.query(Device).count()
        active_devices = db.query(Device).filter(Device.status == "ACTIVE").count()
        devices_by_vendor = db.query(
            Device.vendor,
            func.count(Device.id)
        ).group_by(Device.vendor).all()
        
        # Configuration stats
        total_configs = db.query(Configuration).count()
        configs_by_status = db.query(
            Configuration.status,
            func.count(Configuration.id)
        ).group_by(Configuration.status).all()
        
        # Audit stats
        total_audits = db.query(Audit).count()
        completed_audits = db.query(Audit).filter(Audit.status == "COMPLETED").count()
        failed_audits = db.query(Audit).filter(Audit.status == "FAILED").count()
        pending_audits = db.query(Audit).filter(Audit.status == "PROCESSING").count()
        
        # Finding stats
        total_findings = db.query(Finding).count()
        findings_by_severity = db.query(
            Finding.severity,
            func.count(Finding.id)
        ).group_by(Finding.severity).all()
        
        # Report stats
        total_reports = db.query(Report).count()
        
        # Webhook stats
        total_webhooks = db.query(Webhook).count()
        active_webhooks = db.query(Webhook).filter(Webhook.is_active == True).count()
        
        # Event stats
        total_events = db.query(EventLog).count()
        
        return {
            "success": True,
            "data": {
                "organizations": {
                    "total": total_orgs,
                    "active": active_orgs,
                    "inactive": total_orgs - active_orgs
                },
                "users": {
                    "total": total_users,
                    "active": active_users,
                    "inactive": total_users - active_users
                },
                "devices": {
                    "total": total_devices,
                    "active": active_devices,
                    "by_vendor": dict(devices_by_vendor)
                },
                "configurations": {
                    "total": total_configs,
                    "by_status": dict(configs_by_status)
                },
                "audits": {
                    "total": total_audits,
                    "completed": completed_audits,
                    "failed": failed_audits,
                    "pending": pending_audits
                },
                "findings": {
                    "total": total_findings,
                    "by_severity": dict(findings_by_severity)
                },
                "reports": {
                    "total": total_reports
                },
                "webhooks": {
                    "total": total_webhooks,
                    "active": active_webhooks
                },
                "events": {
                    "total": total_events
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# USAGE STATISTICS
# ============================================================

@router.get("/admin/statistics/usage")
async def get_usage_statistics(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(require_system_admin),
    db: Session = Depends(get_db)
):
    """
    Get platform usage statistics over time
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Audits per day
        audits = db.query(
            func.date(Audit.started_at).label('date'),
            func.count(Audit.id).label('count')
        ).filter(
            Audit.started_at >= cutoff_date
        ).group_by(func.date(Audit.started_at)).all()
        
        # Configurations uploaded
        configs = db.query(
            func.date(Configuration.created_at).label('date'),
            func.count(Configuration.id).label('count')
        ).filter(
            Configuration.created_at >= cutoff_date
        ).group_by(func.date(Configuration.created_at)).all()
        
        # Reports generated
        reports = db.query(
            func.date(Report.generated_at).label('date'),
            func.count(Report.id).label('count')
        ).filter(
            Report.generated_at >= cutoff_date
        ).group_by(func.date(Report.generated_at)).all()
        
        # Findings created
        findings = db.query(
            func.date(Finding.created_at).label('date'),
            func.count(Finding.id).label('count')
        ).filter(
            Finding.created_at >= cutoff_date
        ).group_by(func.date(Finding.created_at)).all()
        
        return {
            "success": True,
            "data": {
                "period_days": days,
                "audits_per_day": [{"date": str(d), "count": c} for d, c in audits],
                "configs_per_day": [{"date": str(d), "count": c} for d, c in configs],
                "reports_per_day": [{"date": str(d), "count": c} for d, c in reports],
                "findings_per_day": [{"date": str(d), "count": c} for d, c in findings]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# AUDIT STATISTICS
# ============================================================

@router.get("/admin/statistics/audits")
async def get_audit_statistics(
    current_user: User = Depends(require_system_admin),
    db: Session = Depends(get_db)
):
    """Get audit execution statistics"""
    try:
        # Audit status distribution
        by_status = db.query(
            Audit.status,
            func.count(Audit.id)
        ).group_by(Audit.status).all()
        
        # Average compliance score
        avg_compliance = db.query(func.avg(Audit.compliance_score)).filter(
            Audit.compliance_score.isnot(None)
        ).scalar() or 0
        
        # Risk level distribution
        by_risk = db.query(
            Audit.risk_level,
            func.count(Audit.id)
        ).group_by(Audit.risk_level).all()
        
        # Audits by organization
        by_org = db.query(
            Organization.name,
            func.count(Audit.id)
        ).join(Organization).group_by(Organization.name).limit(10).all()
        
        return {
            "success": True,
            "data": {
                "by_status": dict(by_status),
                "average_compliance_score": round(float(avg_compliance), 2),
                "by_risk_level": dict(by_risk),
                "top_organizations": [
                    {"organization": org, "count": count}
                    for org, count in by_org
                ]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# COMPLIANCE STATISTICS
# ============================================================

@router.get("/admin/statistics/compliance")
async def get_compliance_statistics(
    current_user: User = Depends(require_system_admin),
    db: Session = Depends(get_db)
):
    """Get compliance assessment statistics"""
    try:
        # Framework usage
        # Note: This would require tracking which frameworks were used in audits
        # For now, return finding categories as a proxy
        by_category = db.query(
            Finding.category,
            func.count(Finding.id)
        ).group_by(Finding.category).all()
        
        # Compliance trend (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        compliance_trend = db.query(
            func.date(Audit.completed_at).label('date'),
            func.avg(Audit.compliance_score).label('avg_score')
        ).filter(
            and_(
                Audit.completed_at >= thirty_days_ago,
                Audit.compliance_score.isnot(None)
            )
        ).group_by(func.date(Audit.completed_at)).all()
        
        return {
            "success": True,
            "data": {
                "findings_by_category": dict(by_category),
                "compliance_trend": [
                    {"date": str(d), "score": round(float(s), 2)}
                    for d, s in compliance_trend
                ]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# RISK STATISTICS
# ============================================================

@router.get("/admin/statistics/risk")
async def get_risk_statistics(
    current_user: User = Depends(require_system_admin),
    db: Session = Depends(get_db)
):
    """Get risk assessment statistics"""
    try:
        # Findings by severity
        by_severity = db.query(
            Finding.severity,
            func.count(Finding.id)
        ).group_by(Finding.severity).all()
        
        # Risk level distribution
        by_risk_level = db.query(
            Audit.risk_level,
            func.count(Audit.id)
        ).group_by(Audit.risk_level).all()
        
        # Average risk score
        avg_risk = db.query(func.avg(Audit.risk_score)).filter(
            Audit.risk_score.isnot(None)
        ).scalar() or 0
        
        # Critical findings trend
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        critical_trend = db.query(
            func.date(Finding.created_at).label('date'),
            func.count(Finding.id).label('count')
        ).filter(
            and_(
                Finding.severity == "CRITICAL",
                Finding.created_at >= thirty_days_ago
            )
        ).group_by(func.date(Finding.created_at)).all()
        
        return {
            "success": True,
            "data": {
                "by_severity": dict(by_severity),
                "by_risk_level": dict(by_risk_level),
                "average_risk_score": round(float(avg_risk), 2),
                "critical_findings_trend": [
                    {"date": str(d), "count": c}
                    for d, c in critical_trend
                ]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# POSTURE STATISTICS
# ============================================================

@router.get("/admin/statistics/posture")
async def get_posture_statistics(
    current_user: User = Depends(require_system_admin),
    db: Session = Depends(get_db)
):
    """Get security posture statistics"""
    try:
        # Average posture score
        avg_posture = db.query(func.avg(PostureScore.current_score)).filter(
            PostureScore.current_score.isnot(None)
        ).scalar() or 0
        
        # Posture distribution
        posture_ranges = [
            ("Excellent (90-100)", 90, 100),
            ("Good (75-89)", 75, 89),
            ("Fair (60-74)", 60, 74),
            ("Poor (< 60)", 0, 59)
        ]
        
        posture_distribution = []
        for label, min_score, max_score in posture_ranges:
            count = db.query(PostureScore).filter(
                and_(
                    PostureScore.current_score >= min_score,
                    PostureScore.current_score <= max_score
                )
            ).count()
            posture_distribution.append({"range": label, "count": count})
        
        # Recent posture changes
        recent_changes = db.query(PostureScore).order_by(
            desc(PostureScore.calculated_at)
        ).limit(10).all()
        
        return {
            "success": True,
            "data": {
                "average_posture_score": round(float(avg_posture), 2),
                "distribution": posture_distribution,
                "recent_assessments": len(recent_changes)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# DRIFT STATISTICS
# ============================================================

@router.get("/admin/statistics/drift")
async def get_drift_statistics(
    current_user: User = Depends(require_system_admin),
    db: Session = Depends(get_db)
):
    """Get configuration drift statistics"""
    try:
        # Total drift events
        total_drift = db.query(DriftAnalysis).count()
        
        # Drift by severity
        by_severity = db.query(
            DriftAnalysis.severity,
            func.count(DriftAnalysis.id)
        ).group_by(DriftAnalysis.severity).all()
        
        # Unresolved drift
        unresolved = db.query(DriftAnalysis).filter(
            DriftAnalysis.status == "DETECTED"
        ).count()
        
        # Drift trend
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        drift_trend = db.query(
            func.date(DriftAnalysis.detected_at).label('date'),
            func.count(DriftAnalysis.id).label('count')
        ).filter(
            DriftAnalysis.detected_at >= thirty_days_ago
        ).group_by(func.date(DriftAnalysis.detected_at)).all()
        
        return {
            "success": True,
            "data": {
                "total_drift_events": total_drift,
                "by_severity": dict(by_severity),
                "unresolved": unresolved,
                "drift_trend": [
                    {"date": str(d), "count": c}
                    for d, c in drift_trend
                ]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# WEBHOOK & EVENT STATISTICS
# ============================================================

@router.get("/admin/statistics/webhooks")
async def get_webhook_statistics(
    current_user: User = Depends(require_system_admin),
    db: Session = Depends(get_db)
):
    """Get webhook delivery statistics"""
    try:
        # Webhook deliveries
        total_deliveries = db.query(WebhookDelivery).count()
        successful = db.query(WebhookDelivery).filter(
            WebhookDelivery.status == "success"
        ).count()
        failed = db.query(WebhookDelivery).filter(
            WebhookDelivery.status == "failed"
        ).count()
        
        # Events by type
        by_event_type = db.query(
            EventLog.event_type,
            func.count(EventLog.id)
        ).group_by(EventLog.event_type).all()
        
        return {
            "success": True,
            "data": {
                "webhook_deliveries": {
                    "total": total_deliveries,
                    "successful": successful,
                    "failed": failed,
                    "success_rate": round((successful / total_deliveries * 100) if total_deliveries > 0 else 0, 2)
                },
                "events_by_type": dict(by_event_type)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# REPORT STATISTICS
# ============================================================

@router.get("/admin/statistics/reports")
async def get_report_statistics(
    current_user: User = Depends(require_system_admin),
    db: Session = Depends(get_db)
):
    """Get report generation statistics"""
    try:
        # Reports by type
        by_type = db.query(
            Report.report_type,
            func.count(Report.id)
        ).group_by(Report.report_type).all()
        
        # Reports by format
        by_format = db.query(
            Report.format,
            func.count(Report.id)
        ).group_by(Report.format).all()
        
        # Recent reports
        recent_count = db.query(Report).filter(
            Report.generated_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        return {
            "success": True,
            "data": {
                "by_type": dict(by_type),
                "by_format": dict(by_format),
                "generated_last_7_days": recent_count
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# HISTORICAL ANALYTICS
# ============================================================

@router.get("/admin/analytics/historical")
async def get_historical_analytics(
    days: int = Query(30, ge=7, le=365),
    current_user: User = Depends(require_system_admin),
    db: Session = Depends(get_db)
):
    """
    Get historical analytics across multiple metrics
    
    Provides trend data for compliance, risk, findings, etc.
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Compliance trend
        compliance_trend = db.query(
            func.date(Audit.completed_at).label('date'),
            func.avg(Audit.compliance_score).label('score')
        ).filter(
            and_(
                Audit.completed_at >= cutoff_date,
                Audit.compliance_score.isnot(None)
            )
        ).group_by(func.date(Audit.completed_at)).all()
        
        # Risk trend
        risk_trend = db.query(
            func.date(Audit.completed_at).label('date'),
            func.avg(Audit.risk_score).label('score')
        ).filter(
            and_(
                Audit.completed_at >= cutoff_date,
                Audit.risk_score.isnot(None)
            )
        ).group_by(func.date(Audit.completed_at)).all()
        
        # Finding trend
        finding_trend = db.query(
            func.date(Finding.created_at).label('date'),
            func.count(Finding.id).label('count')
        ).filter(
            Finding.created_at >= cutoff_date
        ).group_by(func.date(Finding.created_at)).all()
        
        # Critical finding trend
        critical_trend = db.query(
            func.date(Finding.created_at).label('date'),
            func.count(Finding.id).label('count')
        ).filter(
            and_(
                Finding.created_at >= cutoff_date,
                Finding.severity == "CRITICAL"
            )
        ).group_by(func.date(Finding.created_at)).all()
        
        return {
            "success": True,
            "data": {
                "period_days": days,
                "compliance_trend": [
                    {"date": str(d), "score": round(float(s), 2) if s else 0}
                    for d, s in compliance_trend
                ],
                "risk_trend": [
                    {"date": str(d), "score": round(float(s), 2) if s else 0}
                    for d, s in risk_trend
                ],
                "finding_trend": [
                    {"date": str(d), "count": c}
                    for d, c in finding_trend
                ],
                "critical_finding_trend": [
                    {"date": str(d), "count": c}
                    for d, c in critical_trend
                ]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# SYSTEM AUDIT LOGS
# ============================================================

@router.get("/admin/audit-logs")
async def get_audit_logs(
    event_type: Optional[str] = None,
    action: Optional[str] = None,
    user_id: Optional[int] = None,
    organization_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_system_admin),
    db: Session = Depends(get_db)
):
    """
    Get system audit logs with filtering
    
    System admin can view all audit logs
    """
    try:
        query = db.query(SecurityAuditLog)
        
        # Apply filters
        if event_type:
            query = query.filter(SecurityAuditLog.event_type == event_type)
        if action:
            query = query.filter(SecurityAuditLog.action == action)
        if user_id:
            query = query.filter(SecurityAuditLog.user_id == user_id)
        if organization_id:
            query = query.filter(SecurityAuditLog.organization_id == organization_id)
        if start_date:
            query = query.filter(SecurityAuditLog.timestamp >= start_date)
        if end_date:
            query = query.filter(SecurityAuditLog.timestamp <= end_date)
        
        # Get total count
        total = query.count()
        
        # Get logs
        logs = query.order_by(desc(SecurityAuditLog.timestamp)).offset(offset).limit(limit).all()
        
        return {
            "success": True,
            "data": {
                "logs": [
                    {
                        "log_id": log.log_id,
                        "timestamp": log.timestamp.isoformat(),
                        "user_id": log.user_id,
                        "organization_id": log.organization_id,
                        "event_type": log.event_type,
                        "action": log.action,
                        "result": log.result,
                        "resource_type": log.resource_type,
                        "resource_id": log.resource_id,
                        "ip_address": log.ip_address,
                        "details": log.details
                    }
                    for log in logs
                ],
                "total": total,
                "offset": offset,
                "limit": limit
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# SYSTEM HEALTH
# ============================================================

@router.get("/admin/system/health")
async def get_system_health(
    current_user: User = Depends(require_system_admin),
    db: Session = Depends(get_db)
):
    """Get system health status"""
    try:
        # Database health
        try:
            db.execute("SELECT 1")
            db_status = "healthy"
        except:
            db_status = "unhealthy"
        
        # Redis health (would need actual Redis connection)
        redis_status = "healthy"  # Placeholder
        
        # Storage health
        storage_status = "healthy"  # Placeholder
        
        # Recent errors
        recent_errors = db.query(SecurityAuditLog).filter(
            SecurityAuditLog.result == "FAILED"
        ).order_by(desc(SecurityAuditLog.timestamp)).limit(10).count()
        
        return {
            "success": True,
            "data": {
                "database": db_status,
                "redis": redis_status,
                "storage": storage_status,
                "recent_errors": recent_errors,
                "overall_status": "healthy" if db_status == "healthy" else "degraded"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# ORGANIZATION MANAGEMENT
# ============================================================

@router.get("/admin/organizations")
async def list_all_organizations(
    current_user: User = Depends(require_system_admin),
    db: Session = Depends(get_db)
):
    """List all organizations (system admin only)"""
    try:
        orgs = db.query(Organization).order_by(desc(Organization.created_at)).all()
        
        return {
            "success": True,
            "data": {
                "organizations": [
                    {
                        "id": org.id,
                        "name": org.name,
                        "contact_email": org.contact_email,
                        "subscription_tier": org.subscription_tier,
                        "is_active": org.is_active,
                        "created_at": org.created_at.isoformat() if org.created_at else None
                    }
                    for org in orgs
                ]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/users")
async def list_all_users(
    organization_id: Optional[int] = None,
    current_user: User = Depends(require_system_admin),
    db: Session = Depends(get_db)
):
    """List all users (system admin only)"""
    try:
        query = db.query(User)
        
        if organization_id:
            query = query.filter(User.organization_id == organization_id)
        
        users = query.order_by(desc(User.created_at)).all()
        
        return {
            "success": True,
            "data": {
                "users": [
                    {
                        "id": user.id,
                        "email": user.email,
                        "username": user.username,
                        "full_name": user.full_name,
                        "role": user.role,
                        "organization_id": user.organization_id,
                        "is_active": user.is_active,
                        "created_at": user.created_at.isoformat() if user.created_at else None
                    }
                    for user in users
                ]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# VENDOR MANAGEMENT SYSTEM (Phase 10)
# ============================================================

# Import vendor models
from app.database import VendorUser, VendorApprovalRequest, VendorOTP, VendorUploadSession

# Response models
class VendorRequestResponse(BaseModel):
    request_id: str
    vendor_id: str
    vendor_email: str
    company_name: str
    contact_name: str
    phone: Optional[str]
    vendor_type: Optional[str]
    status: str
    created_at: datetime
    reviewed_at: Optional[datetime]
    reviewed_by: Optional[str]

class VendorResponse(BaseModel):
    vendor_id: str
    company_name: str
    contact_name: str
    email: str
    phone: Optional[str]
    approval_status: str
    organization_id: int
    created_at: datetime
    approved_at: Optional[datetime]
    upload_count: int = 0


@router.get("/admin/vendor-requests")
async def get_vendor_requests(
    status: Optional[str] = Query("PENDING"),
    current_user: User = Depends(require_permission(Permission.VENDOR_MANAGE)),
    db: Session = Depends(get_db)
):
    """
    Get pending vendor access requests
    
    Admin can view all vendors requesting access for their organization
    """
    try:
        # Get vendor requests for this org
        query = db.query(VendorApprovalRequest).filter(
            VendorApprovalRequest.organization_id == current_user.organization_id
        )
        
        if status:
            query = query.filter(VendorApprovalRequest.status == status)
        
        requests = query.order_by(desc(VendorApprovalRequest.created_at)).all()
        
        result = []
        for req in requests:
            vendor = db.query(VendorUser).filter(VendorUser.id == req.vendor_id).first()
            if vendor:
                result.append({
                    "request_id": req.request_id,
                    "vendor_id": vendor.vendor_id,
                    "vendor_email": vendor.email,
                    "company_name": vendor.company_name,
                    "contact_name": vendor.contact_name,
                    "phone": vendor.phone,
                    "vendor_type": getattr(vendor, 'vendor_type', None),
                    "status": req.status,
                    "created_at": req.created_at.isoformat(),
                    "reviewed_at": req.reviewed_at.isoformat() if req.reviewed_at else None,
                    "reviewed_by": req.reviewed_by
                })
        
        return {
            "success": True,
            "data": {
                "requests": result,
                "total": len(result)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/vendors")
async def get_all_vendors(
    approval_status: Optional[str] = None,
    current_user: User = Depends(require_permission(Permission.VENDOR_VIEW)),
    db: Session = Depends(get_db)
):
    """
    Get all vendors for this organization
    
    Admin can view all registered vendors
    """
    try:
        query = db.query(VendorUser).filter(
            VendorUser.organization_id == current_user.organization_id
        )
        
        if approval_status:
            query = query.filter(VendorUser.approval_status == approval_status)
        
        vendors = query.order_by(desc(VendorUser.created_at)).all()
        
        result = []
        for vendor in vendors:
            # Count uploads
            upload_count = db.query(func.count(VendorUploadSession.id)).filter(
                VendorUploadSession.vendor_id == vendor.id
            ).scalar() or 0
            
            result.append({
                "vendor_id": vendor.vendor_id,
                "company_name": vendor.company_name,
                "contact_name": vendor.contact_name,
                "email": vendor.email,
                "phone": vendor.phone,
                "approval_status": vendor.approval_status,
                "organization_id": vendor.organization_id,
                "created_at": vendor.created_at.isoformat(),
                "approved_at": vendor.approved_at.isoformat() if vendor.approved_at else None,
                "approved_by": vendor.approved_by,
                "upload_count": upload_count,
                "is_active": vendor.is_active
            })
        
        return {
            "success": True,
            "data": {
                "vendors": result,
                "total": len(result)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/vendor-requests/{request_id}/approve")
async def approve_vendor_request(
    request_id: str,
    notes: Optional[str] = None,
    current_user: User = Depends(require_permission(Permission.VENDOR_MANAGE)),
    db: Session = Depends(get_db)
):
    """
    Approve a vendor access request
    
    Admin can approve vendors to give them access
    """
    try:
        # Find the request
        req = db.query(VendorApprovalRequest).filter(
            VendorApprovalRequest.request_id == request_id,
            VendorApprovalRequest.organization_id == current_user.organization_id
        ).first()
        
        if not req:
            raise HTTPException(status_code=404, detail="Request not found")
        
        if req.status != "PENDING":
            raise HTTPException(status_code=400, detail=f"Request status is {req.status}, not PENDING")
        
        # Get vendor
        vendor = db.query(VendorUser).filter(VendorUser.id == req.vendor_id).first()
        if not vendor:
            raise HTTPException(status_code=404, detail="Vendor not found")
        
        # Update approval request
        req.status = "APPROVED"
        req.reviewed_by = current_user.email
        req.reviewed_at = datetime.utcnow()
        req.review_notes = notes
        
        # Update vendor
        vendor.approval_status = "APPROVED"
        vendor.approved_by = current_user.email
        vendor.approved_at = datetime.utcnow()
        vendor.is_active = True
        
        db.add(req)
        db.add(vendor)
        db.commit()
        
        # Send approval email to vendor
        from app.services.email_service import get_email_service
        email_service = get_email_service()
        email_service.send_vendor_approval_notification(
            to_email=vendor.email,
            vendor_name=vendor.contact_name,
            organization_name=db.query(Organization).filter(
                Organization.id == current_user.organization_id
            ).first().name,
            admin_name=current_user.full_name or current_user.email,
            approved=True,
            notes=notes
        )
        
        # Log security event
        security_log = SecurityAuditLog(
            log_id=f"LOG-{db.query(func.count(SecurityAuditLog.id)).scalar() + 1:06d}",
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            event_type="VENDOR_APPROVAL",
            action="APPROVE",
            result="SUCCESS",
            resource_type="vendor",
            resource_id=vendor.vendor_id,
            details={"vendor_id": vendor.vendor_id, "request_id": request_id},
            ip_address="",
            user_agent=""
        )
        db.add(security_log)
        db.commit()
        
        return {
            "success": True,
            "data": {
                "vendor_id": vendor.vendor_id,
                "status": "APPROVED",
                "message": "Vendor approved successfully"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/vendor-requests/{request_id}/reject")
async def reject_vendor_request(
    request_id: str,
    notes: Optional[str] = None,
    current_user: User = Depends(require_permission(Permission.VENDOR_MANAGE)),
    db: Session = Depends(get_db)
):
    """
    Reject a vendor access request
    
    Admin can reject vendor registrations
    """
    try:
        # Find the request
        req = db.query(VendorApprovalRequest).filter(
            VendorApprovalRequest.request_id == request_id,
            VendorApprovalRequest.organization_id == current_user.organization_id
        ).first()
        
        if not req:
            raise HTTPException(status_code=404, detail="Request not found")
        
        if req.status != "PENDING":
            raise HTTPException(status_code=400, detail=f"Request status is {req.status}, not PENDING")
        
        # Get vendor
        vendor = db.query(VendorUser).filter(VendorUser.id == req.vendor_id).first()
        if not vendor:
            raise HTTPException(status_code=404, detail="Vendor not found")
        
        # Update approval request
        req.status = "REJECTED"
        req.reviewed_by = current_user.email
        req.reviewed_at = datetime.utcnow()
        req.review_notes = notes
        
        # Update vendor
        vendor.approval_status = "REJECTED"
        vendor.approved_by = current_user.email
        vendor.approved_at = datetime.utcnow()
        vendor.is_active = False
        
        db.add(req)
        db.add(vendor)
        db.commit()
        
        # Send rejection email to vendor
        from app.services.email_service import get_email_service
        email_service = get_email_service()
        email_service.send_vendor_approval_notification(
            to_email=vendor.email,
            vendor_name=vendor.contact_name,
            organization_name=db.query(Organization).filter(
                Organization.id == current_user.organization_id
            ).first().name,
            admin_name=current_user.full_name or current_user.email,
            approved=False,
            notes=notes
        )
        
        # Log security event
        security_log = SecurityAuditLog(
            log_id=f"LOG-{db.query(func.count(SecurityAuditLog.id)).scalar() + 1:06d}",
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            event_type="VENDOR_APPROVAL",
            action="REJECT",
            result="SUCCESS",
            resource_type="vendor",
            resource_id=vendor.vendor_id,
            details={"vendor_id": vendor.vendor_id, "request_id": request_id},
            ip_address="",
            user_agent=""
        )
        db.add(security_log)
        db.commit()
        
        return {
            "success": True,
            "data": {
                "vendor_id": vendor.vendor_id,
                "status": "REJECTED",
                "message": "Vendor rejected successfully"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/vendor-activity")
async def get_vendor_activity(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(require_permission(Permission.VENDOR_VIEW)),
    db: Session = Depends(get_db)
):
    """
    Get vendor activity statistics for the past N days
    
    Shows uploads, activity per vendor
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get all vendors
        vendors = db.query(VendorUser).filter(
            VendorUser.organization_id == current_user.organization_id
        ).all()
        
        vendor_stats = []
        total_uploads = 0
        active_vendors = 0
        
        for vendor in vendors:
            # Count sessions
            sessions = db.query(VendorUploadSession).filter(
                VendorUploadSession.vendor_id == vendor.id,
                VendorUploadSession.created_at >= cutoff_date
            ).all()
            
            upload_count = sum(s.upload_count or 0 for s in sessions)
            active_sessions = sum(1 for s in sessions if s.status == "ACTIVE")
            
            if upload_count > 0:
                active_vendors += 1
            total_uploads += upload_count
            
            last_activity = None
            if sessions:
                last_activity = max(s.last_activity for s in sessions if s.last_activity)
            
            vendor_stats.append({
                "vendor_id": vendor.vendor_id,
                "company": vendor.company_name,
                "contact": vendor.contact_name,
                "approval_status": vendor.approval_status,
                "sessions_count": len(sessions),
                "active_sessions": active_sessions,
                "total_uploads": upload_count,
                "last_activity": last_activity.isoformat() if last_activity else None
            })
        
        return {
            "success": True,
            "data": {
                "period_days": days,
                "summary": {
                    "total_uploads": total_uploads,
                    "active_vendors": active_vendors,
                    "total_vendors": len(vendors)
                },
                "vendors": sorted(vendor_stats, key=lambda x: x['total_uploads'], reverse=True)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/vendor-sessions")
async def get_vendor_sessions(
    current_user: User = Depends(require_permission(Permission.VENDOR_VIEW)),
    db: Session = Depends(get_db)
):
    """
    Get all active vendor sessions
    
    Admin can monitor vendor activity
    """
    try:
        # Get active sessions
        sessions = db.query(VendorUploadSession).filter(
            VendorUploadSession.status == "ACTIVE"
        ).all()
        
        result = []
        for session in sessions:
            vendor = db.query(VendorUser).filter(VendorUser.id == session.vendor_id).first()
            if vendor and vendor.organization_id == current_user.organization_id:
                result.append({
                    "session_id": session.session_id,
                    "vendor_id": vendor.vendor_id,
                    "vendor_name": vendor.contact_name,
                    "company": vendor.company_name,
                    "email": vendor.email,
                    "status": session.status,
                    "upload_count": session.upload_count or 0,
                    "created_at": session.created_at.isoformat(),
                    "expires_at": session.expires_at.isoformat(),
                    "last_activity": session.last_activity.isoformat() if session.last_activity else None
                })
        
        return {
            "success": True,
            "data": {
                "sessions": result,
                "total": len(result)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/vendor-sessions/{session_id}/revoke")
async def revoke_vendor_session(
    session_id: str,
    current_user: User = Depends(require_permission(Permission.VENDOR_MANAGE)),
    db: Session = Depends(get_db)
):
    """
    Revoke an active vendor upload session
    
    Admin can force logout a vendor
    """
    try:
        session = db.query(VendorUploadSession).filter(
            VendorUploadSession.session_id == session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        vendor = db.query(VendorUser).filter(VendorUser.id == session.vendor_id).first()
        if vendor and vendor.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        session.status = "REVOKED"
        db.add(session)
        db.commit()
        
        # Log security event
        security_log = SecurityAuditLog(
            log_id=f"LOG-{db.query(func.count(SecurityAuditLog.id)).scalar() + 1:06d}",
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            event_type="VENDOR_SESSION",
            action="REVOKE",
            result="SUCCESS",
            resource_type="session",
            resource_id=session_id,
            details={"vendor_id": vendor.vendor_id if vendor else None},
            ip_address="",
            user_agent=""
        )
        db.add(security_log)
        db.commit()
        
        return {
            "success": True,
            "data": {
                "session_id": session_id,
                "status": "REVOKED"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/admin/vendors/{vendor_id}/suspend")
async def suspend_vendor(
    vendor_id: str,
    current_user: User = Depends(require_permission(Permission.VENDOR_MANAGE)),
    db: Session = Depends(get_db)
):
    """
    Suspend a vendor account
    
    Admin can prevent a vendor from accessing the system
    """
    try:
        vendor = db.query(VendorUser).filter(
            VendorUser.vendor_id == vendor_id,
            VendorUser.organization_id == current_user.organization_id
        ).first()
        
        if not vendor:
            raise HTTPException(status_code=404, detail="Vendor not found")
        
        vendor.approval_status = "SUSPENDED"
        vendor.is_active = False
        
        db.add(vendor)
        db.commit()
        
        # Log security event
        security_log = SecurityAuditLog(
            log_id=f"LOG-{db.query(func.count(SecurityAuditLog.id)).scalar() + 1:06d}",
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            event_type="VENDOR_MANAGEMENT",
            action="SUSPEND",
            result="SUCCESS",
            resource_type="vendor",
            resource_id=vendor_id,
            details={"vendor_id": vendor_id},
            ip_address="",
            user_agent=""
        )
        db.add(security_log)
        db.commit()
        
        return {
            "success": True,
            "data": {
                "vendor_id": vendor_id,
                "status": "SUSPENDED"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
