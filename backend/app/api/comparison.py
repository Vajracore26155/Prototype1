"""
Configuration Comparison API - Deviation Analysis
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db, User, Audit, Configuration
from app.deviation import DeviationEngine
from app.auth.dependencies import require_permission
from app.auth.permissions import Permission

router = APIRouter()


@router.post("/comparisons/audits")
async def compare_audits(
    baseline_audit_id: str,
    current_audit_id: str,
    current_user: User = Depends(require_permission(Permission.AUDIT_VIEW)),
    db: Session = Depends(get_db)
):
    """
    Compare two audits to detect security configuration deviations
    
    Use cases:
    - Before/after remediation validation
    - Configuration drift detection
    - Change impact analysis
    
    SECURITY: Requires AUDIT_VIEW permission and organization ownership verification
    """
    try:
        # Verify both audits exist and belong to user's organization
        baseline_audit = db.query(Audit).join(
            Configuration, Audit.configuration_id == Configuration.id
        ).filter(
            Audit.audit_id == baseline_audit_id,
            Configuration.organization_id == current_user.organization_id
        ).first()
        
        if not baseline_audit:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Baseline audit {baseline_audit_id} not found or access denied"
                    }
                }
            )
        
        current_audit = db.query(Audit).join(
            Configuration, Audit.configuration_id == Configuration.id
        ).filter(
            Audit.audit_id == current_audit_id,
            Configuration.organization_id == current_user.organization_id
        ).first()
        
        if not current_audit:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Current audit {current_audit_id} not found or access denied"
                    }
                }
            )
        
        # Both audits verified - proceed with comparison
        engine = DeviationEngine()
        comparison = engine.compare_audits(baseline_audit_id, current_audit_id, db)
        
        return {
            "success": True,
            "data": comparison
        }
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": str(e)
                }
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "COMPARISON_FAILED",
                    "message": f"Failed to compare audits: {str(e)}"
                }
            }
        )


@router.post("/comparisons/configs")
async def compare_configurations(
    baseline_config_id: str,
    current_config_id: str,
    current_user: User = Depends(require_permission(Permission.CONFIG_READ)),
    db: Session = Depends(get_db)
):
    """
    Compare two configurations by running audits and comparing results
    
    Convenience endpoint that runs audits if needed
    
    SECURITY: Requires CONFIG_READ permission and organization ownership verification
    """
    try:
        from app.findings import run_configuration_audit
        
        # Verify configurations exist and belong to user's organization
        baseline_config = db.query(Configuration).filter(
            Configuration.config_id == baseline_config_id,
            Configuration.organization_id == current_user.organization_id
        ).first()
        
        if not baseline_config:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Baseline configuration {baseline_config_id} not found or access denied"
                    }
                }
            )
        
        current_config = db.query(Configuration).filter(
            Configuration.config_id == current_config_id,
            Configuration.organization_id == current_user.organization_id
        ).first()
        
        if not current_config:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Current configuration {current_config_id} not found or access denied"
                    }
                }
            )
        
        # Get or create audits (organization already verified through configs)
        baseline_audit = db.query(Audit).filter(
            Audit.configuration_id == baseline_config.id
        ).order_by(Audit.created_at.desc()).first()
        
        current_audit = db.query(Audit).filter(
            Audit.configuration_id == current_config.id
        ).order_by(Audit.created_at.desc()).first()
        
        # Run audits if not exist
        if not baseline_audit:
            baseline_audit = run_configuration_audit(baseline_config_id)
        if not current_audit:
            current_audit = run_configuration_audit(current_config_id)
        
        # Compare
        engine = DeviationEngine()
        comparison = engine.compare_audits(
            baseline_audit.audit_id,
            current_audit.audit_id,
            db
        )
        
        return {
            "success": True,
            "data": comparison
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "COMPARISON_FAILED",
                    "message": str(e)
                }
            }
        )
