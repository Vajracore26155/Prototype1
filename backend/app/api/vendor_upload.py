"""
Vendor Upload API Endpoints
Allows approved vendors to upload device configurations after OTP verification
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime
import hashlib
import os

from app.database import (
    get_db, Configuration, Device, VendorUser, 
    VendorUploadSession, SecurityAuditLog
)
from app.auth.vendor_auth import require_vendor_session
from app.parsers import parse_configuration
from app.detection.vendor_detector import detect_vendor
from app.normalization import normalize_parsed_data
from app.ingestion import ingest_configuration
from app.findings import run_configuration_audit
from app.storage import save_uploaded_file, validate_filename, validate_file_size

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
    auto_audit: bool = True,  # Default to true for complete workflow
    vendor_session: tuple = Depends(require_vendor_session()),
    db: Session = Depends(get_db)
):
    """
    Upload device configuration as vendor with COMPLETE processing pipeline
    
    Requires valid vendor session token in header: X-Vendor-Session-Token
    Files are associated with vendor's organization
    
    COMPLETE WORKFLOW:
    1. Upload & validate file
    2. Ingestion (masking/sanitization) 
    3. Vendor detection
    4. Database storage
    5. Automatic audit execution (if auto_audit=True)
    6. Compliance scoring & findings generation
    """
    vendor, session = vendor_session
    
    try:
        # Validate filename (like admin system)
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
        content = await file.read()
        
        # Validate file size (like admin system)
        if not validate_file_size(len(content)):
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
        if len(content) == 0:
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
        
        content_str = content.decode('utf-8', errors='ignore')
        file_hash = calculate_file_hash(content)
        
        # Check for duplicate (vendor-specific)
        existing = db.query(Configuration).filter(
            Configuration.file_hash_sha256 == file_hash,
            Configuration.uploaded_by == vendor.vendor_id
        ).first()
        
        if existing:
            return {
                "success": True,
                "data": {
                    "config_id": existing.config_id,
                    "filename": existing.original_filename,
                    "status": existing.status,
                    "vendor": existing.vendor,
                    "vendor_confidence": existing.vendor_confidence,
                    "file_hash_sha256": existing.file_hash_sha256,
                    "created_at": existing.created_at.isoformat(),
                    "message": "Configuration already exists (duplicate detected)",
                    "duplicate": True,
                    "uploaded_by": {
                        "vendor_id": vendor.vendor_id,
                        "company": vendor.company_name
                    }
                }
            }
        
        # Save uploaded file (like admin system)
        internal_filename, file_path = save_uploaded_file(content, file.filename)
        
        # Generate config ID
        config_id = generate_config_id(db)
        
        # Get file extension
        import os
        file_ext = os.path.splitext(file.filename)[1]
        
        # FULL INGESTION PIPELINE (like admin system)
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
        
        # Create configuration record with FULL admin-like processing
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
            organization_id=vendor.organization_id,
            uploaded_by=vendor.vendor_id,  # CRITICAL: Set vendor-specific ownership
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
        
        # Create a new list to ensure SQLAlchemy detects the change
        current_uploads = session.files_uploaded.copy() if session.files_uploaded else []
        current_uploads.append(config_id)
        session.files_uploaded = current_uploads
        session.upload_count += 1
        session.last_activity = datetime.utcnow()
        
        # Mark the field as modified to ensure SQLAlchemy updates it
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(session, 'files_uploaded')
        
        db.commit()
        
        # Prepare basic response data
        response_data = {
            "config_id": config_id,
            "filename": file.filename,
            "detected_vendor": config.vendor,
            "confidence": config.vendor_confidence,
            "masked_secrets": ingestion_result.masking_result.masked_count,
            "file_size": len(content),
            "file_hash_sha256": config.file_hash_sha256,
            "status": config.status,
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
            "message": "Configuration uploaded and processed successfully",
            "duplicate": False
        }
        
        # AUTOMATIC AUDIT EXECUTION (like admin auto_audit option)
        audit_data = None
        if auto_audit:
            try:
                print(f"[VENDOR AUDIT] Starting automatic audit for {config_id}")
                audit = run_configuration_audit(config_id)
                audit_data = {
                    "audit_id": audit.audit_id,
                    "status": audit.status,
                    "compliance_score": audit.compliance_score,
                    "risk_score": audit.risk_score,
                    "risk_level": audit.risk_level,
                    "passed_count": audit.passed_count,
                    "failed_count": audit.failed_count,
                    "warning_count": audit.warning_count,
                    "started_at": audit.started_at.isoformat(),
                    "completed_at": audit.completed_at.isoformat() if audit.completed_at else None,
                    "requires_human_review": audit.requires_human_review,
                    "message": "Audit completed automatically after upload"
                }
                response_data["audit"] = audit_data
                response_data["message"] = "Configuration uploaded, processed, and audited successfully"
                print(f"[VENDOR AUDIT] Completed for {config_id}: {audit.compliance_score}% compliance")
            except Exception as audit_error:
                print(f"[VENDOR AUDIT ERROR] {config_id}: {audit_error}")
                response_data["audit_error"] = str(audit_error)
                response_data["message"] = "Configuration uploaded and processed, but audit failed"
        
        # Log action with audit details
        log_details = {
            "vendor_id": vendor.vendor_id,
            "vendor_email": vendor.email,
            "company": vendor.company_name,
            "filename": file.filename,
            "detected_vendor": config.vendor,
            "confidence": config.vendor_confidence,
            "session_id": session.session_id,
            "masked_secrets": ingestion_result.masking_result.masked_count,
            "auto_audit": auto_audit
        }
        
        if audit_data:
            log_details.update({
                "audit_id": audit_data["audit_id"],
                "compliance_score": audit_data["compliance_score"],
                "risk_level": audit_data["risk_level"]
            })
        
        log = SecurityAuditLog(
            log_id=generate_log_id(db),
            user_id=None,  # Vendor upload, not internal user
            organization_id=vendor.organization_id,
            event_type="VENDOR_UPLOAD",
            action="UPLOAD_CONFIG_WITH_PROCESSING",
            result="SUCCESS",
            resource_type="configuration",
            resource_id=config_id,
            details=log_details,
            ip_address="",
            user_agent=""
        )
        db.add(log)
        db.commit()
        
        return {
            "success": True,
            "data": response_data
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
    auto_audit: bool = True,  # Default to true for complete workflow
    vendor_session: tuple = Depends(require_vendor_session()),
    db: Session = Depends(get_db)
):
    """
    Bulk upload multiple device configurations as vendor with COMPLETE processing pipeline
    
    Requires valid vendor session token in header: X-Vendor-Session-Token
    
    COMPLETE WORKFLOW for each file:
    1. Upload & validate file
    2. Ingestion (masking/sanitization)
    3. Vendor detection 
    4. Database storage
    5. Automatic audit execution (if auto_audit=True)
    6. Compliance scoring & findings generation
    """
    vendor, session = vendor_session
    
    uploaded = []
    failed = []
    
    for file in files:
        try:
            # Validate filename (like admin system)
            if not validate_filename(file.filename):
                failed.append({
                    "filename": file.filename,
                    "error": "Invalid filename or unsupported file type"
                })
                continue
            
            # Read file content
            content = await file.read()
            
            # Validate file size (like admin system) 
            if not validate_file_size(len(content)):
                failed.append({
                    "filename": file.filename,
                    "error": "File size exceeds maximum (10MB)"
                })
                continue
                
            # Check if empty
            if len(content) == 0:
                failed.append({
                    "filename": file.filename,
                    "error": "Empty file"
                })
                continue
            
            content_str = content.decode('utf-8', errors='ignore')
            file_hash = calculate_file_hash(content)
            
            # Check for duplicate (vendor-specific)
            existing = db.query(Configuration).filter(
                Configuration.file_hash_sha256 == file_hash,
                Configuration.uploaded_by == vendor.vendor_id
            ).first()
            
            if existing:
                failed.append({
                    "filename": file.filename,
                    "error": "Duplicate file",
                    "existing_config_id": existing.config_id
                })
                continue
            
            # Save uploaded file (like admin system)
            internal_filename, file_path = save_uploaded_file(content, file.filename)
            
            # Generate config ID
            config_id = generate_config_id(db)
            
            # Get file extension
            import os
            file_ext = os.path.splitext(file.filename)[1]
            
            # FULL INGESTION PIPELINE (like admin system)
            ingestion_result = ingest_configuration(file_path, file.filename)
            
            if not ingestion_result.success:
                failed.append({
                    "filename": file.filename,
                    "error": f"Ingestion failed: {ingestion_result.error_message}"
                })
                continue
            
            # Create configuration record with FULL admin-like processing
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
                organization_id=vendor.organization_id,
                uploaded_by=vendor.vendor_id,  # Vendor-specific ownership
                created_at=datetime.utcnow()
            )
            
            db.add(config)
            db.commit()
            db.refresh(config)
            
            result_data = {
                "config_id": config_id,
                "filename": file.filename,
                "detected_vendor": config.vendor,
                "confidence": config.vendor_confidence,
                "masked_secrets": ingestion_result.masking_result.masked_count
            }
            
            # AUTOMATIC AUDIT EXECUTION (like admin auto_audit option)
            if auto_audit:
                try:
                    print(f"[VENDOR BULK AUDIT] Starting audit for {config_id}")
                    audit = run_configuration_audit(config_id)
                    result_data["audit_id"] = audit.audit_id
                    result_data["compliance_score"] = audit.compliance_score
                    result_data["risk_level"] = audit.risk_level
                    result_data["audit_status"] = "completed"
                    print(f"[VENDOR BULK AUDIT] Completed for {config_id}: {audit.compliance_score}% compliance")
                except Exception as audit_error:
                    print(f"[VENDOR BULK AUDIT ERROR] {config_id}: {audit_error}")
                    result_data["audit_error"] = str(audit_error)
                    result_data["audit_status"] = "failed"
            
            uploaded.append(result_data)
            
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
    
    # Log bulk upload with processing details
    log_details = {
        "vendor_id": vendor.vendor_id,
        "vendor_email": vendor.email,
        "company": vendor.company_name,
        "uploaded_count": len(uploaded),
        "failed_count": len(failed),
        "session_id": session.session_id,
        "auto_audit": auto_audit
    }
    
    if auto_audit and uploaded:
        successful_audits = sum(1 for u in uploaded if "audit_id" in u)
        log_details["successful_audits"] = successful_audits
        log_details["audit_failures"] = len(uploaded) - successful_audits
    
    log = SecurityAuditLog(
        log_id=generate_log_id(db),
        user_id=None,
        organization_id=vendor.organization_id,
        event_type="VENDOR_UPLOAD",
        action="BULK_UPLOAD_WITH_PROCESSING",
        result="SUCCESS" if uploaded else "PARTIAL" if failed else "FAILED",
        resource_type="configuration",
        resource_id="",
        details=log_details,
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
    Get this specific vendor's upload history only
    
    Requires valid vendor session token
    """
    vendor, session = vendor_session
    
    # Get configurations uploaded ONLY by this specific vendor
    configs = db.query(Configuration).filter(
        Configuration.uploaded_by == vendor.vendor_id  # Direct vendor-specific filtering
    ).order_by(Configuration.created_at.desc()).limit(limit).all()
    
    history = []
    for config in configs:
        history.append({
            "config_id": config.config_id,
            "filename": config.original_filename,
            "uploaded_at": config.created_at.isoformat(),
            "vendor": config.vendor,
            "status": config.status,
            "file_size": getattr(config, 'file_size', 0),
            "uploaded_by": config.uploaded_by  # Verification field
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


@router.post("/vendor/audit/{config_id}")
async def vendor_run_audit(
    config_id: str,
    vendor_session: tuple = Depends(require_vendor_session()),
    db: Session = Depends(get_db)
):
    """
    Run security audit on a vendor's uploaded configuration
    
    Executes same audit pipeline as admin system:
    1. Parse configuration
    2. Normalize to Unified Security Model  
    3. Evaluate compliance rules
    4. Calculate risk
    5. Generate findings with evidence
    6. Create remediation commands
    """
    vendor, session = vendor_session
    
    try:
        # Check if configuration exists and belongs to vendor's organization
        config = db.query(Configuration).filter(
            Configuration.config_id == config_id,
            Configuration.organization_id == vendor.organization_id
        ).first()
        
        if not config:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Configuration {config_id} not found or access denied"
                    }
                }
            )
        
        # Run audit using same system as admin
        audit = run_configuration_audit(config_id)
        
        # Log security event
        log = SecurityAuditLog(
            log_id=generate_log_id(db),
            user_id=None,  # Vendor action
            organization_id=vendor.organization_id,
            event_type="VENDOR_AUDIT",
            action="EXECUTE",
            result="SUCCESS",
            resource_type="audit", 
            resource_id=audit.audit_id,
            details={
                "config_id": config_id,
                "audit_id": audit.audit_id,
                "vendor_id": vendor.vendor_id,
                "vendor_email": vendor.email,
                "company": vendor.company_name
            },
            ip_address="",
            user_agent=""
        )
        db.add(log)
        db.commit()
        
        return {
            "success": True,
            "data": {
                "audit_id": audit.audit_id,
                "configuration_id": config.config_id,
                "status": audit.status,
                "compliance_score": audit.compliance_score,
                "risk_score": audit.risk_score,
                "risk_level": audit.risk_level,
                "passed_count": audit.passed_count,
                "failed_count": audit.failed_count,
                "warning_count": audit.warning_count,
                "started_at": audit.started_at.isoformat(),
                "completed_at": audit.completed_at.isoformat() if audit.completed_at else None,
                "requires_human_review": audit.requires_human_review,
                "message": "Audit completed successfully",
                "vendor_info": {
                    "vendor_id": vendor.vendor_id,
                    "company": vendor.company_name
                }
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
                    "code": "AUDIT_FAILED",
                    "message": f"Failed to run audit: {str(e)}"
                }
            }
        )


