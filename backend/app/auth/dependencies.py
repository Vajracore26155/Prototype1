"""
FastAPI authentication dependencies
Phase 4: Request authentication and authorization
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db, User
from app.auth.security import decode_access_token
from app.auth.permissions import Permission, Role, has_permission

# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current authenticated user from JWT token
    
    Args:
        credentials: HTTP Bearer credentials
        db: Database session
        
    Returns:
        User object or None if not authenticated
        
    Raises:
        HTTPException 401 if token is invalid
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: str = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Fetch user from database
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_active_user(
    current_user: Optional[User] = Depends(get_current_user)
) -> User:
    """
    Get current active user (requires authentication)
    
    Args:
        current_user: Current user from token
        
    Returns:
        Active user object
        
    Raises:
        HTTPException 401 if not authenticated
        HTTPException 403 if user is inactive
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return current_user


def require_role(*allowed_roles: Role):
    """
    Dependency to require specific roles
    
    Usage:
        @app.get("/admin", dependencies=[Depends(require_role(Role.ADMIN))])
        
    Args:
        *allowed_roles: Allowed roles
        
    Returns:
        Dependency function
    """
    async def role_checker(current_user: User = Depends(get_current_active_user)):
        user_role = Role(current_user.role)
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {', '.join(r.value for r in allowed_roles)}"
            )
        return current_user
    
    return role_checker


def require_permission(*required_permissions: Permission):
    """
    Dependency to require specific permissions
    
    Usage:
        @app.post("/upload", dependencies=[Depends(require_permission(Permission.CONFIG_UPLOAD))])
        
    Args:
        *required_permissions: Required permissions
        
    Returns:
        Dependency function
    """
    async def permission_checker(current_user: User = Depends(get_current_active_user)):
        user_role = Role(current_user.role)
        
        for perm in required_permissions:
            if not has_permission(user_role, perm):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required: {perm.value}"
                )
        
        return current_user
    
    return permission_checker


# Optional authentication (allows both authenticated and anonymous)
async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if authenticated, None otherwise
    Does not raise exceptions for unauthenticated requests
    
    Args:
        credentials: HTTP Bearer credentials
        db: Database session
        
    Returns:
        User object or None
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        
        if not payload:
            return None
        
        user_id: str = payload.get("sub")
        if not user_id:
            return None
        
        user = db.query(User).filter(User.user_id == user_id).first()
        return user
    except:
        return None
