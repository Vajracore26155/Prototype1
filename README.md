# SIH26155: AI-Driven Multi-Vendor Network Security Compliance Auditor

**A working prototype demonstrating vendor-agnostic security compliance auditing across Cisco, Fortinet, and unknown network device configurations.**

---

## 🎯 Problem Statement (SIH26155)

Organizations struggle with security compliance across multi-vendor network infrastructures. Each vendor has different configuration syntax, making it difficult to:
- Apply consistent security policies across vendors
- Audit configurations efficiently at scale
- Interpret unknown or custom device configurations
- Learn from security patterns over time

---

## ✨ Solution Overview

This prototype implements an **intelligent, vendor-agnostic compliance auditor** that:

1. **Automatically detects vendors** (Cisco, Fortinet, Unknown) with high confidence
2. **Masks sensitive data** (passwords, keys, tokens) before processing
3. **Normalizes configurations** to a unified security model
4. **Evaluates compliance** using vendor-independent rules
5. **Calculates risk scores** with transparent, explainable formulas
6. **Generates remediation** with vendor-specific fix commands
7. **Learns adaptively** from unknown configurations using AI

### Key Innovation: Vendor-Agnostic Architecture

```
Cisco Config      →  ┌─────────────────────────┐
                     │  Unified Security Model │  →  Compliance Rules
Fortinet Config   →  │  (Vendor Independent)   │  →  Risk Scoring
                     └─────────────────────────┘  →  Findings
Unknown Config    →  AI Interpretation Layer
```

**Example**: Both `transport input telnet ssh` (Cisco) and `set allowaccess ping https ssh telnet` (Fortinet) normalize to `remote_access.telnet_enabled=true`, enabling the same compliance rule to detect Telnet vulnerabilities in both vendors.

---

## 🏗️ Architecture

### Technology Stack

**Backend:**
- FastAPI (Python 3.11+)
- SQLAlchemy + SQLite
- Pydantic for data validation
- sentence-transformers (optional) for semantic AI

**Frontend:**
- React 18 + TypeScript
- Vite build tool
- TailwindCSS for styling
- React Router for navigation

### System Components

```
┌──────────────────────────────────────────────────────────────┐
│                        Frontend (React)                       │
│  Dashboard | Upload | Configurations | Audit Results         │
└────────────────────────────┬─────────────────────────────────┘
                             │ REST API
┌────────────────────────────▼─────────────────────────────────┐
│                     FastAPI Backend                           │
├───────────────────────────────────────────────────────────────┤
│  Security Layer:   Secret Masking | Vendor Detection         │
│  Parsing Layer:    Cisco Parser | Fortinet Parser            │
│  Normalization:    Unified Security Model (Pydantic)         │
│  Compliance:       YAML Rules Engine | Risk Scorer           │
│  Remediation:      Template Engine (per-vendor)              │
│  AI Layer:         Vocabulary | Embeddings | Learning DB     │
├───────────────────────────────────────────────────────────────┤
│                    SQLite Database                            │
│  configurations | audits | findings | learned_mappings       │
└───────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Upload** → Secret masking → Vendor detection → Storage
2. **Parse** → Extract security facts with evidence → Unified Model
3. **Evaluate** → Load YAML rules → Check compliance → Calculate risk
4. **Remediate** → Load templates → Generate vendor-specific fixes
5. **Learn** → Unknown configs → AI suggests mappings → Human validates

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** ([Download](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/))

### Installation

```bash
# Clone repository
git clone <repository-url>
cd Prototype1

# Setup Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Setup Frontend
cd ../frontend
npm install
```

### Database Initialization

**⚠️ Important: Initialize the database before first use**

```bash
cd backend
python init_database.py
```

This will:
- Create all required database tables
- Import any existing configuration files
- Display a summary of the initialization

### Running the Application

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn app.main:app --reload
# Backend runs on http://localhost:8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
# Frontend runs on http://localhost:5173
```

**Access the application:**
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs

**Note:** If you encounter "Failed to run audit" errors, make sure you've run the database initialization script above. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more details.

---

## 🧪 Testing

### Run All Phase Tests

Each phase has dedicated tests demonstrating working functionality:

```bash
cd backend

# Phase 1: Foundation (Upload API, Database)
python test_phase1.py

# Phase 2: Security (Masking, Vendor Detection)
python test_phase2.py

# Phase 3: Cisco End-to-End (Parser, Compliance, Risk)
python test_phase3.py

# Phase 4: Fortinet (Multi-vendor normalization proof)
python test_phase4.py

# Phase 5: Adaptive AI (Learning system)
python test_phase5.py

# Phase 6: Frontend Integration (Complete workflow)
python test_phase6.py
```

### Expected Results

- **Phase 1-2**: ✅ Upload, masking, detection working
- **Phase 3**: ✅ Cisco insecure scores 70%, secure 100%
- **Phase 4**: ✅ Fortinet insecure scores 75%, secure 100%
- **Phase 5**: ✅ AI mappings stored, retrieved, reused
- **Phase 6**: ✅ Full workflow: upload → audit → findings

---

## 📋 Demo Scenarios

### Scenario 1: Cisco Insecure Configuration

```bash
# Upload demo_configs/cisco/cisco_insecure.cfg
# Expected: 70% compliance, HIGH risk, 2 violations

Violations Detected:
- NET-001: Telnet Must Be Disabled (HIGH)
  Evidence: Line 23 "transport input telnet ssh"
  Fix: "no transport input telnet"
  
- AUTH-002: Console Password Required (CRITICAL)
  Evidence: Line 12 "line con 0"
  Fix: "line con 0\n password 7 <encrypted>\n login"
```

### Scenario 2: Fortinet Insecure Configuration

```bash
# Upload demo_configs/fortinet/fortinet_insecure.conf
# Expected: 75% compliance, MEDIUM risk, 1 violation

Violations Detected:
- NET-001: Telnet Must Be Disabled (HIGH)
  Evidence: Line 18 "set allowaccess ping https ssh telnet"
  Fix: "config system interface\n  edit port1\n    set allowaccess ping https ssh\n  next\nend"
```

**Key Proof**: Same NET-001 rule detects Telnet in both Cisco and Fortinet despite different syntax!

### Scenario 3: Unknown Vendor Configuration

```bash
# Upload demo_configs/unknown/vendor_xyz.conf
# Expected: AI suggests mappings with confidence scores

AI Learning Workflow:
1. System: "Cannot detect vendor (confidence < 50%)"
2. AI analyzes: "enable remote-mgmt telnet ssl" 
3. AI suggests: remote_access.telnet_enabled=true (confidence: 72%)
4. Human validates: ✓ Accept mapping
5. System learns: Future "enable remote-mgmt telnet" auto-mapped
```

---

## 🔍 Key Features Demonstrated

### 1. Secret Masking (10+ Types)

Automatically detects and masks sensitive data before analysis:

- Passwords (plaintext, type 5, type 7)
- SSH keys (RSA, DSA, ECDSA)
- API tokens and keys
- SNMP community strings
- Certificates and private keys
- OAuth tokens

**Example:**
```
Input:  username admin privilege 15 secret MySecureP@ss123
Output: username admin privilege 15 secret ********
```

### 2. Vendor Detection (100% Confidence)

Deterministic fingerprinting using vendor-specific patterns:

**Cisco Markers:**
- `interface GigabitEthernet`, `ip ssh version`, `crypto key generate rsa`

**Fortinet Markers:**
- `config system interface`, `set allowaccess`, `config firewall policy`

### 3. Unified Security Model

Vendor-agnostic Pydantic schema covering:

- **Network Security**: Interfaces, protocols, access control
- **Authentication**: Password policies, AAA, MFA
- **Encryption**: SSH, TLS, VPN settings
- **Access Control**: Management protocols, SNMP, Telnet
- **Firewall**: Zones, policies, NAT
- **Logging**: Syslog, audit trails

### 4. Compliance Rules (10 YAML Rules)

**Categories:**
- Network Security (4 rules): Telnet, SSH, SNMP
- Authentication (3 rules): Passwords, AAA, timeout
- Encryption (2 rules): SSH version, crypto
- Logging (1 rule): Syslog

**Severity Levels:** CRITICAL, HIGH, MEDIUM, LOW

### 5. Risk Scoring (Transparent Formula)