@router.get("/vendor/configuration/{config_id}")
async def vendor_get_configuration_details(
    config_id: str,
    vendor_session: tuple = Depends(require_vendor_session()),
    db: Session = Depends(get_db)
):
    """
    Get detailed configuration information for vendor
    
    Returns comprehensive configuration details including:
    - File metadata and technical specifications
    - File content preview (sanitized)
    - Upload session information
    - Associated audit information
    - Processing statistics
    """
    vendor, session = vendor_session
    
    try:
        # Get configuration with vendor-specific access control
        config = db.query(Configuration).filter(
            Configuration.config_id == config_id,
            Configuration.uploaded_by == vendor.vendor_id  # Vendor-specific access
        ).first()
        
        if not config:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Configuration {config_id} not found or access denied"
                    }
                }
            )
        
        # Get associated audits
        audits = db.query(Audit).filter(Audit.configuration_id == config.id).all()
        
        # Get file content preview (sanitized)
        file_preview = None
        file_stats = {}
        
        try:
            if config.sanitized_path and os.path.exists(config.sanitized_path):
                with open(config.sanitized_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()[:50]  # First 50 lines for preview
                    file_preview = ''.join(lines)
                    file_stats = {
                        "total_lines": len(f.readlines()) + len(lines),
                        "preview_lines": len(lines),
                        "file_size_bytes": os.path.getsize(config.sanitized_path)
                    }
        except Exception as e:
            file_preview = "File content not available"
            print(f"Error reading file preview: {e}")
        
        # Format audit information
        audit_info = []
        for audit in audits:
            audit_data = {
                "audit_id": audit.audit_id,
                "status": audit.status,
                "compliance_score": audit.compliance_score,
                "risk_score": audit.risk_score,
                "risk_level": audit.risk_level,
                "started_at": audit.started_at.isoformat(),
                "completed_at": audit.completed_at.isoformat() if audit.completed_at else None,
                "requires_human_review": audit.requires_human_review,
                "interpretation_confidence": audit.interpretation_confidence,
                "parsing_stats": {
                    "total_lines": audit.total_lines_count,
                    "uninterpreted_lines": audit.uninterpreted_lines_count,
                    "interpretation_rate": (
                        ((audit.total_lines_count - audit.uninterpreted_lines_count) / audit.total_lines_count * 100) 
                        if audit.total_lines_count > 0 else 0
                    ),
                    "pending_mappings": audit.pending_mappings_count
                },
                "review_reason": audit.review_reason,
                "findings_count": {
                    "total": audit.passed_count + audit.failed_count + audit.warning_count,
                    "passed": audit.passed_count,
                    "failed": audit.failed_count,
                    "warnings": audit.warning_count
                }
            }
            audit_info.append(audit_data)
        
        return {
            "success": True,
            "data": {
                "config_id": config.config_id,
                "filename": config.original_filename,
                "internal_filename": config.filename,
                "file_type": config.file_type,
                "status": config.status,
                "vendor_detection": {
                    "detected_vendor": config.vendor,
                    "confidence": config.vendor_confidence
                },
                "file_integrity": {
                    "sha256_hash": config.file_hash_sha256,
                    "storage_path": os.path.basename(config.storage_path) if config.storage_path else None,
                    "sanitized_path": os.path.basename(config.sanitized_path) if config.sanitized_path else None
                },
                "file_content": {
                    "preview": file_preview,
                    "stats": file_stats
                },
                "upload_metadata": {
                    "uploaded_by": config.uploaded_by,
                    "uploaded_at": config.created_at.isoformat(),
                    "organization_id": config.organization_id
                },
                "audits": audit_info,
                "processing_status": {
                    "ingested": bool(config.sanitized_path),
                    "vendor_detected": bool(config.vendor and config.vendor != "Unknown"),
                    "audited": len(audit_info) > 0,
                    "latest_audit": audit_info[0] if audit_info else None
                }
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
                    "message": "Failed to retrieve configuration details"
                }
            }
        )


