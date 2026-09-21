"""
Findings API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db, Audit, Finding, Configuration, User
from app.auth.dependencies import require_permission
from app.auth.permissions import Permission

router = APIRouter()


@router.get("/audits/{audit_id}/findings")
async def get_findings(
    audit_id: str,
    current_user: User = Depends(require_permission(Permission.FINDING_VIEW)),
    db: Session = Depends(get_db)
):
    """
    Get findings for an audit with evidence and remediation
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
        
        # Get findings
        findings = db.query(Finding).filter(Finding.audit_id == audit.id).all()
        
        findings_data = []
        for finding in findings:
            findings_data.append({
                "finding_id": finding.finding_id,
                "rule_id": finding.rule_id,
                "title": finding.title,
                "description": finding.description,
                "status": finding.status,
                "severity": finding.severity,
                "expected": finding.expected,
                "actual": finding.actual,
                "field_path": finding.field_path,
                "evidence": {
                    "file": finding.evidence_file,
                    "line": finding.evidence_line,
                    "text": finding.evidence_text
                } if finding.evidence_file else None,
                "risk_score": finding.risk_score,
                "remediation": finding.remediation,
                "created_at": finding.created_at.isoformat()
            })
        
        return {
            "success": True,
            "data": {
                "audit_id": audit.audit_id,
                "findings": findings_data,
                "total": len(findings_data)
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
                    "message": "Failed to retrieve findings"
                }
            }
        )
