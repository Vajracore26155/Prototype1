"""
Advanced Reporting API
Phase 7.3: Report generation, templates, and scheduling
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, time

from app.database import (
    get_db, Report, ScheduledReport, User, SecurityAuditLog
)
from app.auth.dependencies import require_permission
from app.auth.permissions import Permission
from app.reports.templates import (
    TemplateLibrary, ReportFormat, ReportType
)
from app.reports.scheduler import report_scheduler

router = APIRouter()


def generate_log_id(db: Session) -> str:
    """Generate unique audit log ID"""
    count = db.query(SecurityAuditLog).count()
    return f"LOG-{count + 1:08d}"


class ReportGenerateRequest(BaseModel):
    """Generate report request"""
    template_id: str
    name: str
    format: ReportFormat = ReportFormat.PDF
    filters: Optional[Dict] = {}


class ScheduledReportCreate(BaseModel):
    """Create scheduled report"""
    name: str
    template_id: str
    report_type: ReportType
    format: ReportFormat
    schedule_type: str  # DAILY, WEEKLY, MONTHLY, CUSTOM
    schedule_time: str  # HH:MM format
    schedule_day_of_week: Optional[int] = None  # 1-7 for WEEKLY
    schedule_day_of_month: Optional[int] = None  # 1-31 for MONTHLY
    cron_expression: Optional[str] = None  # For CUSTOM
    filters: Optional[Dict] = {}
    recipients: Optional[List[str]] = []
    is_active: bool = True


@router.get("/reports/templates")
async def list_templates(
    current_user: User = Depends(require_permission(Permission.AUDIT_READ)),
    db: Session = Depends(get_db)
):
    """List available report templates"""
    try:
        templates = TemplateLibrary.get_all_templates()
        
        return {
            "success": True,
            "data": {
                "templates": [
                    {
                        "template_id": t.template_id,
                        "name": t.name,
                        "report_type": t.report_type.value,
                        "description": t.description,
                        "sections": [s.get("title") for s in t.sections]
                    }
                    for t in templates
                ],
                "total": len(templates)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reports/generate")
async def generate_report(
    request: ReportGenerateRequest,
    current_user: User = Depends(require_permission(Permission.AUDIT_READ)),
    db: Session = Depends(get_db)
):
    """
    Generate a report on-demand
    
    This creates a report immediately based on current data
    """
    try:
        # Get template
        templates = TemplateLibrary.get_all_templates()
        template = next(
            (t for t in templates if t.template_id == request.template_id),
            None
        )
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Gather data
        from app.reports.scheduler import ReportScheduler
        scheduler = ReportScheduler()
        report_data = await scheduler._gather_report_data(
            current_user.organization_id,
            request.filters,
            db
        )
        
        report_data["generated_by"] = current_user.email
        report_data["report_title"] = request.name
        report_data["report_id"] = f"RPT-{db.query(Report).count() + 1:08d}"
        
        # Generate report content based on format
        if request.format == ReportFormat.PDF:
            from app.reports.pdf_generator import pdf_generator
            
            # Determine report type and generate appropriate PDF
            if template.report_type == ReportType.EXECUTIVE_SUMMARY:
                content = pdf_generator.generate_executive_report(report_data)
            elif template.report_type == ReportType.TECHNICAL_DETAILED:
                content = pdf_generator.generate_technical_report(report_data)
            elif template.report_type == ReportType.COMPLIANCE_AUDIT:
                content = pdf_generator.generate_compliance_report(report_data)
            else:
                # Fallback to technical report
                content = pdf_generator.generate_technical_report(report_data)
            
            # Store binary content
            content_to_store = None  # Binary PDF stored separately
        else:
            # Use template renderer for other formats
            content = template.render(report_data, format=request.format)
            content_to_store = content
        
        # Save to database
        report_count = db.query(Report).count()
        report_id = f"RPT-{report_count + 1:08d}"
        
        report = Report(
            report_id=report_id,
            organization_id=current_user.organization_id,
            audit_id=None,
            report_type=template.report_type.value,
            name=request.name,
            format=request.format.value,
            content=content,
            metadata={
                "template_id": request.template_id,
                "filters": request.filters
            },
            generated_by=current_user.email,
            file_path=f"reports/{report_id}.{request.format.value}"
        )
        
        db.add(report)
        db.commit()
        db.refresh(report)
        
        # Log
        log = SecurityAuditLog(
            log_id=generate_log_id(db),
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            event_type="REPORT",
            action="GENERATE",
            result="SUCCESS",
            resource_type="report",
            resource_id=report_id,
            details={"template_id": request.template_id, "name": request.name},
            ip_address="",
            user_agent=""
        )
        db.add(log)
        db.commit()
        
        return {
            "success": True,
            "data": {
                "report_id": report_id,
                "name": report.name,
                "format": report.format,
                "file_path": report.file_path,
                "generated_at": report.generated_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports")
async def list_reports(
    current_user: User = Depends(require_permission(Permission.AUDIT_READ)),
    db: Session = Depends(get_db),
    report_type: Optional[str] = None,
    limit: int = Query(50, le=100)
):
    """List generated reports"""
    try:
        query = db.query(Report).filter(
            Report.organization_id == current_user.organization_id
        )
        
        if report_type:
            query = query.filter(Report.report_type == report_type)
        
        reports = query.order_by(desc(Report.generated_at)).limit(limit).all()
        
        return {
            "success": True,
            "data": {
                "reports": [
                    {
                        "report_id": r.report_id,
                        "name": r.name,
                        "report_type": r.report_type,
                        "format": r.format,
                        "generated_by": r.generated_by,
                        "generated_at": r.generated_at.isoformat(),
                        "file_path": r.file_path
                    }
                    for r in reports
                ],
                "total": len(reports)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/{report_id}")
async def get_report(
    report_id: str,
    current_user: User = Depends(require_permission(Permission.AUDIT_READ)),
    db: Session = Depends(get_db)
):
    """Get report content"""
    try:
        report = db.query(Report).filter(
            Report.report_id == report_id,
            Report.organization_id == current_user.organization_id
        ).first()
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return {
            "success": True,
            "data": {
                "report_id": report.report_id,
                "name": report.name,
                "report_type": report.report_type,
                "format": report.format,
                "content": report.content,
                "metadata": report.report_metadata,  # Updated to use report_metadata
                "generated_by": report.generated_by,
                "generated_at": report.generated_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reports/scheduled")
async def create_scheduled_report(
    request: ScheduledReportCreate,
    current_user: User = Depends(require_permission(Permission.SYSTEM_ADMIN)),
    db: Session = Depends(get_db)
):
    """Create a scheduled report"""
    try:
        # Parse time
        hour, minute = map(int, request.schedule_time.split(":"))
        schedule_time = time(hour=hour, minute=minute)
        
        # Generate ID
        count = db.query(ScheduledReport).filter(
            ScheduledReport.organization_id == current_user.organization_id
        ).count()
        schedule_id = f"SCH-{count + 1:06d}"
        
        # Create scheduled report
        scheduled_report = ScheduledReport(
            schedule_id=schedule_id,
            organization_id=current_user.organization_id,
            name=request.name,
            template_id=request.template_id,
            report_type=request.report_type.value,
            format=request.format.value,
            schedule_type=request.schedule_type,
            schedule_time=schedule_time,
            schedule_day_of_week=request.schedule_day_of_week,
            schedule_day_of_month=request.schedule_day_of_month,
            cron_expression=request.cron_expression,
            filters=request.filters,
            recipients=request.recipients,
            is_active=request.is_active,
            created_by=current_user.email,
            run_count=0
        )
        
        db.add(scheduled_report)
        db.commit()
        db.refresh(scheduled_report)
        
        # Add to scheduler
        if scheduled_report.is_active:
            report_scheduler.schedule_report(
                schedule_id,
                scheduled_report,
                db
            )
        
        # Log
        log = SecurityAuditLog(
            log_id=generate_log_id(db),
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            event_type="REPORT",
            action="SCHEDULE",
            result="SUCCESS",
            resource_type="scheduled_report",
            resource_id=schedule_id,
            details={"name": request.name, "schedule_type": request.schedule_type},
            ip_address="",
            user_agent=""
        )
        db.add(log)
        db.commit()
        
        return {
            "success": True,
            "data": {
                "schedule_id": schedule_id,
                "name": scheduled_report.name,
                "schedule_type": scheduled_report.schedule_type,
                "is_active": scheduled_report.is_active
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/scheduled")
async def list_scheduled_reports(
    current_user: User = Depends(require_permission(Permission.AUDIT_READ)),
    db: Session = Depends(get_db)
):
    """List scheduled reports"""
    try:
        scheduled = db.query(ScheduledReport).filter(
            ScheduledReport.organization_id == current_user.organization_id
        ).order_by(desc(ScheduledReport.created_at)).all()
        
        return {
            "success": True,
            "data": {
                "scheduled_reports": [
                    {
                        "schedule_id": s.schedule_id,
                        "name": s.name,
                        "report_type": s.report_type,
                        "schedule_type": s.schedule_type,
                        "schedule_time": s.schedule_time.strftime("%H:%M"),
                        "is_active": s.is_active,
                        "run_count": s.run_count,
                        "last_run_at": s.last_run_at.isoformat() if s.last_run_at else None,
                        "created_at": s.created_at.isoformat()
                    }
                    for s in scheduled
                ],
                "total": len(scheduled)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/reports/scheduled/{schedule_id}")
async def update_scheduled_report(
    schedule_id: str,
    is_active: bool,
    current_user: User = Depends(require_permission(Permission.SYSTEM_ADMIN)),
    db: Session = Depends(get_db)
):
    """Activate/deactivate scheduled report"""
    try:
        scheduled = db.query(ScheduledReport).filter(
            ScheduledReport.schedule_id == schedule_id,
            ScheduledReport.organization_id == current_user.organization_id
        ).first()
        
        if not scheduled:
            raise HTTPException(status_code=404, detail="Scheduled report not found")
        
        scheduled.is_active = is_active
        db.commit()
        
        # Update scheduler
        if is_active:
            report_scheduler.schedule_report(schedule_id, scheduled, db)
        else:
            report_scheduler.unschedule_report(schedule_id)
        
        return {
            "success": True,
            "data": {
                "schedule_id": schedule_id,
                "is_active": is_active
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/reports/{report_id}")
async def delete_report(
    report_id: str,
    current_user: User = Depends(require_permission(Permission.SYSTEM_ADMIN)),
    db: Session = Depends(get_db)
):
    """Delete a report"""
    try:
        report = db.query(Report).filter(
            Report.report_id == report_id,
            Report.organization_id == current_user.organization_id
        ).first()
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        db.delete(report)
        db.commit()
        
        return {
            "success": True,
            "data": {
                "report_id": report_id,
                "message": "Report deleted successfully"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/reports/{report_id}/download")
async def download_report(
    report_id: str,
    current_user: User = Depends(require_permission(Permission.AUDIT_READ)),
    db: Session = Depends(get_db)
):
    """
    Download report file (PDF/HTML/CSV)
    
    Returns the actual report file for download
    """
    from fastapi.responses import Response
    import os
    
    try:
        report = db.query(Report).filter(
            Report.report_id == report_id,
            Report.organization_id == current_user.organization_id
        ).first()
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # For PDF reports, regenerate if not stored
        if report.format == "pdf" or report.format == "PDF":
            from app.reports.pdf_generator import pdf_generator
            from app.reports.scheduler import ReportScheduler
            
            # Gather data again
            scheduler = ReportScheduler()
            report_data = await scheduler._gather_report_data(
                current_user.organization_id,
                report.metadata.get("filters", {}),
                db
            )
            
            report_data["report_title"] = report.name
            report_data["report_id"] = report.report_id
            report_data["generated_by"] = report.generated_by
            
            # Generate PDF based on report type
            if report.report_type == "executive_summary":
                content = pdf_generator.generate_executive_report(report_data)
            elif report.report_type == "technical_detailed":
                content = pdf_generator.generate_technical_report(report_data)
            elif report.report_type == "compliance_audit":
                content = pdf_generator.generate_compliance_report(report_data)
            else:
                content = pdf_generator.generate_technical_report(report_data)
            
            # Return PDF
            return Response(
                content=content,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename={report_id}.pdf"
                }
            )
        
        elif report.format == "html" or report.format == "HTML":
            # Return HTML content
            return Response(
                content=report.content,
                media_type="text/html",
                headers={
                    "Content-Disposition": f"attachment; filename={report_id}.html"
                }
            )
        
        elif report.format == "json" or report.format == "JSON":
            # Return JSON content
            return Response(
                content=report.content,
                media_type="application/json",
                headers={
                    "Content-Disposition": f"attachment; filename={report_id}.json"
                }
            )
        
        else:
            # Default: return as text
            return Response(
                content=report.content or "",
                media_type="text/plain",
                headers={
                    "Content-Disposition": f"attachment; filename={report_id}.txt"
                }
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
