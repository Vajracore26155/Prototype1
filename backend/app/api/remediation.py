"""
Remediation Management API
Phase 5: Remediation plans and approval workflow
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.database import (
    get_db, RemediationPlan, RemediationApproval, User, 
    Device, Audit, Finding, SecurityAuditLog
)
from app.auth.dependencies import require_permission
from app.auth.permissions import Permission

router = APIRouter()


def generate_log_id(db: Session) -> str:
    """Generate unique audit log ID"""
    count = db.query(SecurityAuditLog).count()
    return f"LOG-{count + 1:08d}"


class RemediationPlanCreate(BaseModel):
    """Create remediation plan"""
    device_id: Optional[str] = None
    audit_id: Optional[str] = None
    drift_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    finding_ids: Optional[List[str]] = []
    remediation_commands: str
    rollback_commands: Optional[str] = None
    estimated_impact: str = "MEDIUM"  # LOW, MEDIUM, HIGH
    estimated_downtime: Optional[str] = None
    requires_approval: bool = True


class RemediationApprovalRequest(BaseModel):
    """Approve or reject remediation"""
    decision: str  # APPROVE, REJECT, REQUEST_CHANGES
    comments: Optional[str] = None


@router.post("/remediation/plans")
async def create_remediation_plan(
    plan: RemediationPlanCreate,
    current_user: User = Depends(require_permission(Permission.REMEDIATION_APPROVE)),
    db: Session = Depends(get_db)
):
    """
    Create a remediation plan
    """
    try:
        # Validate device if provided
        device_pk = None
        if plan.device_id:
            device = db.query(Device).filter(
                Device.device_id == plan.device_id,
                Device.organization_id == current_user.organization_id
            ).first()
            if device:
                device_pk = device.id
        
        # Generate plan_id
        plan_count = db.query(RemediationPlan).filter(
            RemediationPlan.organization_id == current_user.organization_id
        ).count()
        plan_id = f"REM-{plan_count + 1:06d}"
        
        # Create plan
        new_plan = RemediationPlan(
            plan_id=plan_id,
            organization_id=current_user.organization_id,
            device_id=device_pk,
            title=plan.title,
            description=plan.description,
            finding_ids=plan.finding_ids,
            remediation_commands=plan.remediation_commands,
            rollback_commands=plan.rollback_commands,
            estimated_impact=plan.estimated_impact,
            estimated_downtime=plan.estimated_downtime,
            requires_approval=plan.requires_approval,
            status="DRAFT" if plan.requires_approval else "APPROVED",
            created_by=current_user.email
        )
        
        db.add(new_plan)
        db.commit()
        db.refresh(new_plan)
        
        # Log
        log = SecurityAuditLog(
            log_id=generate_log_id(db),
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            event_type="REMEDIATION",
            action="CREATE",
            result="SUCCESS",
            resource_type="remediation",
            resource_id=plan_id,
            details={"message": f"Created remediation plan: {plan.title}", "title": plan.title},
            ip_address="",
            user_agent=""
        )
        db.add(log)
        db.commit()
        
        return {
            "success": True,
            "data": {
                "plan_id": plan_id,
                "status": new_plan.status,
                "requires_approval": new_plan.requires_approval
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/remediation/plans")
async def list_remediation_plans(
    current_user: User = Depends(require_permission(Permission.REMEDIATION_READ)),
    db: Session = Depends(get_db),
    status: Optional[str] = None,
    device_id: Optional[str] = None,
    limit: int = 50
):
    """
    List remediation plans
    """
    try:
        query = db.query(RemediationPlan).filter(
            RemediationPlan.organization_id == current_user.organization_id
        )
        
        if status:
            query = query.filter(RemediationPlan.status == status)
        
        if device_id:
            device = db.query(Device).filter(
                Device.device_id == device_id,
                Device.organization_id == current_user.organization_id
            ).first()
            if device:
                query = query.filter(RemediationPlan.device_id == device.id)
        
        plans = query.order_by(RemediationPlan.created_at.desc()).limit(limit).all()
        
        return {
            "success": True,
            "data": {
                "plans": [
                    {
                        "plan_id": p.plan_id,
                        "title": p.title,
                        "status": p.status,
                        "estimated_impact": p.estimated_impact,
                        "requires_approval": p.requires_approval,
                        "created_by": p.created_by,
                        "created_at": p.created_at.isoformat()
                    }
                    for p in plans
                ],
                "total": len(plans)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/remediation/plans/{plan_id}")
async def get_remediation_plan(
    plan_id: str,
    current_user: User = Depends(require_permission(Permission.REMEDIATION_READ)),
    db: Session = Depends(get_db)
):
    """
    Get remediation plan details
    """
    try:
        plan = db.query(RemediationPlan).filter(
            RemediationPlan.plan_id == plan_id,
            RemediationPlan.organization_id == current_user.organization_id
        ).first()
        
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        # Get device info if exists
        device_info = None
        if plan.device_id:
            device = db.query(Device).filter(Device.id == plan.device_id).first()
            if device:
                device_info = {
                    "device_id": device.device_id,
                    "hostname": device.hostname
                }
        
        # Get approvals
        approvals = db.query(RemediationApproval).filter(
            RemediationApproval.plan_id == plan.id
        ).all()
        
        return {
            "success": True,
            "data": {
                "plan_id": plan.plan_id,
                "title": plan.title,
                "description": plan.description,
                "device": device_info,
                "finding_ids": plan.finding_ids,
                "remediation_commands": plan.remediation_commands,
                "rollback_commands": plan.rollback_commands,
                "estimated_impact": plan.estimated_impact,
                "estimated_downtime": plan.estimated_downtime,
                "status": plan.status,
                "requires_approval": plan.requires_approval,
                "created_by": plan.created_by,
                "created_at": plan.created_at.isoformat(),
                "approved_by": plan.approved_by,
                "approved_at": plan.approved_at.isoformat() if plan.approved_at else None,
                "applied_at": plan.applied_at.isoformat() if plan.applied_at else None,
                "approvals": [
                    {
                        "decision": a.decision,
                        "comments": a.comments,
                        "created_at": a.created_at.isoformat()
                    }
                    for a in approvals
                ]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/remediation/plans/{plan_id}/approve")
async def approve_remediation_plan(
    plan_id: str,
    request: RemediationApprovalRequest,
    current_user: User = Depends(require_permission(Permission.REMEDIATION_APPROVE)),
    db: Session = Depends(get_db)
):
    """
    Approve or reject remediation plan
    """
    try:
        plan = db.query(RemediationPlan).filter(
            RemediationPlan.plan_id == plan_id,
            RemediationPlan.organization_id == current_user.organization_id
        ).first()
        
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        if plan.status not in ["PENDING_APPROVAL", "DRAFT"]:
            raise HTTPException(status_code=400, detail=f"Cannot approve plan in {plan.status} status")
        
        # Create approval record
        approval = RemediationApproval(
            plan_id=plan.id,
            approver_id=current_user.id,
            decision=request.decision,
            comments=request.comments
        )
        db.add(approval)
        
        # Update plan status
        if request.decision == "APPROVE":
            plan.status = "APPROVED"
            plan.approved_by = current_user.email
            plan.approved_at = datetime.utcnow()
        elif request.decision == "REJECT":
            plan.status = "REJECTED"
            plan.rejected_by = current_user.email
            plan.rejected_at = datetime.utcnow()
            plan.rejection_reason = request.comments
        elif request.decision == "REQUEST_CHANGES":
            plan.status = "DRAFT"
        
        db.commit()
        
        # Log
        log = SecurityAuditLog(
            log_id=generate_log_id(db),
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            event_type="REMEDIATION",
            action=request.decision,
            result="SUCCESS",
            resource_type="remediation",
            resource_id=plan_id,
            details={"decision": request.decision, "title": plan.title, "comments": request.comments},
            ip_address="",
            user_agent=""
        )
        db.add(log)
        db.commit()
        
        return {
            "success": True,
            "data": {
                "plan_id": plan_id,
                "status": plan.status,
                "decision": request.decision
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/remediation/pending-approvals")
async def get_pending_approvals(
    current_user: User = Depends(require_permission(Permission.REMEDIATION_APPROVE)),
    db: Session = Depends(get_db)
):
    """
    Get remediation plans pending approval
    """
    try:
        plans = db.query(RemediationPlan).filter(
            RemediationPlan.organization_id == current_user.organization_id,
            RemediationPlan.status.in_(["DRAFT", "PENDING_APPROVAL"]),
            RemediationPlan.requires_approval == True
        ).order_by(RemediationPlan.created_at).all()
        
        return {
            "success": True,
            "data": {
                "pending": [
                    {
                        "plan_id": p.plan_id,
                        "title": p.title,
                        "estimated_impact": p.estimated_impact,
                        "created_by": p.created_by,
                        "created_at": p.created_at.isoformat()
                    }
                    for p in plans
                ],
                "total": len(plans)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