@router.get("/vendor/audit/{audit_id}")
async def vendor_get_audit_details(
    audit_id: str,
    vendor_session: tuple = Depends(require_vendor_session()),
    db: Session = Depends(get_db)
):
    """
    Get audit details for vendor
    """
    vendor, session = vendor_session
    
    try:
        from app.database import Audit, Finding
        
        # Get audit with vendor-specific check
        audit = db.query(Audit).join(
            Configuration, Audit.configuration_id == Configuration.id
        ).filter(
            Audit.audit_id == audit_id,
            Configuration.uploaded_by == vendor.vendor_id  # Vendor-specific access control
        ).first()
        
        if not audit:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Audit {audit_id} not found or access denied"
                    }
                }
            )
        
        # Get configuration
        config = db.query(Configuration).filter(
            Configuration.id == audit.configuration_id
        ).first()
        
        # Get findings
        findings = db.query(Finding).filter(Finding.audit_id == audit.id).all()
        
        # Format findings for response
        formatted_findings = []
        for finding in findings:
            formatted_findings.append({
                "finding_id": finding.finding_id,
                "rule_id": finding.rule_id,
                "rule_name": finding.title,
                "description": finding.description,
                "severity": finding.severity,
                "status": finding.status,
                "expected": finding.expected,
                "actual": finding.actual,
                "field_path": finding.field_path,
                "remediation": finding.remediation,
                "impact": getattr(finding, 'impact', 'Not specified'),
                "configuration_lines": getattr(finding, 'configuration_lines', [])
            })
        
        return {
            "success": True,
            "data": {
                "audit_id": audit.audit_id,
                "configuration": {
                    "config_id": config.config_id,
                    "filename": config.original_filename,
                    "vendor": config.vendor
                },
                "status": audit.status,
                "compliance_score": audit.compliance_score,
                "risk_score": audit.risk_score,
                "risk_level": audit.risk_level,
                "passed_count": audit.passed_count,
                "failed_count": audit.failed_count,
                "warning_count": audit.warning_count,
                "started_at": audit.started_at.isoformat(),
                "completed_at": audit.completed_at.isoformat() if audit.completed_at else None,
                "error_message": audit.error_message,
                "requires_human_review": audit.requires_human_review,
                "review_reason": audit.review_reason,
                "interpretation_confidence": audit.interpretation_confidence,
                "findings": formatted_findings,
                "findings_summary": {
                    "total": len(findings),
                    "by_severity": {
                        "critical": len([f for f in findings if f.severity == "CRITICAL"]),
                        "high": len([f for f in findings if f.severity == "HIGH"]),
                        "medium": len([f for f in findings if f.severity == "MEDIUM"]),
                        "low": len([f for f in findings if f.severity == "LOW"])
                    },
                    "by_status": {
                        "pass": len([f for f in findings if f.status == "PASS"]),
                        "fail": len([f for f in findings if f.status == "FAIL"]),
                        "unknown": len([f for f in findings if f.status == "UNKNOWN"])
                    }
                },
                "vendor_info": {
                    "vendor_id": vendor.vendor_id,
                    "company": vendor.company_name
                }
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
                    "message": "Failed to retrieve audit"
                }
            }
        )


