# RBAC Enforcement Guide

## Overview

This document describes the Role-Based Access Control (RBAC) implementation in the Tatva system. All protected endpoints enforce role-based access control to ensure:
- Users can only access data for their organization
- Vendors cannot access admin features
- Admins cannot access vendor portals
- Only authorized roles can perform sensitive operations

---

## System Architecture

### Authentication Flow

1. **User Login** → JWT token issued
2. **Bearer Token** → Sent in `Authorization: Bearer <token>` header
3. **Token Validation** → Decoded and user fetched from database
4. **Role Check** → User role determines permissions
5. **Organization Check** → Data filtered to user's organization

### Protected Endpoints

All endpoints protected with `@Depends()` checks:

```python
# Permission-based protection
@router.post("/endpoint")
async def handler(
    current_user: User = Depends(require_permission(Permission.SPECIFIC_PERMISSION)),
    db: Session = Depends(get_db)
):
    # Handler implementation

# Role-based protection  
@router.post("/endpoint")
async def handler(
    current_user: User = Depends(require_role(Role.ADMIN)),
    db: Session = Depends(get_db)
):
    # Handler implementation
```

---

## Role Definitions

### SUPER_ADMIN
- **Purpose**: System-wide administration
- **Scope**: Access to all organizations and features
- **Key Permissions**: 
  - `SYSTEM_ADMIN` - System administration
  - `ORG_MANAGE` - Manage all organizations
  - `USER_MANAGE` - Manage all users
  - `VENDOR_MANAGE` - Manage all vendors
  - All other permissions

### ADMIN
- **Purpose**: Organization-level administration
- **Scope**: Organization-specific management
- **Key Permissions**:
  - `VENDOR_MANAGE` - Approve/reject vendors for their org
  - `VENDOR_VIEW` - View all vendors in organization
  - `USER_MANAGE` - Manage users in their organization
  - `AUDIT_RUN` - Create audits
  - `FINDING_APPROVE` - Approve findings
  - Configuration, remediation, and reporting permissions

### SECURITY_ANALYST
- **Purpose**: Security operations and analysis
- **Scope**: Operational security tasks
- **Key Permissions**:
  - `CONFIG_UPLOAD` - Upload configurations
  - `CONFIG_READ` - View configurations
  - `AUDIT_RUN` - Run audits
  - `AUDIT_VIEW` - View audit results
  - `FINDING_VIEW` - View findings
  - `FINDING_UPDATE` - Update findings
  - Reporting and AI interpretation

### AUDITOR
- **Purpose**: Compliance auditing and reporting
- **Scope**: Read-only audit and compliance data
- **Key Permissions**:
  - `AUDIT_VIEW` - View audits
  - `FINDING_VIEW` - View findings
  - `REPORT_VIEW` - View reports
  - `REPORT_GENERATE` - Generate reports
  - `AUDIT_LOG_READ` - Access audit logs
  - Framework and rules read

### VIEWER
- **Purpose**: Read-only access for stakeholders
- **Scope**: Minimal read access
- **Key Permissions**:
  - `CONFIG_READ` - View configurations
  - `AUDIT_VIEW` - View audit summaries
  - `FINDING_VIEW` - View findings
  - `REPORT_VIEW` - View reports
  - `REPORT_EXPORT` - Export reports

---

## Organization Isolation

### All Data Queries Filter by Organization

Every protected endpoint queries data with organization isolation:

```python
# Example: Get all vendors for current user's organization
vendors = db.query(VendorUser).filter(
    VendorUser.organization_id == current_user.organization_id
)

# Example: Get audit results for organization
audits = db.query(Audit).join(Configuration).filter(
    Configuration.organization_id == current_user.organization_id
)

# Example: Check if resource belongs to user's organization
resource = db.query(Resource).filter(
    Resource.id == resource_id,
    Resource.organization_id == current_user.organization_id
).first()

if not resource:
    raise HTTPException(status_code=404, detail="Resource not found")
```

---

## Vendor Protection

### Vendor Endpoints (Public)

These endpoints are **PUBLIC** and don't require authentication:

- `POST /vendor/register` - Vendor registration
- `POST /vendor/request-otp` - Request OTP (checked: approval_status)
- `POST /vendor/verify-otp` - Verify OTP (checked: approval_status)
- `POST /vendor/login` - Password login (checked: approval_status)

### Approval Status Checks

All vendor authentication endpoints check `approval_status`:

