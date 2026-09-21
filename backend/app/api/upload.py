"""
Configuration file upload API endpoints
Phase 4: Protected with authentication
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db, Configuration, User
from app.storage import (
    save_uploaded_file,
    validate_filename,
    validate_file_size,
    generate_config_id
)
from app.auth.dependencies import get_current_active_user, get_optional_user, require_permission
from app.auth.permissions import Permission

router = APIRouter()


@router.post("/config/upload")
async def upload_configuration(
    file: UploadFile = File(...),
    current_user: User = Depends(require_permission(Permission.CONFIG_UPLOAD)),
    db: Session = Depends(get_db)
):
    """
    Upload a network configuration file
    
    **Requires:** CONFIG_UPLOAD permission
    
    Accepts: .cfg, .conf, .txt, .json files
    Returns: Configuration metadata with unique ID
    """
    try:
        # Validate filename
        if not validate_filename(file.filename):
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": {
                        "code": "INVALID_FILENAME",
                        "message": "Invalid filename or unsupported file type. Supported: .cfg, .conf, .txt, .json"
                    }
                }
            )
        
        # Read file content
        file_content = await file.read()
        
        # Validate file size
        if not validate_file_size(len(file_content)):
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": {
                        "code": "FILE_TOO_LARGE",
                        "message": "File size exceeds maximum allowed size (10MB)"
                    }
                }
            )
        
        # Check if file is empty
        if len(file_content) == 0:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": {
                        "code": "EMPTY_FILE",
                        "message": "Uploaded file is empty"
                    }
                }
            )
        
        # Save uploaded file
        internal_filename, file_path = save_uploaded_file(file_content, file.filename)
        
        # Calculate SHA-256 hash for integrity and deduplication
        from app.storage.storage_backend import calculate_file_hash
        file_hash = calculate_file_hash(file_content)
        
        # Check for duplicate (same hash)
        existing = db.query(Configuration).filter(
            Configuration.file_hash_sha256 == file_hash,
            Configuration.organization_id == current_user.organization_id
        ).first()
        
        if existing:
            return {
                "success": True,
                "data": {
                    "id": existing.id,
                    "config_id": existing.config_id,
                    "filename": existing.original_filename,
                    "file_type": existing.file_type,
                    "status": existing.status,
                    "vendor": existing.vendor,
                    "vendor_confidence": existing.vendor_confidence,
                    "file_hash_sha256": existing.file_hash_sha256,
                    "created_at": existing.created_at.isoformat(),
                    "message": "Configuration already exists (duplicate detected)",
                    "duplicate": True
                }
            }
        
        # Generate configuration ID
        config_id = generate_config_id()
        
        # Get file extension
        import os
        file_ext = os.path.splitext(file.filename)[1]
        
        # Process configuration: mask secrets and detect vendor
        from app.ingestion import ingest_configuration
        ingestion_result = ingest_configuration(file_path, file.filename)
        
        if not ingestion_result.success:
            raise HTTPException(
                status_code=500,
                detail={
                    "success": False,
                    "error": {
                        "code": "INGESTION_FAILED",
                        "message": f"Failed to process configuration: {ingestion_result.error_message}"
                    }
                }
            )
        
        # Create database record with vendor information and organization
        config = Configuration(
            config_id=config_id,
            filename=internal_filename,
            original_filename=file.filename,
            file_type=file_ext,
            status="UPLOADED",
            storage_path=file_path,
            sanitized_path=ingestion_result.sanitized_path,
            vendor=ingestion_result.detection_result.vendor.value,
            vendor_confidence=ingestion_result.detection_result.confidence,
            file_hash_sha256=file_hash,
            organization_id=current_user.organization_id,  # Phase 4: Multi-tenancy
            created_at=datetime.utcnow()
        )
        
        db.add(config)
        db.commit()
        db.refresh(config)
        
        # Log the upload event
        from app.api.auth import log_security_event
        log_security_event(
            db, "UPLOAD", current_user.id, current_user.organization_id,
            "CREATE", "SUCCESS",
            {"config_id": config.config_id, "filename": file.filename, "vendor": config.vendor}
        )
        
        return {
            "success": True,
            "data": {
                "id": config.id,
                "config_id": config.config_id,
                "filename": config.original_filename,
                "file_type": config.file_type,
                "status": config.status,
                "vendor": config.vendor,
                "vendor_confidence": config.vendor_confidence,
                "masked_secrets": ingestion_result.masking_result.masked_count,
                "file_hash_sha256": config.file_hash_sha256,
                "created_at": config.created_at.isoformat(),
                "message": "Configuration uploaded and processed successfully",
                "duplicate": False
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Upload error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "UPLOAD_FAILED",
                    "message": "Failed to upload configuration file"
                }
            }
        )


@router.get("/configurations")
async def list_configurations(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_permission(Permission.CONFIG_READ)),
    db: Session = Depends(get_db)
):
    """
    List all uploaded configurations for current user's organization
    
    **Requires:** CONFIG_READ permission
    """
    try:
        # Filter by organization
        configs = db.query(Configuration)\
            .filter(Configuration.organization_id == current_user.organization_id)\
            .order_by(Configuration.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
        
        total = db.query(Configuration)\
            .filter(Configuration.organization_id == current_user.organization_id)\
            .count()
        
        return {
            "success": True,
            "data": {
                "configurations": [ 
                    {
                        "id": c.id,
                        "config_id": c.config_id,
                        "filename": c.original_filename,
                        "file_type": c.file_type,
                        "status": c.status,
                        "vendor": c.vendor,
                        "vendor_confidence": c.vendor_confidence,
                        "created_at": c.created_at.isoformat()
                    }
                    for c in configs
                ],
                "total": total,
                "skip": skip,
                "limit": limit
            }
        }
    except Exception as e:
        print(f"List configurations error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "LIST_FAILED",
                    "message": "Failed to retrieve configurations"
                }
            }
        )


@router.get("/configurations/{config_id}")
async def get_configuration(
    config_id: str,
    current_user: User = Depends(require_permission(Permission.CONFIG_READ)),
    db: Session = Depends(get_db)
):
    """
    Get configuration details by config_id (e.g., CFG-000001)
    
    **Requires:** CONFIG_READ permission
    """
    try:
        config = db.query(Configuration)\
            .filter(
                Configuration.config_id == config_id,
                Configuration.organization_id == current_user.organization_id
            )\
            .first()
        
        if not config:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Configuration {config_id} not found"
                    }
                }
            )
        
        return {
            "success": True,
            "data": {
                "id": config.id,
                "config_id": config.config_id,
                "filename": config.original_filename,
                "file_type": config.file_type,
                "status": config.status,
                "vendor": config.vendor,
                "vendor_confidence": config.vendor_confidence,
                "storage_path": config.storage_path,
                "sanitized_path": config.sanitized_path,
                "file_hash_sha256": config.file_hash_sha256,
                "created_at": config.created_at.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get configuration error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "GET_FAILED",
                    "message": "Failed to retrieve configuration"
                }
            }
        )


@router.delete("/configurations/{config_id}")
async def delete_configuration(
    config_id: str,
    current_user: User = Depends(require_permission(Permission.CONFIG_DELETE)),
    db: Session = Depends(get_db)
):
    """
    Delete a configuration
    
    **Requires:** CONFIG_DELETE permission
    """
    try:
        config = db.query(Configuration)\
            .filter(
                Configuration.config_id == config_id,
                Configuration.organization_id == current_user.organization_id
            )\
            .first()
        
        if not config:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Configuration {config_id} not found"
                    }
                }
            )
        
        # Log deletion
        from app.api.auth import log_security_event
        log_security_event(
            db, "DELETE", current_user.id, current_user.organization_id,
            "DELETE", "SUCCESS",
            {"config_id": config.config_id, "filename": config.original_filename}
        )
        
        db.delete(config)
        db.commit()
        
        return {
            "success": True,
            "message": f"Configuration {config_id} deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete configuration error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "DELETE_FAILED",
                    "message": "Failed to delete configuration"
                }
            }
        )