@router.get("/vendor/audit/{audit_id}/report")
async def vendor_download_enhanced_audit_report(
    audit_id: str,
    vendor_session: tuple = Depends(require_vendor_session()),
    db: Session = Depends(get_db)
):
    """
    Generate and download enhanced professional PDF report for vendor's audit
    
    Returns comprehensive professional PDF report including:
    - Professional cover page with vendor branding
    - Executive summary with business impact analysis
    - Technical assessment with AI confidence metrics
    - Detailed configuration analysis with file previews
    - Comprehensive security findings with evidence traceability
    - Prioritized remediation guidance with effort estimates
    - AI analysis appendix with confidence metrics
    - Technical appendices with complete findings summary
    """
    vendor, session = vendor_session
    
    try:
        from app.database import Audit
        from fastapi.responses import StreamingResponse
        from io import BytesIO
        from app.reports.enhanced_pdf_generator import EnhancedPDFReportGenerator
        
        # Get enhanced audit data
        enhanced_audit_response = await vendor_get_audit_enhanced(audit_id, vendor_session, db)
        if not enhanced_audit_response.get('success'):
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "AUDIT_NOT_FOUND",
                        "message": "Audit not found or access denied"
                    }
                }
            )
        
        audit_data = enhanced_audit_response['data']
        
        # Get configuration details
        config_id = audit_data['configuration']['config_id']
        config_response = await vendor_get_configuration_details(config_id, vendor_session, db)
        config_data = config_response.get('data') if config_response.get('success') else {}
        
        # Vendor information
        vendor_info = {
            'vendor_id': vendor.vendor_id,
            'company': vendor.company_name,
            'email': vendor.email
        }
        
        # Generate enhanced PDF report
        pdf_generator = EnhancedPDFReportGenerator()
        pdf_bytes = pdf_generator.generate_comprehensive_vendor_report(
            audit_data=audit_data,
            config_data=config_data,
            vendor_info=vendor_info
        )
        
        # Create filename with vendor and date
        report_date = datetime.now().strftime('%Y%m%d')
        safe_company_name = "".join(c for c in vendor.company_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"Security_Audit_Report_{safe_company_name}_{audit_id}_{report_date}.pdf"
        
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Enhanced PDF generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "PDF_GENERATION_FAILED",
                    "message": "Failed to generate enhanced PDF report"
                }
            }
        )
        
        if not audit:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Audit {audit_id} not found or access denied"
                    }
                }
            )
        
        # Get configuration for filename
        config = db.query(Configuration).filter(
            Configuration.id == audit.configuration_id
        ).first()
        
        # Generate PDF report using same system as admin
        from app.api.audit import generate_audit_report
        pdf_buffer = generate_audit_report(audit_id, db)
        
        # Log security event
        log = SecurityAuditLog(
            log_id=generate_log_id(db),
            user_id=None,  # Vendor action
            organization_id=vendor.organization_id,
            event_type="VENDOR_REPORT",
            action="DOWNLOAD",
            result="SUCCESS",
            resource_type="audit",
            resource_id=audit_id,
            details={
                "audit_id": audit_id,
                "report_type": "pdf",
                "vendor_id": vendor.vendor_id,
                "vendor_email": vendor.email,
                "company": vendor.company_name
            },
            ip_address="",
            user_agent=""
        )
        db.add(log)
        db.commit()
        
        # Create filename
        config_name = config.original_filename.replace('.', '_') if config else 'unknown'
        filename = f"vendor_audit_report_{audit_id}_{config_name}_{vendor.vendor_id}.pdf"
        
        # Return PDF as streaming response
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Vendor PDF generation error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "REPORT_GENERATION_FAILED",
                    "message": f"Failed to generate PDF report: {str(e)}"
                }
            }
        )