```python
Risk Score = (Σ violation_weights) / max_possible_score

Weights:
- CRITICAL: 15 points
- HIGH: 10 points
- MEDIUM: 5 points
- LOW: 2 points

Risk Levels:
- CRITICAL: >90%
- HIGH: 70-90%
- MEDIUM: 40-70%
- LOW: <40%
```

### 6. Evidence Tracking

Every finding includes:
- **File**: Source configuration filename
- **Line**: Exact line number in original file
- **Text**: Actual configuration snippet

**No black box**: Users can verify every finding against source!

### 7. Vendor-Specific Remediation

Templates stored in `backend/app/remediation/templates.yaml`:

```yaml
NET-001:
  title: "Telnet Must Be Disabled"
  cisco: "no transport input telnet"
  fortinet: |
    config system interface
      edit port1
        set allowaccess ping https ssh
      next
    end
```

### 8. Adaptive AI Learning

**Components:**

1. **Vocabulary Engine**: 9 security concepts, 14+ phrases each
2. **Embedding Engine**: sentence-transformers (all-MiniLM-L6-v2)
3. **Confidence Scorer**: 4 factors (keyword 25%, semantic 40%, pattern 25%, vendor 10%)
4. **Learning Database**: Stores validated mappings for reuse

**Confidence Thresholds:**
- ≥85%: High confidence (auto-apply)
- 60-85%: Medium (suggest to user)
- <60%: Low (flag for review)

**Human-in-the-Loop:**
- AI suggests mappings
- Human validates (accept/reject)
- System learns for future configs
- Statistics track reuse count

---

## 📁 Project Structure

```
Prototype1/
├── backend/
│   ├── app/
│   │   ├── adaptive/          # AI learning system
│   │   │   ├── vocabulary.py  # Security concepts
│   │   │   ├── embedding_engine.py
│   │   │   ├── confidence.py  # Multi-factor scoring
│   │   │   ├── candidate_mapper.py
│   │   │   └── learning.py    # Database persistence
│   │   ├── api/               # REST endpoints
│   │   │   ├── upload.py
│   │   │   ├── audit.py
│   │   │   ├── findings.py
│   │   │   └── learning.py
│   │   ├── compliance/        # Rules engine
│   │   │   ├── evaluator.py
│   │   │   └── rules.yaml     # 10 compliance rules
│   │   ├── database/          # SQLAlchemy models
│   │   │   ├── database.py
│   │   │   └── models.py
│   │   ├── detection/         # Vendor detection
│   │   │   └── vendor_detector.py
│   │   ├── findings/          # Audit orchestrator
│   │   │   └── engine.py
│   │   ├── normalization/     # Unified model
│   │   │   └── schema.py      # Pydantic schemas
│   │   ├── parsers/           # Vendor parsers
│   │   │   ├── cisco_parser.py
│   │   │   └── fortinet_parser.py
│   │   ├── remediation/       # Fix templates
│   │   │   └── templates.yaml
│   │   ├── risk/              # Risk scoring
│   │   │   └── scorer.py
│   │   ├── security/          # Secret masking
│   │   │   └── masking.py
│   │   ├── storage/           # File handling
│   │   └── main.py            # FastAPI app
│   ├── data/                  # SQLite database
│   ├── storage/               # Uploaded configs
│   ├── requirements.txt
│   └── test_phase*.py         # Phase tests (1-6)
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── Layout.tsx     # Nav + layout
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx  # Stats overview
│   │   │   ├── Upload.tsx     # File upload
│   │   │   ├── Configurations.tsx
│   │   │   └── AuditResults.tsx  # Findings viewer
│   │   ├── services/
│   │   │   └── api.ts         # API client
│   │   ├── types/
│   │   │   └── index.ts       # TypeScript types
│   │   ├── App.tsx            # Routes
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── demo_configs/              # Demo files
│   ├── cisco/
│   │   ├── cisco_insecure.cfg
│   │   └── cisco_secure.cfg
│   ├── fortinet/
│   │   ├── fortinet_insecure.conf
│   │   └── fortinet_secure.conf
│   └── unknown/
│       └── vendor_xyz.conf
│
├── .env                       # Environment config
└── README.md                  # This file
```

---

## 🎓 Design Decisions

