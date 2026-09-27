# VAJRA TATVA - API Integration Guide

Quick reference for integrating frontend with the vendor system.

## 🔑 Authentication

### Internal Users (Admin)
```javascript
// Login
POST /api/auth/login
{
  "email": "admin@example.com",
  "password": "password"
}
Response: { "access_token": "jwt_token", ... }

// Use token in headers
headers: {
  "Authorization": "Bearer jwt_token"
}
```

### Vendor Users
```javascript
// No login required initially
// Get session token via OTP verification
headers: {
  "X-Vendor-Session-Token": "session_token"
}
```

## 📝 Vendor Registration Flow

### Step 1: Register
```javascript
POST /api/vendor/register
{
  "email": "vendor@company.com",
  "company_name": "ACME Corp",
  "contact_name": "John Doe",
  "phone": "+1-555-0100",
  "organization_id": 1
}

Response:
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

### Step 2: Admin Approval (Admin Portal)
```javascript
// List pending requests
GET /api/admin/vendor-requests?status=PENDING
Headers: { "Authorization": "Bearer admin_token" }

Response:
{
  "success": true,
  "data": {
    "requests": [
      {
        "request_id": "VAR-000001",
        "vendor_id": "VND-000001",
        "vendor_email": "vendor@company.com",
        "company_name": "ACME Corp",
        "status": "PENDING",
        ...
      }
    ]
  }
}

// Approve vendor
POST /api/admin/vendor-requests/VAR-000001/decide
Headers: { "Authorization": "Bearer admin_token" }
{
  "approved": true,
  "notes": "Verified and approved"
}
```

### Step 3: Request OTP (Vendor)
```javascript
POST /api/vendor/request-otp
{
  "vendor_email": "vendor@company.com"
}

Response:
{
  "success": true,
  "data": {
    "otp_id": "OTP-000001",
    "expires_at": "2024-01-15T10:10:00Z",
    "expires_in_minutes": 10,
    "message": "OTP sent to your email"
  }
}
// Vendor receives email with 6-digit code
```

### Step 4: Verify OTP (Vendor)
```javascript
POST /api/vendor/verify-otp
{
  "vendor_email": "vendor@company.com",
  "otp_code": "123456"
}

Response:
{
  "success": true,
  "data": {
    "session_id": "VUS-000001",
    "session_token": "abc123...",
    "vendor_id": "VND-000001",
    "expires_at": "2024-01-16T10:00:00Z",
    "valid_for_hours": 24,
    "message": "OTP verified successfully"
  }
}
// Store session_token for uploads
```

## 📤 Configuration Upload

### Single Upload
```javascript
POST /api/vendor/upload/configuration
Headers: { "X-Vendor-Session-Token": "session_token" }
FormData:
  file: <configuration_file>
  device_id: "DEV-000001" (optional)

Response:
{
  "success": true,
  "data": {
    "config_id": "CFG-000123",
    "filename": "router-config.txt",
    "detected_vendor": "Cisco",
    "confidence": 0.95,
    "uploaded_by": {
      "vendor_id": "VND-000001",
      "company": "ACME Corp"
    },
    "session_info": {
      "files_uploaded": 1,
      "expires_at": "2024-01-16T10:00:00Z"
    }
  }
}
```

### Bulk Upload
```javascript
POST /api/vendor/upload/bulk
Headers: { "X-Vendor-Session-Token": "session_token" }
FormData:
  files: [<file1>, <file2>, <file3>, ...]

Response:
{
  "success": true,
  "data": {
    "uploaded": [
      { "config_id": "CFG-001", "filename": "router1.txt" },
      { "config_id": "CFG-002", "filename": "router2.txt" }
    ],
    "failed": [
      { "filename": "router3.txt", "error": "Duplicate file" }
    ],
    "summary": {
      "uploaded_count": 2,
      "failed_count": 1
    }
  }
}
```

### Check Session
```javascript
GET /api/vendor/upload/session
Headers: { "X-Vendor-Session-Token": "session_token" }

Response:
{
  "success": true,
  "data": {
    "session_id": "VUS-000001",
    "vendor": {
      "vendor_id": "VND-000001",
      "company": "ACME Corp"
    },
    "status": "ACTIVE",
    "expires_at": "2024-01-16T10:00:00Z",
    "upload_count": 3,
    "files_uploaded": ["CFG-001", "CFG-002", "CFG-003"]
  }
}
```

### Logout
```javascript
DELETE /api/vendor/upload/session
Headers: { "X-Vendor-Session-Token": "session_token" }

