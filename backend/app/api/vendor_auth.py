"""
Vendor Authentication API
Registration, OTP, and login - minimal non-breaking implementation
"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import random
import string
import uuid
import hashlib

from app.database import get_db, VendorUser, VendorOTP, VendorApprovalRequest
from app.auth.security import verify_password

router = APIRouter()


# Models
class VendorRegRequest(BaseModel):
    email: EmailStr
    company_name: str
    contact_name: str
    phone: str = None
    organization_id: int = 1


class OTPRequest(BaseModel):
    vendor_email: str


class OTPVerify(BaseModel):
    vendor_email: str
    otp_code: str


class VendorLogin(BaseModel):
    email: str
    password: str


@router.post("/vendor/register")
async def register_vendor(data: VendorRegRequest, db: Session = Depends(get_db)):
    """Register new vendor"""
    try:
        # Check if already exists
        existing = db.query(VendorUser).filter(VendorUser.email == data.email).first()
        if existing:
            raise HTTPException(
                status_code=409,
                detail={"success": False, "error": {"code": "VENDOR_EXISTS", "message": "A vendor account with this email already exists"}}
            )
        
        # Generate vendor ID
        count = db.query(VendorUser).count()
        vendor_id = f"VND-{str(count + 1).zfill(6)}"
        request_id = f"VAR-{str(count + 1).zfill(6)}"
        
        # Create vendor
        vendor = VendorUser(
            vendor_id=vendor_id,
            email=data.email,
            company_name=data.company_name,
            contact_name=data.contact_name,
            phone=data.phone,
            organization_id=data.organization_id,
            approval_status="PENDING",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(vendor)
        db.commit()
        db.refresh(vendor)
        
        # Create approval request for admin workflow
        approval_request = VendorApprovalRequest(
            request_id=request_id,
            vendor_id=vendor.id,
            organization_id=data.organization_id,
            request_type="NEW_VENDOR",
            request_message=f"New vendor registration from {data.company_name}",
            status="PENDING",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(approval_request)
        db.commit()
        
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
            detail={"success": False, "error": {"code": "REG_ERROR", "message": str(e)}}
        )


@router.post("/vendor/request-otp")
async def request_otp(data: OTPRequest, db: Session = Depends(get_db)):
    """Request OTP code for vendor"""
    try:
        # Find vendor by email
        vendor = db.query(VendorUser).filter(VendorUser.email == data.vendor_email).first()
        if not vendor:
            raise HTTPException(
                status_code=404,
                detail={"success": False, "error": {"code": "VENDOR_NOT_FOUND", "message": "Vendor not found"}}
            )
        
        # Check if approved
        if vendor.approval_status != "APPROVED":
            raise HTTPException(
                status_code=403,
                detail={"success": False, "error": {"code": "NOT_APPROVED", "message": "Vendor account not approved yet"}}
            )
        
        # Generate OTP
        otp_code = ''.join(random.choices(string.digits, k=6))
        
        # Store OTP
        try:
            # Generate OTP ID and hash
            otp_count = db.query(VendorOTP).count()
            otp_id = f"OTP-{str(otp_count + 1).zfill(6)}"
            otp_hash = hashlib.sha256(otp_code.encode()).hexdigest()
            
            otp = VendorOTP(
                otp_id=otp_id,
                vendor_id=vendor.id,
                otp_code=otp_code,
                otp_hash=otp_hash,
                expires_at=datetime.utcnow() + timedelta(minutes=10),
                created_at=datetime.utcnow()
            )
            db.add(otp)
            vendor.last_otp_sent = datetime.utcnow()
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"[OTP ERROR] {str(e)}")
            raise
        
        # Send OTP via email
        from app.services.email_service import email_service
        email_sent = email_service.send_otp_email(
            to_email=vendor.email,
            otp_code=otp_code,
            vendor_name=vendor.company_name
        )
        
        # Log OTP (for testing/debugging)
        print(f"[OTP] Email: {vendor.email} | Code: {otp_code} | Email Sent: {email_sent}")
        
        return {
            "success": True,
            "data": {
                "message": "OTP sent to email",
                "email": vendor.email,
                "otp_expires_in_minutes": 10,
                "email_sent": email_sent
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"[OTP HANDLER ERROR] {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": {"code": "OTP_ERROR", "message": str(e)}}
        )


@router.post("/vendor/verify-otp")
async def verify_otp(data: OTPVerify, db: Session = Depends(get_db)):
    """Verify OTP and create vendor session"""
    try:
        # Find vendor by email
        vendor = db.query(VendorUser).filter(VendorUser.email == data.vendor_email).first()
        if not vendor:
            raise HTTPException(
                status_code=404,
                detail={"success": False, "error": {"code": "VENDOR_NOT_FOUND", "message": "Vendor not found"}}
            )
        
        # Check if approved
        if vendor.approval_status != "APPROVED":
            raise HTTPException(
                status_code=403,
                detail={"success": False, "error": {"code": "NOT_APPROVED", "message": "Vendor account not approved"}}
            )
        
        # Verify OTP
        latest_otp = db.query(VendorOTP).filter(
            VendorOTP.vendor_id == vendor.id
        ).order_by(VendorOTP.created_at.desc()).first()
        
        if not latest_otp or latest_otp.otp_code != data.otp_code:
            raise HTTPException(
                status_code=400,
                detail={"success": False, "error": {"code": "INVALID_OTP", "message": "Invalid OTP code"}}
            )
        
        # Create session via vendor_upload system
        from app.database import VendorUploadSession
        
        session_id = f"VUS-{str(db.query(VendorUploadSession).count() + 1).zfill(6)}"
        session_token = str(uuid.uuid4())
        session = VendorUploadSession(
            session_id=session_id,
            vendor_id=vendor.id,
            organization_id=vendor.organization_id,
            session_token=session_token,
            status="ACTIVE",
            expires_at=datetime.utcnow() + timedelta(hours=24),
            created_at=datetime.utcnow()
        )
        db.add(session)
        
        # Update vendor login tracking  
        vendor.last_login = datetime.utcnow()
        vendor.last_login_method = "OTP"
        
        db.commit()
        db.refresh(session)
        
        return {
            "success": True,
            "data": {
                "session_id": session.session_id,
                "session_token": session_token,
                "vendor_id": vendor.vendor_id,
                "expires_at": session.expires_at.isoformat(),
                "valid_for_hours": 24,
                "login_method": "OTP"
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": {"code": "VERIFY_ERROR", "message": str(e)}}
        )


@router.post("/vendor/login")
async def vendor_login(data: VendorLogin, db: Session = Depends(get_db)):
    """Vendor login with email/password"""
    try:
        # Find vendor by email
        vendor = db.query(VendorUser).filter(VendorUser.email == data.email).first()
        if not vendor:
            raise HTTPException(
                status_code=401,
                detail={"success": False, "error": {"code": "INVALID_CREDENTIALS", "message": "Invalid email or password"}}
            )
        
        # Check if approved
        if vendor.approval_status != "APPROVED":
            raise HTTPException(
                status_code=403,
                detail={"success": False, "error": {"code": "NOT_APPROVED", "message": "Vendor account not approved"}}
            )
        
        # Check if vendor has password set
        if not vendor.password_hash:
            raise HTTPException(
                status_code=400,
                detail={"success": False, "error": {"code": "NO_PASSWORD", "message": "No password set. Please use OTP login or set a password first."}}
            )
        
        # Verify password
        if not verify_password(data.password, vendor.password_hash):
            raise HTTPException(
                status_code=401,
                detail={"success": False, "error": {"code": "INVALID_CREDENTIALS", "message": "Invalid email or password"}}
            )
        
        # Create session via vendor_upload system
        from app.database import VendorUploadSession
        
        session_id = f"VUS-{str(db.query(VendorUploadSession).count() + 1).zfill(6)}"
        session_token = str(uuid.uuid4())
        session = VendorUploadSession(
            session_id=session_id,
            vendor_id=vendor.id,
            organization_id=vendor.organization_id,
            session_token=session_token,
            status="ACTIVE",
            expires_at=datetime.utcnow() + timedelta(hours=24),
            created_at=datetime.utcnow()
        )
        db.add(session)
        
        # Update vendor login tracking
        vendor.last_login = datetime.utcnow()
        vendor.last_login_method = "PASSWORD"
        
        db.commit()
        db.refresh(session)
        
        return {
            "success": True,
            "data": {
                "session_id": session.session_id,
                "session_token": session_token,
                "vendor_id": vendor.vendor_id,
                "expires_at": session.expires_at.isoformat(),
                "valid_for_hours": 24,
                "login_method": "PASSWORD"
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={"success": False, "error": {"code": "LOGIN_ERROR", "message": str(e)}}
        )