### Why Modular Monolith?

**Chosen:** Single FastAPI application with clear module boundaries  
**Rejected:** Microservices  
**Reason:** Simplicity for prototype. Can evolve to microservices if needed.

### Why SQLite?

**Chosen:** SQLite with SQLAlchemy ORM  
**Rejected:** PostgreSQL  
**Reason:** Local development, sufficient for demo. Production-ready ORM means easy migration.

### Why YAML Rules?

**Chosen:** YAML declarative rules  
**Rejected:** Open Policy Agent (OPA)  
**Reason:** Simpler for prototype. OPA can be integrated later for complex policies.

### Why Pydantic Unified Model?

**Chosen:** Vendor-agnostic Pydantic schemas  
**Rejected:** Vendor-specific rule sets  
**Reason:** Core architectural principle. Single model enables rule reuse across vendors.

### Why Deterministic Risk Scoring?

**Chosen:** Transparent mathematical formula  
**Rejected:** AI-based risk prediction  
**Reason:** Explainability and trust. Users can verify calculations.

### Why Human-in-the-Loop AI?

**Chosen:** AI suggests, human validates, system learns  
**Rejected:** Fully automated AI mapping  
**Reason:** Security requires human judgment. Learning improves over time.

---

## 🔐 Security Considerations

### Data Protection

- **No external transmission**: All processing is local
- **Secret masking**: Applied before storage and logging
- **Sanitized paths**: Prevent directory traversal
- **No code execution**: Static analysis only

### Compliance Standards Referenced

- CIS Benchmarks (Network Device Hardening)
- NIST Cybersecurity Framework
- PCI DSS (where applicable)
- STIG (Security Technical Implementation Guides)

---

## 🚧 Current Limitations & Future Work

### Current Scope (Prototype)

✅ Cisco and Fortinet syntax support  
✅ 10 core compliance rules  
✅ Basic AI learning for unknown configs  
✅ Local file upload only  
✅ SQLite database  

### Future Enhancements

🔮 **Additional Vendors:**
- Juniper, Palo Alto, Arista, Aruba
- Cloud providers (AWS, Azure, GCP security groups)

🔮 **Advanced Features:**
- Real-time device polling (SNMP, SSH)
- Configuration version control
- Automated remediation deployment
- Multi-tenant support
- Advanced AI (LLM integration)

🔮 **Enterprise Features:**
- PostgreSQL/MongoDB for scale
- REST API authentication (OAuth2)
- Role-based access control (RBAC)
- Audit trails and compliance reports
- Integration with SIEM/ticketing systems

🔮 **AI Improvements:**
- Fine-tuned security language models
- Anomaly detection across configs
- Predictive risk analysis
- Automatic rule generation from policies

---

## 📊 Test Results Summary

| Phase | Component | Status | Key Metrics |
|-------|-----------|--------|-------------|
| 1 | Foundation | ✅ Pass | Upload API functional, DB initialized |
| 2 | Security | ✅ Pass | 10+ secret types masked, 100% vendor confidence |
| 3 | Cisco Audit | ✅ Pass | Insecure: 70%, Secure: 100%, 10 rules evaluated |
| 4 | Fortinet Audit | ✅ Pass | Insecure: 75%, Secure: 100%, Same rules work |
| 5 | Adaptive AI | ✅ Pass | Mappings stored/retrieved, confidence scoring |
| 6 | Frontend | ✅ Pass | Full workflow: upload → audit → results |

**Total Test Coverage:** All critical paths verified ✅

---

## 🤝 Contributing

This is a prototype for SIH26155. For contributions:

1. Follow existing code structure
2. Add tests for new parsers/rules
3. Update documentation
4. Maintain vendor-agnostic principles

---

## 📝 License

[Specify your license here]

---

## 🙏 Acknowledgments

Built for **Smart India Hackathon 2026**  
Problem Statement: **SIH26155**  
Theme: **Network Security Compliance**

---

## 📞 Support

For questions or issues:
- Check test files for usage examples
- Review API docs at http://localhost:8000/docs
- Examine demo configs in `demo_configs/`

---

**Last Updated:** September 8, 2026  
**Version:** 1.0.0 (Prototype)  
**Status:** ✅ All 7 Phases Complete
