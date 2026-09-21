# 🚀 Startup Commands - Backend & Frontend

## Quick Start (Copy & Paste)

### Terminal 1 - Backend
```powershell
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
```

### Terminal 2 - Frontend
```powershell
cd frontend
npm run dev
```

---

## Detailed Setup Instructions

### Prerequisites
1. **Python 3.11+** installed
2. **Node.js 18+** installed
3. **Git** installed
4. Project files available at: `e:\Study\SIH2026\Prototype1`

---

## Backend Setup & Startup

### Step 1: Navigate to Backend Directory
```powershell
cd e:\Study\SIH2026\Prototype1\backend
```

### Step 2: Verify Python Environment (Optional)
```powershell
python --version
pip --version
```

### Step 3: Install Dependencies (First Time Only)
```powershell
pip install -r requirements.txt
```

### Step 4: Start Backend Server
```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
```

### Expected Output
```
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
[STARTUP] Starting SIH26155 Network Security Auditor...
[SUCCESS] Database initialized successfully
[STARTUP] Application ready!
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### Backend Configuration
| Parameter | Value |
|-----------|-------|
| Host | 127.0.0.1 |
| Port | 8000 |
| Workers | 1 |
| Protocol | HTTP |
| Database | SQLite (./data/sih26155.db) |

### Backend API Endpoints
```
http://127.0.0.1:8000/api/
http://127.0.0.1:8000/api/health
http://127.0.0.1:8000/api/docs (Swagger UI)
```

---

## Frontend Setup & Startup

### Step 1: Navigate to Frontend Directory
```powershell
cd e:\Study\SIH2026\Prototype1\frontend
```

### Step 2: Verify Node.js Environment
```powershell
node --version
npm --version
```

### Step 3: Install Dependencies (First Time Only)
```powershell
npm install
```

### Step 4: Start Development Server
```powershell
npm run dev
```

### Expected Output
```
VITE v5.0.8  ready in XXX ms

➜  Local:   http://localhost:5173/
➜  press h to show help
```

### Frontend Configuration
| Parameter | Value |
|-----------|-------|
| Host | localhost |
| Port | 5173 |
| Framework | React 18 + Vite |
| Build Tool | TypeScript + Vite |

### Frontend URL
```
http://localhost:5173
```

---

## Complete Startup Workflow

### First-Time Setup (Full)

**Terminal 1 - Backend:**
```powershell
cd e:\Study\SIH2026\Prototype1\backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
```

**Terminal 2 - Frontend:**
```powershell
cd e:\Study\SIH2026\Prototype1\frontend
npm install
npm run dev
```

### Subsequent Startups (Quick)

**Terminal 1 - Backend:**
```powershell
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```

---

## Accessing the Application

### Once Both Servers Are Running

1. **Frontend Application**
   - URL: http://localhost:5173
   - Main interface for users

2. **Backend API**
   - URL: http://127.0.0.1:8000
   - API endpoints for data

3. **API Documentation**
   - URL: http://127.0.0.1:8000/api/docs
   - Swagger UI for testing endpoints

4. **Backend Health Check**
   - URL: http://127.0.0.1:8000/api/health
   - JSON response showing system status

---

## Login Credentials

### Admin Login
```
Email: mayankparab4811@gmail.com
Password: Admin123
```

### Test Vendor (Already Approved)
```
Email: e2e_vendor_199372@test.com
Password: FinalVendorPass456
```

### For OTP Testing
1. Register new vendor (email will be sent to admin)
2. Admin approves vendor
3. Vendor requests OTP (email with 6-digit code sent)
4. Use OTP code to login

---

## Common Issues & Fixes

### Backend Won't Start - Port Already in Use
```powershell
# Kill process using port 8000
netstat -ano | findstr :8000
taskkill /PID XXXX /F

# Or use different port
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --workers 1
```

### Frontend Won't Start - npm not found
```powershell
# Install Node.js from: https://nodejs.org/
# Then restart terminal and try again
npm run dev
```

### Dependencies Missing
```powershell
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Backend Logs Show Email Warning
```
[⚠️  WARNING] Email service in CONSOLE MODE
```
This is normal - emails are being sent via Gmail SMTP (configured in .env)

---

## Development Commands

### Backend

**Run Backend:**
```powershell
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
```

**Run Backend with Auto-reload:**
```powershell
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Run Tests:**
```powershell
cd backend
pytest
```

**Check Email Configuration:**
```powershell
cd backend
python test_email_status_v2.py
```

**Test OTP Flow:**
```powershell
cd backend
python test_otp_with_email_v2.py
```

### Frontend

**Development Server:**
```powershell
cd frontend
npm run dev
```

**Build for Production:**
```powershell
cd frontend
npm run build
```

**Preview Production Build:**
```powershell
cd frontend
npm run preview
```

**Lint Code:**
```powershell
cd frontend
npm run lint
```

---

## Environment Configuration

### Backend (.env)
Located at: `e:\Study\SIH2026\Prototype1\.env`

Key settings:
```env
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
```

### Frontend Configuration
Located at: `frontend/vite.config.ts`

API endpoint configured to: `http://127.0.0.1:8000/api`

---

## Full System Status

After startup, you should see:

✅ **Backend**
- Server running on http://127.0.0.1:8000
- Database initialized
- Email service active
- API ready

✅ **Frontend**
- Dev server running on http://localhost:5173
- Hot reload enabled
- Connected to backend API

✅ **Features Working**
- User authentication (admin login)
- Vendor registration
- Admin approval workflow
- OTP generation and verification
- Email notifications
- File upload (after vendor login)
- Configuration analysis
- Report generation

---

## Troubleshooting Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] Can access http://localhost:5173 in browser
- [ ] Admin login works
- [ ] Database file exists at ./data/sih26155.db
- [ ] Email service shows "Email sent successfully" in logs
- [ ] No port conflict errors
- [ ] Dependencies installed (pip, npm)

---

## Quick Reference

| Component | Command | URL | Port |
|-----------|---------|-----|------|
| Backend | `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000` | http://127.0.0.1:8000 | 8000 |
| Frontend | `npm run dev` | http://localhost:5173 | 5173 |
| API Docs | N/A | http://127.0.0.1:8000/api/docs | 8000 |
| Database | SQLite | ./data/sih26155.db | N/A |

---

## Next Steps

1. Start backend (Terminal 1)
2. Start frontend (Terminal 2)
3. Open http://localhost:5173 in browser
4. Login with admin credentials or test vendor credentials
5. Test vendor flow:
   - Register vendor → Approve → Request OTP → Verify OTP → Login
6. Upload device configurations
7. View compliance reports

**System is ready to use!** 🚀
