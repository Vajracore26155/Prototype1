"""
Device Management API Endpoints
Phase 5: Device inventory, grouping, tagging
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import csv
import io

from app.database import get_db, Device, Configuration, User, SecurityAuditLog, DeviceTag
from app.auth.dependencies import require_permission
from app.auth.permissions import Permission

router = APIRouter()


def generate_log_id(db: Session) -> str:
    """Generate unique audit log ID"""
    count = db.query(SecurityAuditLog).count()
    return f"LOG-{count + 1:08d}"


# ============================================================
# REQUEST/RESPONSE MODELS
# ============================================================

class DeviceCreate(BaseModel):
    """Request to create a device"""
    hostname: str
    ip_address: Optional[str] = None
    vendor: Optional[str] = None
    model: Optional[str] = None
    platform: Optional[str] = None
    os_version: Optional[str] = None
    device_type: Optional[str] = None
    location: Optional[str] = None
    site: Optional[str] = None
    owner: Optional[str] = None
    criticality: Optional[str] = "MEDIUM"
    management_ip: Optional[str] = None
    serial_number: Optional[str] = None
    tags: Optional[dict] = {}
    metadata: Optional[dict] = {}


class DeviceUpdate(BaseModel):
    """Request to update a device"""
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    vendor: Optional[str] = None
    model: Optional[str] = None
    platform: Optional[str] = None
    os_version: Optional[str] = None
    device_type: Optional[str] = None
    location: Optional[str] = None
    site: Optional[str] = None
    owner: Optional[str] = None
    criticality: Optional[str] = None
    status: Optional[str] = None
    management_ip: Optional[str] = None
    serial_number: Optional[str] = None
    tags: Optional[dict] = None
    metadata: Optional[dict] = None


class DeviceTagRequest(BaseModel):
    """Request to add/update device tags"""
    tags: dict


# ============================================================
# DEVICE CRUD OPERATIONS
# ============================================================

@router.post("/devices")
async def create_device(
    device: DeviceCreate,
    current_user: User = Depends(require_permission(Permission.CONFIG_UPLOAD)),
    db: Session = Depends(get_db)
):
    """
    Create a new network device
    
    Requires: CONFIG_UPLOAD permission
    """
    try:
        # Generate device_id
        device_count = db.query(Device).filter(
            Device.organization_id == current_user.organization_id
        ).count()
        device_id = f"DEV-{device_count + 1:06d}"
        
        # Check for duplicate hostname in organization
        existing = db.query(Device).filter(
            Device.organization_id == current_user.organization_id,
            Device.hostname == device.hostname
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=409,
                detail={
                    "success": False,
                    "error": {
                        "code": "DUPLICATE_DEVICE",
                        "message": f"Device with hostname '{device.hostname}' already exists"
                    }
                }
            )
        
        # Create device
        new_device = Device(
            device_id=device_id,
            organization_id=current_user.organization_id,
            hostname=device.hostname,
            ip_address=device.ip_address,
            vendor=device.vendor,
            model=device.model,
            platform=device.platform,
            os_version=device.os_version,
            device_type=device.device_type,
            location=device.location,
            site=device.site,
            owner=device.owner,
            criticality=device.criticality,
            management_ip=device.management_ip,
            serial_number=device.serial_number,
            tags=device.tags,
            metadata=device.metadata,
            status="ACTIVE"
        )
        
        db.add(new_device)
        db.commit()
        db.refresh(new_device)
        
        # Log action
        log = SecurityAuditLog(
            log_id=generate_log_id(db),
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            event_type="DEVICE",
            action="CREATE",
            result="SUCCESS",
            resource_type="device",
            resource_id=new_device.device_id,
            details={"message": f"Created device {device.hostname}", "hostname": device.hostname},
            ip_address="",
            user_agent=""
        )
        db.add(log)
        db.commit()
        
        return {
            "success": True,
            "data": {
                "device_id": new_device.device_id,
                "hostname": new_device.hostname,
                "message": "Device created successfully"
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
                    "code": "CREATE_FAILED",
                    "message": f"Failed to create device: {str(e)}"
                }
            }
        )


@router.get("/devices")
async def list_devices(
    current_user: User = Depends(require_permission(Permission.CONFIG_READ)),
    db: Session = Depends(get_db),
    vendor: Optional[str] = None,
    device_type: Optional[str] = None,
    status: Optional[str] = None,
    site: Optional[str] = None,
    criticality: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """
    List devices with filtering
    
    Requires: CONFIG_READ permission
    """
    try:
        query = db.query(Device).filter(
            Device.organization_id == current_user.organization_id
        )
        
        # Apply filters
        if vendor:
            query = query.filter(Device.vendor == vendor)
        if device_type:
            query = query.filter(Device.device_type == device_type)
        if status:
            query = query.filter(Device.status == status)
        if site:
            query = query.filter(Device.site == site)
        if criticality:
            query = query.filter(Device.criticality == criticality)
        if search:
            query = query.filter(
                or_(
                    Device.hostname.ilike(f"%{search}%"),
                    Device.ip_address.ilike(f"%{search}%"),
                    Device.serial_number.ilike(f"%{search}%")
                )
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        devices = query.order_by(Device.hostname).offset(offset).limit(limit).all()
        
        return {
            "success": True,
            "data": {
                "devices": [
                    {
                        "device_id": d.device_id,
                        "hostname": d.hostname,
                        "ip_address": d.ip_address,
                        "vendor": d.vendor,
                        "model": d.model,
                        "device_type": d.device_type,
                        "location": d.location,
                        "site": d.site,
                        "owner": d.owner,
                        "criticality": d.criticality,
                        "status": d.status,
                        "last_seen": d.last_seen.isoformat() if d.last_seen else None,
                        "tags": d.tags,
                    "metadata": d.device_metadata
                    }
                    for d in devices
                ],
                "total": total,
                "limit": limit,
                "offset": offset
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "LIST_FAILED",
                    "message": "Failed to list devices"
                }
            }
        )


@router.get("/devices/{device_id}")
async def get_device(
    device_id: str,
    current_user: User = Depends(require_permission(Permission.CONFIG_READ)),
    db: Session = Depends(get_db)
):
    """
    Get device details
    
    Requires: CONFIG_READ permission
    """
    try:
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
        
        return {
            "success": True,
            "data": {
                "device_id": device.device_id,
                "hostname": device.hostname,
                "ip_address": device.ip_address,
                "vendor": device.vendor,
                "model": device.model,
                "platform": device.platform,
                "os_version": device.os_version,
                "device_type": device.device_type,
                "location": device.location,
                "site": device.site,
                "owner": device.owner,
                "criticality": device.criticality,
                "status": device.status,
                "management_ip": device.management_ip,
                "serial_number": device.serial_number,
                "current_config_id": device.current_config_id,
                "baseline_config_id": device.baseline_config_id,
                "tags": device.tags,
                "metadata": device.device_metadata,
                "first_seen": device.first_seen.isoformat(),
                "last_seen": device.last_seen.isoformat() if device.last_seen else None,
                "created_at": device.created_at.isoformat(),
                "updated_at": device.updated_at.isoformat()
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
                    "message": "Failed to retrieve device"
                }
            }
        )


@router.patch("/devices/{device_id}")
async def update_device(
    device_id: str,
    updates: DeviceUpdate,
    current_user: User = Depends(require_permission(Permission.CONFIG_UPLOAD)),
    db: Session = Depends(get_db)
):
    """
    Update device details
    
    Requires: CONFIG_UPLOAD permission
    """
    try:
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
        
        # Apply updates
        update_data = updates.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(device, field, value)
        
        device.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(device)
        
        # Log action
        log = SecurityAuditLog(
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            action="DEVICE_UPDATE",
            resource_type="device",
            resource_id=device_id,
            details=f"Updated device {device.hostname}",
            ip_address="",
            user_agent=""
        )
        db.add(log)
        db.commit()
        
        return {
            "success": True,
            "data": {
                "device_id": device.device_id,
                "message": "Device updated successfully"
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
                    "code": "UPDATE_FAILED",
                    "message": f"Failed to update device: {str(e)}"
                }
            }
        )


@router.delete("/devices/{device_id}")
async def delete_device(
    device_id: str,
    current_user: User = Depends(require_permission(Permission.CONFIG_DELETE)),
    db: Session = Depends(get_db)
):
    """
    Delete a device
    
    Requires: CONFIG_DELETE permission
    """
    try:
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
        
        hostname = device.hostname
        
        # Delete device
        db.delete(device)
        db.commit()
        
        # Log action
        log = SecurityAuditLog(
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            action="DEVICE_DELETE",
            resource_type="device",
            resource_id=device_id,
            details=f"Deleted device {hostname}",
            ip_address="",
            user_agent=""
        )
        db.add(log)
        db.commit()
        
        return {
            "success": True,
            "data": {
                "message": f"Device {device_id} deleted successfully"
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
                    "code": "DELETE_FAILED",
                    "message": "Failed to delete device"
                }
            }
        )


# ============================================================
# BULK OPERATIONS
# ============================================================

@router.post("/devices/bulk-import")
async def bulk_import_devices(
    file: UploadFile = File(...),
    current_user: User = Depends(require_permission(Permission.CONFIG_UPLOAD)),
    db: Session = Depends(get_db)
):
    """
    Bulk import devices from CSV file
    
    CSV Format: hostname,ip_address,vendor,model,device_type,location,site,owner,criticality
    
    Requires: CONFIG_UPLOAD permission
    """
    try:
        # Read CSV content
        content = await file.read()
        csv_data = content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_data))
        
        imported = []
        failed = []
        
        for row in csv_reader:
            try:
                # Check for required fields
                if not row.get('hostname'):
                    failed.append({
                        "row": row,
                        "error": "Missing hostname"
                    })
                    continue
                
                # Generate device_id
                device_count = db.query(Device).filter(
                    Device.organization_id == current_user.organization_id
                ).count()
                device_id = f"DEV-{device_count + len(imported) + 1:06d}"
                
                # Check for duplicate
                existing = db.query(Device).filter(
                    Device.organization_id == current_user.organization_id,
                    Device.hostname == row['hostname']
                ).first()
                
                if existing:
                    failed.append({
                        "row": row,
                        "error": f"Duplicate hostname: {row['hostname']}"
                    })
                    continue
                
                # Create device
                device = Device(
                    device_id=device_id,
                    organization_id=current_user.organization_id,
                    hostname=row['hostname'],
                    ip_address=row.get('ip_address'),
                    vendor=row.get('vendor'),
                    model=row.get('model'),
                    device_type=row.get('device_type'),
                    location=row.get('location'),
                    site=row.get('site'),
                    owner=row.get('owner'),
                    criticality=row.get('criticality', 'MEDIUM'),
                    status="ACTIVE"
                )
                
                db.add(device)
                imported.append(row['hostname'])
                
            except Exception as e:
                failed.append({
                    "row": row,
                    "error": str(e)
                })
        
        db.commit()
        
        # Log action
        log = SecurityAuditLog(
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            action="DEVICE_BULK_IMPORT",
            resource_type="device",
            resource_id="",
            details=f"Imported {len(imported)} devices, {len(failed)} failed",
            ip_address="",
            user_agent=""
        )
        db.add(log)
        db.commit()
        
        return {
            "success": True,
            "data": {
                "imported": len(imported),
                "failed": len(failed),
                "imported_devices": imported,
                "failed_devices": failed
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "IMPORT_FAILED",
                    "message": f"Failed to import devices: {str(e)}"
                }
            }
        )


# ============================================================
# DEVICE STATISTICS
# ============================================================

@router.get("/devices/stats/summary")
async def get_device_stats(
    current_user: User = Depends(require_permission(Permission.CONFIG_READ)),
    db: Session = Depends(get_db)
):
    """
    Get device statistics summary
    
    Requires: CONFIG_READ permission
    """
    try:
        # Total devices
        total = db.query(Device).filter(
            Device.organization_id == current_user.organization_id
        ).count()
        
        # By status
        by_status = db.query(
            Device.status,
            func.count(Device.id)
        ).filter(
            Device.organization_id == current_user.organization_id
        ).group_by(Device.status).all()
        
        # By vendor
        by_vendor = db.query(
            Device.vendor,
            func.count(Device.id)
        ).filter(
            Device.organization_id == current_user.organization_id,
            Device.vendor.isnot(None)
        ).group_by(Device.vendor).all()
        
        # By device type
        by_type = db.query(
            Device.device_type,
            func.count(Device.id)
        ).filter(
            Device.organization_id == current_user.organization_id,
            Device.device_type.isnot(None)
        ).group_by(Device.device_type).all()
        
        # By criticality
        by_criticality = db.query(
            Device.criticality,
            func.count(Device.id)
        ).filter(
            Device.organization_id == current_user.organization_id,
            Device.criticality.isnot(None)
        ).group_by(Device.criticality).all()
        
        return {
            "success": True,
            "data": {
                "total_devices": total,
                "by_status": {status: count for status, count in by_status},
                "by_vendor": {vendor: count for vendor, count in by_vendor},
                "by_type": {dtype: count for dtype, count in by_type},
                "by_criticality": {crit: count for crit, count in by_criticality}
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "STATS_FAILED",
                    "message": "Failed to retrieve device statistics"
                }
            }
        )
