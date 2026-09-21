"""
Configuration Version Management API
Phase 7.1: Version tracking, comparison, and rollback
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import hashlib

from app.database import (
    get_db, ConfigurationVersion, Configuration, Device, User,
    SecurityAuditLog
)
from app.auth.dependencies import require_permission
from app.auth.permissions import Permission

router = APIRouter()


def generate_log_id(db: Session) -> str:
    """Generate unique audit log ID"""
    count = db.query(SecurityAuditLog).count()
    return f"LOG-{count + 1:08d}"


def calculate_content_hash(content: str) -> str:
    """Calculate SHA-256 hash of configuration content"""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


class VersionCreate(BaseModel):
    """Create a new configuration version"""
    configuration_id: str
    device_id: Optional[str] = None
    content: str
    change_summary: Optional[str] = None
    is_baseline: bool = False


class BaselineUpdate(BaseModel):
    """Update baseline version"""
    is_baseline: bool


@router.post("/config-versions")
async def create_version(
    version_data: VersionCreate,
    current_user: User = Depends(require_permission(Permission.CONFIG_UPLOAD)),
    db: Session = Depends(get_db)
):
    """
    Create a new configuration version
    
    Automatically tracks version history for configurations
    
    SECURITY: Verifies configuration belongs to user's organization
    """
    try:
        # Get configuration WITH organization validation
        config = db.query(Configuration).filter(
            Configuration.config_id == version_data.configuration_id,
            Configuration.organization_id == current_user.organization_id
        ).first()
        
        if not config:
            raise HTTPException(
                status_code=404, 
                detail="Configuration not found or access denied"
            )
        
        # Get device if provided
        device_pk = None
        if version_data.device_id:
            device = db.query(Device).filter(
                Device.device_id == version_data.device_id,
                Device.organization_id == current_user.organization_id
            ).first()
            if device:
                device_pk = device.id
        
        # Calculate content hash
        content_hash = calculate_content_hash(version_data.content)
        
        # Check if this exact version already exists
        existing = db.query(ConfigurationVersion).filter(
            ConfigurationVersion.configuration_id == config.id,
            ConfigurationVersion.content_hash == content_hash
        ).first()
        
        if existing:
            return {
                "success": True,
                "data": {
                    "version_id": existing.version_id,
                    "message": "Version already exists",
                    "version_number": existing.version_number
                }
            }
        
        # Get latest version number
        latest = db.query(ConfigurationVersion).filter(
            ConfigurationVersion.configuration_id == config.id
        ).order_by(desc(ConfigurationVersion.version_number)).first()
        
        version_number = (latest.version_number + 1) if latest else 1
        
        # Generate version_id
        version_id = f"{version_data.configuration_id}-V{version_number:03d}"
        
        # If setting as baseline, clear other baselines
        if version_data.is_baseline:
            db.query(ConfigurationVersion).filter(
                ConfigurationVersion.configuration_id == config.id,
                ConfigurationVersion.is_baseline == True
            ).update({"is_baseline": False})
        
        # Create version
        new_version = ConfigurationVersion(
            version_id=version_id,
            configuration_id=config.id,
            device_id=device_pk,
            version_number=version_number,
            content_hash=content_hash,
            content=version_data.content,
            file_size=len(version_data.content.encode('utf-8')),
            uploaded_by=current_user.email,
            change_summary=version_data.change_summary,
            is_baseline=version_data.is_baseline,
            parent_version_id=latest.id if latest else None
        )
        
        db.add(new_version)
        db.commit()
        db.refresh(new_version)
        
        # Log
        log = SecurityAuditLog(
            log_id=generate_log_id(db),
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            event_type="CONFIG_VERSION",
            action="CREATE",
            result="SUCCESS",
            resource_type="config_version",
            resource_id=version_id,
            details={
                "version_number": version_number,
                "config_id": version_data.configuration_id,
                "is_baseline": version_data.is_baseline
            },
            ip_address="",
            user_agent=""
        )
        db.add(log)
        db.commit()
        
        return {
            "success": True,
            "data": {
                "version_id": version_id,
                "version_number": version_number,
                "content_hash": content_hash,
                "is_baseline": version_data.is_baseline
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config-versions/config/{config_id}")
async def list_versions(
    config_id: str,
    current_user: User = Depends(require_permission(Permission.CONFIG_READ)),
    db: Session = Depends(get_db),
    limit: int = 50
):
    """
    List all versions for a configuration
    
    SECURITY: Verifies configuration belongs to user's organization
    """
    try:
        # Get configuration WITH organization validation
        config = db.query(Configuration).filter(
            Configuration.config_id == config_id,
            Configuration.organization_id == current_user.organization_id
        ).first()
        
        if not config:
            raise HTTPException(
                status_code=404, 
                detail="Configuration not found or access denied"
            )
        
        # Get versions
        versions = db.query(ConfigurationVersion).filter(
            ConfigurationVersion.configuration_id == config.id
        ).order_by(desc(ConfigurationVersion.version_number)).limit(limit).all()
        
        return {
            "success": True,
            "data": {
                "config_id": config_id,
                "total_versions": len(versions),
                "versions": [
                    {
                        "version_id": v.version_id,
                        "version_number": v.version_number,
                        "content_hash": v.content_hash,
                        "file_size": v.file_size,
                        "uploaded_by": v.uploaded_by,
                        "change_summary": v.change_summary,
                        "is_baseline": v.is_baseline,
                        "uploaded_at": v.uploaded_at.isoformat()
                    }
                    for v in versions
                ]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config-versions/{version_id}")
async def get_version(
    version_id: str,
    current_user: User = Depends(require_permission(Permission.CONFIG_READ)),
    db: Session = Depends(get_db),
    include_content: bool = False
):
    """
    Get specific version details
    
    SECURITY: Verifies parent configuration belongs to user's organization
    """
    try:
        # Join with Configuration to verify organization ownership
        version = db.query(ConfigurationVersion).join(
            Configuration, ConfigurationVersion.configuration_id == Configuration.id
        ).filter(
            ConfigurationVersion.version_id == version_id,
            Configuration.organization_id == current_user.organization_id
        ).first()
        
        if not version:
            raise HTTPException(
                status_code=404, 
                detail="Version not found or access denied"
            )
        
        # Get configuration info
        config = db.query(Configuration).filter(
            Configuration.id == version.configuration_id
        ).first()
        
        data = {
            "version_id": version.version_id,
            "config_id": config.config_id if config else None,
            "version_number": version.version_number,
            "content_hash": version.content_hash,
            "file_size": version.file_size,
            "uploaded_by": version.uploaded_by,
            "change_summary": version.change_summary,
            "is_baseline": version.is_baseline,
            "uploaded_at": version.uploaded_at.isoformat()
        }
        
        if include_content:
            data["content"] = version.content
        
        return {
            "success": True,
            "data": data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/config-versions/{version_id}/baseline")
async def set_baseline(
    version_id: str,
    baseline_data: BaselineUpdate,
    current_user: User = Depends(require_permission(Permission.CONFIG_UPLOAD)),
    db: Session = Depends(get_db)
):
    """
    Set or unset a version as baseline
    
    SECURITY: Verifies parent configuration belongs to user's organization
    """
    try:
        # Join with Configuration to verify organization ownership
        version = db.query(ConfigurationVersion).join(
            Configuration, ConfigurationVersion.configuration_id == Configuration.id
        ).filter(
            ConfigurationVersion.version_id == version_id,
            Configuration.organization_id == current_user.organization_id
        ).first()
        
        if not version:
            raise HTTPException(
                status_code=404, 
                detail="Version not found or access denied"
            )
        
        # If setting as baseline, clear other baselines
        if baseline_data.is_baseline:
            db.query(ConfigurationVersion).filter(
                ConfigurationVersion.configuration_id == version.configuration_id,
                ConfigurationVersion.is_baseline == True
            ).update({"is_baseline": False})
        
        version.is_baseline = baseline_data.is_baseline
        db.commit()
        
        # Log
        log = SecurityAuditLog(
            log_id=generate_log_id(db),
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            event_type="CONFIG_VERSION",
            action="UPDATE_BASELINE",
            result="SUCCESS",
            resource_type="config_version",
            resource_id=version_id,
            details={"is_baseline": baseline_data.is_baseline},
            ip_address="",
            user_agent=""
        )
        db.add(log)
        db.commit()
        
        return {
            "success": True,
            "data": {
                "version_id": version_id,
                "is_baseline": version.is_baseline
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/config-versions/{version_id}/compare/{target_version_id}")
async def compare_versions(
    version_id: str,
    target_version_id: str,
    current_user: User = Depends(require_permission(Permission.CONFIG_READ)),
    db: Session = Depends(get_db)
):
    """
    Compare two configuration versions
    
    Returns unified diff and change statistics
    
    SECURITY: Verifies both versions' parent configurations belong to user's organization
    """
    try:
        import difflib
        
        # Get both versions WITH organization validation
        version1 = db.query(ConfigurationVersion).join(
            Configuration, ConfigurationVersion.configuration_id == Configuration.id
        ).filter(
            ConfigurationVersion.version_id == version_id,
            Configuration.organization_id == current_user.organization_id
        ).first()
        
        if not version1:
            raise HTTPException(
                status_code=404, 
                detail=f"Version {version_id} not found or access denied"
            )
        
        version2 = db.query(ConfigurationVersion).join(
            Configuration, ConfigurationVersion.configuration_id == Configuration.id
        ).filter(
            ConfigurationVersion.version_id == target_version_id,
            Configuration.organization_id == current_user.organization_id
        ).first()
        
        if not version2:
            raise HTTPException(
                status_code=404, 
                detail=f"Version {target_version_id} not found or access denied"
            )
        
        # Generate diff
        diff = list(difflib.unified_diff(
            version1.content.splitlines(keepends=True),
            version2.content.splitlines(keepends=True),
            fromfile=f"{version1.version_id} ({version1.uploaded_at.strftime('%Y-%m-%d')})",
            tofile=f"{version2.version_id} ({version2.uploaded_at.strftime('%Y-%m-%d')})",
            lineterm=''
        ))
        
        # Calculate statistics
        added_lines = sum(1 for line in diff if line.startswith('+') and not line.startswith('+++'))
        removed_lines = sum(1 for line in diff if line.startswith('-') and not line.startswith('---'))
        
        return {
            "success": True,
            "data": {
                "version1": {
                    "version_id": version1.version_id,
                    "version_number": version1.version_number,
                    "uploaded_at": version1.uploaded_at.isoformat()
                },
                "version2": {
                    "version_id": version2.version_id,
                    "version_number": version2.version_number,
                    "uploaded_at": version2.uploaded_at.isoformat()
                },
                "diff": ''.join(diff),
                "statistics": {
                    "added_lines": added_lines,
                    "removed_lines": removed_lines,
                    "total_changes": added_lines + removed_lines
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config-versions/device/{device_id}")
async def list_device_versions(
    device_id: str,
    current_user: User = Depends(require_permission(Permission.CONFIG_READ)),
    db: Session = Depends(get_db),
    limit: int = 50
):
    """
    List all configuration versions for a device
    """
    try:
        # Get device
        device = db.query(Device).filter(
            Device.device_id == device_id,
            Device.organization_id == current_user.organization_id
        ).first()
        
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        # Get versions
        versions = db.query(ConfigurationVersion).filter(
            ConfigurationVersion.device_id == device.id
        ).order_by(desc(ConfigurationVersion.uploaded_at)).limit(limit).all()
        
        return {
            "success": True,
            "data": {
                "device_id": device_id,
                "hostname": device.hostname,
                "total_versions": len(versions),
                "versions": [
                    {
                        "version_id": v.version_id,
                        "version_number": v.version_number,
                        "content_hash": v.content_hash,
                        "file_size": v.file_size,
                        "uploaded_by": v.uploaded_by,
                        "change_summary": v.change_summary,
                        "is_baseline": v.is_baseline,
                        "uploaded_at": v.uploaded_at.isoformat()
                    }
                    for v in versions
                ]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
