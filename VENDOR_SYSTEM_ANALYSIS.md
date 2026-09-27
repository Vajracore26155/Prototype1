# 📊 Vendor System Analysis & Requirements

## Current System Status

### Total Vendors in System: **19**

| Status | Count |
|--------|-------|
| **APPROVED** | 17 |
| **PENDING** | 1 |
| **REJECTED** | 1 |

### Vendor List (Ordered by Registration Date)

| ID | Vendor ID | Email | Contact | Company | Status | Has Password |
|----|----|-------|---------|---------|--------|---|
| 19 | VND-000019 | siddharthpraj5972@gmail.com | Siddarth | Juniper | APPROVED | ❌ |
| 18 | VND-000018 | kurzo4253@gmail.com | demo doe | demozz | PENDING | ❌ |
| 17 | VND-000017 | nipunalwala@gmail.com | Nipun Alwala | PONDACORP | APPROVED | ❌ |
| 16 | VND-000016 | arya040407@gmail.com | Zhongaaa Bhongaa | JongaBongo Limited | APPROVED | ❌ |
| 15 | VND-000015 | email_test_345641@test.com | Email Test User | Email Test Corp | APPROVED | ✅ |
| 14 | VND-000014 | noobd5427@gmasil.com | nadu | galaxypav | APPROVED | ❌ |
| 13 | VND-000013 | ndhmhatre@gmail.com | Nada Mhatre | Galaxy Vadapav | APPROVED | ❌ |
| 12 | VND-000012 | kingmp142@gmail.com | Mayank Demo | EnhanceMagic | APPROVED | ❌ |
| 11 | VND-000011 | hirahulsawant@gmail.com | Rahul Sawant | Bubblewrap 2.0 | APPROVED | ❌ |
| 10 | VND-000010 | sawantrahul206@gmail.com | Rahul | Bubblewrap | APPROVED | ❌ |
| 9 | VND-000009 | rejected_645399@test.com | Rejected User | Rejected Corp | REJECTED | ❌ |
| 8 | VND-000008 | pending_181468@test.com | Pending User | Pending Corp | APPROVED | ❌ |
| 7 | VND-000007 | login_test_728586@test.com | Test User | Login Test Corp | APPROVED | ✅ |
| 6 | VND-000006 | e2e_vendor_199372@test.com | Test Contact | E2E Test Corp | APPROVED | ✅ |
| 5 | VND-000005 | vendor97269@test.com | Jane Smith | Test Corp | APPROVED | ✅ |
| 4 | VND-000004 | vendor73852@test.com | John Doe | Test Corp | APPROVED | ❌ |
| 3 | VND-000003 | parabami1@gmail.com | Demoss | Fortinet | APPROVED | ❌ |
| 2 | VND-000002 | enhancemagic@gmail.com | Demo | Pal Alto | APPROVED | ❌ |
| 1 | VND-000001 | vendor@test.com | Test Contact | Test Company | APPROVED | ❌ |

**Key Finding:** Only 5 vendors have passwords set. Most vendors (14) don't have passwords!

---

## Data Storage Location

### Database File
```
Location: ./data/sih26155.db
Type: SQLite 3
Size: ~500KB
```

### Main Table: `vendor_users`

```sql
CREATE TABLE vendor_users (
    id                   INTEGER PRIMARY KEY
    vendor_id            VARCHAR(50) UNIQUE      -- VND-000001
    email                VARCHAR(255) UNIQUE     -- Email for login
    password_hash        VARCHAR(255)            -- Optional password storage
    company_name         VARCHAR(255)
    contact_name         VARCHAR(255)
    phone                VARCHAR(50)
    
    email_verified       BOOLEAN
    verification_token   VARCHAR(255)
    verified_at          DATETIME
    
    approval_status      VARCHAR(50)             -- PENDING, APPROVED, REJECTED, SUSPENDED
    approved_by          VARCHAR(255)
    approved_at          DATETIME
    rejection_reason     TEXT
    
    organization_id      INTEGER (Foreign Key)
    devices              JSON
    vendor_metadata      JSON
    
    last_otp_sent        DATETIME
    otp_attempts         INTEGER
    is_active            BOOLEAN
    
    created_at           DATETIME
    updated_at           DATETIME
)
```

### Related Tables
- `vendor_otps` - OTP codes (one-time passwords)
- `vendor_upload_sessions` - Active upload sessions
- `vendor_approval_requests` - Registration requests

---

## Current Authentication Flow

### Phase 1: Registration ✅ (Working)
1. Vendor enters email, company, contact info
2. System generates registration request
3. Admin approves registration
4. Vendor can now request OTP

### Phase 2: OTP Login ✅ (Working)
1. Vendor requests OTP via email
2. System sends 6-digit code
3. Vendor verifies OTP
4. 24-hour upload session created