```python
# Status values
- "PENDING" → Cannot access (awaiting admin approval)
- "APPROVED" → Can access
- "REJECTED" → Cannot access (registration rejected)
- "SUSPENDED" → Cannot access (account suspended)

# Example check
if vendor.approval_status != "APPROVED":
    return HTTPException(status_code=403, detail="Not approved")
```

### Admin Vendor Management Endpoints (Protected)

All admin vendor endpoints require `VENDOR_MANAGE` permission:

- `GET /admin/vendor-requests` - List pending requests
- `POST /admin/vendor-requests/{id}/approve` - Approve vendor
- `POST /admin/vendor-requests/{id}/reject` - Reject vendor
- `GET /admin/vendors` - List vendors in organization
- `GET /admin/vendor-activity` - Activity statistics
- `GET /admin/vendor-sessions` - Monitor sessions
- `POST /admin/vendor-sessions/{id}/revoke` - Revoke session
- `PATCH /admin/vendors/{id}/suspend` - Suspend vendor

All queries filtered by `current_user.organization_id`

---

## Protected Endpoints by Feature

### Configuration Management

| Endpoint | Method | Permission | Scope |
|----------|--------|-----------|-------|
| `/api/configurations` | GET | CONFIG_READ | Org data only |
| `/api/configurations` | POST | CONFIG_UPLOAD | Org assignment |
| `/api/configurations/{id}` | DELETE | CONFIG_DELETE | Org only |
| `/api/configurations/{id}` | PATCH | CONFIG_READ | Org only |

### Audit Management

| Endpoint | Method | Permission | Scope |
|----------|--------|-----------|-------|
| `/api/audits` | GET | AUDIT_VIEW | Org data only |
| `/api/audits` | POST | AUDIT_RUN | Org assignment |
| `/api/audits/{id}/findings` | GET | FINDING_VIEW | Org data only |
| `/api/audits/{id}/findings/{fid}/approve` | POST | FINDING_APPROVE | Org only |

### Findings & Remediation

| Endpoint | Method | Permission | Scope |
|----------|--------|-----------|-------|
| `/api/findings` | GET | FINDING_VIEW | Org data only |
| `/api/findings/{id}/update` | PATCH | FINDING_UPDATE | Org only |
| `/api/findings/{id}/approve` | POST | FINDING_APPROVE | Org only |
| `/api/remediation` | GET | REMEDIATION_READ | Org data only |

### Admin Operations

| Endpoint | Method | Permission | Scope |
|----------|--------|-----------|-------|
| `/api/admin/users` | GET | USER_MANAGE | Org only |
| `/api/admin/statistics` | GET | SYSTEM_ADMIN | System-wide |
| `/api/admin/organizations` | GET | SYSTEM_ADMIN | All orgs |
| `/api/admin/audit-logs` | GET | AUDIT_LOG_READ | Org only |

### Vendor Management

| Endpoint | Method | Permission | Scope |
|----------|--------|-----------|-------|
| `/api/admin/vendor-requests` | GET | VENDOR_MANAGE | Org only |
| `/api/admin/vendor-requests/{id}/approve` | POST | VENDOR_MANAGE | Org only |
| `/api/admin/vendor-requests/{id}/reject` | POST | VENDOR_MANAGE | Org only |
| `/api/admin/vendors` | GET | VENDOR_VIEW | Org only |
| `/api/admin/vendor-activity` | GET | VENDOR_VIEW | Org only |
| `/api/admin/vendor-sessions` | GET | VENDOR_VIEW | Org only |
| `/api/admin/vendor-sessions/{id}/revoke` | POST | VENDOR_MANAGE | Org only |
| `/api/admin/vendors/{id}/suspend` | PATCH | VENDOR_MANAGE | Org only |

---

## Security Checks in Code

### 1. Authentication (Every Protected Endpoint)

```python
from app.auth.dependencies import require_permission, require_role

# Check permission
current_user: User = Depends(require_permission(Permission.OPERATION))

# Check role
current_user: User = Depends(require_role(Role.ADMIN))
```

### 2. Organization Isolation (Every Data Query)

```python
# Always filter by organization_id
data = db.query(Model).filter(
    Model.organization_id == current_user.organization_id
)
```

### 3. Approval Status Check (Vendor Endpoints)

```python
# Check vendor approval before allowing access
if vendor.approval_status != "APPROVED":
    raise HTTPException(status_code=403, detail="Not approved")
```

### 4. Active User Check (Authentication)

```python
# Verify user is active and not suspended
if not current_user.is_active:
    raise HTTPException(status_code=403, detail="Inactive user")
```

