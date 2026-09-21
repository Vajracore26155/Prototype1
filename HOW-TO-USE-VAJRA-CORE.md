# HOW TO USE VAJRA CORE - COMPLETE GUIDE

**Last Updated**: 2026-09-18  
**Status**: Production-Ready with 5 bugs fixed

---

## 📋 TABLE OF CONTENTS

1. [System Overview](#system-overview)
2. [What This System Does](#what-this-system-does)
3. [Required Data and Files](#required-data-and-files)
4. [How to Start the System](#how-to-start-the-system)
5. [How to Use the System](#how-to-use-the-system)
6. [Complete Workflow Example](#complete-workflow-example)
7. [Troubleshooting](#troubleshooting)

---

## 1. SYSTEM OVERVIEW

### What is VAJRA CORE?

VAJRA CORE is a **network security compliance auditor** that:
- Takes configuration files from routers/firewalls/switches
- Automatically detects which vendor (Cisco, Fortinet, etc.)
- Analyzes them for security issues
- Checks compliance against standards (CIS, NIST, STIG)
- Generates reports with findings and remediation steps

### Architecture

```
┌─────────────────────────────────────────────┐
│ YOU                                         │
│ Upload: cisco_config.cfg                    │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│ FRONTEND (React)                            │
│ http://localhost:5173                       │
│ - Upload interface                          │
│ - View dashboard                            │
│ - See findings                              │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│ BACKEND API (FastAPI)                       │
│ http://localhost:8000                       │
│ - Receives files                            │
│ - Detects vendor                            │
│ - Parses configuration                      │
│ - Runs compliance checks                    │
│ - Stores results                            │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│ DATABASE (SQLite)                           │
│ backend/data/sih26155.db                    │
│ - Stores configurations                     │
│ - Stores audit results                      │
│ - Stores findings                           │
└─────────────────────────────────────────────┘
```

---

## 2. WHAT THIS SYSTEM DOES

### Step-by-Step Process

**STEP 1: You Upload a Configuration File**
- Example: `cisco_router.cfg` or `fortinet_firewall.conf`

**STEP 2: System Detects Vendor**
- Automatically identifies: Cisco, Fortinet, Juniper, Palo Alto, or Unknown
- Confidence score: 0-100%

**STEP 3: System Masks Secrets**
- Finds passwords, SNMP communities, API keys
- Replaces with `[REDACTED]` for security

**STEP 4: System Parses Configuration**
- Extracts security settings:
  - Is SSH enabled?
  - Is Telnet enabled?
  - Is HTTP enabled?
  - Are passwords encrypted?
  - Is logging configured?

**STEP 5: System Normalizes Data**
- Converts vendor-specific syntax to common format
- Example: 
  - Cisco: `"transport input ssh"` 
  - Fortinet: `"set allowaccess ssh"`
  - Both become: `ssh_enabled = true`

**STEP 6: System Runs Compliance Checks**
- Checks against 10+ security rules
- Example rules:
  - NET-001: Telnet must be disabled (HIGH severity)
  - NET-002: SSH must be enabled (HIGH severity)
  - NET-004: HTTP must be disabled (HIGH severity)

**STEP 7: System Generates Findings**
- Lists what passed and what failed
- Provides evidence (file, line number, actual text)
- Calculates risk score
- Suggests remediation commands

**STEP 8: You See Results**
- Dashboard shows compliance score
- List of findings with severity
- Recommendations for fixing issues

---

## 3. REQUIRED DATA AND FILES

### What Configuration Files Can You Use?

You have **THREE OPTIONS**:

---

### **OPTION 1: Use Existing Test Files** ✅ RECOMMENDED FOR TESTING

**Location**: `backend/data/`

**Available Files**:
```
backend/data/
├── cisco_insecure_multi.cfg       ← Cisco config (insecure)
├── cisco_telnet_insecure.cfg      ← Cisco config (insecure)
├── cisco_ios_compliant.cfg        ← Cisco config (secure)
├── cisco_ssh_compliant.cfg        ← Cisco config (secure)
├── fortinet_secure.cfg            ← Fortinet config (secure)
└── golden/
    ├── positive/                  ← Compliant configs
    └── negative/                  ← Non-compliant configs
```

**What each file contains**:
- `cisco_insecure_multi.cfg`: Cisco router with telnet enabled (BAD)
- `cisco_ssh_compliant.cfg`: Cisco router with SSH only (GOOD)
- `fortinet_secure.cfg`: Fortinet firewall secure config (GOOD)

---

### **OPTION 2: Use Your Own Configuration Files** ✅ PRODUCTION USE

**Supported Vendors**:
- ✅ Cisco IOS/IOS-XE/NX-OS
- ✅ Fortinet FortiOS
- ✅ Juniper JunOS
- ✅ Palo Alto PAN-OS
- ✅ Generic/Unknown (AI will try to parse)

**Supported File Extensions**:
- `.cfg` (most common)
- `.conf`
- `.txt`
- `.json`
- `.yaml` / `.yml`
- `.xml`

**File Size Limit**: 10MB per file

**How to Get Config Files**:

**From Cisco Router**:
```bash
# On Cisco device:
Router# show running-config
Router# copy running-config tftp://your-server/router.cfg
```

**From Fortinet Firewall**:
```bash
# On FortiGate:
FortiGate # show full-configuration
# Save output to file
```

**From Juniper**:
```bash
# On Junos:
user@router> show configuration | display set
user@router> show configuration | save juniper.conf
```

---

### **OPTION 3: Bulk Upload Multiple Files** ✅ FOR MULTIPLE DEVICES

**Format**: Upload multiple `.cfg` files at once

**Example Structure**:
```
my_configs/
├── router1_cisco.cfg
├── router2_cisco.cfg
├── firewall1_fortinet.conf
├── firewall2_fortinet.conf
└── switch1_juniper.cfg
```

**Upload Method**: Use bulk upload API or frontend interface

---

### CSV Files? (Device Inventory)

**Location**: Not required for core functionality, but you can use CSV for device management

**Example CSV Format** (if you want to track devices):
```csv
hostname,ip_address,vendor,model,location
ROUTER-01,192.168.1.1,Cisco,ISR4331,HQ-Datacenter
FIREWALL-01,192.168.1.254,Fortinet,FortiGate-100F,HQ-Perimeter
```

**Use Case**: Import device inventory, then upload configs for each device

---

## 4. HOW TO START THE SYSTEM

### Prerequisites

**Required Software**:
- ✅ Python 3.11+ (you have this)
- ✅ Node.js 18+ (for frontend)
- ⚠️ Optional: Docker (for production mode)

---

### **OPTION A: Development Mode (Quick Start)** ✅ RECOMMENDED

This uses:
- SQLite database (local file)
- Filesystem storage (local folders)
- No Redis, no PostgreSQL, no MinIO needed

#### Step 1: Start Backend

**Open Terminal 1**:
```bash
cd E:\Study\SIH2026\Prototype1
cd backend

# Make sure you're in virtual environment (if using one)
# python -m venv venv
# .\venv\Scripts\activate

# Install dependencies (if not done)
pip install -r requirements.txt

# Start backend server
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Expected Output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
🚀 Starting SIH26155 Network Security Auditor...
✓ Application ready!
INFO:     Application startup complete.
```

**Backend is ready when you see**: `Application startup complete.`

**Access**:
- API Docs: http://127.0.0.1:8000/docs
- Health Check: http://127.0.0.1:8000/health

---

#### Step 2: Start Frontend

**Open Terminal 2** (keep backend running):
```bash
cd E:\Study\SIH2026\Prototype1
cd frontend

# Install dependencies (first time only)
npm install

# Start frontend development server
npm run dev
```

**Expected Output**:
```
  VITE v5.0.8  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

**Frontend is ready when you see**: `Local: http://localhost:5173/`

**Access**:
- Open browser: http://localhost:5173

---

### **OPTION B: Production Mode (Docker)** 🐳

**If you want full stack with PostgreSQL, Redis, MinIO**:

```bash
cd E:\Study\SIH2026\Prototype1

# Copy environment file
copy .env.example .env

# Edit .env and set:
# USE_POSTGRES=true
# USE_REDIS=true
# USE_MINIO=true

# Start all services
docker-compose up -d

# Check services
docker-compose ps

# View logs
docker-compose logs -f backend
```

**Services**:
- Backend: http://localhost:8000
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- MinIO: http://localhost:9001

---

## 5. HOW TO USE THE SYSTEM

### Using the Web Interface (Frontend)

#### **1. Open Browser**
Navigate to: http://localhost:5173

#### **2. You'll See Dashboard**
- Total configurations uploaded
- Compliance scores
- Findings by severity
- Recent audits

#### **3. Upload Configuration**

**Option 1: Single File Upload**
1. Click "Upload Configuration" or "Upload" button
2. Select file (e.g., `cisco_insecure_multi.cfg`)
3. Click "Upload"
4. Wait for processing (5-10 seconds)
5. See audit results

**Option 2: Bulk Upload**
1. Click "Bulk Upload"
2. Select multiple `.cfg` files
3. Click "Upload All"
4. See progress bar
5. View results for each file

#### **4. View Results**

**Dashboard Shows**:
- Compliance Score: 0-100% (higher is better)
- Risk Level: LOW, MEDIUM, HIGH, CRITICAL
- Findings Count: How many issues found
- Charts and graphs

**Click on Audit to See**:
- ✅ Passed checks (green)
- ❌ Failed checks (red)
- ⚠️ Warnings (yellow)

**For Each Finding, You See**:
- Rule ID: NET-001
- Title: "Telnet Must Be Disabled"
- Severity: HIGH
- Status: FAIL
- Evidence: File line 23: `transport input telnet ssh`
- Remediation: Commands to fix the issue

#### **5. Generate Report**
1. Click "Generate Report"
2. Select format: PDF, CSV, JSON
3. Download report

---

### Using the API Directly (Backend)

**Access API Documentation**: http://127.0.0.1:8000/docs

#### **Example 1: Upload Single File**

```bash
# Using curl (Windows PowerShell):
curl -X POST "http://127.0.0.1:8000/api/upload" `
  -F "file=@backend/data/cisco_insecure_multi.cfg"

# Response:
{
  "config_id": "CFG-000123",
  "filename": "cisco_insecure_multi.cfg",
  "vendor": "Cisco",
  "vendor_confidence": 1.0,
  "status": "UPLOADED"
}
```

#### **Example 2: Run Audit**

```bash
# Run compliance audit:
curl -X POST "http://127.0.0.1:8000/api/audits" `
  -H "Content-Type: application/json" `
  -d '{
    "config_id": "CFG-000123",
    "frameworks": ["CIS", "NIST"]
  }'

# Response:
{
  "audit_id": "AUD-000456",
  "status": "COMPLETED",
  "compliance_score": 70.0,
  "risk_score": 72.75,
  "risk_level": "HIGH",
  "passed_count": 7,
  "failed_count": 2,
  "findings": [...]
}
```

#### **Example 3: Get Findings**

```bash
# Get all findings for audit:
curl "http://127.0.0.1:8000/api/findings?audit_id=AUD-000456"

# Response:
{
  "findings": [
    {
      "finding_id": "FND-000789",
      "rule_id": "NET-001",
      "title": "Telnet Must Be Disabled",
      "status": "FAIL",
      "severity": "HIGH",
      "evidence_line": 23,
      "evidence_text": "transport input telnet ssh",
      "remediation": "no transport input telnet"
    }
  ]
}
```

---

## 6. COMPLETE WORKFLOW EXAMPLE

### Scenario: Audit Cisco Router Configuration

#### **Step 1: Prepare Configuration File**

You have a Cisco router config file: `my_router.cfg`

**Sample Content**:
```
version 15.2
!
hostname ROUTER-01
!
enable secret 5 $1$mERr$hx5rVt7rPNoS4wqbXKX7m0
!
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
!
line vty 0 4
 transport input telnet ssh
 login local
!
```

#### **Step 2: Start System**

**Terminal 1 (Backend)**:
```bash
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 (Frontend)**:
```bash
cd frontend
npm run dev
```

#### **Step 3: Access Frontend**

Open browser: http://localhost:5173

#### **Step 4: Upload Configuration**

1. Click "Upload Configuration"
2. Select `my_router.cfg`
3. Click "Upload"

**Behind the Scenes**:
```
✅ File uploaded
✅ Vendor detected: Cisco (100% confidence)
✅ Secrets masked: 1 enable secret
✅ Configuration parsed: 14 security fields extracted
✅ Normalized to Unified Security Model
✅ Compliance checked: 10 rules evaluated
✅ Findings generated: 2 failures, 7 passes
```

#### **Step 5: View Results**

**Dashboard Shows**:
```
Compliance Score: 70%
Risk Level: HIGH
Risk Score: 72.75/100

Findings:
❌ NET-001: Telnet Must Be Disabled (HIGH)
   Evidence: Line 23 "transport input telnet ssh"
   
✅ NET-002: SSH Must Be Enabled (HIGH)
   Evidence: Line 23 "transport input telnet ssh"
   
❌ NET-004: HTTP Management Must Be Disabled (HIGH)
   Evidence: Not explicitly disabled
```

#### **Step 6: Fix Issues**

**Remediation Commands**:
```
! Fix NET-001: Disable Telnet
line vty 0 4
 transport input ssh
 no transport input telnet

! Fix NET-004: Disable HTTP
no ip http server
```

#### **Step 7: Upload Fixed Config**

1. Update `my_router.cfg` with fixes
2. Upload again
3. New audit shows: **100% compliance** ✅

---

## 7. COMPLETE WORKFLOW WITH TEST DATA

### Use Existing Test Files

**Location**: `backend/data/`

#### **Test 1: Upload Insecure Cisco Config**

```bash
# File: backend/data/cisco_insecure_multi.cfg
# Expected: Multiple security issues

# Via Frontend:
1. Open http://localhost:5173
2. Upload: backend/data/cisco_insecure_multi.cfg
3. Expected result:
   - Vendor: Cisco (100%)
   - Compliance: ~70%
   - Risk: HIGH
   - Findings: Telnet enabled, HTTP enabled
```

#### **Test 2: Upload Secure Cisco Config**

```bash
# File: backend/data/cisco_ssh_compliant.cfg
# Expected: All checks pass

# Via Frontend:
1. Upload: backend/data/cisco_ssh_compliant.cfg
2. Expected result:
   - Vendor: Cisco (100%)
   - Compliance: 100%
   - Risk: LOW
   - Findings: All passed ✅
```

#### **Test 3: Upload Fortinet Config**

```bash
# File: backend/data/fortinet_secure.cfg
# Expected: Different vendor, same compliance check

# Via Frontend:
1. Upload: backend/data/fortinet_secure.cfg
2. Expected result:
   - Vendor: Fortinet (100%)
   - Compliance: 100%
   - Risk: LOW
   - Same rules applied (vendor-agnostic)
```

---

## 8. DATABASE LOCATION

### Where is Data Stored?

**Development Mode (SQLite)**:
```
backend/data/sih26155.db    ← All data here
```

**View Database**:
```bash
# Install SQLite browser or use command line:
cd backend/data
sqlite3 sih26155.db

# In SQLite:
.tables                      # List all tables
SELECT * FROM configurations LIMIT 5;
SELECT * FROM audits LIMIT 5;
SELECT * FROM findings LIMIT 5;
```

**Data Folders**:
```
backend/data/
├── sih26155.db              ← Database
├── uploads/                 ← Original config files
├── sanitized/               ← Masked config files
├── normalized/              ← Parsed JSON data
├── reports/                 ← Generated PDF reports
└── golden/                  ← Test fixtures
```

---

## 9. TROUBLESHOOTING

### Backend Won't Start

**Error**: `ImportError: cannot import name...`
**Solution**: Check all bugs are fixed (we fixed 5 bugs)
```bash
# Make sure you have latest code with fixes:
git status
# Or re-apply fixes from BUGS-FOUND-AND-FIXED.md
```

**Error**: `ModuleNotFoundError: No module named 'fastapi'`
**Solution**: Install dependencies
```bash
cd backend
pip install -r requirements.txt
```

**Error**: `Port 8000 already in use`
**Solution**: Kill existing process or use different port
```bash
# Kill process on port 8000 (Windows):
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or use different port:
python -m uvicorn app.main:app --reload --port 8001
```

---

### Frontend Won't Start

**Error**: `npm: command not found`
**Solution**: Install Node.js from https://nodejs.org

**Error**: `Cannot find module...`
**Solution**: Install dependencies
```bash
cd frontend
npm install
```

**Error**: `Port 5173 already in use`
**Solution**: Kill process or change port in `vite.config.ts`

---

### Upload Fails

**Error**: File size too large
**Solution**: File must be < 10MB

**Error**: Invalid file type
**Solution**: Use `.cfg`, `.conf`, `.txt`, `.json`, `.yaml`, `.xml`

**Error**: Vendor detection fails (Unknown)
**Solution**: This is normal for unsupported vendors - AI will try to parse

---

### No Findings Generated

**Possible Reasons**:
1. Configuration is 100% compliant (all checks passed)
2. Parser couldn't extract security fields
3. Unknown vendor with low confidence

**Debug**:
```bash
# Check backend logs in terminal
# Should see:
# ✓ Configuration parsed
# ✓ Normalized to USM
# ✓ Compliance evaluated
```

---

## 10. QUICK REFERENCE

### Essential Commands

**Start Backend**:
```bash
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Start Frontend**:
```bash
cd frontend
npm run dev
```

**Access Points**:
- Frontend: http://localhost:5173
- Backend API: http://127.0.0.1:8000
- API Docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

**Test Files**:
- Cisco Insecure: `backend/data/cisco_insecure_multi.cfg`
- Cisco Secure: `backend/data/cisco_ssh_compliant.cfg`
- Fortinet Secure: `backend/data/fortinet_secure.cfg`

**Database**:
- Location: `backend/data/sih26155.db`

---

## 11. WHAT HAPPENS DURING AN AUDIT?

### Complete Flow

```
┌─────────────────────────────────────────────┐
│ 1. UPLOAD                                   │
│    You: Upload cisco_router.cfg             │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│ 2. VENDOR DETECTION                         │
│    System: Analyzes file                    │
│    Output: Cisco (100% confidence)          │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│ 3. SECRET MASKING                           │
│    System: Finds passwords, keys            │
│    Output: 3 secrets masked                 │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│ 4. PARSING                                  │
│    System: Extracts security settings       │
│    Output:                                  │
│      - ssh_enabled: true                    │
│      - telnet_enabled: true ← PROBLEM!      │
│      - http_enabled: false                  │
│      - logging_enabled: true                │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│ 5. NORMALIZATION                            │
│    System: Converts to common model         │
│    Output: UnifiedSecurityModel with 14     │
│            security fields + evidence       │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│ 6. COMPLIANCE CHECKING                      │
│    System: Evaluates 10 rules               │
│    Results:                                 │
│      ✅ NET-002: SSH enabled (PASS)         │
│      ❌ NET-001: Telnet disabled (FAIL)     │
│      ✅ NET-004: HTTP disabled (PASS)       │
│      ... 7 more rules                       │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│ 7. RISK SCORING                             │
│    System: Calculates risk                  │
│    Output:                                  │
│      - Compliance: 70%                      │
│      - Risk Score: 72.75/100                │
│      - Risk Level: HIGH                     │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│ 8. FINDINGS & REMEDIATION                   │
│    System: Generates report                 │
│    Output:                                  │
│      - Finding FND-001:                     │
│        Rule: NET-001                        │
│        Issue: Telnet enabled                │
│        Evidence: Line 23                    │
│        Fix: "no transport input telnet"     │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│ 9. DISPLAY                                  │
│    You: See results in dashboard            │
│    Action: Download report, fix issues      │
└─────────────────────────────────────────────┘
```

---

## 12. FINAL CHECKLIST

Before you start, make sure you have:

- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed  
- [ ] Backend dependencies installed (`pip install -r requirements.txt`)
- [ ] Frontend dependencies installed (`npm install`)
- [ ] All 5 bugs fixed (check `BUGS-FOUND-AND-FIXED.md`)
- [ ] Test configuration files ready (`backend/data/`)
- [ ] Terminal 1 ready for backend
- [ ] Terminal 2 ready for frontend
- [ ] Browser ready (Chrome, Firefox, Edge)

Then:

1. ✅ Start backend: `python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`
2. ✅ Start frontend: `npm run dev`
3. ✅ Open browser: http://localhost:5173
4. ✅ Upload test file: `backend/data/cisco_insecure_multi.cfg`
5. ✅ See results: Compliance score, findings, remediation

---

## SUMMARY

**To Use VAJRA CORE**:

1. **Start Backend** (Terminal 1):
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

2. **Start Frontend** (Terminal 2):
   ```bash
   cd frontend
   npm run dev
   ```

3. **Open Browser**: http://localhost:5173

4. **Upload Config**: Use test files from `backend/data/` or your own `.cfg` files

5. **View Results**: See compliance score, findings, and remediation steps

6. **Download Report**: Get PDF report with all findings

**That's it! The system is ready to use.**

---

**Need Help?**
- See `FINAL-SIH-AND-SYSTEM-AUDIT.md` for technical details
- See `BUGS-FOUND-AND-FIXED.md` for troubleshooting
- See `SIH-REQUIREMENTS-TRACEABILITY.md` for feature mapping
