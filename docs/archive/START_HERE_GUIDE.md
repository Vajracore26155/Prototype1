# 🚀 START HERE - Complete Startup Guide

## Choose Your Guide

Pick the format that works best for you:

### 📄 **For Quick Copy-Paste** 
👉 **`STARTUP_CARD.txt`** - Visual reference card with exact commands
- Most concise format
- Commands ready to copy-paste
- Login credentials included
- Troubleshooting quick tips

### 🎯 **For Step-by-Step Instructions**
👉 **`STEP_BY_STEP_STARTUP.txt`** - Detailed walkthrough
- Perfect for first time setup
- Every step explained
- What to expect at each step
- Common issues and fixes
- Approximately 5-10 minutes to complete

### 📖 **For Complete Reference**
👉 **`STARTUP_COMMANDS.md`** - Full documentation
- Comprehensive guide
- All configuration details
- Development commands
- Troubleshooting section
- System architecture explained

### ⚡ **For Ultra-Quick Start**
👉 **`QUICK_STARTUP.txt`** - Minimal instructions
- Just the essentials
- Key commands only
- Ports and URLs
- Test accounts

### 📚 **For Detailed Understanding**
👉 **`README_STARTUP.md`** - In-depth guide
- Complete system overview
- Architecture diagrams
- Workflow explanations
- Performance tips
- Support resources

---

## Quick Start (30 Seconds)

### Step 1: Open Terminal 1
```powershell
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
```

### Step 2: Open Terminal 2
```powershell
cd frontend
npm run dev
```

### Step 3: Open Browser
```
http://localhost:5173
```

### Step 4: Login
```
Email: mayankparab4811@gmail.com
Password: Admin123
```

✅ **Done!** System is running.

---

## What Each Component Does

### Backend (Port 8000)
- REST API server
- Database management
- Email service
- Vendor authentication
- File processing

**Start Command:**
```powershell
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
```

### Frontend (Port 5173)
- React user interface
- Admin dashboard
- Vendor registration
- Configuration upload
- Report viewing

**Start Command:**
```powershell
cd frontend
npm run dev
```

### Browser Access
- Main app: http://localhost:5173
- API docs: http://127.0.0.1:8000/api/docs
- Health check: http://127.0.0.1:8000/api/health

---

## System Status

| Component | Port | Status | URL |
|-----------|------|--------|-----|
| Backend | 8000 | ✅ Ready | http://127.0.0.1:8000 |
| Frontend | 5173 | ✅ Ready | http://localhost:5173 |
| Database | N/A | ✅ SQLite | ./data/sih26155.db |
| Email | SMTP | ✅ Gmail | noreply@vajra-security.com |

---

## Login Credentials

### Admin Account
```
Email:    mayankparab4811@gmail.com
Password: Admin123
```

### Test Vendor
```
Email:    e2e_vendor_199372@test.com
Password: FinalVendorPass456
```

---

## First Time Setup (Dependencies)

### Backend Dependencies
```powershell
cd backend
pip install -r requirements.txt
```

### Frontend Dependencies
```powershell
cd frontend
npm install
```

Run these once, then use the startup commands above.

---

## Troubleshooting Quick Links

**Can't start backend?**
→ See: `STARTUP_COMMANDS.md` - Backend Setup section

**Can't start frontend?**
→ See: `STARTUP_COMMANDS.md` - Frontend Setup section

**Port already in use?**
→ See: `QUICK_STARTUP.txt` - Troubleshooting section

**Can't login?**
→ See: `STEP_BY_STEP_STARTUP.txt` - Verify Credentials

**Email not sending?**
→ See: `OTP_EMAIL_FIXED.md` - Email system working confirmation

---

## What You'll See

### After Backend Starts
```
✅ INFO:     Uvicorn running on http://127.0.0.1:8000
✅ [SUCCESS] Database initialized successfully
✅ [STARTUP] Application ready!
```

### After Frontend Starts
```
✅ ➜  Local:   http://localhost:5173/
✅ ➜  press h to show help
```

### In Browser (http://localhost:5173)
```
✅ VAJRA Security System login page
✅ Input fields for email/password
✅ "Admin" button in top right
✅ "Vendor" button for vendor login
```

### After Login
```
✅ Admin Dashboard
✅ Vendor Requests list
✅ System functionality
```

