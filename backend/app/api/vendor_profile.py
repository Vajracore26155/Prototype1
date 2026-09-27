"""
Vendor Profile Management API
Handles vendor profile, password, and username management
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime
import hashlib

from app.database import get_db, VendorUser
from app.auth.vendor_auth import require_vendor_session
from app.auth.security import get_password_hash, verify_password

router = APIRouter()


# Request/Response Models
class UpdateProfileRequest(BaseModel):
    contact_name: str | None = None
    phone: str | None = None
    username: str | None = None


class SetPasswordRequest(BaseModel):
    username: str
    password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class VendorProfileResponse(BaseModel):
    vendor_id: str
    email: str
    username: str | None
    company_name: str
    contact_name: str | None
    phone: str | None
    email_verified: bool
    approval_status: str
    has_password: bool
    created_at: str
    updated_at: str


# ============================================================
# PROFILE ENDPOINTS
# ============================================================

@router.get("/vendor/profile/{vendor_id}")
async def get_vendor_profile(
    vendor_id: str,
    vendor_session: tuple = Depends(require_vendor_session()),
    db: Session = Depends(get_db)
):
    """Get vendor profile information"""
    vendor, session = vendor_session
    
    # Verify vendor is requesting their own profile
    if vendor.vendor_id != vendor_id:
        raise HTTPException(
            status_code=403,
            detail={
                "success": False,
                "error": {
                    "code": "FORBIDDEN",
                    "message": "Cannot access other vendor's profile"
                }
            }
        )
    
    return {
        "success": True,
        "data": {
            "vendor_id": vendor.vendor_id,
            "email": vendor.email,
            "username": vendor.username,
            "company_name": vendor.company_name,
            "contact_name": vendor.contact_name,
            "phone": vendor.phone,
            "email_verified": vendor.email_verified,
            "approval_status": vendor.approval_status,
            "has_password": vendor.password_hash is not None,
            "created_at": vendor.created_at.isoformat() if vendor.created_at else None,
            "updated_at": vendor.updated_at.isoformat() if vendor.updated_at else None,
        }
    }


@router.put("/vendor/profile/{vendor_id}")
async def update_vendor_profile(
    vendor_id: str,
    data: UpdateProfileRequest,
    vendor_session: tuple = Depends(require_vendor_session()),
    db: Session = Depends(get_db)
):
    """Update vendor profile information"""
    vendor, session = vendor_session
    
    # Verify vendor is updating their own profile
    if vendor.vendor_id != vendor_id:
        raise HTTPException(
            status_code=403,
            detail={
                "success": False,
                "error": {
                    "code": "FORBIDDEN",
                    "message": "Cannot update other vendor's profile"
                }
            }
        )
    
    try:
        # Update fields if provided
        if data.contact_name is not None:
            vendor.contact_name = data.contact_name
        
        if data.phone is not None:
            vendor.phone = data.phone
        
        if data.username is not None:
            # Check if username is already taken
            existing = db.query(VendorUser).filter(
                VendorUser.username == data.username,
                VendorUser.id != vendor.id
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "success": False,
                        "error": {
                            "code": "USERNAME_EXISTS",
                            "message": "Username already taken"
                        }
                    }
                )
            
            vendor.username = data.username
        
        vendor.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(vendor)
        
        return {
            "success": True,
            "data": {
                "vendor_id": vendor.vendor_id,
                "email": vendor.email,
                "username": vendor.username,
                "company_name": vendor.company_name,
                "contact_name": vendor.contact_name,
                "phone": vendor.phone,
                "email_verified": vendor.email_verified,
                "approval_status": vendor.approval_status,
                "has_password": vendor.password_hash is not None,
                "message": "Profile updated successfully"
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
                    "code": "UPDATE_ERROR",
                    "message": str(e)
                }
            }
        )


# ============================================================
# PASSWORD MANAGEMENT ENDPOINTS
# ============================================================

@router.post("/vendor/set-password/{vendor_id}")
async def set_password(
    vendor_id: str,
    data: SetPasswordRequest,
    vendor_session: tuple = Depends(require_vendor_session()),
    db: Session = Depends(get_db)
):
    """Set password for vendor (OTP-only vendors can add password login)"""
    vendor, session = vendor_session
    
    # Verify vendor is setting their own password
    if vendor.vendor_id != vendor_id:
        raise HTTPException(
            status_code=403,
            detail={
                "success": False,
                "error": {
                    "code": "FORBIDDEN",
                    "message": "Cannot set password for other vendor"
                }
            }
        )
    
    # Check if vendor already has password
    if vendor.password_hash is not None:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": {
                    "code": "PASSWORD_EXISTS",
                    "message": "Vendor already has password set. Use change-password instead."
                }
            }
        )
    
    # Validate password length
    if len(data.password) < 8:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": {
                    "code": "PASSWORD_TOO_SHORT",
                    "message": "Password must be at least 8 characters"
                }
            }
        )
    
    try:
        # Check if username is already taken
        if data.username:
            existing = db.query(VendorUser).filter(
                VendorUser.username == data.username,
                VendorUser.id != vendor.id
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "success": False,
                        "error": {
                            "code": "USERNAME_EXISTS",
                            "message": "Username already taken"
                        }
                    }
                )
            
            vendor.username = data.username
        
        # Hash and set password
        password_hash = get_password_hash(data.password)
        vendor.password_hash = password_hash
        vendor.password_set_at = datetime.utcnow()
        vendor.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(vendor)
        
        return {
            "success": True,
            "data": {
                "vendor_id": vendor.vendor_id,
                "message": "Password set successfully",
                "username": vendor.username,
                "can_login_with": ["OTP", "PASSWORD"]
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
                    "code": "SET_PASSWORD_ERROR",
                    "message": str(e)
                }
            }
        )


@router.post("/vendor/change-password/{vendor_id}")
async def change_password(
    vendor_id: str,
    data: ChangePasswordRequest,
    vendor_session: tuple = Depends(require_vendor_session()),
    db: Session = Depends(get_db)
):
    """Change vendor password"""
    vendor, session = vendor_session
    
    # Verify vendor is changing their own password
    if vendor.vendor_id != vendor_id:
        raise HTTPException(
            status_code=403,
            detail={
                "success": False,
                "error": {
                    "code": "FORBIDDEN",
                    "message": "Cannot change password for other vendor"
                }
            }
        )
    
    # Check if vendor has password set
    if vendor.password_hash is None:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": {
                    "code": "NO_PASSWORD",
                    "message": "Vendor has no password set. Use set-password first."
                }
            }
        )
    
    # Verify current password
    if not verify_password(data.current_password, vendor.password_hash):
        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "error": {
                    "code": "INVALID_PASSWORD",
                    "message": "Current password is incorrect"
                }
            }
        )
    
    # Validate new password length
    if len(data.new_password) < 8:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": {
                    "code": "PASSWORD_TOO_SHORT",
                    "message": "New password must be at least 8 characters"
                }
            }
        )
    
    try:
        # Hash and set new password
        new_password_hash = get_password_hash(data.new_password)
        vendor.password_hash = new_password_hash
        vendor.password_changed_at = datetime.utcnow()
        vendor.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(vendor)
        
        return {
            "success": True,
            "data": {
                "vendor_id": vendor.vendor_id,
                "message": "Password changed successfully",
                "password_changed_at": vendor.password_changed_at.isoformat()
            }
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "CHANGE_PASSWORD_ERROR",
                    "message": str(e)
                }
            }
        )