### Phase 3: MISSING ⚠️ (Needs Implementation)
1. **NO option to set username/password during registration**
2. Vendor must use OTP every single time
3. No way to change password after approval

---

## What You're Asking For

### Requirements Analysis

✅ **You want to:**

1. **Let vendors set username & password during registration**
   - Not mandatory, but available option
   - Better than only OTP-based login

2. **Provide vendor settings panel**
   - Three-dot menu (⋮) in vendor dashboard
   - Shows vendor profile information
   - Allows changing username/password
   - Shows account details

3. **Enable password-based login**
   - Vendor logs in with email + password
   - No need for OTP each time
   - Faster, more convenient

4. **Keep OTP as backup option**
   - For security
   - For password reset
   - Optional enhanced authentication

---

## Implementation Plan

### Phase 1: Backend Changes

#### 1. Add `username` field to VendorUser model
```python
username = Column(String(100), unique=True, nullable=True)
# Vendor can choose their own username
```

#### 2. Create vendor profile update endpoint
```
PUT /api/vendor/profile
- Update username
- Update password
- Update phone/contact info
```

#### 3. Create vendor settings endpoint
```
GET /api/vendor/settings      -- Get vendor info
PUT /api/vendor/settings      -- Update vendor info
POST /api/vendor/change-password
```

### Phase 2: Frontend Changes

#### 1. Registration form enhancement
- Add optional "Username" field during registration
- Add optional "Set Password" checkbox
- If checked, show password setup form

#### 2. Vendor dashboard menu
- Add three-dot menu (⋮) in top right
- Options:
  - My Profile
  - Settings
  - Change Password
  - Logout

#### 3. Vendor settings page
```
┌─────────────────────────────┐
│ Vendor Settings             │
├─────────────────────────────┤
│ Email:          vendor@...  │
│ Username:       [text]      │
│ Contact:        [text]      │
│ Phone:          [text]      │
│ Company:        [text]      │
├─────────────────────────────┤
│ Change Password:            │
│ Old Password: [______]      │
│ New Password: [______]      │
│ Confirm:      [______]      │
│               [Save]        │
└─────────────────────────────┘
```

---

## Architecture Overview

### Current System
```
Vendor Registration
    ↓
OTP Login (Every time)
    ↓
Upload Session
    ↓
Upload Files
```

### Proposed System
```
Vendor Registration (with optional password setup)
    ↓
Two Login Options:
  ├─ Email + Password (new)
  └─ OTP Login (backup)
    ↓
Upload Session
    ↓
Vendor Settings/Profile (new)
    ├─ Change Username
    ├─ Change Password
    └─ View Profile
    ↓
Upload Files
```

---

## Database Changes Needed

### Add to VendorUser model
```python
# Username option
username = Column(String(100), unique=True, nullable=True)

# Track password setup
password_set_at = Column(DateTime, nullable=True)
password_changed_at = Column(DateTime, nullable=True)

# Last login tracking
last_login = Column(DateTime, nullable=True)
last_login_method = Column(String(50), nullable=True)  # 'password' or 'otp'
```

### Migration Script Needed
- Add columns to existing `vendor_users` table
- Set default values for existing vendors
- Create index on username

---

## Summary of Vendor Types

### By Registration Status
- **APPROVED** (17): Can login and upload
- **PENDING** (1): Waiting for admin approval
- **REJECTED** (1): Denied access

### By Login Capability
- **With Password** (5): Can use email + password
- **Without Password** (14): Only OTP login available
- **New Requirement**: All vendors should have option to set password

### By Organization
- **Different companies** represented
- **Different vendors/partners** for same organization
- All uploading configurations

---

## Next Steps

1. **Database Migration** - Add username and password fields
2. **Backend APIs** - Create settings/profile endpoints
3. **Frontend UI** - Add settings page and vendor menu
4. **Registration Form** - Add optional password setup
5. **Testing** - Verify all login methods work

---

## Questions to Clarify

1. Should username be required or optional during registration?
2. Should vendors be able to change their email address?
3. What's the minimum password length?
4. Should there be password complexity requirements?
5. Should we keep OTP as an option or make it backup-only?

---

## Files to Check/Modify

### Backend
- `backend/app/database/models.py` - Add fields
- `backend/app/api/vendor.py` - Add endpoints
- `backend/app/services/auth_service.py` - Update auth logic

### Frontend
- `frontend/src/pages/VendorDashboard.tsx` - Add menu
- `frontend/src/pages/VendorSettings.tsx` - New page
- `frontend/src/pages/VendorRegister.tsx` - Update form
- `frontend/src/components/VendorHeader.tsx` - Add menu

---

**Status: Ready for Implementation** ✅

Once you confirm the requirements and answer the clarification questions, I'll implement everything.
