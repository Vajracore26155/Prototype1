# End-to-End Testing Guide: Vendor Registration → Approval → Login

## Overview

This guide provides step-by-step instructions to test the complete vendor onboarding flow:

1. **Vendor Registration** - Vendor creates account
2. **Admin Approval** - Admin reviews and approves
3. **Vendor Login** - Vendor accesses system using OTP or password
4. **Dashboard Access** - Vendor sees their own data only

---

## Prerequisites

### Before Starting

1. **Backend Running**
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```
   Expected: No startup errors, listening on port 8000

2. **Frontend Running**
   ```bash
   cd frontend
   npm run dev
   ```
   Expected: Running on port 5173, able to access http://localhost:5173

3. **Database Ready**
   - SQLite database at `backend/data/sih26155.db`
   - Tables created via Alembic migrations
   - Organizations and users populated

4. **Test Admin Account**
   - Email: `admin@example.com`
   - Role: `ADMIN`
   - Organization: Test Org
   - Password: (set during initial setup)

---

## Flow Test Scenarios

### Test 1: Vendor Registration (PENDING Status)

**Objective**: Verify vendor registration creates PENDING account

**Steps**:

1. Go to http://localhost:5173/
   - See Landing Page with Vendor Portal section
   
2. Click "Register as Vendor" button
   - Navigate to /vendor/register page
   
3. Fill registration form:
   ```
   Email: vendor1@company.com
   Company Name: Test Company Inc
   Contact Name: John Doe
   Phone: 555-0001
   Password: SecurePass123 (optional)
   ```
   
4. Click "Register"
   - Should see success message
   - Response includes vendor_id (e.g., "VND-000001")
   
**Expected Result**:
```json
{
  "success": true,
  "data": {
    "vendor_id": "VND-000001",
    "request_id": "VAR-000001",
    "status": "PENDING_APPROVAL",
    "message": "Vendor registration submitted. Awaiting admin approval."
  }
}
```

**Verification**:
- ✓ Vendor created with `approval_status = "PENDING"`
- ✓ Admin notification email logged to console
- ✓ Request ID returned for tracking

---

### Test 2: Vendor Cannot Login While PENDING

**Objective**: Verify PENDING vendors are blocked from access

**Steps**:

1. Go to http://localhost:5173/vendor/login
   
2. Try OTP Login:
   - Email: vendor1@company.com
   - Click "Send OTP Code"
   
**Expected Result**:
```json
{
  "success": false,
  "error": {
    "code": "VENDOR_NOT_APPROVED",
    "message": "Your registration is currently pending administrator approval..."
  }
}
```

**Verification**:
- ✓ 403 Forbidden returned
- ✓ Friendly message explains PENDING status
- ✓ No OTP sent to email

---

### Test 3: Admin Reviews Pending Vendor

**Objective**: Verify admin can see and manage vendor requests

**Steps**:

1. Login as Admin
   - Email: admin@example.com
   - Navigate to /admin/dashboard
   
2. Check Admin Dashboard
   - Should show "Pending" count in metrics
   - See vendor request in activity table
   
3. Click "Vendor Management" section
   - See pending vendor: vendor1@company.com
   - Shows: Company, Contact, Email, Status: PENDING
   
**Expected Result**:
```json
{
  "success": true,
  "data": {
    "requests": [
      {
        "request_id": "VAR-000001",
        "vendor_id": "VND-000001",
        "vendor_email": "vendor1@company.com",
        "company_name": "Test Company Inc",
        "contact_name": "John Doe",
        "phone": "555-0001",
        "request_type": "NEW_VENDOR",
        "status": "PENDING",
        "created_at": "2026-09-18T..."
      }
    ],
    "total": 1
  }
}
```

**Verification**:
- ✓ Admin sees pending request
- ✓ All vendor details displayed
- ✓ Request ID shows for tracking

---

### Test 4: Admin Approves Vendor

**Objective**: Verify admin can approve vendor and vendor receives notification

**Steps**:

1. From Admin Dashboard, click "Approve" on vendor request
   
2. Optional: Add approval notes
   - "Approved - credentials verified"
   
3. Click "Approve Vendor"
   
**Expected Result**:
```json
{
  "success": true,
  "data": {
    "request_id": "VAR-000001",
    "vendor_id": "VND-000001",
    "decision": "APPROVED",
    "message": "Vendor approved successfully"
  }
}
```

**Console Should Show**:
```
[CONSOLE] Vendor Approval Email
To: vendor1@company.com
Subject: Your Tatva Registration - Approved
Message: Your registration has been approved...
```

**Verification**:
- ✓ Approval recorded in database
- ✓ Vendor status changed to "APPROVED"
- ✓ Approval notification logged
- ✓ Approved admin name recorded

---

### Test 5: Approved Vendor Can Request OTP

**Objective**: Verify approved vendor can now request OTP

**Steps**:

1. Go to http://localhost:5173/vendor/login
   
2. Select "OTP Login" tab
   
3. Enter email: vendor1@company.com
   
4. Click "Send OTP Code"
   
**Expected Result**:
```json
{
  "success": true,
  "data": {
    "otp_id": "OTP-000001",
    "expires_at": "2026-09-18T...",
    "expires_in_minutes": 10,
    "message": "OTP sent to your email. Please check your inbox."
  }
}
```

**Console Should Show**:
```
[CONSOLE] OTP Email
To: vendor1@company.com
Code: 123456
Expires: 10 minutes
```

**Verification**:
- ✓ OTP generated and hashed
- ✓ OTP email logged to console
- ✓ Expires in 10 minutes
- ✓ OTP sent successfully message

---

### Test 6: Vendor Verifies OTP and Gets Session

**Objective**: Verify OTP verification creates upload session

**Steps**:

1. Copy OTP code from console log (e.g., 123456)
   
2. Back in browser, OTP field should be ready
   
3. Enter OTP code: 123456
   
4. Click "Verify & Login"
   
**Expected Result**:
```json
{
  "success": true,
  "data": {
    "session_id": "VUS-000001",
    "session_token": "eyJhbG...",
    "vendor_id": "VND-000001",
    "vendor_name": "John Doe",
    "company_name": "Test Company Inc",
    "expires_at": "2026-09-19T...",
    "valid_for_hours": 24,
    "message": "OTP verified successfully..."
  }
}
```

**Verification**:
- ✓ Session created (24-hour validity)
- ✓ Session token returned
- ✓ Vendor info in response
- ✓ Redirects to /vendor/dashboard

---

### Test 7: Vendor Dashboard Shows Own Data

**Objective**: Verify vendor sees only their session data

**Steps**:

1. Should be automatically redirected to /vendor/dashboard
   
2. Verify dashboard shows:
   - Company: Test Company Inc
   - Vendor ID: VND-000001
   - Email: vendor1@company.com
   - Session expiry countdown
   - "Session expires in 23 hours 59 minutes"
   - Green/yellow/red status indicator
   
**Expected Display**:
```
VENDOR DASHBOARD
Company: Test Company Inc
Vendor ID: VND-000001
Email: vendor1@company.com

