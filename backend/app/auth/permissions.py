"""
RBAC Permissions and Roles
Phase 4: Authorization System
"""
from enum import Enum
from typing import Set


class Permission(str, Enum):
    """System permissions"""
    # Configuration permissions
    CONFIG_UPLOAD = "configuration.upload"
    CONFIG_READ = "configuration.read"
    CONFIG_DELETE = "configuration.delete"
    
    # Audit permissions
    AUDIT_RUN = "audit.run"
    AUDIT_VIEW = "audit.view"
    AUDIT_DELETE = "audit.delete"
    
    # Legacy aliases (for backward compatibility)
    AUDIT_EXECUTE = "audit.execute"  # Alias for AUDIT_RUN
    AUDIT_READ = "audit.read"  # Alias for AUDIT_VIEW
    
    # Finding permissions
    FINDING_VIEW = "finding.view"
    FINDING_UPDATE = "finding.update"
    FINDING_APPROVE = "finding.approve"
    
    # Legacy alias
    FINDING_READ = "finding.read"  # Alias for FINDING_VIEW
    
    # Remediation permissions
    REMEDIATION_READ = "remediation.read"
    REMEDIATION_APPROVE = "remediation.approve"
    
    # Framework permissions
    FRAMEWORK_MANAGE = "framework.manage"
    FRAMEWORK_READ = "framework.read"
    
    # Rules permissions
    RULES_MANAGE = "rules.manage"
    RULES_READ = "rules.read"
    
    # AI Learning permissions
    AI_INTERPRET = "ai.interpret"
    AI_REVIEW = "ai.review"
    AI_APPROVE = "ai.approve"
    AI_REJECT = "ai.reject"
    
    # Legacy mapping permissions (aliases)
    MAPPING_REVIEW = "mapping.review"
    MAPPING_APPROVE = "mapping.approve"
    MAPPING_REJECT = "mapping.reject"
    
    # Job permissions
    JOB_VIEW = "job.view"
    JOB_DELETE = "job.delete"
    
    # Report permissions
    REPORT_VIEW = "report.view"
    REPORT_GENERATE = "report.generate"
    REPORT_EXPORT = "report.export"
    
    # User management
    USER_MANAGE = "user.manage"
    USER_READ = "user.read"
    
    # Organization management
    ORG_MANAGE = "organization.manage"
    ORG_READ = "organization.read"
    
    # Audit logs
    AUDIT_LOG_READ = "audit_log.read"
    
    # System administration
    SYSTEM_ADMIN = "system.admin"
    
    # Phase 10: Vendor permissions
    VENDOR_VIEW = "vendor.view"
    VENDOR_MANAGE = "vendor.manage"
    VENDOR_APPROVE = "vendor.approve"


class Role(str, Enum):
    """User roles with associated permissions"""
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    SECURITY_ANALYST = "SECURITY_ANALYST"
    AUDITOR = "AUDITOR"
    VIEWER = "VIEWER"