@router.get("/vendor/audits")
async def vendor_list_audits(
    vendor_session: tuple = Depends(require_vendor_session()),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50
):
    """
    List all audits for this specific vendor's uploaded configurations only
    """
    vendor, session = vendor_session
    
    try:
        from app.database import Audit
        
        # Get audits ONLY for configurations uploaded by this specific vendor
        audits = db.query(Audit).join(
            Configuration, Audit.configuration_id == Configuration.id
        ).filter(
            Configuration.uploaded_by == vendor.vendor_id  # Vendor-specific filtering
        ).order_by(Audit.started_at.desc()).offset(skip).limit(limit).all()
        
        total = db.query(Audit).join(
            Configuration, Audit.configuration_id == Configuration.id
        ).filter(
            Configuration.uploaded_by == vendor.vendor_id  # Vendor-specific filtering
        ).count()
        
        audit_list = []
        for audit in audits:
            config = db.query(Configuration).filter(Configuration.id == audit.configuration_id).first()
            audit_list.append({
                "audit_id": audit.audit_id,
                "configuration": {
                    "config_id": config.config_id if config else None,
                    "filename": config.original_filename if config else None,
                    "vendor": config.vendor if config else None,
                    "uploaded_by": config.uploaded_by if config else None  # Verification field
                },
                "status": audit.status,
                "compliance_score": audit.compliance_score,
                "risk_level": audit.risk_level,
                "started_at": audit.started_at.isoformat(),
                "completed_at": audit.completed_at.isoformat() if audit.completed_at else None,
                "requires_human_review": audit.requires_human_review
            })
        
        return {
            "success": True,
            "data": {
                "audits": audit_list,
                "total": total,
                "skip": skip,
                "limit": limit,
                "vendor_info": {
                    "vendor_id": vendor.vendor_id,
                    "company": vendor.company_name
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "LIST_FAILED",
                    "message": "Failed to retrieve audit list"
                }
            }
        )


