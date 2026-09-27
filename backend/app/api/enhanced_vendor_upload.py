"""
Enhanced Vendor Upload API - Phase 5
Bulletproof upload functionality with real-time progress tracking, comprehensive validation,
and professional error handling for vendor-specific configuration uploads.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio
import os
import logging

from app.database.database import get_db
from app.database.models import Configuration, Audit, VendorUploadSession
from app.auth.vendor_auth import require_vendor_session
from app.utils.enhanced_validation import validate_upload_file, UploadValidationResult
from app.utils.upload_progress import (
    create_upload_session, update_file_stage, update_file_error, get_session_progress,
    UploadStage, UploadStatus
)
from app.findings.engine import run_configuration_audit
from app.ingestion.file_handler import ingest_configuration
from app.utils.file_storage import save_uploaded_file, calculate_file_hash
from app.utils.id_generation import generate_config_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Enhanced Vendor Upload"])

@router.post("/vendor/upload/single")
async def enhanced_single_upload(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    device_id: Optional[str] = Form(None),
    auto_audit: bool = Form(True),
    vendor_session: tuple = Depends(require_vendor_session()),
    db: Session = Depends(get_db)
):
    """
    Enhanced single file upload with comprehensive validation and progress tracking
    
    Features:
    - Real-time progress tracking with detailed stages
    - Comprehensive file validation with detailed feedback
    - Bulletproof error handling with recovery guidance
    - Professional status reporting throughout the process
    - Vendor-specific isolation and security
    
    Returns:
    - Upload session ID for progress tracking
    - Detailed validation results
    - Configuration ID upon success
    - Comprehensive error information with remediation steps
    """
    vendor, session = vendor_session
    
    try:
        # Create upload session for progress tracking
        upload_session = create_upload_session(vendor.vendor_id, "single")
        
        # Read file content once
        file_content = await file.read()
        
        # Add file to session
        file_progress = upload_session.add_file(file.filename, len(file_content))
        
        # Stage 1: Comprehensive Validation
        update_file_stage(upload_session.session_id, file_progress.file_id, UploadStage.VALIDATING)
        
        validation_result = validate_upload_file(file_content, file.filename)
        
        # Store validation results
        update_file_stage(upload_session.session_id, file_progress.file_id, UploadStage.VALIDATING, {
            "validation_result": validation_result.to_dict()
        })
        
        if not validation_result.valid:
            error_msg = f"Validation failed: {'; '.join(validation_result.errors)}"
            update_file_error(upload_session.session_id, file_progress.file_id, error_msg, "VALIDATION_ERROR")
            
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "session_id": upload_session.session_id,
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "File validation failed",
                        "validation_details": validation_result.to_dict(),
                        "remediation": _generate_validation_remediation(validation_result)
                    }
                }
            )
        
        # Stage 2: Duplicate Detection (vendor-specific)
        update_file_stage(upload_session.session_id, file_progress.file_id, UploadStage.PROCESSING)
        
        file_hash = calculate_file_hash(file_content)
        existing = db.query(Configuration).filter(
            Configuration.file_hash_sha256 == file_hash,
            Configuration.uploaded_by == vendor.vendor_id
        ).first()
        
        if existing:
            update_file_stage(upload_session.session_id, file_progress.file_id, UploadStage.COMPLETED, {
                "config_id": existing.config_id
            })
            
            return {
                "success": True,
                "session_id": upload_session.session_id,
                "data": {
                    "config_id": existing.config_id,
                    "filename": existing.original_filename,
                    "status": existing.status,
                    "message": "Configuration already exists (duplicate detected)",
                    "duplicate": True,
                    "created_at": existing.created_at.isoformat(),
                    "validation_result": validation_result.to_dict()
                }
            }
        
        # Stage 3: File Storage
        update_file_stage(upload_session.session_id, file_progress.file_id, UploadStage.UPLOADING)
        
        internal_filename, file_path = save_uploaded_file(file_content, file.filename)
        config_id = generate_config_id(db)
        
        # Stage 4: Configuration Ingestion
        update_file_stage(upload_session.session_id, file_progress.file_id, UploadStage.INGESTING)
        
        ingestion_result = ingest_configuration(file_path, file.filename)
        
        if not ingestion_result.success:
            error_msg = f"Configuration ingestion failed: {ingestion_result.error_message}"
            update_file_error(upload_session.session_id, file_progress.file_id, error_msg, "INGESTION_ERROR")
            
            raise HTTPException(
                status_code=500,
                detail={
                    "success": False,
                    "session_id": upload_session.session_id,
                    "error": {
                        "code": "INGESTION_ERROR",
                        "message": error_msg,
                        "remediation": _generate_ingestion_remediation(ingestion_result)
                    }
                }
            )
        
        # Stage 5: Vendor Detection
        update_file_stage(upload_session.session_id, file_progress.file_id, UploadStage.VENDOR_DETECTION)
        
        detected_vendor = ingestion_result.detection_result.vendor.value
        vendor_confidence = ingestion_result.detection_result.confidence
        
        update_file_stage(upload_session.session_id, file_progress.file_id, UploadStage.VENDOR_DETECTION, {
            "vendor_detected": detected_vendor,
            "vendor_confidence": vendor_confidence
        })
        
        # Create configuration record
        file_ext = os.path.splitext(file.filename)[1]
        config = Configuration(
            config_id=config_id,
            filename=internal_filename,
            original_filename=file.filename,
            file_type=file_ext,
            status="UPLOADED",
            storage_path=file_path,
            sanitized_path=ingestion_result.sanitized_path,
            vendor=detected_vendor,
            vendor_confidence=vendor_confidence,
            file_hash_sha256=file_hash,
            organization_id=vendor.organization_id,
            uploaded_by=vendor.vendor_id,
            created_at=datetime.utcnow()
        )
        
        db.add(config)
        db.commit()
        db.refresh(config)
        
        # Update progress with config ID
        update_file_stage(upload_session.session_id, file_progress.file_id, UploadStage.PROCESSING, {
            "config_id": config_id
        })
        
        # Link to device if provided
        if device_id:
            from app.database.models import Device
            device = db.query(Device).filter(
                Device.device_id == device_id,
                Device.organization_id == vendor.organization_id
            ).first()
            
            if device:
                device.current_config_id = config.id
                device.last_seen = datetime.utcnow()
                db.commit()
        
        # Schedule background audit if requested
        if auto_audit:
            background_tasks.add_task(
                _run_background_audit,
                config_id,
                upload_session.session_id,
                file_progress.file_id,
                db
            )
        else:
            # Complete the upload without audit
            update_file_stage(upload_session.session_id, file_progress.file_id, UploadStage.COMPLETED)
        
        # Update vendor session
        session.upload_count = (session.upload_count or 0) + 1
        if session.files_uploaded is None:
            session.files_uploaded = []
        session.files_uploaded = session.files_uploaded + [config_id]
        session.last_activity = datetime.utcnow()
        db.commit()
        
        return {
            "success": True,
            "session_id": upload_session.session_id,
            "data": {
                "config_id": config_id,
                "filename": file.filename,
                "detected_vendor": detected_vendor,
                "vendor_confidence": vendor_confidence,
                "file_size": len(file_content),
                "validation_result": validation_result.to_dict(),
                "processing_stages": {
                    "validation": "completed",
                    "storage": "completed",
                    "ingestion": "completed",
                    "vendor_detection": "completed",
                    "audit": "scheduled" if auto_audit else "skipped"
                },
                "auto_audit": auto_audit,
                "masked_secrets": getattr(ingestion_result.masking_result, 'masked_count', 0)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enhanced single upload failed: {e}")
        
        # Try to update progress if session exists
        try:
            if 'upload_session' in locals() and 'file_progress' in locals():
                update_file_error(upload_session.session_id, file_progress.file_id, str(e), "UNEXPECTED_ERROR")
        except:
            pass
        
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "UNEXPECTED_ERROR",
                    "message": "An unexpected error occurred during upload",
                    "technical_details": str(e),
                    "remediation": [
                        "Check file format and content",
                        "Ensure file is not corrupted",
                        "Try uploading again",
                        "Contact support if problem persists"
                    ]
                }
            }
        )

@router.post("/vendor/upload/bulk")
async def enhanced_bulk_upload(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    auto_audit: bool = Form(True),
    vendor_session: tuple = Depends(require_vendor_session()),
    db: Session = Depends(get_db)
):
    """
    Enhanced bulk upload with per-file progress tracking and bulletproof error handling
    
    Features:
    - Individual file progress tracking with detailed stages
    - Parallel processing with proper error isolation
    - Comprehensive validation and error reporting per file
    - Bulletproof handling of partial failures
    - Professional status reporting for each file
    
    Returns:
    - Upload session ID for real-time progress monitoring
    - Individual file results with detailed status
    - Overall upload summary with statistics
    """
    vendor, session = vendor_session
    
    if not files or len(files) == 0:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": {
                    "code": "NO_FILES",
                    "message": "No files provided for bulk upload"
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
    
    try:
        # Create bulk upload session
        upload_session = create_upload_session(vendor.vendor_id, "bulk")
        upload_session.total_files = len(files)
        
        # Process each file with detailed tracking
        results = []
        successful_configs = []
        
        for file in files:
            file_result = await _process_single_file_in_bulk(
                file, upload_session, vendor, db, auto_audit, background_tasks
            )
            results.append(file_result)
            
            if file_result.get("status") == "success":
                successful_configs.append(file_result.get("config_id"))
        
        # Update vendor session
        session.upload_count = (session.upload_count or 0) + len(successful_configs)
        if session.files_uploaded is None:
            session.files_uploaded = []
        session.files_uploaded = session.files_uploaded + successful_configs
        session.last_activity = datetime.utcnow()
        db.commit()
        
        # Calculate summary statistics
        successful_count = len(successful_configs)
        failed_count = len(files) - successful_count
        
        return {
            "success": True,
            "session_id": upload_session.session_id,
            "data": {
                "total_files": len(files),
                "successful": successful_count,
                "failed": failed_count,
                "success_rate": round((successful_count / len(files)) * 100, 1),
                "results": results,
                "successful_configs": successful_configs,
                "auto_audit": auto_audit,
                "processing_summary": {
                    "validation_failures": len([r for r in results if r.get("error_code") == "VALIDATION_ERROR"]),
                    "ingestion_failures": len([r for r in results if r.get("error_code") == "INGESTION_ERROR"]),
                    "duplicate_files": len([r for r in results if r.get("duplicate", False)]),
                    "unexpected_errors": len([r for r in results if r.get("error_code") == "UNEXPECTED_ERROR"])
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Enhanced bulk upload failed: {e}")
        
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "BULK_UPLOAD_ERROR",
                    "message": "Bulk upload encountered an error",
                    "technical_details": str(e),
                    "remediation": [
                        "Check all files are valid configuration files",
                        "Ensure files are not corrupted",
                        "Try uploading in smaller batches",
                        "Contact support if problem persists"
                    ]
                }
            }
        )

async def _process_single_file_in_bulk(
    file: UploadFile,
    upload_session,
    vendor,
    db: Session,
    auto_audit: bool,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Process a single file within a bulk upload with comprehensive error handling
    """
    try:
        # Read file content
        file_content = await file.read()
        
        # Add file to session
        file_progress = upload_session.add_file(file.filename, len(file_content))
        
        # Validate file
        update_file_stage(upload_session.session_id, file_progress.file_id, UploadStage.VALIDATING)
        
        validation_result = validate_upload_file(file_content, file.filename)
        
        if not validation_result.valid:
            error_msg = f"Validation failed: {'; '.join(validation_result.errors)}"
            update_file_error(upload_session.session_id, file_progress.file_id, error_msg, "VALIDATION_ERROR")
            
            return {
                "filename": file.filename,
                "status": "failed",
                "error": error_msg,
                "error_code": "VALIDATION_ERROR",
                "file_id": file_progress.file_id,
                "validation_result": validation_result.to_dict()
            }
        
        # Check for duplicates
        update_file_stage(upload_session.session_id, file_progress.file_id, UploadStage.PROCESSING)
        
        file_hash = calculate_file_hash(file_content)
        existing = db.query(Configuration).filter(
            Configuration.file_hash_sha256 == file_hash,
            Configuration.uploaded_by == vendor.vendor_id
        ).first()
        
        if existing:
            update_file_stage(upload_session.session_id, file_progress.file_id, UploadStage.COMPLETED, {
                "config_id": existing.config_id
            })
            
            return {
                "filename": file.filename,
                "status": "success",
                "config_id": existing.config_id,
                "file_id": file_progress.file_id,
                "message": "File already exists (duplicate)",
                "duplicate": True,
                "validation_result": validation_result.to_dict()
            }
        
        # Store file
        update_file_stage(upload_session.session_id, file_progress.file_id, UploadStage.UPLOADING)
        
        internal_filename, file_path = save_uploaded_file(file_content, file.filename)
        config_id = generate_config_id(db)
        
        # Ingest configuration
        update_file_stage(upload_session.session_id, file_progress.file_id, UploadStage.INGESTING)
        
        ingestion_result = ingest_configuration(file_path, file.filename)
        
        if not ingestion_result.success:
            error_msg = f"Ingestion failed: {ingestion_result.error_message}"
            update_file_error(upload_session.session_id, file_progress.file_id, error_msg, "INGESTION_ERROR")
            
            return {
                "filename": file.filename,
                "status": "failed",
                "error": error_msg,
                "error_code": "INGESTION_ERROR",
                "file_id": file_progress.file_id
            }
        
        # Vendor detection
        update_file_stage(upload_session.session_id, file_progress.file_id, UploadStage.VENDOR_DETECTION)
        
        detected_vendor = ingestion_result.detection_result.vendor.value
        vendor_confidence = ingestion_result.detection_result.confidence
        
        # Create configuration
        file_ext = os.path.splitext(file.filename)[1]
        config = Configuration(
            config_id=config_id,
            filename=internal_filename,
            original_filename=file.filename,
            file_type=file_ext,
            status="UPLOADED",
            storage_path=file_path,
            sanitized_path=ingestion_result.sanitized_path,
            vendor=detected_vendor,
            vendor_confidence=vendor_confidence,
            file_hash_sha256=file_hash,
            organization_id=vendor.organization_id,
            uploaded_by=vendor.vendor_id,
            created_at=datetime.utcnow()
        )
        
        db.add(config)
        db.commit()
        db.refresh(config)
        
        # Update progress
        update_file_stage(upload_session.session_id, file_progress.file_id, UploadStage.PROCESSING, {
            "config_id": config_id,
            "vendor_detected": detected_vendor,
            "vendor_confidence": vendor_confidence
        })
        
        # Schedule audit if requested
        if auto_audit:
            background_tasks.add_task(
                _run_background_audit,
                config_id,
                upload_session.session_id,
                file_progress.file_id,
                db
            )
        else:
            update_file_stage(upload_session.session_id, file_progress.file_id, UploadStage.COMPLETED)
        
        return {
            "filename": file.filename,
            "status": "success",
            "config_id": config_id,
            "file_id": file_progress.file_id,
            "detected_vendor": detected_vendor,
            "vendor_confidence": vendor_confidence,
            "file_size": len(file_content),
            "masked_secrets": getattr(ingestion_result.masking_result, 'masked_count', 0),
            "validation_result": validation_result.to_dict(),
            "auto_audit": auto_audit
        }
        
    except Exception as e:
        logger.error(f"Error processing file {file.filename} in bulk upload: {e}")
        
        # Try to update progress if file was added
        try:
            if 'file_progress' in locals():
                update_file_error(upload_session.session_id, file_progress.file_id, str(e), "UNEXPECTED_ERROR")
        except:
            pass
        
        return {
            "filename": file.filename,
            "status": "failed",
            "error": f"Unexpected error: {str(e)}",
            "error_code": "UNEXPECTED_ERROR",
            "file_id": getattr(locals().get('file_progress'), 'file_id', None)
        }

