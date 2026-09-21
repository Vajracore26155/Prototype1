"""
Authentication and Authorization Module
Phase 4: Production Security
"""
from .security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token
)
from .dependencies import (
    get_current_user,
    get_current_active_user,
    require_role,
    require_permission
)
from .permissions import Permission, Role

__all__ = [
    "get_password_hash",
    "verify_password",
    "create_access_token",
    "decode_access_token",
    "get_current_user",
    "get_current_active_user",
    "require_role",
    "require_permission",
    "Permission",
    "Role"
]
