"""
Vendor User API Endpoints
Phase 10: Vendor OTP verification and upload sessions
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
import secrets
import hashlib

from app.database import (
    get_db, VendorUser, VendorOTP, VendorUploadSession,
    VendorApprovalRequest, Organization, User
)
from app.auth.dependencies import require_permission
from app.auth.permissions import Permission
from app.auth.security import get_password_hash, verify_password
from app.services.email_service import get_email_service

router = APIRouter()


# ============================================================
# REQUEST/RESPONSE MODELS
# ============================================================

class VendorRegistrationRequest(BaseModel):
    """Request to register as a vendor"""
    email: EmailStr
    company_name: str
    contact_name: str
    phone: Optional[str] = None
    organization_id: Optional[int] = None  # Optional: will use default vendor org if not provided
    password: Optional[str] = None  # Optional: for username/password login


class OTPRequest(BaseModel):
    """Request OTP for vendor"""
    vendor_email: EmailStr


class PasswordLoginRequest(BaseModel):
    """Login with email and password"""
    email: EmailStr
    password: str


class OTPVerificationRequest(BaseModel):
    """Verify OTP code"""
    vendor_email: EmailStr
    otp_code: str


class VendorApprovalDecision(BaseModel):
    """Admin decision on vendor approval"""
    approved: bool
    notes: Optional[str] = None


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def generate_vendor_id(db: Session) -> str:
    """Generate unique vendor ID"""
    count = db.query(VendorUser).count()
    return f"VND-{count + 1:06d}"


def generate_otp_id(db: Session) -> str:
    """Generate unique OTP ID"""
    count = db.query(VendorOTP).count()
    return f"OTP-{count + 1:06d}"


def generate_session_id(db: Session) -> str:
    """Generate unique upload session ID"""
    count = db.query(VendorUploadSession).count()
    return f"VUS-{count + 1:06d}"


def generate_request_id(db: Session) -> str:
    """Generate unique approval request ID"""
    count = db.query(VendorApprovalRequest).count()
    return f"VAR-{count + 1:06d}"


def generate_otp_code() -> str:
    """Generate 6-digit OTP code"""
    return str(secrets.randbelow(1000000)).zfill(6)


def hash_otp(otp_code: str) -> str:
    """Hash OTP for secure storage"""
    return hashlib.sha256(otp_code.encode()).hexdigest()


def verify_otp_hash(otp_code: str, otp_hash: str) -> bool:
    """Verify OTP against hash"""
    return hash_otp(otp_code) == otp_hash


def generate_session_token() -> str:
    """Generate secure session token"""
    return secrets.token_urlsafe(32)


# ============================================================
# VENDOR REGISTRATION
# ============================================================

@router.post("/vendor/register")
async def register_vendor(
    request: VendorRegistrationRequest,
    db: Session = Depends(get_db)
):
    """
    Register as a new vendor
    
    PUBLIC ENDPOINT - No authentication required
    Creates vendor account and sends approval request to admins
    """
    try:
        # Check if vendor already exists
        existing = db.query(VendorUser).filter(
            VendorUser.email == request.email
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=409,
                detail={
                    "success": False,
                    "error": {
                        "code": "VENDOR_EXISTS",
                        "message": "A vendor account with this email already exists"
                    }
                }
            )
        
        # Determine organization
        # If organization_id not provided, use default vendor organization
        if request.organization_id:
            organization = db.query(Organization).filter(
                Organization.id == request.organization_id
            ).first()
            
            if not organization:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "success": False,
                        "error": {
                            "code": "ORGANIZATION_NOT_FOUND",
                            "message": "Organization not found"
                        }
                    }
                )
        else:
            # Use admin organization as default (ID 1)
            organization = db.query(Organization).filter(
                Organization.id == 1
            ).first()
            
            if not organization:
                raise HTTPException(
                    status_code=500,
                    detail={
                        "success": False,
                        "error": {
                            "code": "ORGANIZATION_ERROR",
                            "message": "Default organization not found"
                        }
                    }
                )
        
        org_id_to_use = organization.id
        
        # Create vendor user
        vendor_id = generate_vendor_id(db)
        vendor = VendorUser(
            vendor_id=vendor_id,
            email=request.email,
            company_name=request.company_name,
            contact_name=request.contact_name,
            phone=request.phone,
            organization_id=org_id_to_use,
            email_verified=False,
            approval_status="PENDING",
            password_hash=None  # Skip password hashing for now
        )
        
        db.add(vendor)
        db.commit()
        db.refresh(vendor)
        
        # Create approval request
        request_id = generate_request_id(db)
        approval_request = VendorApprovalRequest(
            request_id=request_id,
            vendor_id=vendor.id,
            organization_id=org_id_to_use,
            request_type="NEW_VENDOR",
            status="PENDING"
        )
        
        db.add(approval_request)
        db.commit()
        
        # Send notification to all organization admins
        try:
            admins = db.query(User).filter(
                User.organization_id == org_id_to_use,
                User.role.in_(["ADMIN", "SUPER_ADMIN"]),
                User.is_active == True
            ).all()
            
            email_service = get_email_service()
            for admin in admins:
                try:
                    email_service.send_admin_approval_request(
                        admin_email=admin.email,
                        admin_name=admin.full_name,
                        vendor_name=request.contact_name,
                        vendor_email=request.email,
                        company_name=request.company_name,
                        organization_name=organization.name,
                        request_id=request_id
                    )
                except Exception as email_err:
                    print(f"Warning: Failed to send email to {admin.email}: {str(email_err)}")
        except Exception as email_err:
            print(f"Warning: Email service error: {str(email_err)}")
        
        return {
            "success": True,
            "data": {
                "vendor_id": vendor_id,
                "request_id": request_id,
                "status": "PENDING_APPROVAL",
                "message": "Vendor registration submitted. Awaiting admin approval."
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "REGISTRATION_FAILED",
                    "message": f"Failed to register vendor: {str(e)}"
                }
            }
        )


# ============================================================
# OTP GENERATION AND VERIFICATION
# ============================================================

@router.post("/vendor/request-otp")
async def request_vendor_otp(
    request: OTPRequest,
    db: Session = Depends(get_db)
):
    """
    Request OTP for vendor upload session
    
    PUBLIC ENDPOINT - No authentication required
    Sends OTP to vendor's email if they are approved
    """
    try:
        # Find vendor
        vendor = db.query(VendorUser).filter(
            VendorUser.email == request.vendor_email,
            VendorUser.is_active == True
        ).first()
        
        if not vendor:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "VENDOR_NOT_FOUND",
                        "message": "Vendor not found or inactive"
                    }
                }
            )
        
        # Check approval status
        if vendor.approval_status != "APPROVED":
            status_message = {
                "PENDING": "Your registration is currently pending administrator approval. You will receive access once your request has been approved.",
                "REJECTED": "Your vendor registration has not been approved. Please contact your system administrator for more information.",
                "SUSPENDED": "Your vendor account has been suspended. Please contact your system administrator.",
            }.get(vendor.approval_status, f"Your vendor account status is {vendor.approval_status}. Access required before requesting OTP.")
            
            raise HTTPException(
                status_code=403,
                detail={
                    "success": False,
                    "error": {
                        "code": "VENDOR_NOT_APPROVED",
                        "message": status_message
                    }
                }
            )
        
        # Rate limiting: Check if OTP was sent recently (prevent spam)
        if vendor.last_otp_sent:
            time_since_last = datetime.utcnow() - vendor.last_otp_sent
            if time_since_last.total_seconds() < 60:  # 1 minute cooldown
                wait_seconds = 60 - int(time_since_last.total_seconds())
                raise HTTPException(
                    status_code=429,
                    detail={
                        "success": False,
                        "error": {
                            "code": "TOO_MANY_REQUESTS",
                            "message": f"Please wait {wait_seconds} seconds before requesting another OTP"
                        }
                    }
                )
        
        # Generate OTP
        otp_code = generate_otp_code()
        otp_hash = hash_otp(otp_code)
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        
        # Save OTP
        otp_id = generate_otp_id(db)
        otp_record = VendorOTP(
            otp_id=otp_id,
            vendor_id=vendor.id,
            otp_code=otp_code,  # Store plaintext temporarily for email
            otp_hash=otp_hash,
            expires_at=expires_at,
            is_used=False
        )
        
        db.add(otp_record)
        vendor.last_otp_sent = datetime.utcnow()
        db.commit()
        
        # Get organization name
        organization = db.query(Organization).filter(
            Organization.id == vendor.organization_id
        ).first()
        
        # Send OTP email
        email_service = get_email_service()
        email_sent = email_service.send_vendor_otp(
            to_email=vendor.email,
            vendor_name=vendor.contact_name,
            otp_code=otp_code,
            organization_name=organization.name if organization else "Unknown",
            expires_minutes=10
        )
        
        if not email_sent:
            raise HTTPException(
                status_code=500,
                detail={
                    "success": False,
                    "error": {
                        "code": "EMAIL_FAILED",
                        "message": "Failed to send OTP email"
                    }
                }
            )
        
        return {
            "success": True,
            "data": {
                "otp_id": otp_id,
                "expires_at": expires_at.isoformat(),
                "expires_in_minutes": 10,
                "message": "OTP sent to your email. Please check your inbox."
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "OTP_REQUEST_FAILED",
                    "message": f"Failed to request OTP: {str(e)}"
                }
            }
        )


@router.post("/vendor/verify-otp")
async def verify_vendor_otp(
    request: OTPVerificationRequest,
    db: Session = Depends(get_db)
):
    """
    Verify OTP and create upload session
    
    PUBLIC ENDPOINT - No authentication required
    Returns session token for uploading configurations
    """
    try:
        # Find vendor
        vendor = db.query(VendorUser).filter(
            VendorUser.email == request.vendor_email,
            VendorUser.is_active == True,
            VendorUser.approval_status == "APPROVED"
        ).first()
        
        if not vendor:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "VENDOR_NOT_FOUND",
                        "message": "Vendor not found or not approved"
                    }
                }
            )
        
        # Find most recent unused OTP
        otp_record = db.query(VendorOTP).filter(
            VendorOTP.vendor_id == vendor.id,
            VendorOTP.is_used == False,
            VendorOTP.expires_at > datetime.utcnow()
        ).order_by(VendorOTP.created_at.desc()).first()
        
        if not otp_record:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "OTP_NOT_FOUND",
                        "message": "No valid OTP found. Please request a new one."
                    }
                }
            )
        
        # Increment verification attempts
        otp_record.verification_attempts += 1
        
        # Check max attempts
        if otp_record.verification_attempts > 5:
            db.commit()
            raise HTTPException(
                status_code=403,
                detail={
                    "success": False,
                    "error": {
                        "code": "TOO_MANY_ATTEMPTS",
                        "message": "Too many verification attempts. Please request a new OTP."
                    }
                }
            )
        
        # Verify OTP
        if not verify_otp_hash(request.otp_code, otp_record.otp_hash):
            db.commit()
            raise HTTPException(
                status_code=401,
                detail={
                    "success": False,
                    "error": {
                        "code": "INVALID_OTP",
                        "message": "Invalid OTP code"
                    }
                }
            )
        
        # Mark OTP as used
        otp_record.is_used = True
        otp_record.used_at = datetime.utcnow()
        
        # Create upload session
        session_id = generate_session_id(db)
        session_token = generate_session_token()
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        upload_session = VendorUploadSession(
            session_id=session_id,
            vendor_id=vendor.id,
            organization_id=vendor.organization_id,
            otp_id=otp_record.id,
            session_token=session_token,
            expires_at=expires_at,
            status="ACTIVE"
        )
        
        db.add(upload_session)
        db.commit()
        db.refresh(upload_session)
        
        return {
            "success": True,
            "data": {
                "session_id": session_id,
                "session_token": session_token,
                "vendor_id": vendor.vendor_id,
                "vendor_name": vendor.contact_name,
                "company_name": vendor.company_name,
                "organization_id": vendor.organization_id,
                "expires_at": expires_at.isoformat(),
                "valid_for_hours": 24,
                "message": "OTP verified successfully. You can now upload configurations."
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "VERIFICATION_FAILED",
                    "message": f"Failed to verify OTP: {str(e)}"
                }
            }
        )


# ============================================================
# ADMIN APPROVAL ENDPOINTS
# ============================================================

@router.get("/admin/vendor-requests")
async def get_vendor_approval_requests(
    current_user: User = Depends(require_permission(Permission.VENDOR_MANAGE)),
    db: Session = Depends(get_db),
    status: Optional[str] = None
):
    """
    Get vendor approval requests
    
    Requires: VENDOR_MANAGE permission (ADMIN)
    """
    try:
        query = db.query(VendorApprovalRequest).filter(
            VendorApprovalRequest.organization_id == current_user.organization_id
        )
        
        if status:
            query = query.filter(VendorApprovalRequest.status == status)
        
        requests = query.order_by(VendorApprovalRequest.created_at.desc()).all()
        
        result = []
        for req in requests:
            vendor = db.query(VendorUser).filter(VendorUser.id == req.vendor_id).first()
            if vendor:
                result.append({
                    "request_id": req.request_id,
                    "vendor_id": vendor.vendor_id,
                    "vendor_email": vendor.email,
                    "company_name": vendor.company_name,
                    "contact_name": vendor.contact_name,
                    "phone": vendor.phone,
                    "request_type": req.request_type,
                    "status": req.status,
                    "created_at": req.created_at.isoformat(),
                    "reviewed_by": req.reviewed_by,
                    "reviewed_at": req.reviewed_at.isoformat() if req.reviewed_at else None
                })
        
        return {
            "success": True,
            "data": {
                "requests": result,
                "total": len(result)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "GET_REQUESTS_FAILED",
                    "message": "Failed to retrieve vendor requests"
                }
            }
        )


@router.post("/admin/vendor-requests/{request_id}/decide")
async def decide_vendor_approval(
    request_id: str,
    decision: VendorApprovalDecision,
    current_user: User = Depends(require_permission(Permission.VENDOR_MANAGE)),
    db: Session = Depends(get_db)
):
    """
    Approve or reject vendor request
    
    Requires: VENDOR_MANAGE permission (ADMIN)
    """
    try:
        # Find request
        approval_request = db.query(VendorApprovalRequest).filter(
            VendorApprovalRequest.request_id == request_id,
            VendorApprovalRequest.organization_id == current_user.organization_id
        ).first()
        
        if not approval_request:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "REQUEST_NOT_FOUND",
                        "message": "Vendor request not found"
                    }
                }
            )
        
        if approval_request.status != "PENDING":
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": {
                        "code": "ALREADY_REVIEWED",
                        "message": f"Request already {approval_request.status}"
                    }
                }
            )
        
        # Get vendor
        vendor = db.query(VendorUser).filter(
            VendorUser.id == approval_request.vendor_id
        ).first()
        
        if not vendor:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "VENDOR_NOT_FOUND",
                        "message": "Vendor not found"
                    }
                }
            )
        
        # Update request
        approval_request.status = "APPROVED" if decision.approved else "REJECTED"
        approval_request.reviewed_by = current_user.email
        approval_request.reviewed_at = datetime.utcnow()
        approval_request.review_notes = decision.notes
        
        # Update vendor
        vendor.approval_status = "APPROVED" if decision.approved else "REJECTED"
        vendor.approved_by = current_user.email
        vendor.approved_at = datetime.utcnow()
        
        if not decision.approved and decision.notes:
            vendor.rejection_reason = decision.notes
        
        db.commit()
        
        # Get organization
        organization = db.query(Organization).filter(
            Organization.id == vendor.organization_id
        ).first()
        
        # Send notification to vendor
        email_service = get_email_service()
        email_service.send_vendor_approval_notification(
            to_email=vendor.email,
            vendor_name=vendor.contact_name,
            organization_name=organization.name if organization else "Unknown",
            approved=decision.approved,
            admin_name=current_user.full_name,
            notes=decision.notes
        )
        
        return {
            "success": True,
            "data": {
                "request_id": request_id,
                "vendor_id": vendor.vendor_id,
                "decision": "APPROVED" if decision.approved else "REJECTED",
                "message": f"Vendor {'approved' if decision.approved else 'rejected'} successfully"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "DECISION_FAILED",
                    "message": f"Failed to process decision: {str(e)}"
                }
            }
        )


@router.get("/admin/vendors")
async def list_vendors(
    current_user: User = Depends(require_permission(Permission.VENDOR_VIEW)),
    db: Session = Depends(get_db),
    status: Optional[str] = None
):
    """
    List all vendors for organization
    
    Requires: VENDOR_VIEW permission
    """
    try:
        query = db.query(VendorUser).filter(
            VendorUser.organization_id == current_user.organization_id
        )
        
        if status:
            query = query.filter(VendorUser.approval_status == status)
        
        vendors = query.order_by(VendorUser.created_at.desc()).all()
        
        result = []
        for vendor in vendors:
            # Get upload session count
            session_count = db.query(VendorUploadSession).filter(
                VendorUploadSession.vendor_id == vendor.id
            ).count()
            
            result.append({
                "vendor_id": vendor.vendor_id,
                "email": vendor.email,
                "company_name": vendor.company_name,
                "contact_name": vendor.contact_name,
                "phone": vendor.phone,
                "approval_status": vendor.approval_status,
                "email_verified": vendor.email_verified,
                "is_active": vendor.is_active,
                "approved_by": vendor.approved_by,
                "approved_at": vendor.approved_at.isoformat() if vendor.approved_at else None,
                "upload_sessions": session_count,
                "created_at": vendor.created_at.isoformat()
            })
        
        return {
            "success": True,
            "data": {
                "vendors": result,
                "total": len(result)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "LIST_VENDORS_FAILED",
                    "message": "Failed to list vendors"
                }
            }
        )



# ============================================================
# ADMIN VENDOR ACTIVITY MONITORING
# ============================================================

@router.get("/admin/vendor-activity")
async def get_vendor_activity(
    current_user: User = Depends(require_permission(Permission.VENDOR_VIEW)),
    db: Session = Depends(get_db),
    days: int = 30
):
    """
    Get vendor activity summary
    
    Requires: VENDOR_VIEW permission
    """
    try:
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get all vendors for organization
        vendors = db.query(VendorUser).filter(
            VendorUser.organization_id == current_user.organization_id
        ).all()
        
        activity = []
        for vendor in vendors:
            # Get upload sessions
            sessions = db.query(VendorUploadSession).filter(
                VendorUploadSession.vendor_id == vendor.id,
                VendorUploadSession.created_at >= cutoff_date
            ).all()
            
            # Get configurations uploaded
            configs = db.query(Configuration).filter(
                Configuration.organization_id == vendor.organization_id,
                Configuration.filename.like(f"vendor_{vendor.vendor_id}_%"),
                Configuration.created_at >= cutoff_date
            ).count()
            
            activity.append({
                "vendor_id": vendor.vendor_id,
                "company": vendor.company_name,
                "contact": vendor.contact_name,
                "email": vendor.email,
                "approval_status": vendor.approval_status,
                "sessions_count": len(sessions),
                "active_sessions": sum(1 for s in sessions if s.status == "ACTIVE"),
                "expired_sessions": sum(1 for s in sessions if s.status == "EXPIRED"),
                "total_uploads": configs,
                "last_activity": max([s.last_activity for s in sessions]).isoformat() if sessions else None
            })
        
        return {
            "success": True,
            "data": {
                "period_days": days,
                "vendors": activity,
                "total_vendors": len(activity),
                "summary": {
                    "total_uploads": sum(v["total_uploads"] for v in activity),
                    "active_vendors": sum(1 for v in activity if v["active_sessions"] > 0)
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "ACTIVITY_FAILED",
                    "message": "Failed to retrieve vendor activity"
                }
            }
        )


@router.get("/admin/vendor-sessions")
async def get_active_vendor_sessions(
    current_user: User = Depends(require_permission(Permission.VENDOR_VIEW)),
    db: Session = Depends(get_db)
):
    """
    Get all active vendor upload sessions
    
    Requires: VENDOR_VIEW permission
    """
    try:
        sessions = db.query(VendorUploadSession).filter(
            VendorUploadSession.organization_id == current_user.organization_id,
            VendorUploadSession.status == "ACTIVE"
        ).order_by(VendorUploadSession.created_at.desc()).all()
        
        result = []
        for session in sessions:
            vendor = db.query(VendorUser).filter(VendorUser.id == session.vendor_id).first()
            if vendor:
                result.append({
                    "session_id": session.session_id,
                    "vendor": {
                        "vendor_id": vendor.vendor_id,
                        "company": vendor.company_name,
                        "contact": vendor.contact_name,
                        "email": vendor.email
                    },
                    "created_at": session.created_at.isoformat(),
                    "expires_at": session.expires_at.isoformat(),
                    "last_activity": session.last_activity.isoformat(),
                    "upload_count": session.upload_count,
                    "files_uploaded": session.files_uploaded or []
                })
        
        return {
            "success": True,
            "data": {
                "sessions": result,
                "total": len(result)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "SESSIONS_FAILED",
                    "message": "Failed to retrieve vendor sessions"
                }
            }
        )


@router.post("/admin/vendor-sessions/{session_id}/revoke")
async def admin_revoke_vendor_session(
    session_id: str,
    current_user: User = Depends(require_permission(Permission.VENDOR_MANAGE)),
    db: Session = Depends(get_db)
):
    """
    Admin: Forcefully revoke a vendor session
    
    Requires: VENDOR_MANAGE permission
    """
    try:
        session = db.query(VendorUploadSession).filter(
            VendorUploadSession.session_id == session_id,
            VendorUploadSession.organization_id == current_user.organization_id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "SESSION_NOT_FOUND",
                        "message": "Vendor session not found"
                    }
                }
            )
        
        # Get vendor info
        vendor = db.query(VendorUser).filter(VendorUser.id == session.vendor_id).first()
        
        # Revoke session
        old_status = session.status
        session.status = "REVOKED"
        db.commit()
        
        # Log action
        log = SecurityAuditLog(
            log_id=generate_log_id(db),
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            event_type="ADMIN_ACTION",
            action="REVOKE_VENDOR_SESSION",
            result="SUCCESS",
            resource_type="vendor_session",
            resource_id=session_id,
            details={
                "admin": current_user.email,
                "vendor_id": vendor.vendor_id if vendor else None,
                "vendor_email": vendor.email if vendor else None,
                "old_status": old_status,
                "uploads_in_session": session.upload_count
            },
            ip_address="",
            user_agent=""
        )
        db.add(log)
        db.commit()
        
        return {
            "success": True,
            "data": {
                "session_id": session_id,
                "vendor_id": vendor.vendor_id if vendor else None,
                "revoked_by": current_user.email,
                "message": "Vendor session revoked successfully"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "REVOKE_FAILED",
                    "message": f"Failed to revoke session: {str(e)}"
                }
            }
        )


@router.patch("/admin/vendors/{vendor_id}/suspend")
async def suspend_vendor(
    vendor_id: str,
    current_user: User = Depends(require_permission(Permission.VENDOR_MANAGE)),
    db: Session = Depends(get_db)
):
    """
    Admin: Suspend a vendor account
    
    Requires: VENDOR_MANAGE permission
    """
    try:
        vendor = db.query(VendorUser).filter(
            VendorUser.vendor_id == vendor_id,
            VendorUser.organization_id == current_user.organization_id
        ).first()
        
        if not vendor:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "VENDOR_NOT_FOUND",
                        "message": "Vendor not found"
                    }
                }
            )
        
        # Suspend vendor
        vendor.approval_status = "SUSPENDED"
        vendor.is_active = False
        
        # Revoke all active sessions
        active_sessions = db.query(VendorUploadSession).filter(
            VendorUploadSession.vendor_id == vendor.id,
            VendorUploadSession.status == "ACTIVE"
        ).all()
        
        for session in active_sessions:
            session.status = "REVOKED"
        
        db.commit()
        
        # Log action
        log = SecurityAuditLog(
            log_id=generate_log_id(db),
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            event_type="ADMIN_ACTION",
            action="SUSPEND_VENDOR",
            result="SUCCESS",
            resource_type="vendor",
            resource_id=vendor_id,
            details={
                "admin": current_user.email,
                "vendor_email": vendor.email,
                "company": vendor.company_name,
                "sessions_revoked": len(active_sessions)
            },
            ip_address="",
            user_agent=""
        )
        db.add(log)
        db.commit()
        
        return {
            "success": True,
            "data": {
                "vendor_id": vendor_id,
                "status": "SUSPENDED",
                "sessions_revoked": len(active_sessions),
                "suspended_by": current_user.email,
                "message": "Vendor suspended successfully"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "SUSPEND_FAILED",
                    "message": f"Failed to suspend vendor: {str(e)}"
                }
            }
        )



# ============================================================
# PASSWORD LOGIN (ALTERNATIVE TO OTP)
# ============================================================

@router.post("/vendor/login")
async def vendor_password_login(
    request: PasswordLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Vendor login with email and password
    
    Alternative to OTP-based login
    PUBLIC ENDPOINT - No authentication required
    Returns session token for uploading configurations
    """
    try:
        # Find vendor by email
        vendor = db.query(VendorUser).filter(
            VendorUser.email == request.email,
            VendorUser.is_active == True
        ).first()
        
        if not vendor:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "VENDOR_NOT_FOUND",
                        "message": "Invalid email or password"
                    }
                }
            )
        
        # Check approval status first
        if vendor.approval_status != "APPROVED":
            status_message = {
                "PENDING": "Your registration is currently pending administrator approval. You will receive access once your request has been approved.",
                "REJECTED": "Your vendor registration has not been approved. Please contact your system administrator for more information.",
                "SUSPENDED": "Your vendor account has been suspended. Please contact your system administrator.",
            }.get(vendor.approval_status, f"Your vendor account status is {vendor.approval_status}. Access required before login.")
            
            raise HTTPException(
                status_code=403,
                detail={
                    "success": False,
                    "error": {
                        "code": "VENDOR_NOT_APPROVED",
                        "message": status_message
                    }
                }
            )
        
        # Check if password is set
        if not vendor.password_hash:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": {
                        "code": "PASSWORD_NOT_SET",
                        "message": "Password login is not available. Please use OTP login instead."
                    }
                }
            )
        
        # Verify password
        if not verify_password(request.password, vendor.password_hash):
            raise HTTPException(
                status_code=401,
                detail={
                    "success": False,
                    "error": {
                        "code": "INVALID_PASSWORD",
                        "message": "Invalid email or password"
                    }
                }
            )
        
        # Create upload session (like OTP verification does)
        session_id = generate_session_id(db)
        session_token = generate_session_token()
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        # No OTP for password login, use a dummy OTP record or None
        upload_session = VendorUploadSession(
            session_id=session_id,
            vendor_id=vendor.id,
            organization_id=vendor.organization_id,
            otp_id=None,  # No OTP for password login
            session_token=session_token,
            expires_at=expires_at,
            status="ACTIVE"
        )
        
        db.add(upload_session)
        db.commit()
        db.refresh(upload_session)
        
        # Get organization name
        organization = db.query(Organization).filter(
            Organization.id == vendor.organization_id
        ).first()
        
        return {
            "success": True,
            "data": {
                "session_id": session_id,
                "session_token": session_token,
                "vendor_id": vendor.vendor_id,
                "vendor_name": vendor.contact_name,
                "company_name": vendor.company_name,
                "organization_id": vendor.organization_id,
                "organization_name": organization.name if organization else "Unknown",
                "expires_at": expires_at.isoformat(),
                "valid_for_hours": 24,
                "login_method": "PASSWORD",
                "message": "Login successful. You can now upload configurations."
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "LOGIN_FAILED",
                    "message": f"Login failed: {str(e)}"
                }
            }
        )