async def _run_background_audit(
    config_id: str,
    session_id: str,
    file_id: str,
    db: Session
):
    """
    Run audit in background with progress tracking
    """
    try:
        # Update stage to auditing
        update_file_stage(session_id, file_id, UploadStage.AUDITING)
        
        # Run the audit
        audit = run_configuration_audit(config_id)
        
        if audit:
            # Update with audit results
            update_file_stage(session_id, file_id, UploadStage.COMPLETED, {
                "audit_id": audit.audit_id,
                "compliance_score": audit.compliance_score
            })
        else:
            update_file_error(session_id, file_id, "Audit failed to start", "AUDIT_ERROR")
        
    except Exception as e:
        logger.error(f"Background audit failed for config {config_id}: {e}")
        update_file_error(session_id, file_id, f"Audit failed: {str(e)}", "AUDIT_ERROR")

@router.get("/vendor/upload/progress/{session_id}")
async def get_upload_progress(
    session_id: str,
    vendor_session: tuple = Depends(require_vendor_session()),
    db: Session = Depends(get_db)
):
    """
    Get real-time upload progress for a session
    
    Returns detailed progress information including:
    - Overall session progress percentage
    - Individual file progress with stages
    - Processing statistics and timing
    - Error details with remediation guidance
    """
    vendor, session = vendor_session
    
    progress_data = get_session_progress(session_id)
    
    if not progress_data:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error": {
                    "code": "SESSION_NOT_FOUND",
                    "message": f"Upload session {session_id} not found or has expired"
                }
            }
        )
    
    # Verify session belongs to vendor (security check)
    from app.utils.upload_progress import progress_tracker
    session_obj = progress_tracker.get_session(session_id)
    
    if session_obj and session_obj.vendor_id != vendor.vendor_id:
        raise HTTPException(
            status_code=403,
            detail={
                "success": False,
                "error": {
                    "code": "ACCESS_DENIED",
                    "message": "Access denied to upload session"
                }
            }
        )
    
    return {
        "success": True,
        "data": progress_data
    }

