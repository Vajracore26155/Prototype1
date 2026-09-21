"""
Async Job Status API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db, Job, User
from app.auth.dependencies import require_permission
from app.auth.permissions import Permission

router = APIRouter()


@router.get("/jobs/{job_id}")
async def get_job_status(
    job_id: str,
    current_user: User = Depends(require_permission(Permission.JOB_VIEW)),
    db: Session = Depends(get_db)
):
    """
    Get status of an async job
    
    Returns:
        Job status, progress, and result if completed
    """
    try:
        # Get job with organization check
        job = db.query(Job).filter(
            Job.job_id == job_id,
            Job.organization_id == current_user.organization_id
        ).first()
        
        if not job:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Job {job_id} not found"
                    }
                }
            )
        
        return {
            "success": True,
            "data": {
                "job_id": job.job_id,
                "job_type": job.job_type,
                "status": job.status,
                "progress": job.progress,
                "created_at": job.created_at.isoformat(),
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "result": job.result,
                "error_message": job.error_message
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
                    "message": "Failed to retrieve job status"
                }
            }
        )


@router.get("/jobs")
async def list_jobs(
    current_user: User = Depends(require_permission(Permission.JOB_VIEW)),
    db: Session = Depends(get_db),
    status: Optional[str] = None,
    job_type: Optional[str] = None,
    limit: int = 50
):
    """
    List jobs for the current organization
    
    Query Parameters:
        status: Filter by status (PENDING, RUNNING, COMPLETED, FAILED)
        job_type: Filter by job type (AUDIT, REPORT, BULK_UPLOAD)
        limit: Maximum number of results (default 50)
    """
    try:
        query = db.query(Job).filter(
            Job.organization_id == current_user.organization_id
        )
        
        if status:
            query = query.filter(Job.status == status)
        
        if job_type:
            query = query.filter(Job.job_type == job_type)
        
        jobs = query.order_by(Job.created_at.desc()).limit(limit).all()
        
        return {
            "success": True,
            "data": {
                "jobs": [
                    {
                        "job_id": job.job_id,
                        "job_type": job.job_type,
                        "status": job.status,
                        "progress": job.progress,
                        "created_at": job.created_at.isoformat(),
                        "started_at": job.started_at.isoformat() if job.started_at else None,
                        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                        "error_message": job.error_message
                    }
                    for job in jobs
                ],
                "total": len(jobs)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "LIST_FAILED",
                    "message": "Failed to list jobs"
                }
            }
        )


@router.delete("/jobs/{job_id}")
async def delete_job(
    job_id: str,
    current_user: User = Depends(require_permission(Permission.JOB_DELETE)),
    db: Session = Depends(get_db)
):
    """
    Delete a job record
    
    Note: This only deletes the database record, not the actual task if it's running
    """
    try:
        # Get job with organization check
        job = db.query(Job).filter(
            Job.job_id == job_id,
            Job.organization_id == current_user.organization_id
        ).first()
        
        if not job:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Job {job_id} not found"
                    }
                }
            )
        
        db.delete(job)
        db.commit()
        
        return {
            "success": True,
            "data": {
                "message": f"Job {job_id} deleted successfully"
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
                    "code": "DELETE_FAILED",
                    "message": "Failed to delete job"
                }
            }
        )
