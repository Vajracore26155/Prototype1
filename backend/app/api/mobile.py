"""
Mobile QR Session API
Phase 12: Secure mobile authentication and assessment view
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import and_
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import secrets
import hashlib

from app.database import (
    get_db, User, Device, Audit, Finding, PostureScore,
    DriftAnalysis, SecurityAuditLog
)
from app.auth.dependencies import get_current_user
from app.auth.permissions import Permission

router = APIRouter()


# ============================================================
# QR SESSION MODEL
# ============================================================

# In-memory QR session store (production would use Redis)
qr_sessions = {}


class QRSession:
    """QR session model"""
    
    def __init__(
        self,
        session_id: str,
        user_id: int,
        organization_id: int,
        device_id: Optional[str] = None
    ):
        self.session_id = session_id
        self.user_id = user_id
        self.organization_id = organization_id
        self.device_id = device_id
        self.created_at = datetime.utcnow()
        self.expires_at = datetime.utcnow() + timedelta(minutes=10)
        self.consumed = False
        self.revoked = False
    
    def is_valid(self) -> bool:
        """Check if session is still valid"""
        if self.revoked:
            return False
        if self.consumed:
            return False
        if datetime.utcnow() > self.expires_at:
            return False
        return True
    
    def consume(self):
        """Mark session as consumed"""
        self.consumed = True


# ============================================================
# QR SESSION GENERATION
# ============================================================

@router.post("/mobile/qr/generate")
async def generate_qr_session(
    device_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate secure QR session token
    
    Returns a short-lived, cryptographically secure session token
    that can be encoded in a QR code
    """
    try:
        # Generate cryptographically secure token
        token = secrets.token_urlsafe(32)
        session_id = hashlib.sha256(token.encode()).hexdigest()[:32]
        
        # Create session
        session = QRSession(
            session_id=session_id,
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            device_id=device_id
        )
        
        # Store session (in production, use Redis with TTL)
        qr_sessions[token] = session
        
        # Log
        log = SecurityAuditLog(
            log_id=f"LOG-{db.query(SecurityAuditLog).count() + 1:08d}",
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            event_type="MOBILE",
            action="QR_GENERATE",
            result="SUCCESS",
            resource_type="qr_session",
            resource_id=session_id,
            details={"device_id": device_id},
            ip_address="",
            user_agent=""
        )
        db.add(log)
        db.commit()
        
        return {
            "success": True,
            "data": {
                "token": token,
                "session_id": session_id,
                "expires_in": 600,  # 10 minutes
                "qr_url": f"/mobile/session?token={token}"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# QR SESSION VALIDATION
# ============================================================

@router.get("/mobile/session/validate")
async def validate_qr_session(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Validate QR session token
    
    Returns session info if valid
    """
    try:
        # Get session
        session = qr_sessions.get(token)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if not session.is_valid():
            status = "expired" if datetime.utcnow() > session.expires_at else "invalid"
            raise HTTPException(status_code=401, detail=f"Session {status}")
        
        # Get user info
        user = db.query(User).filter(User.id == session.user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "success": True,
            "data": {
                "session_id": session.session_id,
                "user_id": session.user_id,
                "organization_id": session.organization_id,
                "device_id": session.device_id,
                "expires_at": session.expires_at.isoformat(),
                "user": {
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# MOBILE AUTHENTICATION
# ============================================================

@router.post("/mobile/session/authenticate")
async def authenticate_mobile_session(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Authenticate mobile session
    
    Consumes the QR token and returns authenticated session
    """
    try:
        # Get session
        session = qr_sessions.get(token)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if not session.is_valid():
            raise HTTPException(status_code=401, detail="Session expired or invalid")
        
        # Consume session (single-use)
        session.consume()
        
        # Get user
        user = db.query(User).filter(User.id == session.user_id).first()
        
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="User not active")
        
        # Log
        log = SecurityAuditLog(
            log_id=f"LOG-{db.query(SecurityAuditLog).count() + 1:08d}",
            user_id=user.id,
            organization_id=session.organization_id,
            event_type="MOBILE",
            action="SESSION_AUTH",
            result="SUCCESS",
            resource_type="qr_session",
            resource_id=session.session_id,
            details={},
            ip_address="",
            user_agent=""
        )
        db.add(log)
        db.commit()
        
        return {
            "success": True,
            "data": {
                "session_id": session.session_id,
                "authenticated": True,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role,
                    "organization_id": user.organization_id
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# MOBILE DASHBOARD
# ============================================================

@router.get("/mobile/dashboard")
async def get_mobile_dashboard(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get mobile security dashboard
    
    Compact view optimized for mobile
    """
    try:
        # Get recent audit
        recent_audit = db.query(Audit).filter(
            Audit.organization_id == current_user.organization_id
        ).order_by(Audit.completed_at.desc()).first()
        
        # Get critical/high findings
        critical_findings = db.query(Finding).filter(
            and_(
                Finding.organization_id == current_user.organization_id,
                Finding.severity.in_(["CRITICAL", "HIGH"])
            )
        ).count()
        
        # Get posture
        latest_posture = db.query(PostureScore).filter(
            PostureScore.organization_id == current_user.organization_id
        ).order_by(PostureScore.calculated_at.desc()).first()
        
        # Get drift count
        unresolved_drift = db.query(DriftAnalysis).filter(
            and_(
                DriftAnalysis.organization_id == current_user.organization_id,
                DriftAnalysis.status == "DETECTED"
            )
        ).count()
        
        return {
            "success": True,
            "data": {
                "organization_id": current_user.organization_id,
                "latest_audit": {
                    "audit_id": recent_audit.audit_id if recent_audit else None,
                    "compliance_score": recent_audit.compliance_score if recent_audit else 0,
                    "risk_level": recent_audit.risk_level if recent_audit else "UNKNOWN",
                    "completed_at": recent_audit.completed_at.isoformat() if recent_audit and recent_audit.completed_at else None
                } if recent_audit else None,
                "critical_high_findings": critical_findings,
                "posture_score": latest_posture.current_score if latest_posture else 0,
                "unresolved_drift": unresolved_drift
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# MOBILE DEVICE VIEW
# ============================================================

@router.get("/mobile/device/{device_id}")
async def get_mobile_device(
    device_id: str,
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get device details for mobile view
    """
    try:
        # Get device
        device = db.query(Device).filter(
            and_(
                Device.device_id == device_id,
                Device.organization_id == current_user.organization_id
            )
        ).first()
        
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        # Get latest audit for this device
        latest_audit = db.query(Audit).filter(
            and_(
                Audit.organization_id == current_user.organization_id,
                # Would need device_id in Audit model for precise filtering
            )
        ).order_by(Audit.completed_at.desc()).first()
        
        # Get findings count
        findings_count = db.query(Finding).filter(
            and_(
                Finding.device_id == device_id,
                Finding.organization_id == current_user.organization_id
            )
        ).count()
        
        return {
            "success": True,
            "data": {
                "device_id": device.device_id,
                "vendor": device.vendor,
                "model": device.model,
                "hostname": device.hostname,
                "status": device.status,
                "latest_audit": {
                    "compliance_score": latest_audit.compliance_score if latest_audit else 0,
                    "risk_level": latest_audit.risk_level if latest_audit else "UNKNOWN"
                } if latest_audit else None,
                "findings_count": findings_count
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# MOBILE FINDINGS
# ============================================================

@router.get("/mobile/findings")
async def get_mobile_findings(
    session_id: str,
    severity: Optional[str] = None,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get findings for mobile view
    """
    try:
        query = db.query(Finding).filter(
            Finding.organization_id == current_user.organization_id
        )
        
        if severity:
            query = query.filter(Finding.severity == severity)
        
        findings = query.order_by(Finding.created_at.desc()).limit(limit).all()
        
        return {
            "success": True,
            "data": {
                "findings": [
                    {
                        "finding_id": f.finding_id,
                        "title": f.title,
                        "severity": f.severity,
                        "category": f.category,
                        "device_id": f.device_id,
                        "status": f.status
                    }
                    for f in findings
                ],
                "total": len(findings)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# SESSION REVOCATION
# ============================================================

@router.post("/mobile/session/revoke")
async def revoke_qr_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Revoke a QR session
    """
    try:
        # Find session
        session = None
        for token, sess in qr_sessions.items():
            if sess.session_id == session_id and sess.user_id == current_user.id:
                session = sess
                break
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Revoke
        session.revoked = True
        
        # Log
        log = SecurityAuditLog(
            log_id=f"LOG-{db.query(SecurityAuditLog).count() + 1:08d}",
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            event_type="MOBILE",
            action="SESSION_REVOKE",
            result="SUCCESS",
            resource_type="qr_session",
            resource_id=session_id,
            details={},
            ip_address="",
            user_agent=""
        )
        db.add(log)
        db.commit()
        
        return {
            "success": True,
            "data": {
                "session_id": session_id,
                "revoked": True
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
