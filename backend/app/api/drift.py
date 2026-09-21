"""
Configuration Drift Detection API
Phase 5: Drift analysis and tracking
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

from app.database import (
    get_db, Device, Configuration, ConfigurationVersion, 
    DriftAnalysis, User, SecurityAuditLog
)
from app.auth.dependencies import require_permission
from app.auth.permissions import Permission
from app.drift import detect_drift, compare_configurations
from app.parsers import parse_configuration
from app.normalization import normalize_parsed_data

router = APIRouter()


class DriftDetectionRequest(BaseModel):
    """Request to detect drift"""
    baseline_version_id: Optional[str] = None  # If not provided, use device baseline


@router.post("/devices/{device_id}/detect-drift")
async def detect_device_drift(
    device_id: str,
    request: DriftDetectionRequest,
    current_user: User = Depends(require_permission(Permission.AUDIT_RUN)),
    db: Session = Depends(get_db)
):
    """
    Detect configuration drift for a device
    
    Compares current configuration against baseline
    """
    try:
        # Get device
        device = db.query(Device).filter(
            Device.device_id == device_id,
            Device.organization_id == current_user.organization_id
        ).first()
        
        if not device:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Device {device_id} not found"
                    }
                }
            )
        
        # Get baseline configuration
        if request.baseline_version_id:
            baseline_version = db.query(ConfigurationVersion).filter(
                ConfigurationVersion.version_id == request.baseline_version_id
            ).first()
        elif device.baseline_config_id:
            baseline_config = db.query(Configuration).filter(
                Configuration.id == device.baseline_config_id
            ).first()
            if baseline_config:
                baseline_version = db.query(ConfigurationVersion).filter(
                    ConfigurationVersion.configuration_id == device.baseline_config_id,
                    ConfigurationVersion.is_baseline == True
                ).first()
        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": {
                        "code": "NO_BASELINE",
                        "message": "Device has no baseline configuration set"
                    }
                }
            )
        
        if not baseline_version:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "BASELINE_NOT_FOUND",
                        "message": "Baseline configuration not found"
                    }
                }
            )
        
        # Get current configuration
        if not device.current_config_id:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": {
                        "code": "NO_CURRENT_CONFIG",
                        "message": "Device has no current configuration"
                    }
                }
            )
        
        current_config = db.query(Configuration).filter(
            Configuration.id == device.current_config_id
        ).first()
        
        current_version = db.query(ConfigurationVersion).filter(
            ConfigurationVersion.configuration_id == device.current_config_id
        ).order_by(ConfigurationVersion.version_number.desc()).first()
        
        if not current_version:
            # Create version for current config if doesn't exist
            current_version = ConfigurationVersion(
                version_id=f"VER-{db.query(ConfigurationVersion).count() + 1:06d}",
                configuration_id=current_config.id,
                device_id=device.id,
                version_number=1,
                content_hash=current_config.file_hash_sha256,
                content=current_config.sanitized_content,
                file_size=current_config.file_size,
                uploaded_by=current_user.email,
                is_baseline=False
            )
            db.add(current_version)
            db.commit()
            db.refresh(current_version)
        
        # Parse both configurations
        baseline_parsed = parse_configuration(baseline_version.content, baseline_config.vendor)
        current_parsed = parse_configuration(current_version.content, current_config.vendor)
        
        # Normalize to UnifiedSecurityModel
        baseline_model = normalize_parsed_data(baseline_parsed, baseline_config.vendor)
        current_model = normalize_parsed_data(current_parsed, current_config.vendor)
        
        # Detect drift
        drift_result = detect_drift(baseline_model, current_model)
        
        # Generate drift_id
        drift_count = db.query(DriftAnalysis).filter(
            DriftAnalysis.organization_id == current_user.organization_id
        ).count()
        drift_id = f"DRF-{drift_count + 1:06d}"
        
        # Save drift analysis
        drift_analysis = DriftAnalysis(
            drift_id=drift_id,
            organization_id=current_user.organization_id,
            device_id=device.id,
            baseline_version_id=baseline_version.id,
            current_version_id=current_version.id,
            drift_score=drift_result.drift_score,
            drift_severity=drift_result.drift_severity,
            field_drifts=[
                {
                    "field_path": d.field_path,
                    "baseline_value": str(d.baseline_value),
                    "current_value": str(d.current_value),
                    "drift_type": d.drift_type,
                    "severity": d.severity,
                    "security_impact": d.security_impact
                }
                for d in drift_result.field_drifts
            ],
            added_fields=drift_result.added_fields,
            removed_fields=drift_result.removed_fields,
            modified_fields=drift_result.modified_fields,
            security_impact=drift_result.security_impact
        )
        
        db.add(drift_analysis)
        db.commit()
        db.refresh(drift_analysis)
        
        # Log action
        log = SecurityAuditLog(
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            action="DRIFT_DETECT",
            resource_type="drift",
            resource_id=drift_id,
            details=f"Detected drift for device {device.hostname}: score={drift_result.drift_score}",
            ip_address="",
            user_agent=""
        )
        db.add(log)
        db.commit()
        
        return {
            "success": True,
            "data": {
                "drift_id": drift_id,
                "device_id": device_id,
                "drift_score": drift_result.drift_score,
                "drift_severity": drift_result.drift_severity,
                "security_impact": drift_result.security_impact,
                "added_fields": drift_result.added_fields,
                "removed_fields": drift_result.removed_fields,
                "modified_fields": drift_result.modified_fields,
                "total_fields": drift_result.total_fields,
                "field_drifts": [
                    {
                        "field_path": d.field_path,
                        "drift_type": d.drift_type,
                        "severity": d.severity,
                        "security_impact": d.security_impact
                    }
                    for d in drift_result.field_drifts[:10]  # First 10 for preview
                ],
                "message": f"Drift analysis complete: {drift_result.drift_severity} severity"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "DRIFT_DETECTION_FAILED",
                    "message": f"Failed to detect drift: {str(e)}"
                }
            }
        )


@router.get("/devices/{device_id}/drift-history")
async def get_drift_history(
    device_id: str,
    current_user: User = Depends(require_permission(Permission.AUDIT_VIEW)),
    db: Session = Depends(get_db),
    limit: int = 50
):
    """
    Get drift history for a device
    """
    try:
        # Get device
        device = db.query(Device).filter(
            Device.device_id == device_id,
            Device.organization_id == current_user.organization_id
        ).first()
        
        if not device:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Device {device_id} not found"
                    }
                }
            )
        
        # Get drift analyses
        drifts = db.query(DriftAnalysis).filter(
            DriftAnalysis.device_id == device.id
        ).order_by(DriftAnalysis.detected_at.desc()).limit(limit).all()
        
        return {
            "success": True,
            "data": {
                "device_id": device_id,
                "hostname": device.hostname,
                "drifts": [
                    {
                        "drift_id": d.drift_id,
                        "drift_score": d.drift_score,
                        "drift_severity": d.drift_severity,
                        "security_impact": d.security_impact,
                        "added_fields": d.added_fields,
                        "removed_fields": d.removed_fields,
                        "modified_fields": d.modified_fields,
                        "detected_at": d.detected_at.isoformat(),
                        "acknowledged": d.acknowledged,
                        "acknowledged_by": d.acknowledged_by
                    }
                    for d in drifts
                ],
                "total": len(drifts)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "GET_FAILED",
                    "message": "Failed to retrieve drift history"
                }
            }
        )


@router.get("/drift/{drift_id}")
async def get_drift_details(
    drift_id: str,
    current_user: User = Depends(require_permission(Permission.AUDIT_VIEW)),
    db: Session = Depends(get_db)
):
    """
    Get detailed drift analysis
    """
    try:
        drift = db.query(DriftAnalysis).filter(
            DriftAnalysis.drift_id == drift_id,
            DriftAnalysis.organization_id == current_user.organization_id
        ).first()
        
        if not drift:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Drift analysis {drift_id} not found"
                    }
                }
            )
        
        # Get device
        device = db.query(Device).filter(Device.id == drift.device_id).first()
        
        return {
            "success": True,
            "data": {
                "drift_id": drift.drift_id,
                "device": {
                    "device_id": device.device_id,
                    "hostname": device.hostname
                },
                "drift_score": drift.drift_score,
                "drift_severity": drift.drift_severity,
                "security_impact": drift.security_impact,
                "added_fields": drift.added_fields,
                "removed_fields": drift.removed_fields,
                "modified_fields": drift.modified_fields,
                "field_drifts": drift.field_drifts,
                "detected_at": drift.detected_at.isoformat(),
                "acknowledged": drift.acknowledged,
                "acknowledged_by": drift.acknowledged_by,
                "acknowledged_at": drift.acknowledged_at.isoformat() if drift.acknowledged_at else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "GET_FAILED",
                    "message": "Failed to retrieve drift details"
                }
            }
        )


@router.post("/drift/{drift_id}/acknowledge")
async def acknowledge_drift(
    drift_id: str,
    current_user: User = Depends(require_permission(Permission.FINDING_UPDATE)),
    db: Session = Depends(get_db)
):
    """
    Acknowledge a drift analysis
    """
    try:
        drift = db.query(DriftAnalysis).filter(
            DriftAnalysis.drift_id == drift_id,
            DriftAnalysis.organization_id == current_user.organization_id
        ).first()
        
        if not drift:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Drift analysis {drift_id} not found"
                    }
                }
            )
        
        drift.acknowledged = True
        drift.acknowledged_by = current_user.email
        drift.acknowledged_at = datetime.utcnow()
        
        db.commit()
        
        # Log action
        log = SecurityAuditLog(
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            action="DRIFT_ACKNOWLEDGE",
            resource_type="drift",
            resource_id=drift_id,
            details=f"Acknowledged drift {drift_id}",
            ip_address="",
            user_agent=""
        )
        db.add(log)
        db.commit()
        
        return {
            "success": True,
            "data": {
                "drift_id": drift_id,
                "acknowledged": True,
                "acknowledged_by": current_user.email,
                "message": "Drift acknowledged successfully"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "ACKNOWLEDGE_FAILED",
                    "message": "Failed to acknowledge drift"
                }
            }
        )


@router.get("/dashboard/drift-summary")
async def get_drift_summary(
    current_user: User = Depends(require_permission(Permission.AUDIT_VIEW)),
    db: Session = Depends(get_db)
):
    """
    Get organization-wide drift summary
    """
    try:
        # Total drifts
        total_drifts = db.query(DriftAnalysis).filter(
            DriftAnalysis.organization_id == current_user.organization_id
        ).count()
        
        # By severity
        by_severity = db.query(
            DriftAnalysis.drift_severity,
            func.count(DriftAnalysis.id)
        ).filter(
            DriftAnalysis.organization_id == current_user.organization_id
        ).group_by(DriftAnalysis.drift_severity).all()
        
        # Unacknowledged
        unacknowledged = db.query(DriftAnalysis).filter(
            DriftAnalysis.organization_id == current_user.organization_id,
            DriftAnalysis.acknowledged == False
        ).count()
        
        # Average drift score
        avg_drift_score = db.query(func.avg(DriftAnalysis.drift_score)).filter(
            DriftAnalysis.organization_id == current_user.organization_id
        ).scalar() or 0
        
        # Devices with critical drift
        critical_devices = db.query(DriftAnalysis.device_id).filter(
            DriftAnalysis.organization_id == current_user.organization_id,
            DriftAnalysis.drift_severity == "CRITICAL"
        ).distinct().count()
        
        return {
            "success": True,
            "data": {
                "total_drifts": total_drifts,
                "unacknowledged": unacknowledged,
                "average_drift_score": round(avg_drift_score, 2),
                "critical_devices": critical_devices,
                "by_severity": {severity: count for severity, count in by_severity}
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "SUMMARY_FAILED",
                    "message": "Failed to retrieve drift summary"
                }
            }
        )