@router.post("/vendor/set-password")
async def vendor_set_password(
    password: str,
    session_token: str,
    db: Session = Depends(get_db)
):
    """
    Vendor: Set password for future login
    
    Can be used after OTP verification to enable password login
    Requires valid session_token
    """
    try:
        # Find session by token
        session = db.query(VendorUploadSession).filter(
            VendorUploadSession.session_token == session_token,
            VendorUploadSession.status == "ACTIVE",
            VendorUploadSession.expires_at > datetime.utcnow()
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=401,
                detail={
                    "success": False,
                    "error": {
                        "code": "INVALID_SESSION",
                        "message": "Invalid or expired session token"
                    }
                }
            )
        
        # Find vendor
        vendor = db.query(VendorUser).filter(
            VendorUser.id == session.vendor_id
        ).first()
        
        if not vendor:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "VENDOR_NOT_FOUND",
                        "message": "Vendor not found"
                    }
                }
            )
        
        # Validate password strength
        if len(password) < 8:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": {
                        "code": "WEAK_PASSWORD",
                        "message": "Password must be at least 8 characters long"
                    }
                }
            )
        
        # Set password hash
        vendor.password_hash = get_password_hash(password)
        db.commit()
        
        return {
            "success": True,
            "data": {
                "message": "Password set successfully. You can now use email/password for future logins."
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "SET_PASSWORD_FAILED",
                    "message": f"Failed to set password: {str(e)}"
                }
            }
        )