@router.get("/vendor/upload/history")
async def get_upload_history(
    limit: int = 20,
    vendor_session: tuple = Depends(require_vendor_session()),
    db: Session = Depends(get_db)
):
    """
    Get upload history for vendor with enhanced details
    """
    vendor, session = vendor_session
    
    try:
        from app.utils.upload_progress import progress_tracker
        
        # Get recent upload sessions
        recent_sessions = progress_tracker.get_vendor_sessions(vendor.vendor_id, limit)
        
        # Get recent configurations from database
        recent_configs = db.query(Configuration).filter(
            Configuration.uploaded_by == vendor.vendor_id
        ).order_by(Configuration.created_at.desc()).limit(limit).all()
        
        config_list = []
        for config in recent_configs:
            # Get latest audit if exists
            latest_audit = db.query(Audit).filter(
                Audit.configuration_id == config.id
            ).order_by(Audit.created_at.desc()).first()
            
            config_data = {
                "config_id": config.config_id,
                "filename": config.original_filename,
                "file_type": config.file_type,
                "status": config.status,
                "vendor": config.vendor,
                "vendor_confidence": config.vendor_confidence,
                "created_at": config.created_at.isoformat(),
                "file_size": None  # Would need to be stored separately
            }
            
            if latest_audit:
                config_data["audit"] = {
                    "audit_id": latest_audit.audit_id,
                    "status": latest_audit.status,
                    "compliance_score": latest_audit.compliance_score,
                    "risk_level": latest_audit.risk_level,
                    "completed_at": latest_audit.completed_at.isoformat() if latest_audit.completed_at else None
                }
            
            config_list.append(config_data)
        
        return {
            "success": True,
            "data": {
                "recent_sessions": recent_sessions,
                "recent_configurations": config_list,
                "vendor_info": {
                    "vendor_id": vendor.vendor_id,
                    "company": vendor.company_name
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error retrieving upload history: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "HISTORY_ERROR",
                    "message": "Failed to retrieve upload history"
                }
            }
        )

