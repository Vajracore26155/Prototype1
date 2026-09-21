"""
Authentication API Endpoints
Phase 4: User authentication and session management
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

from app.database import get_db, User, Organization, SecurityAuditLog
from app.auth.security import verify_password, create_access_token, get_password_hash
from app.auth.dependencies import get_current_active_user
from app.auth.permissions import Role

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# ============================================================
# REQUEST/RESPONSE MODELS
# ============================================================

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user_id: str
    email: str
    role: str
    organization: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    user_id: str
    email: str
    username: str
    full_name: Optional[str]
    role: str
    organization_id: int
    organization_name: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=72)  # BCrypt limit


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def generate_log_id(db: Session) -> str:
    """Generate unique audit log ID"""
    count = db.query(SecurityAuditLog).count()
    return f"LOG-{str(count + 1).zfill(6)}"


def log_security_event(
    db: Session,
    event_type: str,
    user_id: Optional[int],
    org_id: Optional[int],
    action: str,
    result: str,
    details: Optional[dict] = None
):
    """Log security event"""
    log = SecurityAuditLog(
        log_id=generate_log_id(db),
        user_id=user_id,
        organization_id=org_id,
        event_type=event_type,
        action=action,
        result=result,
        details=details,
        timestamp=datetime.utcnow()
    )
    db.add(log)
    db.commit()


# ============================================================
# ENDPOINTS
# ============================================================

@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login with email and password
    
    Returns JWT access token
    """
    try:
        # Find user by email
        user = db.query(User).filter(User.email == login_data.email).first()
        
        if not user:
            log_security_event(
                db, "LOGIN", None, None, "AUTHENTICATE", "FAILURE",
                {"email": login_data.email, "reason": "user_not_found"}
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Verify password
        if not verify_password(login_data.password, user.hashed_password):
            log_security_event(
                db, "LOGIN", user.id, user.organization_id, "AUTHENTICATE", "FAILURE",
                {"email": login_data.email, "reason": "invalid_password"}
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Check if user is active
        if not user.is_active:
            log_security_event(
                db, "LOGIN", user.id, user.organization_id, "AUTHENTICATE", "DENIED",
                {"email": login_data.email, "reason": "inactive_user"}
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Create access token
        access_token_expires = timedelta(minutes=60)
        access_token = create_access_token(
            data={
                "sub": user.user_id,
                "email": user.email,
                "role": user.role,
                "org_id": user.organization_id
            },
            expires_delta=access_token_expires
        )
        
        # Log successful login
        log_security_event(
            db, "LOGIN", user.id, user.organization_id, "AUTHENTICATE", "SUCCESS",
            {"email": login_data.email}
        )
        
        # Get organization name
        org = db.query(Organization).filter(Organization.id == user.organization_id).first()
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=3600,
            user_id=user.user_id,
            email=user.email,
            role=user.role,
            organization=org.name if org else "Unknown"
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current authenticated user info"""
    org = db.query(Organization).filter(Organization.id == current_user.organization_id).first()
    
    return UserResponse(
        user_id=current_user.user_id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        role=current_user.role,
        organization_id=current_user.organization_id,
        organization_name=org.name if org else "Unknown",
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Logout current user
    
    Note: JWT tokens cannot be truly invalidated without a blacklist.
    This endpoint logs the event and the client should discard the token.
    """
    log_security_event(
        db, "LOGOUT", current_user.id, current_user.organization_id, 
        "LOGOUT", "SUCCESS", {"email": current_user.email}
    )
    
    return {"message": "Logout successful"}


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        log_security_event(
            db, "PASSWORD_CHANGE", current_user.id, current_user.organization_id,
            "UPDATE", "FAILURE", {"reason": "invalid_current_password"}
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    # Log password change
    log_security_event(
        db, "PASSWORD_CHANGE", current_user.id, current_user.organization_id,
        "UPDATE", "SUCCESS", {}
    )
    
    return {"message": "Password changed successfully"}


@router.get("/verify-token")
async def verify_token(current_user: User = Depends(get_current_active_user)):
    """Verify if current token is valid"""
    return {
        "valid": True,
        "user_id": current_user.user_id,
        "email": current_user.email,
        "role": current_user.role
    }