Session Status: ACTIVE ✓
Files Uploaded: 0
Session Expires: 23h 59m

Quick Actions:
- Upload Configurations
- View Upload History
- Logout
```

**Verification**:
- ✓ Only vendor's own data displayed
- ✓ Session info accurate
- ✓ No other vendor data visible
- ✓ No admin features visible
- ✓ Logout button available

---

### Test 8: Vendor Password Login (Alternative)

**Objective**: Verify password-based login works

**Steps**:

1. Logout from vendor dashboard
   - Clears vendor_session_token
   
2. Go to http://localhost:5173/vendor/login
   
3. Click "Password Login" tab
   
4. Enter credentials:
   ```
   Email: vendor1@company.com
   Password: SecurePass123
   ```
   
5. Click "Login"
   
**Expected Result**:
```json
{
  "success": true,
  "data": {
    "session_id": "VUS-000002",
    "session_token": "...",
    "vendor_id": "VND-000001",
    "login_method": "PASSWORD",
    "message": "Login successful..."
  }
}
```

**Verification**:
- ✓ Password verified against hash
- ✓ Session created for password login
- ✓ OTP not required
- ✓ Redirects to /vendor/dashboard

---

### Test 9: Admin Rejects Another Vendor

**Objective**: Verify rejected vendors cannot access

**Steps**:

1. Register another vendor
   ```
   Email: vendor2@company.com
   Company: Rejected Inc
   Contact: Jane Smith
   ```
   
2. Login as Admin
   
3. Go to Vendor Management
   
4. Find vendor2, click "Reject"
   
5. Add note: "Does not meet compliance requirements"
   
6. Click "Reject Vendor"
   
**Expected Result**:
```json
{
  "success": true,
  "data": {
    "decision": "REJECTED",
    "message": "Vendor rejected successfully"
  }
}
```

**Verification**:
- ✓ Vendor status = "REJECTED"
- ✓ Rejection email sent
- ✓ Rejection notes recorded

---

### Test 10: Rejected Vendor Cannot Login

**Objective**: Verify permanently rejected vendors stay locked out

**Steps**:

1. Try to login as vendor2
   - Email: vendor2@company.com
   
2. Try OTP request
   
**Expected Result**:
```json
{
  "success": false,
  "error": {
    "code": "VENDOR_NOT_APPROVED",
    "message": "Your vendor registration has not been approved..."
  }
}
```

**Verification**:
- ✓ 403 Forbidden
- ✓ REJECTED status persists
- ✓ Cannot be bypassed by retrying

---

### Test 11: Admin Suspends Vendor

**Objective**: Verify vendor suspension works

**Steps**:

1. Login as Admin
   
2. Go to Vendor Management
   
3. Find vendor1, click "Suspend"
   
4. Confirm suspension
   
**Expected Result**:
- Vendor approval_status = "SUSPENDED"

**Verification**:
- ✓ Vendor appears in "Suspended" count on dashboard

---

### Test 12: Suspended Vendor Cannot Access

**Objective**: Verify suspended vendors are locked out

**Steps**:

1. Logout vendor1 session
   
2. Try to login as vendor1
   
**Expected Result**:
```json
{
  "success": false,
  "error": {
    "code": "VENDOR_NOT_APPROVED",
    "message": "Your vendor account has been suspended..."
  }
}
```

**Verification**:
- ✓ SUSPENDED status blocks access
- ✓ Friendly error message

---

## Complete Flow Test Checklist

### Registration Phase
- [ ] Vendor can register (creates PENDING account)
- [ ] Admin notification sent
- [ ] Request ID provided for tracking
- [ ] Email validation works

### Blocking Phase
- [ ] PENDING vendors cannot request OTP
- [ ] PENDING vendors cannot login
- [ ] Friendly error message shown
- [ ] Rate limiting works (1 OTP per 60 seconds)

### Approval Phase
- [ ] Admin sees pending requests
- [ ] Admin can approve vendor
- [ ] Admin can reject vendor
- [ ] Admin can suspend vendor
- [ ] Approval emails sent
- [ ] Rejection emails sent

### Access Phase (Approved)
- [ ] Vendor can request OTP
- [ ] OTP sent to email
- [ ] OTP verification works
- [ ] Session token created
- [ ] Vendor redirected to dashboard
- [ ] Session expires in 24 hours

### Alternative Access (Password)
- [ ] Vendor can set password during registration
- [ ] Vendor can login with password
- [ ] Password verified against hash
- [ ] Session created for password login
- [ ] Different login methods both work

### Dashboard Phase
- [ ] Vendor sees own dashboard
- [ ] Only vendor's data displayed
- [ ] No other vendor data visible
- [ ] No admin features visible
- [ ] Session expiry shown
- [ ] Logout works
- [ ] Clears vendor_session_token

### Rejection Phase
- [ ] REJECTED vendors cannot access
- [ ] Status persists (not retryable)
- [ ] Error message clear

### Suspension Phase
- [ ] Admin can suspend vendor
- [ ] SUSPENDED vendors cannot access
- [ ] Status persists until unsuspended

---

## Error Scenarios

### Scenario 1: Invalid OTP Code
```
Input: 999999
Expected: 401 INVALID_OTP
Message: "Invalid OTP code"
```

### Scenario 2: Expired OTP
```
Wait 11+ minutes after OTP sent
Try to verify
Expected: 404 OTP_NOT_FOUND
Message: "No valid OTP found"
```

### Scenario 3: Too Many OTP Attempts
```
Submit wrong OTP 5+ times
Expected: 403 TOO_MANY_ATTEMPTS
Message: "Too many verification attempts"
```

### Scenario 4: Wrong Password
```
Email: vendor1@company.com
Password: WrongPassword
Expected: 401 INVALID_PASSWORD
Message: "Invalid email or password"
```

### Scenario 5: Weak Password
```
Password: "short"
Expected: 400 WEAK_PASSWORD
Message: "Password must be at least 8 characters"
```

### Scenario 6: Non-existent Vendor
```
Email: nonexistent@company.com
Expected: 404 VENDOR_NOT_FOUND
Message: "Vendor not found"
```

---

## Performance Expectations

### Response Times (Target)

| Operation | Time |
|-----------|------|
| Register vendor | < 500ms |
| Request OTP | < 1000ms |
| Verify OTP | < 500ms |
| Password login | < 500ms |
| Get vendor dashboard | < 500ms |

### Session Performance

| Metric | Target |
|--------|--------|
| OTP validity | 10 minutes |
| Session validity | 24 hours |
| OTP retry cooldown | 60 seconds |
| Rate limit | 1 OTP per minute |

---

## Monitoring & Logs

### Console Output Should Show

**Registration**:
```
[ADMIN_NOTIFICATION] New Vendor Registration
To: admin@example.com
Vendor: John Doe (Test Company Inc)
Action: Admin approval required
```

**Approval**:
```
[VENDOR_APPROVAL] Vendor Approved
To: vendor1@company.com
Status: APPROVED
```

**OTP Request**:
```
[CONSOLE] OTP Email
To: vendor1@company.com
Code: 123456
Expires: 10 minutes
```

### Database Verification

**Check vendor status**:
```sql
SELECT vendor_id, email, approval_status, created_at 
FROM vendor_users 
WHERE email = 'vendor1@company.com';

