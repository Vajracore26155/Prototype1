"""
Vendor Authentication Dependencies
Validates vendor session tokens for uploads
"""
from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db, VendorUser, VendorUploadSession


async def get_vendor_from_session(
    session_token: Optional[str] = Header(None, alias="X-Vendor-Session-Token"),
    db: Session = Depends(get_db)
) -> tuple[VendorUser, VendorUploadSession]:
    """
    Validate vendor session token and return vendor + session
    
    Args:
        session_token: Session token from header
        db: Database session
        
    Returns:
        Tuple of (VendorUser, VendorUploadSession)
        
    Raises:
        HTTPException: If token invalid or expired
    """
    if not session_token:
        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "error": {
                    "code": "NO_SESSION_TOKEN",
                    "message": "Vendor session token required. Header: X-Vendor-Session-Token"
                }
            }
        )
    
    # Find session
    session = db.query(VendorUploadSession).filter(
        VendorUploadSession.session_token == session_token,
        VendorUploadSession.status == "ACTIVE"
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "error": {
                    "code": "INVALID_SESSION",
                    "message": "Invalid or inactive vendor session"
                }
            }
        )
    
    # Check expiration
    if session.expires_at < datetime.utcnow():
        session.status = "EXPIRED"
        db.commit()
        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "error": {
                    "code": "SESSION_EXPIRED",
                    "message": "Vendor session has expired. Please request a new OTP."
                }
            }
        )
    
    # Get vendor
    vendor = db.query(VendorUser).filter(
        VendorUser.id == session.vendor_id,
        VendorUser.is_active == True,
        VendorUser.approval_status == "APPROVED"
    ).first()
    
    if not vendor:
        raise HTTPException(
            status_code=403,
            detail={
                "success": False,
                "error": {
                    "code": "VENDOR_NOT_APPROVED",
                    "message": "Vendor account is not active or approved"
                }
            }
        )
    
    # Update last activity
    session.last_activity = datetime.utcnow()
    db.commit()
    
    return vendor, session


class VendorAuth:
    """Vendor authentication dependency"""
    
    def __init__(self, require_session: bool = True):
        self.require_session = require_session
    
    async def __call__(
        self,
        session_token: Optional[str] = Header(None, alias="X-Vendor-Session-Token"),
        db: Session = Depends(get_db)
    ) -> tuple[VendorUser, VendorUploadSession]:
        """Validate vendor session"""
        return await get_vendor_from_session(session_token, db)


def require_vendor_session() -> VendorAuth:
    """Dependency factory for vendor session requirement"""
    return VendorAuth(require_session=True)
