"""
Configuration file upload API endpoints
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db, Configuration
from app.storage import (
    save_uploaded_file,
    validate_filename,
    validate_file_size,
    generate_config_id
)

router = APIRouter()


@router.post("/config/upload")
async def upload_configuration(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a network configuration file
    
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
        
        # Create database record with vendor information
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
            created_at=datetime.utcnow()
        )
        
        db.add(config)
        db.commit()
        db.refresh(config)
        
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
                "created_at": config.created_at.isoformat(),
                "message": "Configuration uploaded and processed successfully"
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
    db: Session = Depends(get_db)
):
    """
    List all uploaded configurations
    """
    try:
        configs = db.query(Configuration)\
            .order_by(Configuration.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
        
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
                "total": db.query(Configuration).count()
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
    db: Session = Depends(get_db)
):
    """
    Get configuration details by config_id (e.g., CFG-000001)
    """
    try:
        config = db.query(Configuration)\
            .filter(Configuration.config_id == config_id)\
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