---

## Common Operations

### Stop Backend
```powershell
# In Terminal 1
Ctrl+C
Y (confirm)
```

### Stop Frontend
```powershell
# In Terminal 2
Ctrl+C
Y (confirm)
```

### Restart Both
```powershell
# Stop both (Ctrl+C in each terminal)
# Then run the startup commands again
```

### Test OTP Email System
```powershell
cd backend
python test_otp_with_email_v2.py
```

### Check API Documentation
Open in browser: http://127.0.0.1:8000/api/docs

### Check System Health
Open in browser: http://127.0.0.1:8000/api/health

---

## Project Structure

```
e:\Study\SIH2026\Prototype1\
├── backend/                 # Python FastAPI server
│   ├── app/
│   ├── requirements.txt
│   └── app.main:app
├── frontend/                # React/Vite application
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
├── data/
│   └── sih26155.db         # SQLite database
└── .env                     # Configuration file
```

---

## Available Test Flows

### 1. Admin Dashboard Test
- Login with admin credentials
- View vendor requests
- Approve/reject vendors

### 2. Vendor Registration Test
- Register new vendor
- Admin receives email
- Admin approves
- Vendor gets approval email

### 3. OTP Login Test
- Approved vendor requests OTP
- Receives OTP via email
- Verifies OTP code
- Creates session

### 4. Password Setup Test
- After OTP verification
- Set password
- Use for future logins

### 5. File Upload Test
- Login as approved vendor
- Upload configuration file
- System analyzes file
- View compliance report

---

## Quick Reference

### Commands
| Task | Command |
|------|---------|
| Start backend | `cd backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000` |
| Start frontend | `cd frontend && npm run dev` |
| Install backend deps | `cd backend && pip install -r requirements.txt` |
| Install frontend deps | `cd frontend && npm install` |
| Build frontend | `cd frontend && npm run build` |
| Test OTP flow | `cd backend && python test_otp_with_email_v2.py` |

### URLs
| Service | URL |
|---------|-----|
| Application | http://localhost:5173 |
| API | http://127.0.0.1:8000 |
| API Docs | http://127.0.0.1:8000/api/docs |
| Health | http://127.0.0.1:8000/api/health |

### Ports
| Service | Port |
|---------|------|
| Backend | 8000 |
| Frontend | 5173 |
| Database | SQLite (file-based) |

---

## Support & Help

### Documentation Files
- `STARTUP_CARD.txt` - Quick reference
- `STARTUP_COMMANDS.md` - Full reference
- `QUICK_STARTUP.txt` - Minimal guide
- `STEP_BY_STEP_STARTUP.txt` - Detailed walkthrough
- `README_STARTUP.md` - Complete documentation

### System Status Files
- `OTP_EMAIL_FIXED.md` - Email system confirmation
- `EMAIL_SYSTEM_QUICK_STATUS.txt` - Email status
- `TROUBLESHOOTING.md` - Common issues

### Testing Files
- `backend/test_otp_with_email_v2.py` - Test OTP flow
- `backend/test_email_status_v2.py` - Check email config

---

## Next Steps

1. ✅ Pick your guide format above
2. ✅ Follow the startup commands
3. ✅ Start backend (Terminal 1)
4. ✅ Start frontend (Terminal 2)
5. ✅ Open http://localhost:5173
6. ✅ Login and explore

---

## System Status

- ✅ Backend: Ready to run
- ✅ Frontend: Ready to run
- ✅ Database: Initialized
- ✅ Email: Configured (Gmail SMTP)
- ✅ OTP: Fully working
- ✅ Documentation: Complete

---

## Ready to Start?

### Choose your guide:

- 🎯 **Quick (30 sec):** Copy commands from this page → Run → Done
- ⚡ **Ultra-quick:** Open `STARTUP_CARD.txt` → Copy-paste commands
- 📋 **Step-by-step:** Open `STEP_BY_STEP_STARTUP.txt` → Follow steps
- 📖 **Full reference:** Open `STARTUP_COMMANDS.md` → Read and setup

---

**Let's go! 🚀**

Open Terminal 1:
```powershell
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
```

Open Terminal 2:
```powershell
cd frontend
npm run dev
```

Open Browser:
```
http://localhost:5173
```

**Enjoy!** 🎉
