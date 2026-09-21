"""
Configuration Monitoring & Change Detection API
Phase 7.1: Real-time monitoring dashboard
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta

from app.database import (
    get_db, ConfigurationVersion, Device, Configuration,
    DriftAnalysis, User, SecurityAuditLog
)
from app.auth.dependencies import require_permission
from app.auth.permissions import Permission
from app.monitoring.change_detector import ChangeDetector

router = APIRouter()


def generate_log_id(db: Session) -> str:
    """Generate unique audit log ID"""
    count = db.query(SecurityAuditLog).count()
    return f"LOG-{count + 1:08d}"


class ChangeDetectionRequest(BaseModel):
    """Request to detect changes"""
    device_id: str
    baseline_version_id: Optional[str] = None
    current_version_id: Optional[str] = None


@router.get("/monitoring/dashboard")
async def get_monitoring_dashboard(
    current_user: User = Depends(require_permission(Permission.CONFIG_READ)),
    db: Session = Depends(get_db),
    days: int = 7
):
    """
    Get monitoring dashboard overview
    
    Provides real-time overview of configuration changes, drift, and alerts
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Recent configuration changes
        recent_versions = db.query(ConfigurationVersion).filter(
            ConfigurationVersion.uploaded_at >= cutoff_date
        ).count()
        
        # Recent drift detections
        recent_drift = db.query(DriftAnalysis).filter(
            DriftAnalysis.organization_id == current_user.organization_id,
            DriftAnalysis.detected_at >= cutoff_date
        ).count()
        
        # Critical drift
        critical_drift = db.query(DriftAnalysis).filter(
            DriftAnalysis.organization_id == current_user.organization_id,
            DriftAnalysis.drift_severity == "CRITICAL",
            DriftAnalysis.acknowledged == False
        ).count()
        
        # Devices with recent changes
        devices_changed = db.query(func.count(func.distinct(ConfigurationVersion.device_id))).filter(
            ConfigurationVersion.uploaded_at >= cutoff_date,
            ConfigurationVersion.device_id.isnot(None)
        ).scalar()
        
        # Recent security audit events
        security_events = db.query(SecurityAuditLog).filter(
            SecurityAuditLog.organization_id == current_user.organization_id,
            SecurityAuditLog.timestamp >= cutoff_date,
            SecurityAuditLog.event_type.in_(['CONFIG_VERSION', 'DEVICE', 'REMEDIATION'])
        ).order_by(desc(SecurityAuditLog.timestamp)).limit(10).all()
        
        # Change timeline (daily counts)
        timeline = []
        for i in range(days):
            day_start = datetime.utcnow() - timedelta(days=i+1)
            day_end = datetime.utcnow() - timedelta(days=i)
            
            day_changes = db.query(ConfigurationVersion).filter(
                ConfigurationVersion.uploaded_at >= day_start,
                ConfigurationVersion.uploaded_at < day_end
            ).count()
            
            timeline.append({
                "date": day_start.strftime("%Y-%m-%d"),
                "changes": day_changes
            })
        
        return {
            "success": True,
            "data": {
                "period_days": days,
                "summary": {
                    "total_changes": recent_versions,
                    "drift_detections": recent_drift,
                    "critical_drift": critical_drift,
                    "devices_changed": devices_changed,
                    "security_events": len(security_events)
                },
                "timeline": list(reversed(timeline)),
                "recent_events": [
                    {
                        "log_id": e.log_id,
                        "event_type": e.event_type,
                        "action": e.action,
                        "result": e.result,
                        "resource_type": e.resource_type,
                        "resource_id": e.resource_id,
                        "timestamp": e.timestamp.isoformat()
                    }
                    for e in security_events
                ],
                "alerts": {
                    "critical": critical_drift,
                    "warnings": 0,  # Could add more alert types
                    "info": recent_versions
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/monitoring/detect-changes")
async def detect_configuration_changes(
    request: ChangeDetectionRequest,
    current_user: User = Depends(require_permission(Permission.CONFIG_READ)),
    db: Session = Depends(get_db)
):
    """
    Detect changes between two configuration versions
    
    Performs deep analysis of changes including severity and impact
    """
    try:
        # Get device
        device = db.query(Device).filter(
            Device.device_id == request.device_id,
            Device.organization_id == current_user.organization_id
        ).first()
        
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        # Get baseline version
        if request.baseline_version_id:
            baseline = db.query(ConfigurationVersion).filter(
                ConfigurationVersion.version_id == request.baseline_version_id
            ).first()
        else:
            # Use device's baseline or latest
            baseline = db.query(ConfigurationVersion).filter(
                ConfigurationVersion.device_id == device.id,
                ConfigurationVersion.is_baseline == True
            ).first()
            
            if not baseline:
                # Get oldest version
                baseline = db.query(ConfigurationVersion).filter(
                    ConfigurationVersion.device_id == device.id
                ).order_by(ConfigurationVersion.version_number).first()
        
        # Get current version
        if request.current_version_id:
            current = db.query(ConfigurationVersion).filter(
                ConfigurationVersion.version_id == request.current_version_id
            ).first()
        else:
            # Get latest version
            current = db.query(ConfigurationVersion).filter(
                ConfigurationVersion.device_id == device.id
            ).order_by(desc(ConfigurationVersion.version_number)).first()
        
        if not baseline or not current:
            raise HTTPException(status_code=404, detail="Version not found")
        
        # Perform change detection
        detector = ChangeDetector()
        changes = detector.detect_changes(baseline, current)
        
        # Log detection
        log = SecurityAuditLog(
            log_id=generate_log_id(db),
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            event_type="MONITORING",
            action="DETECT_CHANGES",
            result="SUCCESS",
            resource_type="device",
            resource_id=request.device_id,
            details={
                "baseline_version": baseline.version_id,
                "current_version": current.version_id,
                "severity": changes["severity"],
                "change_score": changes["change_score"]
            },
            ip_address="",
            user_agent=""
        )
        db.add(log)
        db.commit()
        
        return {
            "success": True,
            "data": {
                "device_id": request.device_id,
                "device_hostname": device.hostname,
                **changes
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/monitoring/device-status/{device_id}")
async def get_device_monitoring_status(
    device_id: str,
    current_user: User = Depends(require_permission(Permission.CONFIG_READ)),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive monitoring status for a device
    """
    try:
        # Get device
        device = db.query(Device).filter(
            Device.device_id == device_id,
            Device.organization_id == current_user.organization_id
        ).first()
        
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        # Get version count
        version_count = db.query(ConfigurationVersion).filter(
            ConfigurationVersion.device_id == device.id
        ).count()
        
        # Get latest version
        latest_version = db.query(ConfigurationVersion).filter(
            ConfigurationVersion.device_id == device.id
        ).order_by(desc(ConfigurationVersion.version_number)).first()
        
        # Get baseline version
        baseline_version = db.query(ConfigurationVersion).filter(
            ConfigurationVersion.device_id == device.id,
            ConfigurationVersion.is_baseline == True
        ).first()
        
        # Get drift status
        latest_drift = db.query(DriftAnalysis).filter(
            DriftAnalysis.device_id == device.id
        ).order_by(desc(DriftAnalysis.detected_at)).first()
        
        # Calculate status
        status = "HEALTHY"
        if latest_drift and not latest_drift.acknowledged:
            if latest_drift.drift_severity in ["CRITICAL", "HIGH"]:
                status = "ALERT"
            else:
                status = "WARNING"
        
        return {
            "success": True,
            "data": {
                "device_id": device_id,
                "hostname": device.hostname,
                "status": status,
                "monitoring": {
                    "total_versions": version_count,
                    "latest_version": {
                        "version_id": latest_version.version_id if latest_version else None,
                        "version_number": latest_version.version_number if latest_version else None,
                        "uploaded_at": latest_version.uploaded_at.isoformat() if latest_version else None
                    } if latest_version else None,
                    "baseline_version": {
                        "version_id": baseline_version.version_id if baseline_version else None,
                        "version_number": baseline_version.version_number if baseline_version else None,
                        "uploaded_at": baseline_version.uploaded_at.isoformat() if baseline_version else None
                    } if baseline_version else None,
                    "drift": {
                        "has_drift": latest_drift is not None,
                        "drift_score": latest_drift.drift_score if latest_drift else 0,
                        "drift_severity": latest_drift.drift_severity if latest_drift else None,
                        "acknowledged": latest_drift.acknowledged if latest_drift else None,
                        "detected_at": latest_drift.detected_at.isoformat() if latest_drift else None
                    } if latest_drift else None
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/monitoring/alerts")
async def get_monitoring_alerts(
    current_user: User = Depends(require_permission(Permission.CONFIG_READ)),
    db: Session = Depends(get_db),
    severity: Optional[str] = None,
    acknowledged: Optional[bool] = False
):
    """
    Get active monitoring alerts
    """
    try:
        # Get unacknowledged drift
        query = db.query(DriftAnalysis).filter(
            DriftAnalysis.organization_id == current_user.organization_id,
            DriftAnalysis.acknowledged == acknowledged
        )
        
        if severity:
            query = query.filter(DriftAnalysis.drift_severity == severity)
        
        drift_alerts = query.order_by(desc(DriftAnalysis.detected_at)).limit(50).all()
        
        alerts = []
        for drift in drift_alerts:
            device = db.query(Device).filter(Device.id == drift.device_id).first()
            
            alerts.append({
                "alert_type": "DRIFT",
                "severity": drift.drift_severity,
                "drift_id": drift.drift_id,
                "device_id": device.device_id if device else None,
                "device_hostname": device.hostname if device else None,
                "drift_score": drift.drift_score,
                "detected_at": drift.detected_at.isoformat(),
                "acknowledged": drift.acknowledged,
                "message": f"Configuration drift detected on {device.hostname if device else 'device'}"
            })
        
        return {
            "success": True,
            "data": {
                "total_alerts": len(alerts),
                "alerts": alerts
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
