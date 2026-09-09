"""
Audit execution API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db, Configuration, Audit, Finding
from app.findings import run_configuration_audit
from app.reports import generate_audit_report

router = APIRouter()


@router.get("/audits/review-queue")
async def get_audits_needing_review(
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
        audits = db.query(Audit).filter(
            Audit.requires_human_review == True
        ).order_by(Audit.started_at.desc()).all()
        
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
        # Check if configuration exists
        config = db.query(Configuration).filter(
            Configuration.config_id == config_id
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
    db: Session = Depends(get_db)
):
    """
    Get audit details
    """
    try:
        audit = db.query(Audit).filter(Audit.audit_id == audit_id).first()
        
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
    db: Session = Depends(get_db)
):
    """
    Get dashboard summary statistics
    """
    try:
        # Count configurations
        total_configs = db.query(Configuration).count()
        
        # Count audits
        total_audits = db.query(Audit).count()
        
        # Calculate average compliance score
        avg_compliance = db.query(func.avg(Audit.compliance_score)).filter(
            Audit.status == "COMPLETED"
        ).scalar() or 0
        
        # Count findings by severity
        critical = db.query(Finding).filter(
            Finding.severity == "CRITICAL",
            Finding.status == "FAIL"
        ).count()
        
        high = db.query(Finding).filter(
            Finding.severity == "HIGH",
            Finding.status == "FAIL"
        ).count()
        
        medium = db.query(Finding).filter(
            Finding.severity == "MEDIUM",
            Finding.status == "FAIL"
        ).count()
        
        low = db.query(Finding).filter(
            Finding.severity == "LOW",
            Finding.status == "FAIL"
        ).count()
        
        # Count passed controls
        passed = db.query(Finding).filter(Finding.status == "PASS").count()
        
        # Vendor distribution
        vendor_dist = db.query(
            Configuration.vendor,
            func.count(Configuration.id)
        ).group_by(Configuration.vendor).all()
        
        vendor_distribution = {vendor: count for vendor, count in vendor_dist if vendor}
        
        # Count audits needing human review
        audits_needing_review = db.query(Audit).filter(
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
        # Check if audit exists
        audit = db.query(Audit).filter(Audit.audit_id == audit_id).first()
        
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
        pdf_buffer = generate_audit_report(audit_id)
        
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