# Role-Permission Mapping
ROLE_PERMISSIONS: dict[Role, Set[Permission]] = {
    Role.SUPER_ADMIN: {
        # All permissions
        Permission.CONFIG_UPLOAD,
        Permission.CONFIG_READ,
        Permission.CONFIG_DELETE,
        Permission.AUDIT_RUN,
        Permission.AUDIT_VIEW,
        Permission.AUDIT_DELETE,
        Permission.FINDING_VIEW,
        Permission.FINDING_UPDATE,
        Permission.FINDING_APPROVE,
        Permission.REMEDIATION_READ,
        Permission.REMEDIATION_APPROVE,
        Permission.FRAMEWORK_MANAGE,
        Permission.FRAMEWORK_READ,
        Permission.RULES_MANAGE,
        Permission.RULES_READ,
        Permission.AI_INTERPRET,
        Permission.AI_REVIEW,
        Permission.AI_APPROVE,
        Permission.AI_REJECT,
        Permission.JOB_VIEW,
        Permission.JOB_DELETE,
        Permission.USER_MANAGE,
        Permission.USER_READ,
        Permission.ORG_MANAGE,
        Permission.ORG_READ,
        Permission.REPORT_VIEW,
        Permission.REPORT_GENERATE,
        Permission.REPORT_EXPORT,
        Permission.AUDIT_LOG_READ,
        Permission.SYSTEM_ADMIN,
        Permission.VENDOR_VIEW,
        Permission.VENDOR_MANAGE,
        Permission.VENDOR_APPROVE,
    },
    
    Role.ADMIN: {
        # Organization-level admin
        Permission.CONFIG_UPLOAD,
        Permission.CONFIG_READ,
        Permission.CONFIG_DELETE,
        Permission.AUDIT_RUN,
        Permission.AUDIT_VIEW,
        Permission.AUDIT_DELETE,
        Permission.FINDING_VIEW,
        Permission.FINDING_UPDATE,
        Permission.FINDING_APPROVE,
        Permission.REMEDIATION_READ,
        Permission.REMEDIATION_APPROVE,
        Permission.FRAMEWORK_READ,
        Permission.RULES_READ,
        Permission.AI_INTERPRET,
        Permission.AI_REVIEW,
        Permission.AI_APPROVE,
        Permission.AI_REJECT,
        Permission.JOB_VIEW,
        Permission.JOB_DELETE,
        Permission.USER_MANAGE,
        Permission.USER_READ,
        Permission.ORG_READ,
        Permission.REPORT_VIEW,
        Permission.REPORT_GENERATE,
        Permission.REPORT_EXPORT,
        Permission.AUDIT_LOG_READ,
        Permission.VENDOR_VIEW,
        Permission.VENDOR_MANAGE,
        Permission.VENDOR_APPROVE,
    },
    
    Role.SECURITY_ANALYST: {
        # Security operations
        Permission.CONFIG_UPLOAD,
        Permission.CONFIG_READ,
        Permission.AUDIT_RUN,
        Permission.AUDIT_VIEW,
        Permission.FINDING_VIEW,
        Permission.FINDING_UPDATE,
        Permission.REMEDIATION_READ,
        Permission.FRAMEWORK_READ,
        Permission.RULES_READ,
        Permission.AI_INTERPRET,
        Permission.AI_REVIEW,
        Permission.JOB_VIEW,
        Permission.REPORT_VIEW,
        Permission.REPORT_GENERATE,
        Permission.REPORT_EXPORT,
    },
    
    Role.AUDITOR: {
        # Compliance auditing
        Permission.CONFIG_READ,
        Permission.AUDIT_RUN,
        Permission.AUDIT_VIEW,
        Permission.FINDING_VIEW,
        Permission.REMEDIATION_READ,
        Permission.FRAMEWORK_READ,
        Permission.RULES_READ,
        Permission.JOB_VIEW,
        Permission.REPORT_VIEW,
        Permission.REPORT_GENERATE,
        Permission.REPORT_EXPORT,
        Permission.AUDIT_LOG_READ,
    },
    
    Role.VIEWER: {
        # Read-only access
        Permission.CONFIG_READ,
        Permission.AUDIT_VIEW,
        Permission.FINDING_VIEW,
        Permission.REMEDIATION_READ,
        Permission.FRAMEWORK_READ,
        Permission.RULES_READ,
        Permission.JOB_VIEW,
        Permission.REPORT_VIEW,
        Permission.REPORT_EXPORT,
    },
}


def has_permission(role: Role, permission: Permission) -> bool:
    """
    Check if a role has a specific permission
    
    Args:
        role: User role
        permission: Required permission
        
    Returns:
        True if role has permission
    """
    return permission in ROLE_PERMISSIONS.get(role, set())


def get_role_permissions(role: Role) -> Set[Permission]:
    """
    Get all permissions for a role
    
    Args:
        role: User role
        
    Returns:
        Set of permissions
    """
    return ROLE_PERMISSIONS.get(role, set())