@router.get("/vendor/configurations")
async def vendor_list_configurations(
    vendor_session: tuple = Depends(require_vendor_session()),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50
):
    """
    List all configurations uploaded by this specific vendor only
    """
    vendor, session = vendor_session
    
    try:
        # Get configurations uploaded ONLY by this specific vendor
        configs = db.query(Configuration).filter(
            Configuration.uploaded_by == vendor.vendor_id  # Vendor-specific filtering
        ).order_by(Configuration.created_at.desc()).offset(skip).limit(limit).all()
        
        total = db.query(Configuration).filter(
            Configuration.uploaded_by == vendor.vendor_id  # Vendor-specific filtering
        ).count()
        
        config_list = []
        for config in configs:
            config_list.append({
                "config_id": config.config_id,
                "filename": config.original_filename,
                "file_type": config.file_type,
                "status": config.status,
                "vendor": config.vendor,
                "vendor_confidence": config.vendor_confidence,
                "created_at": config.created_at.isoformat(),
                "file_size": getattr(config, 'file_size', None),
                "uploaded_by": config.uploaded_by  # Show who uploaded it for verification
            })
        
        return {
            "success": True,
            "data": {
                "configurations": config_list,
                "total": total,
                "skip": skip,
                "limit": limit,
                "vendor_info": {
                    "vendor_id": vendor.vendor_id,
                    "company": vendor.company_name
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "LIST_FAILED",
                    "message": "Failed to retrieve configuration list"
                }
            }
        )


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
@router.get("/vendor/configuration/{config_id}")
async def vendor_get_configuration_details(
    config_id: str,
    vendor_session: tuple = Depends(require_vendor_session()),
    db: Session = Depends(get_db)
):
    """
    Get detailed configuration information for vendor
    
    Returns comprehensive configuration details including:
    - File metadata and technical specifications
    - File content preview (sanitized)
    - Upload session information
    - Associated audit information
    - Processing statistics
    """
    vendor, session = vendor_session
    
    try:
        import os
        
        # Get configuration with vendor-specific access control
        config = db.query(Configuration).filter(
            Configuration.config_id == config_id,
            Configuration.uploaded_by == vendor.vendor_id  # Vendor-specific access
        ).first()
        
        if not config:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Configuration {config_id} not found or access denied"
                    }
                }
            )
        
        # Get associated audits
        audits = db.query(Audit).filter(Audit.configuration_id == config.id).all()
        
        # Get file content preview (sanitized)
        file_preview = None
        file_stats = {}
        
        try:
            if config.sanitized_path and os.path.exists(config.sanitized_path):
                with open(config.sanitized_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()[:50]  # First 50 lines for preview
                    file_preview = ''.join(lines)
                    file_stats = {
                        "total_lines": len(f.readlines()) + len(lines),
                        "preview_lines": len(lines),
                        "file_size_bytes": os.path.getsize(config.sanitized_path)
                    }
        except Exception as e:
            file_preview = "File content not available"
            print(f"Error reading file preview: {e}")
        
        # Format audit information
        audit_info = []
        for audit in audits:
            audit_data = {
                "audit_id": audit.audit_id,
                "status": audit.status,
                "compliance_score": audit.compliance_score,
                "risk_score": audit.risk_score,
                "risk_level": audit.risk_level,
                "started_at": audit.started_at.isoformat(),
                "completed_at": audit.completed_at.isoformat() if audit.completed_at else None,
                "requires_human_review": audit.requires_human_review,
                "interpretation_confidence": audit.interpretation_confidence,
                "parsing_stats": {
                    "total_lines": audit.total_lines_count,
                    "uninterpreted_lines": audit.uninterpreted_lines_count,
                    "interpretation_rate": (
                        ((audit.total_lines_count - audit.uninterpreted_lines_count) / audit.total_lines_count * 100) 
                        if audit.total_lines_count > 0 else 0
                    ),
                    "pending_mappings": audit.pending_mappings_count
                },
                "review_reason": audit.review_reason,
                "findings_count": {
                    "total": audit.passed_count + audit.failed_count + audit.warning_count,
                    "passed": audit.passed_count,
                    "failed": audit.failed_count,
                    "warnings": audit.warning_count
                }
            }
            audit_info.append(audit_data)
        
        return {
            "success": True,
            "data": {
                "config_id": config.config_id,
                "filename": config.original_filename,
                "internal_filename": config.filename,
                "file_type": config.file_type,
                "status": config.status,
                "vendor_detection": {
                    "detected_vendor": config.vendor,
                    "confidence": config.vendor_confidence
                },
                "file_integrity": {
                    "sha256_hash": config.file_hash_sha256,
                    "storage_path": os.path.basename(config.storage_path) if config.storage_path else None,
                    "sanitized_path": os.path.basename(config.sanitized_path) if config.sanitized_path else None
                },
                "file_content": {
                    "preview": file_preview,
                    "stats": file_stats
                },
                "upload_metadata": {
                    "uploaded_by": config.uploaded_by,
                    "uploaded_at": config.created_at.isoformat(),
                    "organization_id": config.organization_id
                },
                "audits": audit_info,
                "processing_status": {
                    "ingested": bool(config.sanitized_path),
                    "vendor_detected": bool(config.vendor and config.vendor != "Unknown"),
                    "audited": len(audit_info) > 0,
                    "latest_audit": audit_info[0] if audit_info else None
                }
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
                    "message": "Failed to retrieve configuration details"
                }
            }
        )


