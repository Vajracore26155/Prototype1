# 🚀 Backend & Frontend Startup Guide

## TL;DR - Quick Start

### Terminal 1 (Backend)
```powershell
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
```

### Terminal 2 (Frontend)
```powershell
cd frontend
npm run dev
```

### Browser
```
http://localhost:5173
```

---

## Full Details

### Backend Startup

**Command:**
```powershell
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
```

**What Happens:**
- Python starts FastAPI server
- Initializes SQLite database at `./data/sih26155.db`
- Loads environment variables from `.env`
- Activates email service (Gmail SMTP)
- Listens on http://127.0.0.1:8000

**Expected Output:**
```
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
[STARTUP] Starting SIH26155 Network Security Auditor...
[SUCCESS] Database initialized successfully
[STARTUP] Application ready!
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

**Keep Running:** Yes - leave this terminal open

**API Available At:**
- Main API: http://127.0.0.1:8000/api/
- Swagger Docs: http://127.0.0.1:8000/api/docs
- Health Check: http://127.0.0.1:8000/api/health

---

### Frontend Startup

**Command:**
```powershell
cd frontend
npm run dev
```

**What Happens:**
- Vite starts React development server
- Builds TypeScript and JSX
- Enables hot module replacement (auto-reload)
- Connects to backend API
- Listens on http://localhost:5173

**Expected Output:**
```
VITE v5.0.8  ready in XXX ms

➜  Local:   http://localhost:5173/
➜  press h to show help
```

**Keep Running:** Yes - leave this terminal open

**UI Available At:**
- Main Application: http://localhost:5173

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Web Browser                            │
│          http://localhost:5173                           │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  React Frontend (Vite Development Server)         │   │
│  │  - Port: 5173                                    │   │
│  │  - Hot reload enabled                            │   │
│  │  - TypeScript + React 18                         │   │
│  └──────────────────────────────────────────────────┘   │
└────────┬────────────────────────────────────────────────┘
         │
         │ HTTP Requests
         │ JSON APIs
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│  FastAPI Backend (Uvicorn)                              │
│  - Port: 8000                                           │
│  - Host: 127.0.0.1                                      │
│  - Workers: 1                                           │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │  SQLite Database                                 │   │
│  │  ./data/sih26155.db                              │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Email Service (Gmail SMTP)                      │   │
│  │  Configured: .env                                │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## Login Credentials

### Admin Account
- **Email:** mayankparab4811@gmail.com
- **Password:** Admin123
- **Role:** Administrator
- **Access:** Full system access, approve/reject vendors

### Test Vendor (Pre-approved)
- **Email:** e2e_vendor_199372@test.com
- **Password:** FinalVendorPass456
- **Status:** APPROVED
- **Access:** Can request OTP, upload configurations

### Create New Vendor
- Visit http://localhost:5173/register
- Fill in company details
- Password will be hashed and stored
- Admin will need to approve the request
- Vendor receives email notification

---

## Complete Workflow

### 1. Start Systems
- Terminal 1: Start backend
- Terminal 2: Start frontend
- Browser: Open http://localhost:5173

### 2. Admin Login
- Use admin credentials above
- View vendor requests dashboard

### 3. Vendor Registration (Optional)
- Click "Register as Vendor"
- Fill in company information
- Submit
- Admin receives email notification

### 4. Admin Approval
- Login as admin
- View pending vendor requests
- Approve or reject

### 5. Vendor OTP Login
- Vendor requests OTP
- Email with 6-digit code sent
- Vendor enters OTP
- Creates session

### 6. Password Setup
- After OTP verification
- Set secure password
- Used for future logins

### 7. File Upload
- Vendor can upload configuration files
- System analyzes files
- Generates compliance reports

---

## Configuration Files

### Backend Configuration (`.env`)
```env
# Application
APP_ENV=development
APP_NAME=SIH26155 Network Security Auditor

# API
API_HOST=0.0.0.0
API_PORT=8000

# Database
DATABASE_URL=sqlite:///./data/sih26155.db

# Email (Gmail SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=mayankparab4811@gmail.com
SMTP_PASSWORD=itwytihnoujxirjy

