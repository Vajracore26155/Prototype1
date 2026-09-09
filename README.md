# SIH26155 Network Security Auditor

A premium enterprise-grade web application for automated network device configuration auditing and compliance checking.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm or yarn

### Installation

**Backend**:
```bash
cd backend
pip install -r requirements.txt
```

**Frontend**:
```bash
cd frontend
npm install
```

### Running the Application

**Option 1: PowerShell Script (Windows)**
```powershell
.\start-all.ps1
```

**Option 2: Manual Start**

Terminal 1 - Backend:
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

### Access the Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## ✨ Features

### Core Functionality
- ✅ **Multi-Vendor Support**: Cisco IOS/IOS-XE, Fortinet FortiGate, Unknown vendors with AI
- ✅ **Automated Vendor Detection**: ML-based configuration analysis
- ✅ **Security Auditing**: Compliance rules engine with risk scoring
- ✅ **AI-Assisted Learning**: Human-in-the-loop for unknown configurations
- ✅ **PDF Report Generation**: Professional compliance reports
- ✅ **Real-time Dashboard**: KPI tracking and status monitoring

### Design System
- ✅ **Premium Light Theme**: Sophisticated enterprise UI
- ✅ **Glassmorphism**: Selective glass effects on key elements
- ✅ **Motion System**: Smooth, responsive interactions
- ✅ **Accessibility**: High contrast, reduced-motion support
- ✅ **Responsive**: Works on desktop, laptop, tablet

## 📁 Project Structure

```
Prototype1/
├── backend/
│   ├── app/
│   │   ├── adaptive/        # AI learning engine
│   │   ├── api/             # FastAPI routes
│   │   ├── compliance/      # Rules engine
│   │   ├── database/        # SQLAlchemy models
│   │   ├── detection/       # Vendor detection
│   │   ├── findings/        # Security findings
│   │   ├── ingestion/       # File processing
│   │   ├── normalization/   # Schema normalization
│   │   ├── parsers/         # Vendor-specific parsers
│   │   ├── remediation/     # Fix templates
│   │   ├── reports/         # PDF generation
│   │   ├── risk/            # Risk scoring
│   │   ├── security/        # Data masking
│   │   └── main.py          # FastAPI app
│   ├── data/                # Storage directories
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API client
│   │   ├── types/           # TypeScript types
│   │   └── App.tsx          # Root component
│   ├── public/
│   ├── package.json
│   └── vite.config.ts
│
├── start-all.ps1            # Quick startup script
├── SYSTEM_STATUS.md         # Current system status
└── README.md                # This file
```

## 🎨 Design Documentation

- **DESIGN_SYSTEM.md** - Color palette, typography, spacing system
- **DASHBOARD_ARCHITECTURE.md** - Layout and information hierarchy
- **GLASSMORPHISM_GUIDE.md** - Glass effect usage guidelines
- **MOTION_SYSTEM.md** - Animation and interaction patterns
- **SHADOW_FIX_SUMMARY.md** - Technical details of shadow implementation

## 🔧 Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM
- **SQLite** - Embedded database
- **Sentence-Transformers** - NLP embeddings
- **PyYAML** - Configuration parsing
- **ReportLab** - PDF generation

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **React Router** - Navigation
- **Axios** - HTTP client
- **Lucide React** - Icon system
- **Tailwind CSS** - Styling framework

## 📊 Current Status

✅ **All Systems Operational**

- Backend API: Running on port 8000
- Frontend: Running on port 5173
- Database: Initialized with 9 configurations
- All pages: Dashboard, Upload, Configurations, Audit Results
- All features: Upload, audit, reports, learning

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find process on port 5173
netstat -ano | findstr :5173

# Kill process (use PID from above)
taskkill /PID <PID> /F
```

### Backend Not Responding
```bash
# Check if Python is running
Get-Process python

# Restart backend
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Build Errors
```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules
rm package-lock.json
npm install
```

### API Connection Issues
- Verify backend is running on port 8000
- Check `frontend/vite.config.ts` proxy configuration
- Ensure no firewall blocking localhost connections

## 📝 Recent Fixes (September 9, 2026)

1. **CSS Compilation Errors** - Replaced all custom shadow classes with inline styles or Tailwind standards
2. **Configurations Page** - Fixed missing icon import causing white screen
3. **Server Ports** - Corrected port conflicts and proxy configuration
4. **Backend Startup** - Ensured backend starts before frontend for proper API connectivity

## 🎯 Usage Workflow

1. **Upload Configuration**
   - Navigate to Upload page
   - Drag & drop or select `.conf`, `.cfg`, or `.txt` files
   - System automatically detects vendor

2. **View Configurations**
   - Navigate to Configurations page
   - See all uploaded configurations
   - Click "Run Audit" to analyze

3. **View Audit Results**
   - Review compliance score and risk level
   - Examine security findings by severity
   - Download PDF report

4. **AI Learning (if needed)**
   - System flags unknown configuration patterns
   - Navigate to Learning page
   - Accept or reject AI suggestions
   - System improves over time

## 🔒 Security Features

- Sensitive data masking (IPs, passwords, keys)
- Risk-based finding prioritization
- Compliance rule engine
- Audit trail tracking
- Secure file handling

## 📄 License

This project was developed for SIH 2026.

---

**Status**: ✅ Fully Operational
**Last Updated**: September 9, 2026
