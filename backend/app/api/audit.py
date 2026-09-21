"""
Audit execution API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from io import BytesIO

from app.database import get_db, Configuration, Audit, Finding, User, SecurityAuditLog, Organization
from app.findings import run_configuration_audit
from app.auth.dependencies import require_permission
from app.auth.permissions import Permission
from app.reports.pdf_generator import PDFReportGenerator

router = APIRouter()


def generate_log_id(db: Session) -> str:
    """Generate unique audit log ID"""
    count = db.query(SecurityAuditLog).count()
    return f"LOG-{count + 1:06d}"


def generate_audit_report(audit_id: str, db: Session) -> BytesIO:
    """
    Generate PDF report for an audit
    
    Args:
        audit_id: Audit ID to generate report for
        db: Database session
        
    Returns:
        BytesIO buffer containing PDF content
    """
    from datetime import datetime
    from app.database import Organization
    
    # Get audit with all data
    audit = db.query(Audit).filter(Audit.audit_id == audit_id).first()
    if not audit:
        raise ValueError(f"Audit {audit_id} not found")
    
    # Get configuration
    config = db.query(Configuration).filter(Configuration.id == audit.configuration_id).first()
    
    # Get organization
    org = db.query(Organization).filter(Organization.id == config.organization_id).first() if config else None
    
    # Get findings
    findings = db.query(Finding).filter(Finding.audit_id == audit.id).all()
    
    # Count findings by severity
    critical_findings = [f for f in findings if f.severity == "CRITICAL" and f.status == "FAIL"]
    high_findings = [f for f in findings if f.severity == "HIGH" and f.status == "FAIL"]
    medium_findings = [f for f in findings if f.severity == "MEDIUM" and f.status == "FAIL"]
    low_findings = [f for f in findings if f.severity == "LOW" and f.status == "FAIL"]
    
    # Prepare data for PDF generator
    report_data = {
        "report_title": "Security Audit Report",
        "report_id": f"RPT-{audit.audit_id}",
        "audit_id": audit.audit_id,
        "config_id": config.config_id if config else "Unknown",
        "config_filename": config.original_filename if config else "Unknown",
        "vendor": config.vendor if config else "Unknown",
        "audit_date": audit.completed_at.strftime("%Y-%m-%d %H:%M:%S") if audit.completed_at else audit.started_at.strftime("%Y-%m-%d %H:%M:%S"),
        "compliance_score": audit.compliance_score or 0,
        "risk_score": audit.risk_score or 0,
        "risk_level": audit.risk_level or "UNKNOWN",
        "passed_count": audit.passed_count or 0,
        "failed_count": audit.failed_count or 0,
        "warning_count": audit.warning_count or 0,
        "total_findings": len(findings),
        "metadata": {
            "organization_name": org.name if org else "Unknown Organization",
            "assessment_period": audit.started_at.strftime("%B %d, %Y") if audit.started_at else datetime.utcnow().strftime("%B %d, %Y"),
            "generated_by": "VAJRA CORE System"
        },
        "findings": [
            {
                "finding_id": f.finding_id,
                "rule_id": f.rule_id,
                "title": f.title,
                "description": f.description or "No description available",
                "severity": f.severity,
                "status": f.status,
                "expected": f.expected or "N/A",
                "actual": f.actual or "N/A",
                "field_path": f.field_path or "",
                "evidence": f.evidence_text if hasattr(f, 'evidence_text') else "",
                "remediation": f.remediation or "No remediation guidance available",
                "risk_score": f.risk_score if hasattr(f, 'risk_score') else 0
            }
            for f in findings
        ],
        "findings_by_severity": {
            "critical": len(critical_findings),
            "high": len(high_findings),
            "medium": len(medium_findings),
            "low": len(low_findings)
        },
        "summary": {
            "total_controls_assessed": len(findings),
            "passed": audit.passed_count or 0,
            "failed": audit.failed_count or 0,
            "warnings": audit.warning_count or 0,
            "compliance_percentage": audit.compliance_score or 0,
            "risk_level": audit.risk_level or "UNKNOWN"
        }
    }
    
    # Generate PDF
    pdf_gen = PDFReportGenerator()
    pdf_bytes = pdf_gen.generate_technical_report(report_data)
    
    # Return as BytesIO buffer
    return BytesIO(pdf_bytes)


@router.get("/audits/review-queue")
async def get_audits_needing_review(
    current_user: User = Depends(require_permission(Permission.AUDIT_VIEW)),
    db: Session = Depends(get_db)
):
    """
    Get all audits that require human review
    
    Returns audits flagged for manual validation due to:
    - Low interpretation confidence
    - Many uninterpreted lines
    - Pending AI mappings requiring approval
    """
    try:
        # Filter by organization for multi-tenancy
        query = db.query(Audit).join(
            Configuration, Audit.configuration_id == Configuration.id
        ).filter(
            Configuration.organization_id == current_user.organization_id,
            Audit.requires_human_review == True
        ).order_by(Audit.started_at.desc())
        
        audits = query.all()
        
        result = []
        for audit in audits:
            # Get configuration info
            config = db.query(Configuration).filter(
                Configuration.id == audit.configuration_id
            ).first()
            
            result.append({
                "audit_id": audit.audit_id,
                "configuration_id": config.config_id if config else None,
                "filename": config.original_filename if config else None,
                "vendor": config.vendor if config else None,
                "status": audit.status,
                "review_reason": audit.review_reason,
                "interpretation_confidence": audit.interpretation_confidence,
                "uninterpreted_lines": audit.uninterpreted_lines_count,
                "total_lines": audit.total_lines_count,
                "pending_mappings": audit.pending_mappings_count,
                "started_at": audit.started_at.isoformat(),
                "compliance_score": audit.compliance_score,
                "risk_level": audit.risk_level
            })
        
        return {
            "success": True,
            "data": {
                "total": len(result),
                "audits": result
            }
        }
        
    except Exception as e:
        print(f"Review queue error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "QUEUE_FAILED",
                    "message": "Failed to retrieve review queue"
                }
            }
        )


@router.post("/audits/{config_id}/run")
async def run_audit(
    config_id: str,
    current_user: User = Depends(require_permission(Permission.AUDIT_RUN)),
    db: Session = Depends(get_db)
):
    """
    Run security audit on a configuration
    
    Executes complete audit pipeline:
    1. Parse configuration
    2. Normalize to Unified Security Model
    3. Evaluate compliance rules
    4. Calculate risk
    5. Generate findings with evidence
    6. Create remediation commands
    """
    try:
        # Check if configuration exists and belongs to user's organization
        config = db.query(Configuration).filter(
            Configuration.config_id == config_id,
            Configuration.organization_id == current_user.organization_id
        ).first()
        
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
        
        # Run audit
        audit = run_configuration_audit(config_id)
        
        # Log security event
        log = SecurityAuditLog(
            log_id=generate_log_id(db),
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            event_type="AUDIT",
            action="EXECUTE",
            result="SUCCESS",
            resource_type="audit",
            resource_id=audit.audit_id,
            details={"config_id": config_id, "audit_id": audit.audit_id},
            ip_address="",  # Will be filled by middleware
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
                "message": "Audit completed successfully"
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


@router.get("/audits/{audit_id}")
async def get_audit(
    audit_id: str,
    current_user: User = Depends(require_permission(Permission.AUDIT_VIEW)),
    db: Session = Depends(get_db)
):
    """
    Get audit details
    """
    try:
        # Get audit with organization check
        audit = db.query(Audit).join(
            Configuration, Audit.configuration_id == Configuration.id
        ).filter(
            Audit.audit_id == audit_id,
            Configuration.organization_id == current_user.organization_id
        ).first()
        
        if not audit:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Audit {audit_id} not found"
                    }
                }
            )
        
        # Get configuration
        config = db.query(Configuration).filter(
            Configuration.id == audit.configuration_id
        ).first()
        
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
                # Human review metadata
                "requires_human_review": audit.requires_human_review,
                "review_reason": audit.review_reason,
                "interpretation_confidence": audit.interpretation_confidence,
                "uninterpreted_lines": audit.uninterpreted_lines_count,
                "total_lines": audit.total_lines_count,
                "pending_mappings": audit.pending_mappings_count
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


@router.get("/dashboard/summary")
async def get_dashboard_summary(
    current_user: User = Depends(require_permission(Permission.AUDIT_VIEW)),
    db: Session = Depends(get_db)
):
    """
    Get dashboard summary statistics
    """
    try:
        # Count configurations in organization
        total_configs = db.query(Configuration).filter(
            Configuration.organization_id == current_user.organization_id
        ).count()
        
        # Count audits for organization
        total_audits = db.query(Audit).join(
            Configuration, Audit.configuration_id == Configuration.id
        ).filter(
            Configuration.organization_id == current_user.organization_id
        ).count()
        
        # Calculate average compliance score for organization
        avg_compliance = db.query(func.avg(Audit.compliance_score)).join(
            Configuration, Audit.configuration_id == Configuration.id
        ).filter(
            Audit.status == "COMPLETED",
            Configuration.organization_id == current_user.organization_id
        ).scalar() or 0
        
        # Count findings by severity for organization
        base_finding_query = db.query(Finding).join(
            Audit, Finding.audit_id == Audit.id
        ).join(
            Configuration, Audit.configuration_id == Configuration.id
        ).filter(
            Configuration.organization_id == current_user.organization_id
        )
        
        critical = base_finding_query.filter(
            Finding.severity == "CRITICAL",
            Finding.status == "FAIL"
        ).count()
        
        high = base_finding_query.filter(
            Finding.severity == "HIGH",
            Finding.status == "FAIL"
        ).count()
        
        medium = base_finding_query.filter(
            Finding.severity == "MEDIUM",
            Finding.status == "FAIL"
        ).count()
        
        low = base_finding_query.filter(
            Finding.severity == "LOW",
            Finding.status == "FAIL"
        ).count()
        
        # Count passed controls
        passed = base_finding_query.filter(Finding.status == "PASS").count()
        
        # Vendor distribution for organization
        vendor_dist = db.query(
            Configuration.vendor,
            func.count(Configuration.id)
        ).filter(
            Configuration.organization_id == current_user.organization_id
        ).group_by(Configuration.vendor).all()
        
        vendor_distribution = {vendor: count for vendor, count in vendor_dist if vendor}
        
        # Count audits needing human review for organization
        audits_needing_review = db.query(Audit).join(
            Configuration, Audit.configuration_id == Configuration.id
        ).filter(
            Configuration.organization_id == current_user.organization_id,
            Audit.requires_human_review == True
        ).count()
        
        return {
            "success": True,
            "data": {
                "total_configs": total_configs,
                "total_audits": total_audits,
                "compliance_score": round(avg_compliance, 2),
                "critical_findings": critical,
                "high_findings": high,
                "medium_findings": medium,
                "low_findings": low,
                "passed_controls": passed,
                "vendor_distribution": vendor_distribution,
                "audits_needing_review": audits_needing_review
            }
        }
        
    except Exception as e:
        print(f"Dashboard summary error: {str(e)}")
        # Return zeros if there's an error
        return {
            "success": True,
            "data": {
                "total_configs": 0,
                "total_audits": 0,
                "compliance_score": 0,
                "critical_findings": 0,
                "high_findings": 0,
                "medium_findings": 0,
                "low_findings": 0,
                "passed_controls": 0,
                "vendor_distribution": {},
                "audits_needing_review": 0
            }
        }


@router.get("/audits/{audit_id}/report")
async def download_audit_report(
    audit_id: str,
    current_user: User = Depends(require_permission(Permission.REPORT_VIEW)),
    db: Session = Depends(get_db)
):
    """
    Generate and download PDF report for an audit
    
    Returns a professionally formatted PDF report including:
    - Executive summary
    - Compliance scores and risk analysis
    - Detailed findings with evidence
    - Remediation recommendations
    - Human intervention alerts (if applicable)
    """
    try:
        # Check if audit exists and belongs to organization
        audit = db.query(Audit).join(
            Configuration, Audit.configuration_id == Configuration.id
        ).filter(
            Audit.audit_id == audit_id,
            Configuration.organization_id == current_user.organization_id
        ).first()
        
        if not audit:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Audit {audit_id} not found"
                    }
                }
            )
        
        # Get configuration for filename
        config = db.query(Configuration).filter(
            Configuration.id == audit.configuration_id
        ).first()
        
        # Generate PDF report
        pdf_buffer = generate_audit_report(audit_id, db)
        
        # Log security event
        log = SecurityAuditLog(
            log_id=generate_log_id(db),
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            event_type="REPORT",
            action="DOWNLOAD",
            result="SUCCESS",
            resource_type="audit",
            resource_id=audit_id,
            details={"audit_id": audit_id, "report_type": "pdf"},
            ip_address="",
            user_agent=""
        )
        db.add(log)
        db.commit()
        
        # Create filename
        config_name = config.original_filename.replace('.', '_') if config else 'unknown'
        filename = f"audit_report_{audit_id}_{config_name}.pdf"
        
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
        print(f"PDF generation error: {str(e)}")
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

