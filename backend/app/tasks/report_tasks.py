"""
Celery Tasks for Report Generation
"""
import logging
from datetime import datetime, timedelta
from io import BytesIO
from celery import Task
from sqlalchemy.orm import Session

from app.tasks.celery_app import celery_app
from app.database import SessionLocal, Audit, Configuration, Organization, Job
from app.reports import generate_audit_report
from app.storage import get_storage_backend, BUCKET_REPORTS

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


@celery_app.task(base=DatabaseTask, bind=True, name="app.tasks.report_tasks.generate_report_async")
def generate_report_async(self, audit_id: str, job_id: str = None):
    """
    Generate PDF report asynchronously
    
    Args:
        audit_id: Audit ID to generate report for
        job_id: Optional Job ID for tracking
    
    Returns:
        dict: Report generation result with storage path
    """
    db = self.db
    storage = get_storage_backend()
    
    try:
        logger.info(f"Starting async report generation for audit {audit_id}")
        
        # Update job status
        if job_id:
            job = db.query(Job).filter(Job.job_id == job_id).first()
            if job:
                job.status = "RUNNING"
                job.started_at = datetime.utcnow()
                db.commit()
        
        # Check if audit exists
        audit = db.query(Audit).filter(Audit.audit_id == audit_id).first()
        
        if not audit:
            error_msg = f"Audit {audit_id} not found"
            logger.error(error_msg)
            
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
        
        # Generate PDF report
        pdf_buffer = generate_audit_report(audit_id)
        pdf_bytes = pdf_buffer.getvalue()
        
        # Get configuration for filename
        config = db.query(Configuration).filter(
            Configuration.id == audit.configuration_id
        ).first()
        
        config_name = config.original_filename.replace('.', '_') if config else 'unknown'
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        object_name = f"reports/{audit_id}_{config_name}_{timestamp}.pdf"
        
        # Save to storage
        storage_path = storage.save_file(pdf_bytes, BUCKET_REPORTS, object_name)
        
        # Update job status
        if job_id:
            job = db.query(Job).filter(Job.job_id == job_id).first()
            if job:
                job.status = "COMPLETED"
                job.result = {
                    "audit_id": audit_id,
                    "storage_path": storage_path,
                    "file_size": len(pdf_bytes)
                }
                job.completed_at = datetime.utcnow()
                db.commit()
        
        logger.info(f"Completed async report generation for audit {audit_id}: {storage_path}")
        
        return {
            "success": True,
            "audit_id": audit_id,
            "storage_path": storage_path,
            "file_size": len(pdf_bytes),
            "object_name": object_name
        }
        
    except Exception as e:
        error_msg = f"Report generation failed: {str(e)}"
        logger.error(f"Async report error for audit {audit_id}: {error_msg}", exc_info=True)
        
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


@celery_app.task(base=DatabaseTask, bind=True, name="app.tasks.report_tasks.generate_bulk_reports")
def generate_bulk_reports(self, audit_ids: list, organization_id: int):
    """
    Generate reports for multiple audits
    
    Args:
        audit_ids: List of audit IDs
        organization_id: Organization ID for filtering
    
    Returns:
        dict: Bulk report generation results
    """
    db = self.db
    storage = get_storage_backend()
    
    try:
        logger.info(f"Starting bulk report generation for {len(audit_ids)} audits")
        
        results = []
        for audit_id in audit_ids:
            # Verify organization ownership
            audit = db.query(Audit).join(
                Configuration, Audit.configuration_id == Configuration.id
            ).filter(
                Audit.audit_id == audit_id,
                Configuration.organization_id == organization_id
            ).first()
            
            if not audit:
                logger.warning(f"Audit {audit_id} not found or not owned by org {organization_id}")
                results.append({
                    "audit_id": audit_id,
                    "success": False,
                    "error": "Not found or access denied"
                })
                continue
            
            # Generate report
            try:
                pdf_buffer = generate_audit_report(audit_id)
                pdf_bytes = pdf_buffer.getvalue()
                
                config = db.query(Configuration).filter(
                    Configuration.id == audit.configuration_id
                ).first()
                
                config_name = config.original_filename.replace('.', '_') if config else 'unknown'
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                object_name = f"reports/{audit_id}_{config_name}_{timestamp}.pdf"
                
                storage_path = storage.save_file(pdf_bytes, BUCKET_REPORTS, object_name)
                
                results.append({
                    "audit_id": audit_id,
                    "success": True,
                    "storage_path": storage_path,
                    "file_size": len(pdf_bytes)
                })
            except Exception as e:
                logger.error(f"Failed to generate report for {audit_id}: {str(e)}")
                results.append({
                    "audit_id": audit_id,
                    "success": False,
                    "error": str(e)
                })
        
        successful = sum(1 for r in results if r["success"])
        failed = len(results) - successful
        
        logger.info(f"Bulk report generation complete: {successful} succeeded, {failed} failed")
        
        return {
            "success": True,
            "total": len(results),
            "successful": successful,
            "failed": failed,
            "results": results
        }
        
    except Exception as e:
        error_msg = f"Bulk report generation failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "success": False,
            "error": error_msg
        }


@celery_app.task(base=DatabaseTask, bind=True, name="app.tasks.report_tasks.generate_daily_summary")
def generate_daily_summary(self):
    """
    Generate daily summary reports for all organizations (periodic task)
    
    Returns:
        dict: Summary generation results
    """
    db = self.db
    
    try:
        logger.info("Starting daily summary generation")
        
        # Get all organizations
        organizations = db.query(Organization).filter(Organization.is_active == True).all()
        
        summaries = []
        for org in organizations:
            try:
                # Count audits run in last 24 hours
                yesterday = datetime.utcnow() - timedelta(days=1)
                audit_count = db.query(Audit).join(
                    Configuration, Audit.configuration_id == Configuration.id
                ).filter(
                    Configuration.organization_id == org.id,
                    Audit.started_at >= yesterday
                ).count()
                
                summaries.append({
                    "organization_id": org.id,
                    "organization_name": org.name,
                    "audits_last_24h": audit_count,
                    "success": True
                })
            except Exception as e:
                logger.error(f"Failed to generate summary for org {org.id}: {str(e)}")
                summaries.append({
                    "organization_id": org.id,
                    "organization_name": org.name,
                    "success": False,
                    "error": str(e)
                })
        
        logger.info(f"Daily summary generation complete for {len(summaries)} organizations")
        
        return {
            "success": True,
            "total_organizations": len(summaries),
            "summaries": summaries
        }
        
    except Exception as e:
        error_msg = f"Daily summary generation failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "success": False,
            "error": error_msg
        }