-- Expected
VND-000001, vendor1@company.com, APPROVED, 2026-09-18...
```

**Check OTP records**:
```sql
SELECT otp_id, vendor_id, is_used, expires_at 
FROM vendor_otps 
WHERE vendor_id = 1;
```

**Check sessions**:
```sql
SELECT session_id, status, expires_at 
FROM vendor_upload_sessions 
WHERE vendor_id = 1 
ORDER BY created_at DESC 
LIMIT 5;
```

---

## Troubleshooting

### Issue: OTP email not appearing
**Solution**:
1. Check console for `[CONSOLE] OTP Email` log
2. If not there, backend in console mode (SMTP not configured)
3. Configure Gmail App Password in .env
4. See EMAIL_CONFIGURATION_GUIDE.md

### Issue: Session token not storing
**Solution**:
1. Check browser localStorage for `vendor_session_token`
2. Open DevTools → Application → LocalStorage
3. Should see token after OTP verification

### Issue: Dashboard not loading
**Solution**:
1. Check URL: should be `/vendor/dashboard`
2. Check vendor_session_token in localStorage
3. Check backend logs for API errors
4. Verify session hasn't expired (24 hours)

### Issue: Admin dashboard not showing vendors
**Solution**:
1. Verify logged in as ADMIN role
2. Check Organization ID matches
3. Check vendor status: should show in appropriate count
4. Verify VENDOR_VIEW permission assigned

---

## Success Criteria

✅ All tests pass
✅ Complete registration → approval → login flow works
✅ Both OTP and password login work
✅ Vendor can access dashboard
✅ Only vendor's own data visible
✅ Admin approval workflow functional
✅ Email notifications work (console mode)
✅ Rejection/suspension prevent access
✅ No errors in browser console
✅ No errors in backend logs

---

**Test Status**: Ready for testing

**Estimated Duration**: 30-45 minutes for full test run

**Required**: Backend and frontend running simultaneously