---

## Testing RBAC

### Test Scenarios

#### Scenario 1: Vendor Cannot Access Admin Endpoints

1. Login as vendor
2. Get session token
3. Try to access `/admin/vendors`
4. Expected: 403 Forbidden (no permission)

#### Scenario 2: Admin Cannot Access Other Organization Data

1. Login as admin for Org A
2. Get data for Org B using database directly
3. Try to query endpoints with Org B resource ID
4. Expected: 404 Not Found (organization isolation)

#### Scenario 3: Pending Vendor Cannot Login

1. Register vendor (status = "PENDING")
2. Try to request OTP
3. Expected: 403 Not Approved (must wait for admin approval)

#### Scenario 4: Rejected Vendor Stays Rejected

1. Admin rejects vendor
2. Vendor tries OTP login
3. Expected: 403 Not Approved (rejection persists)

#### Scenario 5: Suspended Vendor Cannot Access

1. Admin suspends vendor (status = "SUSPENDED")
2. Vendor tries password login
3. Expected: 403 Not Approved (suspended status)

#### Scenario 6: User Role Change Takes Effect

1. User is VIEWER with limited permissions
2. Admin changes role to ANALYST
3. User logs in again (new token)
4. Expected: New permissions reflected in token

---

## Deployment Checklist

- [ ] All admin endpoints require `require_permission()` or `require_role()`
- [ ] All data queries include `.filter(organization_id == user.organization_id)`
- [ ] All vendor endpoints check `approval_status` before allowing access
- [ ] All endpoints return 401 for unauthenticated requests
- [ ] All endpoints return 403 for unauthorized requests
- [ ] Passwords hashed with bcrypt (never stored in plain text)
- [ ] Tokens expire after configured time (default 60 minutes)
- [ ] Vendor session tokens have 24-hour expiration
- [ ] Audit logs record all permission checks
- [ ] Cross-org data access attempts are logged
- [ ] Failed authentication attempts are logged

---

## Common Vulnerabilities Prevented

### 1. Horizontal Privilege Escalation
**Prevention**: Organization isolation on all queries
```python
# WRONG: Returns data from all orgs
data = db.query(Model).filter(Model.id == id).first()

# RIGHT: Filters by organization
data = db.query(Model).filter(
    Model.id == id,
    Model.organization_id == current_user.organization_id
).first()
```

### 2. Vertical Privilege Escalation
**Prevention**: Role-based permissions checked for each operation
```python
# WRONG: No permission check
@router.post("/admin/endpoint")
async def handler(current_user: User = Depends(get_current_user)):
    # Can be called by any authenticated user!

# RIGHT: Permission required
@router.post("/admin/endpoint")
async def handler(
    current_user: User = Depends(require_permission(Permission.ADMIN_ONLY)):
    # Only users with permission can call
```

### 3. Cross-Organization Data Access
**Prevention**: All queries filter by organization
```python
# Every GET, POST, PATCH, DELETE filters by organization_id
```

### 4. Unauthenticated Admin Access
**Prevention**: All admin endpoints require authentication
```python
# All /admin/* endpoints require require_permission() or require_role()
```

### 5. Token Forgery
**Prevention**: JWT tokens validated with SECRET_KEY
```python
# Tokens cannot be forged without SECRET_KEY
# Each token contains user_id and expires at
```

---

## Monitoring & Logging

### Audit Trail

All protected operations logged with:
- User ID
- Action performed
- Resource accessed
- Organization context
- Timestamp
- Success/failure
- IP address (if available)

### Security Alerts

Automated alerts for:
- Multiple failed login attempts
- Vendor approval changes
- Admin access to unusual operations
- Cross-organization access attempts
- Token-related errors

---

## References

**Files**:
- `backend/app/auth/permissions.py` - Role/Permission definitions
- `backend/app/auth/dependencies.py` - Authentication/Authorization middleware
- `backend/app/auth/security.py` - Token & password utilities
- `backend/app/api/admin.py` - Protected admin endpoints
- `backend/app/api/vendor.py` - Vendor management endpoints
- `backend/app/api/findings.py` - Protected findings endpoints

**Configuration**:
- `.env` - JWT_SECRET_KEY and JWT settings

---

**Status**: ✅ RBAC fully implemented and enforced

**Test Coverage**:
- Admin endpoints: Permission required
- Vendor endpoints: Approval status checked
- Organization isolation: All queries filtered
- Role-based access: Permissions enforced
- Token validation: JWT verified