Response:
{
  "success": true,
  "data": {
    "message": "Session revoked",
    "uploads_completed": 3
  }
}
```

## 🎛️ Admin Vendor Management

### View All Vendors
```javascript
GET /api/admin/vendors?status=APPROVED
Headers: { "Authorization": "Bearer admin_token" }

Response:
{
  "success": true,
  "data": {
    "vendors": [
      {
        "vendor_id": "VND-000001",
        "company_name": "ACME Corp",
        "email": "vendor@company.com",
        "approval_status": "APPROVED",
        "upload_sessions": 5,
        "approved_at": "2024-01-15T09:00:00Z"
      }
    ],
    "total": 1
  }
}
```

### Monitor Activity
```javascript
GET /api/admin/vendor-activity?days=30
Headers: { "Authorization": "Bearer admin_token" }

Response:
{
  "success": true,
  "data": {
    "vendors": [
      {
        "vendor_id": "VND-000001",
        "company": "ACME Corp",
        "sessions_count": 5,
        "active_sessions": 1,
        "total_uploads": 47,
        "last_activity": "2024-01-15T14:30:00Z"
      }
    ],
    "summary": {
      "total_uploads": 47,
      "active_vendors": 1
    }
  }
}
```

### View Active Sessions
```javascript
GET /api/admin/vendor-sessions
Headers: { "Authorization": "Bearer admin_token" }

Response:
{
  "success": true,
  "data": {
    "sessions": [
      {
        "session_id": "VUS-000001",
        "vendor": {
          "vendor_id": "VND-000001",
          "company": "ACME Corp"
        },
        "created_at": "2024-01-15T10:00:00Z",
        "expires_at": "2024-01-16T10:00:00Z",
        "upload_count": 3
      }
    ]
  }
}
```

### Suspend Vendor
```javascript
PATCH /api/admin/vendors/VND-000001/suspend
Headers: { "Authorization": "Bearer admin_token" }

Response:
{
  "success": true,
  "data": {
    "vendor_id": "VND-000001",
    "status": "SUSPENDED",
    "sessions_revoked": 1,
    "message": "Vendor suspended"
  }
}
```

## ⚠️ Error Handling

All errors follow this format:
```javascript
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message"
  }
}
```

Common error codes:
- `VENDOR_NOT_FOUND` - Vendor doesn't exist
- `VENDOR_NOT_APPROVED` - Vendor not approved yet
- `INVALID_OTP` - Wrong OTP code
- `SESSION_EXPIRED` - Upload session expired
- `DUPLICATE_FILE` - File already uploaded
- `TOO_MANY_REQUESTS` - Rate limit exceeded

## 📱 Frontend Implementation Example (React)

```jsx
// VendorRegistration.jsx
const registerVendor = async (formData) => {
  const response = await fetch('/api/vendor/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(formData)
  });
  const data = await response.json();
  if (data.success) {
    alert('Registration submitted! Check email for approval.');
  }
};

// VendorOTP.jsx
const requestOTP = async (email) => {
  await fetch('/api/vendor/request-otp', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ vendor_email: email })
  });
  alert('OTP sent to your email!');
};

const verifyOTP = async (email, code) => {
  const response = await fetch('/api/vendor/verify-otp', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ vendor_email: email, otp_code: code })
  });
  const data = await response.json();
  if (data.success) {
    localStorage.setItem('vendorToken', data.data.session_token);
    return data.data.session_token;
  }
};

// VendorUpload.jsx
const uploadConfig = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('/api/vendor/upload/configuration', {
    method: 'POST',
    headers: {
      'X-Vendor-Session-Token': localStorage.getItem('vendorToken')
    },
    body: formData
  });
  
  const data = await response.json();
  return data;
};
```

## 🔒 Security Checklist

- [ ] Always use HTTPS in production
- [ ] Store session tokens securely
- [ ] Clear tokens on logout
- [ ] Handle token expiration gracefully
- [ ] Validate file types before upload
- [ ] Show clear error messages
- [ ] Implement upload progress indicators
- [ ] Add session timeout warnings

## 📊 Rate Limits

- OTP requests: 1 per minute per vendor
- OTP attempts: 5 attempts per OTP code
- Upload session: 24 hours validity
- OTP validity: 10 minutes

## 🎯 Quick Start Checklist

1. [ ] User registers as vendor
2. [ ] Admin receives email notification
3. [ ] Admin approves vendor
4. [ ] Vendor receives approval email
5. [ ] Vendor requests OTP
6. [ ] Vendor receives OTP via email
7. [ ] Vendor verifies OTP
8. [ ] Vendor uploads configurations
9. [ ] Admin monitors activity
10. [ ] Vendor logs out or session expires

---

**For full API documentation, see inline code comments in backend/app/api/vendor.py and vendor_upload.py**
