# 🔐 Authentication Setup Guide

## Overview

The Tatva Security Platform now includes a complete JWT-based authentication system with role-based access control (RBAC).

## Quick Start

### 1. Start the Application

**Backend (Terminal 1):**
```powershell
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Frontend (Terminal 2):**
```powershell
cd frontend
npm run dev
```

### 2. Access the Application

Open your browser and navigate to: **http://localhost:5173**

You will be redirected to the login page.

## First-Time Setup

### Option 1: Create Admin User (If No Users Exist)

If the database is empty, run the setup script:

```powershell
cd backend
python scripts/create_admin.py
```

**Default Admin Credentials:**
- Email: `admin@tatva.security`
- Password: `admin123`

⚠️ **IMPORTANT:** Change this password immediately after first login!

### Option 2: Register a New Organization

1. Navigate to **http://localhost:5173/register**
2. Fill in the registration form:
   - **Full Name:** Your name
   - **Username:** Unique username
   - **Email:** Your email address
   - **Organization Name:** Your company/organization name
   - **Password:** Secure password (min 6 characters)
   - **Confirm Password:** Re-enter password

3. Click "Create Account"
4. You will be automatically logged in as an **ADMIN** of your organization

## User Roles & Permissions

The system supports 5 roles with hierarchical permissions:

### 1. **SUPER_ADMIN** (System Administrator)
- Full system access
- Manage all organizations
- System configuration
- All permissions

### 2. **ADMIN** (Organization Admin)
- Manage organization users
- Upload configurations
- Run audits
- Approve findings
- Generate reports
- View audit logs

### 3. **SECURITY_ANALYST**
- Upload configurations
- Run audits
- View and update findings
- Generate reports
- AI interpretation

### 4. **AUDITOR** (Compliance Auditor)
- Run audits
- View configurations
- View findings
- Generate compliance reports
- View audit logs

### 5. **VIEWER** (Read-Only)
- View configurations
- View audit results
- View findings
- Export reports

## Features

### ✅ Authentication Flow
- **Login:** JWT token-based authentication (60-minute expiration)
- **Register:** Create new organization with admin user
- **Logout:** Secure token invalidation
- **Auto-redirect:** Unauthenticated users redirected to login
- **Token refresh:** Automatic verification on page load

### ✅ Security Features
- **Password hashing:** Bcrypt with salt
- **JWT tokens:** Secure token generation and validation
- **Multi-tenancy:** Organization-based data isolation
- **RBAC:** Permission-based access control
- **Audit logging:** All authentication events logged
- **Token expiration:** Automatic logout after timeout
- **401 handling:** Auto-redirect on unauthorized access

### ✅ UI Components
- **Login page:** Email/password authentication
- **Register page:** Organization creation with validation
- **User profile dropdown:** Shows name, email, organization, role
- **Role badges:** Color-coded role indicators
- **Logout button:** Secure sign-out
- **Protected routes:** All dashboard routes require authentication

## API Endpoints

### Public Endpoints
- `POST /api/auth/login` - Login
- `POST /api/auth/register` - Register new organization
- `GET /health` - Health check

### Protected Endpoints
All other endpoints require authentication via `Authorization: Bearer <token>` header.

**Examples:**
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/logout` - Logout
- `POST /api/config/upload` - Upload configuration (requires CONFIG_UPLOAD permission)
- `POST /api/audits/{id}/run` - Run audit (requires AUDIT_RUN permission)
- `GET /api/configurations` - List configurations (requires CONFIG_READ permission)

## Development Notes

### Token Storage
- Tokens stored in `localStorage` as `auth_token`
- User data stored in `localStorage` as `auth_user`
- Automatic cleanup on logout

### Axios Interceptors
- **Request interceptor:** Automatically adds `Authorization` header to all API calls
- **Response interceptor:** Handles 401 errors and redirects to login

### Protected Routes
All dashboard routes are wrapped with `<ProtectedRoute>` component:
- Shows loading spinner during auth check
- Redirects to `/login` if not authenticated
- Renders page if authenticated

## Troubleshooting

### Issue: "Request failed with status code 401"
**Solution:** You need to log in. The backend requires authentication for all protected endpoints.

### Issue: "Users already exist in the database"
**Solution:** Use the register page to create a new organization, or log in with existing credentials.

### Issue: Redirected to login after page refresh
**Solution:** Your token may have expired (60-minute lifetime). Log in again.

### Issue: Can't access certain features
**Solution:** Check your user role. Some features require specific permissions (e.g., only ADMIN can delete configurations).

## Password Requirements

- Minimum 6 characters
- Recommended: Mix of uppercase, lowercase, numbers, and special characters
- Password strength indicator shows real-time validation

## Security Best Practices

1. **Change default passwords** immediately in production
2. **Use strong passwords** with mixed character types
3. **Don't share credentials** between team members
4. **Set token expiration** appropriately for your security needs
5. **Enable HTTPS** in production
6. **Monitor audit logs** for suspicious activity
7. **Regular security audits** of user permissions

## Multi-Tenancy

- Each organization is isolated
- Users can only access data from their organization
- Organization admins manage their own users
- SUPER_ADMIN can access all organizations

## Testing Authentication

### Test Login
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@tatva.security","password":"admin123"}'
```

### Test Protected Endpoint
```bash
curl -X GET http://127.0.0.1:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Test Upload with Auth
```bash
curl -X POST http://127.0.0.1:8000/api/config/upload \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@config.txt"
```

## Next Steps

After setting up authentication:

1. ✅ Log in or register
2. ✅ Update your profile (change default password if using admin account)
3. ✅ Upload network configurations
4. ✅ Run compliance audits
5. ✅ Review findings
6. ✅ Generate reports
7. ✅ Manage your organization users (Admin only)

## Support

For issues or questions:
- Check the API documentation: http://127.0.0.1:8000/docs
- Review backend logs for detailed error messages
- Check browser console for frontend errors

---

**Version:** 1.0.0  
**Last Updated:** September 18, 2026
