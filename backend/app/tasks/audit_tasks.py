"""
Celery Tasks for Audit Processing
"""
import logging
from datetime import datetime, timedelta
from celery import Task
from sqlalchemy.orm import Session

from app.tasks.celery_app import celery_app
from app.database import SessionLocal, Audit, Configuration, Job
from app.findings import run_configuration_audit

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


@celery_app.task(base=DatabaseTask, bind=True, name="app.tasks.audit_tasks.run_audit_async")
def run_audit_async(self, config_id: str, job_id: str = None):
    """
    Run security audit on a configuration asynchronously
    
    Args:
        config_id: Configuration ID to audit
        job_id: Optional Job ID for tracking
    
    Returns:
        dict: Audit result with audit_id and status
    """
    db = self.db
    
    try:
        logger.info(f"Starting async audit for config {config_id}")
        
        # Update job status if provided
        if job_id:
            job = db.query(Job).filter(Job.job_id == job_id).first()
            if job:
                job.status = "RUNNING"
                job.started_at = datetime.utcnow()
                db.commit()
        
        # Check if configuration exists
        config = db.query(Configuration).filter(
            Configuration.config_id == config_id
        ).first()
        
        if not config:
            error_msg = f"Configuration {config_id} not found"
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
        
        # Run audit
        audit = run_configuration_audit(config_id)
        
        # Update job status
        if job_id:
            job = db.query(Job).filter(Job.job_id == job_id).first()
            if job:
                job.status = "COMPLETED"
                job.result = {
                    "audit_id": audit.audit_id,
                    "compliance_score": audit.compliance_score,
                    "risk_score": audit.risk_score
                }
                job.completed_at = datetime.utcnow()
                db.commit()
        
        logger.info(f"Completed async audit for config {config_id}: {audit.audit_id}")
        
        return {
            "success": True,
            "audit_id": audit.audit_id,
            "config_id": config_id,
            "compliance_score": audit.compliance_score,
            "risk_score": audit.risk_score,
            "status": audit.status
        }
        
    except Exception as e:
        error_msg = f"Audit failed: {str(e)}"
        logger.error(f"Async audit error for config {config_id}: {error_msg}", exc_info=True)
        
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


@celery_app.task(base=DatabaseTask, bind=True, name="app.tasks.audit_tasks.run_bulk_audit")
def run_bulk_audit(self, config_ids: list, organization_id: int):
    """
    Run audits on multiple configurations
    
    Args:
        config_ids: List of configuration IDs
        organization_id: Organization ID for filtering
    
    Returns:
        dict: Bulk audit results
    """
    db = self.db
    
    try:
        logger.info(f"Starting bulk audit for {len(config_ids)} configurations")
        
        results = []
        for config_id in config_ids:
            # Verify organization ownership
            config = db.query(Configuration).filter(
                Configuration.config_id == config_id,
                Configuration.organization_id == organization_id
            ).first()
            
            if not config:
                logger.warning(f"Config {config_id} not found or not owned by org {organization_id}")
                results.append({
                    "config_id": config_id,
                    "success": False,
                    "error": "Not found or access denied"
                })
                continue
            
            # Run audit
            try:
                audit = run_configuration_audit(config_id)
                results.append({
                    "config_id": config_id,
                    "success": True,
                    "audit_id": audit.audit_id,
                    "compliance_score": audit.compliance_score
                })
            except Exception as e:
                logger.error(f"Failed to audit {config_id}: {str(e)}")
                results.append({
                    "config_id": config_id,
                    "success": False,
                    "error": str(e)
                })
        
        successful = sum(1 for r in results if r["success"])
        failed = len(results) - successful
        
        logger.info(f"Bulk audit complete: {successful} succeeded, {failed} failed")
        
        return {
            "success": True,
            "total": len(results),
            "successful": successful,
            "failed": failed,
            "results": results
        }
        
    except Exception as e:
        error_msg = f"Bulk audit failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "success": False,
            "error": error_msg
        }


@celery_app.task(base=DatabaseTask, bind=True, name="app.tasks.audit_tasks.cleanup_old_audits")
def cleanup_old_audits(self, days: int = 90):
    """
    Clean up old audit records (periodic task)
    
    Args:
        days: Delete audits older than this many days
    
    Returns:
        dict: Cleanup results
    """
    db = self.db
    
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Count audits to delete
        count = db.query(Audit).filter(
            Audit.started_at < cutoff_date
        ).count()
        
        if count == 0:
            logger.info("No old audits to clean up")
            return {
                "success": True,
                "deleted": 0,
                "message": "No audits older than cutoff date"
            }
        
        # Delete old audits
        db.query(Audit).filter(
            Audit.started_at < cutoff_date
        ).delete(synchronize_session=False)
        
        db.commit()
        
        logger.info(f"Cleaned up {count} audits older than {days} days")
        
        return {
            "success": True,
            "deleted": count,
            "cutoff_date": cutoff_date.isoformat()
        }
        
    except Exception as e:
        error_msg = f"Cleanup failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        db.rollback()
        return {
            "success": False,
            "error": error_msg
        }
