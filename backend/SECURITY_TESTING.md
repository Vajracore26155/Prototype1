# Security Regression Testing

This document describes the security regression test suite created to prevent re-introduction of fixed vulnerabilities.

## Overview

The security test suite (`tests/test_security_regression.py`) contains comprehensive tests for all CRITICAL security vulnerabilities fixed during Phase 4+ security hardening.

## Test Coverage

### 1. Unauthenticated Endpoint Access (401 Tests)
**Vulnerability**: Several endpoints were accessible without authentication
**Fix**: Added `require_permission` dependency to all endpoints
**Tests**:
- `test_comparison_requires_auth` - Comparison endpoints require auth
- `test_frameworks_requires_auth` - Framework endpoints require auth
- `test_bulk_upload_requires_auth` - Bulk upload endpoints require auth

**Expected Result**: All unauthenticated requests return 401 Unauthorized

### 2. IDOR - Configuration Access
**Vulnerability**: Users could access other organizations' configurations by guessing IDs
**Fix**: Added organization_id filter to all configuration queries
**Tests**:
- `test_cannot_compare_other_org_configs` - Cannot compare cross-org configs
- `test_cannot_access_other_org_config_versions` - Cannot access cross-org versions
- `test_cannot_compare_other_org_versions` - Cannot compare cross-org versions

**Expected Result**: Cross-org access attempts return 404 Not Found

### 3. IDOR - Audit and Findings Access
**Vulnerability**: Users could access other organizations' audit results
**Fix**: Join Configuration table and filter by organization_id
**Tests**:
- `test_cannot_compare_other_org_audits` - Cannot compare cross-org audits
- `test_cannot_access_other_org_audit_details` - Cannot view cross-org audit details
- `test_cannot_access_other_org_findings` - Cannot view cross-org findings
- `test_cannot_download_other_org_report` - Cannot download cross-org reports

**Expected Result**: Cross-org access attempts return 404 Not Found

### 4. IDOR - Device Access
**Vulnerability**: Users could access/modify other organizations' devices
**Fix**: Added organization_id filter to all device queries
**Tests**:
- `test_cannot_get_other_org_device` - Cannot get cross-org device
- `test_cannot_update_other_org_device` - Cannot update cross-org device
- `test_cannot_delete_other_org_device` - Cannot delete cross-org device
- `test_list_devices_returns_only_own_org` - Device list is org-scoped

**Expected Result**: Cross-org access attempts return 404 Not Found

### 5. IDOR - Drift Analysis Access
**Vulnerability**: Users could access other organizations' drift analyses
**Fix**: Added organization_id filter to drift queries
**Tests**:
- `test_cannot_get_other_org_drift` - Cannot get cross-org drift
- `test_cannot_acknowledge_other_org_drift` - Cannot acknowledge cross-org drift
- `test_drift_history_returns_only_own_org` - Drift history is org-scoped

**Expected Result**: Cross-org access attempts return 404 Not Found

### 6. Organization Assignment
**Vulnerability**: Uploaded resources might not be assigned to correct organization
**Fix**: Added organization_id=current_user.organization_id on creation
**Tests**:
- `test_uploaded_config_assigned_to_user_org` - Configs assigned to uploader's org
- `test_created_device_assigned_to_user_org` - Devices assigned to creator's org

**Expected Result**: Created resources have correct organization_id

### 7. Dashboard and Summary Data Isolation
**Vulnerability**: Dashboard might show cross-org data
**Fix**: All dashboard queries filter by organization_id
**Tests**:
- `test_dashboard_summary_org_scoped` - Dashboard shows only own org
- `test_device_stats_org_scoped` - Device stats show only own org

**Expected Result**: Dashboard data is org-scoped

### 8. Search Isolation
**Vulnerability**: Search could return cross-org results
**Fix**: Added organization_id to search filters and indexer
**Tests**:
- `test_search_returns_only_own_org_results` - Search is org-scoped

**Expected Result**: Search results contain only own organization data

**NOTE**: This test will fail until search index is rebuilt with `POST /search/reindex`

### 9. Positive Access Tests
**Purpose**: Verify legitimate access still works
**Tests**:
- `test_can_access_own_config` - Can access own organization's config
- `test_can_access_own_audit` - Can access own organization's audit
- `test_can_access_own_device` - Can access own organization's device
- `test_can_compare_own_configs` - Can compare own organization's configs

**Expected Result**: Own organization access works correctly

## Running the Tests

### Quick Run
```bash
cd backend
python run_security_tests.py
```

### With Coverage
```bash
python run_security_tests.py --coverage --html
# View coverage: open htmlcov/index.html
```

### Fail Fast (stop on first failure)
```bash
python run_security_tests.py --fail-fast
```

### Direct pytest
```bash
pytest tests/test_security_regression.py -v
```

## Test Data Setup

The test suite creates two isolated organizations:
- **Organization A**: User A, Config A, Audit A, Device A, etc.
- **Organization B**: User B, Config B, Audit B, Device B, etc.

Each test verifies:
1. User A can access Org A resources ✅
2. User A cannot access Org B resources ❌
3. Proper 404 responses for cross-org attempts
4. Proper 401 responses for unauthenticated attempts

## Integration with CI/CD

Add to `.github/workflows/security.yml`:
```yaml
- name: Run Security Regression Tests
  run: |
    cd backend
    python run_security_tests.py --coverage
  
- name: Upload Security Test Results
  uses: actions/upload-artifact@v3
  with:
    name: security-test-results
    path: backend/htmlcov/
```

## Maintenance

**When adding new endpoints:**
1. Add authentication with `require_permission` dependency
2. Add organization_id filter to all queries
3. Add corresponding security tests to this suite
4. Run tests to verify isolation

**When modifying existing endpoints:**
1. Run security tests before and after changes
2. Verify no regressions in organization isolation
3. Update tests if behavior intentionally changes

## Known Limitations

1. **Search Tests**: Will fail until search index is rebuilt
   - Run `POST /search/reindex` as SYSTEM_ADMIN
   - Then re-run security tests

2. **Learning Endpoints**: Intentionally global (documented)
   - AI learning is cross-org by design
   - Not tested in this suite (see Task #6 documentation)

3. **Admin Endpoints**: Intentionally global (documented)
   - SYSTEM_ADMIN endpoints show platform-wide data
   - Protected by Permission.SYSTEM_ADMIN check

## Compliance

These tests verify:
- ✅ **OWASP A01:2021 - Broken Access Control**: IDOR fixed
- ✅ **OWASP A07:2021 - Authentication Failures**: Endpoints protected
- ✅ **ISO 27001 A.9.4 - Access Control**: Tenant isolation enforced
- ✅ **NIST 800-53 AC-3 - Access Enforcement**: Org-based access control

## Contact

For questions about security testing:
- Review `tests/test_security_regression.py` source code
- See Phase 4 security audit documentation
- Consult security team before modifying isolation logic