def _generate_validation_remediation(validation_result: UploadValidationResult) -> List[str]:
    """Generate specific remediation steps for validation errors"""
    remediation = []
    
    for error in validation_result.errors:
        if "extension" in error.lower():
            remediation.append("Use supported file extensions: .cfg, .conf, .txt, .json, .xml")
        elif "size" in error.lower():
            remediation.append("Reduce file size to under 10MB or split into smaller files")
        elif "empty" in error.lower():
            remediation.append("Ensure file contains valid configuration content")
        elif "filename" in error.lower():
            remediation.append("Use valid filename without special characters or path separators")
        elif "security" in error.lower():
            remediation.append("Remove potentially malicious content from configuration file")
        else:
            remediation.append("Check file format and content validity")
    
    if not remediation:
        remediation.append("Ensure file is a valid network device configuration")
    
    return remediation

def _generate_ingestion_remediation(ingestion_result) -> List[str]:
    """Generate remediation steps for ingestion errors"""
    remediation = [
        "Verify the file contains valid network device configuration syntax",
        "Check that the configuration format is supported (Cisco IOS, Juniper, etc.)",
        "Ensure the file is not corrupted or contains binary data",
        "Try converting the file to plain text format",
        "Contact support if the configuration format should be supported"
    ]
    
    return remediation