"""
Vendor Upload API Endpoints
Allows approved vendors to upload device configurations after OTP verification
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime
import hashlib

from app.database import (
    get_db, Configuration, Device, VendorUser, 
    VendorUploadSession, SecurityAuditLog
)
from app.auth.vendor_auth import require_vendor_session
from app.parsers import parse_configuration
from app.detection.vendor_detector import detect_vendor
from app.normalization import normalize_parsed_data

router = APIRouter()


def generate_config_id(db: Session) -> str:
    """Generate unique configuration ID"""
    count = db.query(Configuration).count()
    return f"CFG-{count + 1:06d}"


def generate_log_id(db: Session) -> str:
    """Generate unique audit log ID"""
    count = db.query(SecurityAuditLog).count()
    return f"LOG-{count + 1:08d}"


def calculate_file_hash(content: bytes) -> str:
    """Calculate SHA-256 hash of file content"""
    return hashlib.sha256(content).hexdigest()


@router.post("/vendor/upload/configuration")
async def vendor_upload_configuration(
    file: UploadFile = File(...),
    device_id: str = None,
    vendor_session: tuple = Depends(require_vendor_session()),
    db: Session = Depends(get_db)
):
    """
    Upload device configuration as vendor
    
    Requires valid vendor session token in header: X-Vendor-Session-Token
    Files are associated with vendor's organization
    """
    vendor, session = vendor_session
    
    try:
        # Read file content
        content = await file.read()
        content_str = content.decode('utf-8', errors='ignore')
        file_hash = calculate_file_hash(content)
        
        # Check for duplicate
        existing = db.query(Configuration).filter(
            Configuration.file_hash_sha256 == file_hash,
            Configuration.organization_id == vendor.organization_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=409,
                detail={
                    "success": False,
                    "error": {
                        "code": "DUPLICATE_FILE",
                        "message": f"This configuration file already exists: {existing.config_id}"
                    }
                }
            )
        
        # Detect vendor
        detection_result = detect_vendor(content_str)
        detected_vendor = detection_result.get("vendor", "Unknown")
        confidence = detection_result.get("confidence", 0.0)
        
        # Parse configuration
        try:
            parsed_data = parse_configuration(content_str, detected_vendor)
        except Exception as e:
            parsed_data = {"error": str(e), "raw_lines": content_str.split('\n')[:10]}
        
        # Generate config ID
        config_id = generate_config_id(db)
        
        # Create configuration record
        config = Configuration(
            config_id=config_id,
            filename=f"vendor_{vendor.vendor_id}_{file.filename}",
            original_filename=file.filename,
            file_type=file.filename.split('.')[-1] if '.' in file.filename else 'txt',
            status="UPLOADED",
            vendor=detected_vendor,
            vendor_confidence=confidence,
            storage_path=f"/uploads/vendor/{vendor.vendor_id}/{config_id}_{file.filename}",
            sanitized_path=f"/uploads/vendor/{vendor.vendor_id}/sanitized_{config_id}_{file.filename}",
            sanitized_content=content_str,
            file_hash_sha256=file_hash,
            file_size=len(content),
            organization_id=vendor.organization_id,
            created_at=datetime.utcnow()
        )
        
        db.add(config)
        db.commit()
        db.refresh(config)
        
        # If device_id provided, link configuration to device
        if device_id:
            device = db.query(Device).filter(
                Device.device_id == device_id,
                Device.organization_id == vendor.organization_id
            ).first()
            
            if device:
                device.current_config_id = config.id
                device.last_seen = datetime.utcnow()
                db.commit()
        
        # Track upload in session
        if session.files_uploaded is None:
            session.files_uploaded = []
        session.files_uploaded.append(config_id)
        session.upload_count += 1
        session.last_activity = datetime.utcnow()
        db.commit()
        
        # Log action
        log = SecurityAuditLog(
            log_id=generate_log_id(db),
            user_id=None,  # Vendor upload, not internal user
            organization_id=vendor.organization_id,
            event_type="VENDOR_UPLOAD",
            action="UPLOAD_CONFIG",
            result="SUCCESS",
            resource_type="configuration",
            resource_id=config_id,
            details={
                "vendor_id": vendor.vendor_id,
                "vendor_email": vendor.email,
                "company": vendor.company_name,
                "filename": file.filename,
                "detected_vendor": detected_vendor,
                "confidence": confidence,
                "session_id": session.session_id
            },
            ip_address="",
            user_agent=""
        )
        db.add(log)
        db.commit()
        
        return {
            "success": True,
            "data": {
                "config_id": config_id,
                "filename": file.filename,
                "detected_vendor": detected_vendor,
                "confidence": confidence,
                "file_size": len(content),
                "organization_id": vendor.organization_id,
                "uploaded_by": {
                    "vendor_id": vendor.vendor_id,
                    "company": vendor.company_name,
                    "contact": vendor.contact_name
                },
                "session_info": {
                    "session_id": session.session_id,
                    "files_uploaded": session.upload_count,
                    "expires_at": session.expires_at.isoformat()
                },
                "message": "Configuration uploaded successfully"
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
                    "code": "UPLOAD_FAILED",
                    "message": f"Failed to upload configuration: {str(e)}"
                }
            }
        )


@router.post("/vendor/upload/bulk")
async def vendor_bulk_upload(
    files: list[UploadFile] = File(...),
    vendor_session: tuple = Depends(require_vendor_session()),
    db: Session = Depends(get_db)
):
    """
    Bulk upload multiple device configurations as vendor
    
    Requires valid vendor session token in header: X-Vendor-Session-Token
    """
    vendor, session = vendor_session
    
    uploaded = []
    failed = []
    
    for file in files:
        try:
            # Read file content
            content = await file.read()
            content_str = content.decode('utf-8', errors='ignore')
            file_hash = calculate_file_hash(content)
            
            # Check for duplicate
            existing = db.query(Configuration).filter(
                Configuration.file_hash_sha256 == file_hash,
                Configuration.organization_id == vendor.organization_id
            ).first()
            
            if existing:
                failed.append({
                    "filename": file.filename,
                    "error": "Duplicate file",
                    "existing_config_id": existing.config_id
                })
                continue
            
            # Detect vendor
            detection_result = detect_vendor(content_str)
            detected_vendor = detection_result.get("vendor", "Unknown")
            confidence = detection_result.get("confidence", 0.0)
            
            # Generate config ID
            config_id = generate_config_id(db)
            
            # Create configuration record
            config = Configuration(
                config_id=config_id,
                filename=f"vendor_{vendor.vendor_id}_{file.filename}",
                original_filename=file.filename,
                file_type=file.filename.split('.')[-1] if '.' in file.filename else 'txt',
                status="UPLOADED",
                vendor=detected_vendor,
                vendor_confidence=confidence,
                storage_path=f"/uploads/vendor/{vendor.vendor_id}/{config_id}_{file.filename}",
                sanitized_path=f"/uploads/vendor/{vendor.vendor_id}/sanitized_{config_id}_{file.filename}",
                sanitized_content=content_str,
                file_hash_sha256=file_hash,
                file_size=len(content),
                organization_id=vendor.organization_id,
                created_at=datetime.utcnow()
            )
            
            db.add(config)
            db.commit()
            db.refresh(config)
            
            uploaded.append({
                "config_id": config_id,
                "filename": file.filename,
                "detected_vendor": detected_vendor,
                "confidence": confidence
            })
            
            # Track in session
            if session.files_uploaded is None:
                session.files_uploaded = []
            session.files_uploaded.append(config_id)
            session.upload_count += 1
            
        except Exception as e:
            failed.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    # Update session
    session.last_activity = datetime.utcnow()
    db.commit()
    
    # Log bulk upload
    log = SecurityAuditLog(
        log_id=generate_log_id(db),
        user_id=None,
        organization_id=vendor.organization_id,
        event_type="VENDOR_UPLOAD",
        action="BULK_UPLOAD",
        result="SUCCESS" if uploaded else "PARTIAL" if failed else "FAILED",
        resource_type="configuration",
        resource_id="",
        details={
            "vendor_id": vendor.vendor_id,
            "vendor_email": vendor.email,
            "company": vendor.company_name,
            "uploaded_count": len(uploaded),
            "failed_count": len(failed),
            "session_id": session.session_id
        },
        ip_address="",
        user_agent=""
    )
    db.add(log)
    db.commit()
    
    return {
        "success": True,
        "data": {
            "uploaded": uploaded,
            "failed": failed,
            "summary": {
                "total_files": len(files),
                "uploaded_count": len(uploaded),
                "failed_count": len(failed)
            },
            "session_info": {
                "session_id": session.session_id,
                "total_uploads": session.upload_count,
                "expires_at": session.expires_at.isoformat()
            }
        }
    }


@router.get("/vendor/upload/session")
async def get_vendor_session_info(
    vendor_session: tuple = Depends(require_vendor_session()),
    db: Session = Depends(get_db)
):
    """
    Get current vendor upload session information
    
    Requires valid vendor session token
    """
    vendor, session = vendor_session
    
    return {
        "success": True,
        "data": {
            "session_id": session.session_id,
            "vendor": {
                "vendor_id": vendor.vendor_id,
                "company": vendor.company_name,
                "contact": vendor.contact_name,
                "email": vendor.email
            },
            "organization_id": vendor.organization_id,
            "status": session.status,
            "created_at": session.created_at.isoformat(),
            "expires_at": session.expires_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "upload_count": session.upload_count,
            "files_uploaded": session.files_uploaded or []
        }
    }


@router.get("/vendor/upload/history")
async def get_vendor_upload_history(
    vendor_session: tuple = Depends(require_vendor_session()),
    db: Session = Depends(get_db),
    limit: int = 50
):
    """
    Get vendor's upload history
    
    Requires valid vendor session token
    """
    vendor, session = vendor_session
    
    # Get all configurations uploaded by this vendor
    configs = db.query(Configuration).filter(
        Configuration.organization_id == vendor.organization_id,
        Configuration.filename.like(f"vendor_{vendor.vendor_id}_%")
    ).order_by(Configuration.created_at.desc()).limit(limit).all()
    
    history = []
    for config in configs:
        history.append({
            "config_id": config.config_id,
            "filename": config.original_filename,
            "uploaded_at": config.created_at.isoformat(),
            "vendor": config.vendor,
            "status": config.status,
            "file_size": config.file_size
        })
    
    return {
        "success": True,
        "data": {
            "vendor_id": vendor.vendor_id,
            "company": vendor.company_name,
            "uploads": history,
            "total": len(history)
        }
    }


@router.delete("/vendor/upload/session")
async def revoke_vendor_session(
    vendor_session: tuple = Depends(require_vendor_session()),
    db: Session = Depends(get_db)
):
    """
    Revoke current vendor session (logout)
    
    Requires valid vendor session token
    """
    vendor, session = vendor_session
    
    try:
        # Revoke session
        session.status = "REVOKED"
        db.commit()
        
        # Log action
        log = SecurityAuditLog(
            log_id=generate_log_id(db),
            user_id=None,
            organization_id=vendor.organization_id,
            event_type="VENDOR_SESSION",
            action="REVOKE",
            result="SUCCESS",
            resource_type="session",
            resource_id=session.session_id,
            details={
                "vendor_id": vendor.vendor_id,
                "vendor_email": vendor.email,
                "uploads_in_session": session.upload_count
            },
            ip_address="",
            user_agent=""
        )
        db.add(log)
        db.commit()
        
        return {
            "success": True,
            "data": {
                "message": "Vendor session revoked successfully",
                "session_id": session.session_id,
                "uploads_completed": session.upload_count
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "REVOKE_FAILED",
                    "message": f"Failed to revoke session: {str(e)}"
                }
            }
        )
