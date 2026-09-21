"""
Bulk upload API endpoints - Phase 0 Critical Feature
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import asyncio

from app.database import get_db, Configuration, User
from app.storage import (
    save_uploaded_file,
    validate_filename,
    validate_file_size,
    generate_config_id
)
from app.storage.storage_backend import calculate_file_hash
from app.ingestion import ingest_configuration
from app.auth.dependencies import require_permission
from app.auth.permissions import Permission

router = APIRouter()


@router.post("/configurations/bulk-upload")
async def bulk_upload_configurations(
    files: List[UploadFile] = File(...),
    auto_audit: bool = False,
    current_user: User = Depends(require_permission(Permission.CONFIG_UPLOAD)),
    db: Session = Depends(get_db)
):
    """
    Bulk upload multiple configuration files
    
    Supports:
    - Multiple file upload in single request
    - Partial failure handling
    - Optional auto-audit on each upload
    - Progress tracking
    
    Returns job summary with success/failure details
    
    SECURITY: Requires CONFIG_UPLOAD permission and assigns organization ownership
    """
    if not files or len(files) == 0:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": {
                    "code": "NO_FILES",
                    "message": "No files provided for upload"
                }
            }
        )
    
    if len(files) > 50:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": {
                    "code": "TOO_MANY_FILES",
                    "message": "Maximum 50 files per bulk upload"
                }
            }
        )
    
    results = []
    successful = 0
    failed = 0
    
    for file in files:
        try:
            # Validate filename
            if not validate_filename(file.filename):
                results.append({
                    "filename": file.filename,
                    "status": "failed",
                    "error": "Invalid filename or unsupported file type"
                })
                failed += 1
                continue
            
            # Read file content
            file_content = await file.read()
            
            # Validate file size
            if not validate_file_size(len(file_content)):
                results.append({
                    "filename": file.filename,
                    "status": "failed",
                    "error": "File size exceeds maximum (10MB)"
                })
                failed += 1
                continue
            
            # Check if empty
            if len(file_content) == 0:
                results.append({
                    "filename": file.filename,
                    "status": "failed",
                    "error": "Empty file"
                })
                failed += 1
                continue
            
            # Save file
            internal_filename, file_path = save_uploaded_file(file_content, file.filename)
            
            # Calculate hash
            file_hash = calculate_file_hash(file_content)
            
            # Generate config ID
            config_id = generate_config_id()
            
            # Get file extension
            import os
            file_ext = os.path.splitext(file.filename)[1]
            
            # Process configuration
            ingestion_result = ingest_configuration(file_path, file.filename)
            
            if not ingestion_result.success:
                results.append({
                    "filename": file.filename,
                    "status": "failed",
                    "error": f"Ingestion failed: {ingestion_result.error_message}"
                })
                failed += 1
                continue
            
            # Create database record WITH organization ownership
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
                organization_id=current_user.organization_id,  # SECURITY FIX: Assign organization
                created_at=datetime.utcnow()
            )
            
            db.add(config)
            db.commit()
            db.refresh(config)
            
            result_data = {
                "filename": file.filename,
                "status": "success",
                "config_id": config.config_id,
                "vendor": config.vendor,
                "vendor_confidence": config.vendor_confidence,
                "masked_secrets": ingestion_result.masking_result.masked_count
            }
            
            # Auto-audit if requested
            if auto_audit:
                try:
                    from app.findings import run_configuration_audit
                    audit = run_configuration_audit(config.config_id)
                    result_data["audit_id"] = audit.audit_id
                    result_data["compliance_score"] = audit.compliance_score
                except Exception as audit_error:
                    result_data["audit_error"] = str(audit_error)
            
            results.append(result_data)
            successful += 1
            
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "failed",
                "error": f"Unexpected error: {str(e)}"
            })
            failed += 1
    
    return {
        "success": True,
        "data": {
            "total_files": len(files),
            "successful": successful,
            "failed": failed,
            "results": results
        }
    }


@router.post("/configurations/bulk-audit")
async def bulk_audit_configurations(
    config_ids: List[str],
    current_user: User = Depends(require_permission(Permission.AUDIT_RUN)),
    db: Session = Depends(get_db)
):
    """
    Run audits on multiple configurations
    
    Useful for batch processing after bulk upload
    
    SECURITY: Requires AUDIT_RUN permission and verifies organization ownership
    """
    if not config_ids or len(config_ids) == 0:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": {
                    "code": "NO_CONFIGS",
                    "message": "No configuration IDs provided"
                }
            }
        )
    
    results = []
    from app.findings import run_configuration_audit
    
    for config_id in config_ids:
        try:
            # Check if config exists AND belongs to user's organization
            config = db.query(Configuration).filter(
                Configuration.config_id == config_id,
                Configuration.organization_id == current_user.organization_id
            ).first()
            
            if not config:
                results.append({
                    "config_id": config_id,
                    "status": "failed",
                    "error": "Configuration not found or access denied"
                })
                continue
            
            # Run audit
            audit = run_configuration_audit(config_id)
            
            results.append({
                "config_id": config_id,
                "status": "success",
                "audit_id": audit.audit_id,
                "compliance_score": audit.compliance_score,
                "risk_level": audit.risk_level,
                "failed_count": audit.failed_count
            })
            
        except Exception as e:
            results.append({
                "config_id": config_id,
                "status": "failed",
                "error": str(e)
            })
    
    successful = sum(1 for r in results if r["status"] == "success")
    failed = sum(1 for r in results if r["status"] == "failed")
    
    return {
        "success": True,
        "data": {
            "total": len(config_ids),
            "successful": successful,
            "failed": failed,
            "results": results
        }
    }
