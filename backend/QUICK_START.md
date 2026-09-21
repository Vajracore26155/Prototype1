# VAJRA TATVA - Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Setup Database
```powershell
.\setup_database.ps1
```

This will:
- Check if Alembic is installed
- Run all database migrations
- Create all tables including vendor tables

### Step 2: Start Server
```powershell
.\start_server.ps1
```

This will:
- Activate virtual environment (if exists)
- Check for .env file
- Start server on http://127.0.0.1:8000

### Step 3: Access Application
- **API Docs**: http://127.0.0.1:8000/docs
- **Frontend**: http://localhost:5173 (if running)
- **Health Check**: http://127.0.0.1:8000/health

---

## 📋 Manual Setup (Alternative)

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Configure Environment
```powershell
# Copy example environment file
Copy-Item .env.example .env

# Edit .env with your settings
notepad .env
```

### 3. Run Migrations
```powershell
alembic upgrade head
```

### 4. Start Server
```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

---

## 🔧 Configuration

### Required Settings (.env)
```env
# Database
DATABASE_URL=sqlite:///./tatva.db

# JWT
JWT_SECRET_KEY=your-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Optional Settings (Email/Redis)
```env
# SMTP (for vendor OTP emails)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@vajra-security.com
FROM_NAME=VAJRA Security System

# Redis (for caching, optional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

---

## 🧪 Testing

### Run All Tests
```powershell
python run_all_tests.py
```

### Run Security Tests Only
```powershell
python run_security_tests.py
```

### Verify Test Readiness
```powershell
python verify_test_readiness.py
```

---

## 📊 API Endpoints

### Core Endpoints
- `POST /api/auth/login` - User authentication
- `GET /api/configurations` - List configurations
- `POST /api/upload` - Upload configuration
- `POST /api/audits/{config_id}/run` - Run security audit
- `GET /api/audits/{audit_id}` - Get audit results

### Vendor Endpoints (Public)
- `POST /api/vendor/register` - Register as vendor
- `POST /api/vendor/request-otp` - Request OTP code
- `POST /api/vendor/verify-otp` - Verify OTP and get session

### Vendor Upload Endpoints (Authenticated)
- `POST /api/vendor/upload/configuration` - Upload config
- `GET /api/vendor/upload/session` - Check session
- `DELETE /api/vendor/upload/session` - Logout

### Admin Vendor Management
- `GET /api/admin/vendor-requests` - List vendor requests
- `POST /api/admin/vendor-requests/{id}/decide` - Approve/reject
- `GET /api/admin/vendors` - List all vendors
- `GET /api/admin/vendor-activity` - Monitor activity
- `GET /api/admin/vendor-sessions` - View active sessions

---

## 🔐 Default Users

### Create Admin User
```python
# Run in Python shell
from app.database import SessionLocal
from app.database.models import User, Organization
from app.auth.security import hash_password

db = SessionLocal()

# Create organization
org = Organization(name="Default Org", org_code="ORG001")
db.add(org)
db.commit()

# Create admin user
admin = User(
    user_id="USR-000001",
    email="admin@example.com",
    name="Admin User",
    password_hash=hash_password("admin123"),
    role="ADMIN",
    organization_id=org.id,
    permissions=["AUDIT_VIEW", "AUDIT_RUN", "CONFIG_UPLOAD", "ADMIN_ACCESS"]
)
db.add(admin)
db.commit()
print(f"Created admin user: {admin.email}")
```

---

## 🐛 Troubleshooting

### Issue: Server Won't Start - Unicode Error
**Solution**: Already fixed! All emoji characters replaced with ASCII-safe alternatives.

### Issue: Database Not Found
**Solution**: Run `alembic upgrade head` to create tables.

### Issue: Import Errors
**Solution**: Install dependencies with `pip install -r requirements.txt`

### Issue: Port Already in Use
**Solution**: 
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace PID)
taskkill /F /PID <PID>
```

### Issue: SMTP Errors
**Solution**: Email service runs in console mode if SMTP not configured. Set SMTP variables in .env for production.

### Issue: Redis Connection Failed
**Solution**: Redis is optional. Application falls back to in-memory storage if Redis is unavailable.

---

## 📚 Documentation

- **IMPLEMENTATION_COMPLETE.md** - Full implementation details
- **API_INTEGRATION_GUIDE.md** - Frontend integration guide
- **SECURITY_TESTING.md** - Security test documentation
- **ENCODING_FIX.md** - Windows encoding fix details
- **STARTUP_FIX.md** - SQLAlchemy metadata fix

---

## 🎯 Next Steps

1. ✅ Start the server
2. ✅ Access API documentation at /docs
3. ✅ Create organizations and users
4. ✅ Test vendor registration flow
5. ✅ Upload configurations
6. ✅ Run security audits
7. ✅ Monitor vendor activity

---

## 📞 Support

For issues or questions:
1. Check the documentation files
2. Review API docs at /docs
3. Check console logs for errors
4. Verify .env configuration

---

## ✅ Success Indicators

You'll know everything is working when:
- ✅ Server starts without errors
- ✅ /docs page loads successfully
- ✅ /health endpoint returns 200
- ✅ Can create users and organizations
- ✅ Can upload configurations
- ✅ Can run audits
- ✅ Vendor registration works
- ✅ OTP emails are sent (console or SMTP)

---

**Version**: 1.0  
**Status**: Production Ready  
**Last Updated**: January 2024