@router.get("/vendor/audit/{audit_id}")
async def vendor_get_audit_enhanced(
    audit_id: str,
    vendor_session: tuple = Depends(require_vendor_session()),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive audit details for vendor with full evidence and technical information
    
    Returns detailed audit information including:
    - Complete compliance and risk analysis
    - Detailed findings with evidence traceability
    - AI parsing statistics and confidence metrics
    - Configuration line mappings
    - Remediation guidance with priority sequencing
    """
    vendor, session = vendor_session
    
    try:
        from app.database import Audit, Finding
        
        # Get audit with vendor-specific check
        audit = db.query(Audit).join(
            Configuration, Audit.configuration_id == Configuration.id
        ).filter(
            Audit.audit_id == audit_id,
            Configuration.uploaded_by == vendor.vendor_id  # Vendor-specific access control
        ).first()
        
        if not audit:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Audit {audit_id} not found or access denied"
                    }
                }
            )
        
        # Get configuration
        config = db.query(Configuration).filter(
            Configuration.id == audit.configuration_id
        ).first()
        
        # Get findings with detailed information
        findings = db.query(Finding).filter(Finding.audit_id == audit.id).all()
        
        def calculate_remediation_priority(finding):
            """Calculate remediation priority based on severity and business impact"""
            severity_weights = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
            base_priority = severity_weights.get(finding.severity, 1)
            
            # Adjust based on risk score if available
            if finding.risk_score:
                if finding.risk_score > 8.0:
                    base_priority += 1
                elif finding.risk_score < 3.0:
                    base_priority = max(1, base_priority - 1)
            
            return min(5, max(1, base_priority))  # Scale 1-5
        
        def estimate_remediation_effort(finding):
            """Estimate effort required to remediate finding"""
            effort_map = {
                "CRITICAL": "High (4-8 hours)",
                "HIGH": "Medium (2-4 hours)", 
                "MEDIUM": "Low (1-2 hours)",
                "LOW": "Minimal (15-30 minutes)"
            }
            return effort_map.get(finding.severity, "Unknown")
        
        def assess_business_impact(finding):
            """Assess business impact of the finding"""
            impact_keywords = {
                "data breach": "High - Potential data exposure",
                "unauthorized access": "High - Security compromise risk",
                "password": "Medium - Authentication weakness",
                "encryption": "High - Data protection risk",
                "logging": "Low - Audit trail impact",
                "configuration": "Low - Operational impact"
            }
            
            description = (finding.description or "").lower()
            for keyword, impact in impact_keywords.items():
                if keyword in description:
                    return impact
            
            return "Medium - Security best practice"
        
        def get_compliance_frameworks(rule_id):
            """Map rule to compliance frameworks"""
            framework_map = {
                "NET-001": ["CIS Controls", "NIST CSF"],
                "NET-002": ["ISO 27001", "SOC 2"],
                "AUTH-001": ["PCI DSS", "NIST CSF"]
            }
            return framework_map.get(rule_id, ["General Security"])
        
        def get_security_standards(rule_id):
            """Map rule to security standards"""
            return ["Industry Best Practice", "Vendor Security Guide"]
        
        # Format findings with comprehensive evidence and technical details
        formatted_findings = []
        for finding in findings:
            finding_data = {
                "finding_id": finding.finding_id,
                "rule_id": finding.rule_id,
                "rule_name": finding.title,
                "description": finding.description,
                "severity": finding.severity,
                "status": finding.status,
                "technical_details": {
                    "expected": finding.expected,
                    "actual": finding.actual,
                    "field_path": finding.field_path,
                    "risk_score": finding.risk_score
                },
                "evidence": {
                    "evidence_file": finding.evidence_file,
                    "evidence_line": finding.evidence_line,
                    "evidence_text": finding.evidence_text,
                    "configuration_context": getattr(finding, 'configuration_lines', [])
                },
                "remediation": {
                    "guidance": finding.remediation,
                    "priority": calculate_remediation_priority(finding),
                    "estimated_effort": estimate_remediation_effort(finding),
                    "business_impact": assess_business_impact(finding)
                },
                "compliance_mapping": {
                    "frameworks": get_compliance_frameworks(finding.rule_id),
                    "standards": get_security_standards(finding.rule_id)
                },
                "created_at": finding.created_at.isoformat()
            }
            formatted_findings.append(finding_data)
        
        # Calculate comprehensive statistics
        findings_by_severity = {
            "critical": len([f for f in findings if f.severity == "CRITICAL"]),
            "high": len([f for f in findings if f.severity == "HIGH"]),
            "medium": len([f for f in findings if f.severity == "MEDIUM"]),
            "low": len([f for f in findings if f.severity == "LOW"])
        }
        
        findings_by_status = {
            "pass": len([f for f in findings if f.status == "PASS"]),
            "fail": len([f for f in findings if f.status == "FAIL"]),
            "warning": len([f for f in findings if f.status == "WARNING"]),
            "unknown": len([f for f in findings if f.status == "UNKNOWN"])
        }
        
        # AI Parsing and Technical Analysis
        parsing_analysis = {
            "interpretation_confidence": audit.interpretation_confidence,
            "total_config_lines": audit.total_lines_count,
            "successfully_interpreted": audit.total_lines_count - audit.uninterpreted_lines_count if audit.total_lines_count else 0,
            "uninterpreted_lines": audit.uninterpreted_lines_count,
            "interpretation_rate": (
                ((audit.total_lines_count - audit.uninterpreted_lines_count) / audit.total_lines_count * 100) 
                if audit.total_lines_count > 0 else 0
            ),
            "pending_ai_mappings": audit.pending_mappings_count,
            "requires_human_review": audit.requires_human_review,
            "review_reason": audit.review_reason,
            "normalized_data_available": bool(audit.normalized_data)
        }
        
        def calculate_security_posture_risk(findings):
            """Calculate security posture risk score"""
            critical_fails = len([f for f in findings if f.severity == "CRITICAL" and f.status == "FAIL"])
            high_fails = len([f for f in findings if f.severity == "HIGH" and f.status == "FAIL"])
            
            risk_score = (critical_fails * 10) + (high_fails * 5)
            return min(100, risk_score)
        
        def calculate_compliance_gap_risk(compliance_score):
            """Calculate compliance gap risk"""
            if compliance_score >= 90:
                return "Low"
            elif compliance_score >= 70:
                return "Medium"
            else:
                return "High"
        
        def calculate_complexity_risk(total_lines, uninterpreted_lines):
            """Calculate configuration complexity risk"""
            if not total_lines:
                return "Unknown"
            
            uninterpreted_rate = (uninterpreted_lines / total_lines) * 100
            
            if uninterpreted_rate > 20:
                return "High - Many uninterpreted sections"
            elif uninterpreted_rate > 10:
                return "Medium - Some unclear configurations"
            else:
                return "Low - Well-understood configuration"
        
        def assess_business_risk_factors(findings):
            """Assess business-level risk factors"""
            factors = []
            
            auth_issues = len([f for f in findings if "auth" in (f.rule_id or "").lower() and f.status == "FAIL"])
            if auth_issues > 0:
                factors.append(f"Authentication vulnerabilities ({auth_issues} issues)")
            
            access_issues = len([f for f in findings if "access" in (f.rule_id or "").lower() and f.status == "FAIL"])
            if access_issues > 0:
                factors.append(f"Access control weaknesses ({access_issues} issues)")
            
            return factors if factors else ["No significant business risk factors identified"]
        
        # Risk Assessment Details
        risk_assessment = {
            "overall_risk_score": audit.risk_score,
            "risk_level": audit.risk_level,
            "risk_breakdown": {
                "security_posture": calculate_security_posture_risk(findings),
                "compliance_gap": calculate_compliance_gap_risk(audit.compliance_score),
                "configuration_complexity": calculate_complexity_risk(audit.total_lines_count, audit.uninterpreted_lines_count)
            },
            "business_risk_factors": assess_business_risk_factors(findings)
        }
        
        def assess_security_posture(findings):
            """Comprehensive security posture assessment"""
            total_findings = len(findings)
            failed_findings = len([f for f in findings if f.status == "FAIL"])
            
            if total_findings == 0:
                return "Insufficient data for assessment"
            
            failure_rate = (failed_findings / total_findings) * 100
            
            if failure_rate < 10:
                return "Strong - Minimal security issues identified"
            elif failure_rate < 30:
                return "Good - Some areas for improvement"
            elif failure_rate < 60:
                return "Fair - Multiple security concerns"
            else:
                return "Poor - Significant security vulnerabilities"
        
        def assess_config_quality(audit):
            """Assess configuration quality"""
            if not audit.total_lines_count:
                return "Cannot assess - No configuration data"
            
            interpretation_rate = ((audit.total_lines_count - audit.uninterpreted_lines_count) / audit.total_lines_count) * 100
            
            if interpretation_rate > 90:
                return "Excellent - Clear, standard configuration"
            elif interpretation_rate > 75:
                return "Good - Mostly standard practices"
            elif interpretation_rate > 50:
                return "Fair - Some non-standard configurations"
            else:
                return "Poor - Many unclear or non-standard settings"
        
        def assess_vendor_practices(vendor_name, findings):
            """Assess adherence to vendor best practices"""
            if vendor_name == "Unknown":
                return "Cannot assess - Unknown device vendor"
            
            # This would be expanded with vendor-specific best practice checks
            vendor_specific_issues = len([f for f in findings if vendor_name.lower() in (f.rule_id or "").lower() and f.status == "FAIL"])
            
            if vendor_specific_issues == 0:
                return f"Excellent - Follows {vendor_name} security best practices"
            elif vendor_specific_issues < 3:
                return f"Good - Minor deviations from {vendor_name} recommendations"
            else:
                return f"Poor - Multiple violations of {vendor_name} security guidelines"
        
        def generate_maintenance_recommendations(audit, findings):
            """Generate maintenance recommendations"""
            recommendations = []
            
            if audit.requires_human_review:
                recommendations.append("Schedule expert review for configuration interpretation")
            
            critical_issues = len([f for f in findings if f.severity == "CRITICAL" and f.status == "FAIL"])
            if critical_issues > 0:
                recommendations.append("Immediately address critical security vulnerabilities")
            
            if audit.uninterpreted_lines_count > 0:
                recommendations.append("Review and document non-standard configuration sections")
            
            if not recommendations:
                recommendations.append("Maintain current security configuration standards")
            
            return recommendations
        
        # Device Assessment Summary
        device_assessment = {
            "security_posture": assess_security_posture(findings),
            "configuration_quality": assess_config_quality(audit),
            "vendor_best_practices": assess_vendor_practices(config.vendor, findings),
            "maintenance_recommendations": generate_maintenance_recommendations(audit, findings)
        }
        
        def calculate_total_remediation_effort(findings):
            """Calculate estimated total remediation effort"""
            effort_hours = 0
            
            for finding in findings:
                if finding['status'] == 'FAIL':
                    severity = finding['severity']
                    if severity == 'CRITICAL':
                        effort_hours += 6  # 4-8 hours avg = 6
                    elif severity == 'HIGH':
                        effort_hours += 3  # 2-4 hours avg = 3
                    elif severity == 'MEDIUM':
                        effort_hours += 1.5  # 1-2 hours avg = 1.5
                    elif severity == 'LOW':
                        effort_hours += 0.25  # 15-30 min avg = 22.5 min
            
            if effort_hours < 1:
                return "Less than 1 hour"
            elif effort_hours < 8:
                return f"Approximately {effort_hours:.1f} hours"
            else:
                return f"Approximately {effort_hours:.0f} hours (plan multi-day effort)"
        
        return {
            "success": True,
            "data": {
                "audit_id": audit.audit_id,
                "configuration": {
                    "config_id": config.config_id,
                    "filename": config.original_filename,
                    "vendor": config.vendor,
                    "vendor_confidence": config.vendor_confidence,
                    "file_hash": config.file_hash_sha256
                },
                "audit_summary": {
                    "status": audit.status,
                    "compliance_score": audit.compliance_score,
                    "risk_score": audit.risk_score,
                    "risk_level": audit.risk_level,
                    "started_at": audit.started_at.isoformat(),
                    "completed_at": audit.completed_at.isoformat() if audit.completed_at else None,
                    "duration_seconds": (
                        (audit.completed_at - audit.started_at).total_seconds() 
                        if audit.completed_at and audit.started_at else None
                    ),
                    "error_message": audit.error_message
                },
                "parsing_analysis": parsing_analysis,
                "risk_assessment": risk_assessment,
                "device_assessment": device_assessment,
                "findings": {
                    "total_count": len(findings),
                    "summary": {
                        "by_severity": findings_by_severity,
                        "by_status": findings_by_status
                    },
                    "details": formatted_findings
                },
                "evidence_and_provenance": {
                    "evidence_files_analyzed": len(set([f.evidence_file for f in findings if f.evidence_file])),
                    "configuration_lines_referenced": len(set([f.evidence_line for f in findings if f.evidence_line])),
                    "total_evidence_entries": len([f for f in findings if f.evidence_text])
                },
                "remediation_guidance": {
                    "priority_1_critical": [f for f in formatted_findings if f['severity'] in ['CRITICAL', 'HIGH'] and f['status'] == 'FAIL'],
                    "priority_2_important": [f for f in formatted_findings if f['severity'] == 'MEDIUM' and f['status'] == 'FAIL'],
                    "priority_3_maintenance": [f for f in formatted_findings if f['severity'] == 'LOW' and f['status'] == 'FAIL'],
                    "estimated_total_effort": calculate_total_remediation_effort(formatted_findings)
                },
                "vendor_info": {
                    "vendor_id": vendor.vendor_id,
                    "company": vendor.company_name
                }
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
                    "message": "Failed to retrieve comprehensive audit details"
                }
            }
        )