# Credentials
JWT_SECRET_KEY=tatva-prod-secret-key-2026-secure-change-this-in-production-12345
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60
```

### Frontend Configuration (`vite.config.ts`)
- API Target: http://127.0.0.1:8000/api
- Port: 5173
- Host: localhost
- Hot reload: Enabled

---

## Port Management

| Service | Port | Protocol | URL |
|---------|------|----------|-----|
| Backend API | 8000 | HTTP | http://127.0.0.1:8000 |
| Frontend Dev | 5173 | HTTP | http://localhost:5173 |
| API Swagger | 8000 | HTTP | http://127.0.0.1:8000/api/docs |

**Port Conflict?**
- If port 8000 is in use: `--port 8001`
- If port 5173 is in use: `npm run dev -- --port 3000`

---

## Troubleshooting

### Backend Won't Start

**Error: "Address already in use"**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process
taskkill /PID <PID> /F

# Or use different port
python -m uvicorn app.main:app --port 8001
```

**Error: "ModuleNotFoundError"**
```powershell
cd backend
pip install -r requirements.txt
```

### Frontend Won't Start

**Error: "npm not found"**
- Install Node.js from https://nodejs.org/
- Restart terminal
- Retry `npm run dev`

**Error: "Port 5173 in use"**
```powershell
npm run dev -- --port 3000
```

### Can't Connect to Backend

**Frontend shows connection error**
- Verify backend is running on port 8000
- Check firewall settings
- Verify network connectivity

**Test connection:**
```powershell
# Should return API status
Invoke-WebRequest http://127.0.0.1:8000/api/health
```

### Database Issues

**Error: "Database locked"**
- Close other processes accessing database
- Restart backend

**Database not initializing**
- Check `./data/` directory exists
- Verify write permissions
- Check `.env` DATABASE_URL path

---

## Development Tips

### Hot Reload
Both frontend and backend support hot reload:
- **Frontend:** Edit React files → auto-refresh in browser
- **Backend:** Edit Python files → auto-reload (if `--reload` flag)

### Enable Backend Auto-reload
```powershell
python -m uvicorn app.main:app --reload
```

### Debug Backend
Check terminal 1 for:
- API request logs
- Database queries
- Email sending status
- Error messages

### Debug Frontend
Use browser DevTools (F12):
- Console tab for JavaScript errors
- Network tab for API calls
- Application tab for storage/cookies

### Test API Endpoints
Use Swagger UI:
- Open: http://127.0.0.1:8000/api/docs
- Try all endpoints
- View request/response format

---

## Performance

### Expected Startup Times
- Backend: 2-5 seconds
- Frontend: 3-10 seconds
- First load in browser: 5-15 seconds

### System Requirements
- **RAM:** 2GB minimum, 4GB recommended
- **Disk:** 500MB for code + 100MB for database
- **CPU:** Any modern processor
- **Python:** 3.11+
- **Node.js:** 18+

---

## Stopping the System

### Stop Backend
```powershell
# In Terminal 1 (Backend)
Ctrl+C
# Or type: Y and Enter
```

### Stop Frontend
```powershell
# In Terminal 2 (Frontend)
Ctrl+C
# Or type: Y and Enter
```

### Stop All
- Close both terminals
- System stops

---

## Next Steps

1. ✅ Start backend (Terminal 1)
2. ✅ Start frontend (Terminal 2)
3. ✅ Open http://localhost:5173
4. ✅ Login with admin credentials
5. ✅ Explore the system
6. ✅ Test vendor workflow

---

## Useful Resources

### Documentation
- Backend API: http://127.0.0.1:8000/api/docs
- Project README: See `README.md`
- Startup Guide: `STARTUP_COMMANDS.md`

### Test Files
```
backend/test_otp_with_email_v2.py - Test OTP flow
backend/test_email_status_v2.py - Check email config
backend/test_full_flow.py - Full vendor flow test
```

### Configuration
- Backend config: `.env`
- Frontend config: `frontend/vite.config.ts`

---

## Support

If you encounter issues:

1. Check terminal output for error messages
2. Verify all dependencies are installed
3. Ensure ports 8000 and 5173 are available
4. Check `.env` file configuration
5. Review `TROUBLESHOOTING.md`

---

## Status Check

```powershell
# Terminal 1 Output Should Show:
✅ Uvicorn running on http://127.0.0.1:8000
✅ [SUCCESS] Database initialized
✅ [STARTUP] Application ready!

# Terminal 2 Output Should Show:
✅ ➜  Local:   http://localhost:5173/

# Browser Should Show:
✅ VAJRA System UI (Login page)

# After Login:
✅ Dashboard visible
✅ Vendor requests list
✅ System functionality
```

---

**Ready to start?** 🚀 Follow the Quick Start commands above!

**Questions?** Check `STEP_BY_STEP_STARTUP.txt` for detailed walkthrough.
