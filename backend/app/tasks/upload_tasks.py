"""
Celery Tasks for Bulk Upload Processing
"""
import logging
import zipfile
from io import BytesIO
from datetime import datetime
from celery import Task
from sqlalchemy.orm import Session

from app.tasks.celery_app import celery_app
from app.database import SessionLocal, Configuration, Job
from app.ingestion import process_configuration_file
from app.storage import get_storage_backend, BUCKET_CONFIGS

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """Base task that provides database session"""
    _db = None
    
    @property
    def db(self):
        if self._db is None:
            self._db = SessionLocal()
        return self._db
    
    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()
            self._db = None


@celery_app.task(base=DatabaseTask, bind=True, name="app.tasks.upload_tasks.process_bulk_upload")
def process_bulk_upload(self, zip_storage_path: str, organization_id: int, uploaded_by: str, job_id: str = None):
    """
    Process bulk configuration upload from ZIP file
    
    Args:
        zip_storage_path: Storage path to ZIP file
        organization_id: Organization ID for uploaded configs
        uploaded_by: Email of user who uploaded
        job_id: Optional Job ID for tracking
    
    Returns:
        dict: Processing results with list of created configurations
    """
    db = self.db
    storage = get_storage_backend()
    
    try:
        logger.info(f"Starting bulk upload processing: {zip_storage_path}")
        
        # Update job status
        if job_id:
            job = db.query(Job).filter(Job.job_id == job_id).first()
            if job:
                job.status = "RUNNING"
                job.started_at = datetime.utcnow()
                job.progress = 0
                db.commit()
        
        # Extract bucket and object name from storage path
        # Format: "s3://bucket/object" or "/path/to/file"
        if zip_storage_path.startswith("s3://"):
            parts = zip_storage_path[5:].split("/", 1)
            bucket = parts[0]
            object_name = parts[1]
        else:
            # Filesystem path
            bucket = BUCKET_CONFIGS
            object_name = zip_storage_path.split("/")[-1]
        
        # Download ZIP file
        zip_bytes = storage.get_file(bucket, object_name)
        
        # Open ZIP file
        with zipfile.ZipFile(BytesIO(zip_bytes), 'r') as zip_ref:
            file_list = [f for f in zip_ref.namelist() if not f.endswith('/')]
            total_files = len(file_list)
            
            logger.info(f"Found {total_files} files in ZIP archive")
            
            results = []
            processed = 0
            
            for filename in file_list:
                try:
                    # Read file content
                    file_content = zip_ref.read(filename)
                    
                    # Process configuration file
                    config = process_configuration_file(
                        file_content=file_content,
                        filename=filename,
                        organization_id=organization_id,
                        uploaded_by=uploaded_by
                    )
                    
                    results.append({
                        "filename": filename,
                        "success": True,
                        "config_id": config.config_id,
                        "vendor": config.vendor
                    })
                    
                    logger.info(f"Processed {filename}: {config.config_id}")
                    
                except Exception as e:
                    logger.error(f"Failed to process {filename}: {str(e)}")
                    results.append({
                        "filename": filename,
                        "success": False,
                        "error": str(e)
                    })
                
                # Update progress
                processed += 1
                if job_id:
                    job = db.query(Job).filter(Job.job_id == job_id).first()
                    if job:
                        job.progress = int((processed / total_files) * 100)
                        db.commit()
        
        successful = sum(1 for r in results if r["success"])
        failed = total_files - successful
        
        # Update job status
        if job_id:
            job = db.query(Job).filter(Job.job_id == job_id).first()
            if job:
                job.status = "COMPLETED"
                job.result = {
                    "total_files": total_files,
                    "successful": successful,
                    "failed": failed,
                    "results": results
                }
                job.progress = 100
                job.completed_at = datetime.utcnow()
                db.commit()
        
        logger.info(f"Bulk upload processing complete: {successful} succeeded, {failed} failed")
        
        return {
            "success": True,
            "total_files": total_files,
            "successful": successful,
            "failed": failed,
            "results": results
        }
        
    except Exception as e:
        error_msg = f"Bulk upload processing failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        # Update job with error
        if job_id:
            job = db.query(Job).filter(Job.job_id == job_id).first()
            if job:
                job.status = "FAILED"
                job.error_message = error_msg
                job.completed_at = datetime.utcnow()
                db.commit()
        
        return {
            "success": False,
            "error": error_msg
        }


@celery_app.task(base=DatabaseTask, bind=True, name="app.tasks.upload_tasks.validate_config_file")
def validate_config_file(self, file_content: bytes, filename: str):
    """
    Validate a configuration file before processing
    
    Args:
        file_content: Raw file bytes
        filename: Original filename
    
    Returns:
        dict: Validation results
    """
    try:
        from app.detection import detect_vendor
        from app.security.masking import detect_sensitive_data
        
        # Check file size (max 10MB)
        if len(file_content) > 10 * 1024 * 1024:
            return {
                "valid": False,
                "error": "File too large (max 10MB)"
            }
        
        # Check for sensitive data
        text_content = file_content.decode('utf-8', errors='ignore')
        sensitive_found = detect_sensitive_data(text_content)
        
        # Detect vendor
        vendor, confidence = detect_vendor(text_content)
        
        # Check if parseable
        if vendor == "Unknown" and confidence < 0.3:
            return {
                "valid": False,
                "error": "Could not identify configuration vendor",
                "detected_vendor": vendor,
                "confidence": confidence
            }
        
        return {
            "valid": True,
            "filename": filename,
            "file_size": len(file_content),
            "detected_vendor": vendor,
            "vendor_confidence": confidence,
            "has_sensitive_data": len(sensitive_found) > 0,
            "sensitive_types": list(sensitive_found.keys()) if sensitive_found else []
        }
        
    except Exception as e:
        logger.error(f"Validation failed for {filename}: {str(e)}")
        return {
            "valid": False,
            "error": f"Validation error: {str(e)}"
        }
