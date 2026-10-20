# VAJRA CORE — AI-Driven Multi-Vendor Network Security Compliance Auditor

**Organization / problem-statement alignment:** National Technical Research Organisation (NTRO)  
**Live preview:** https://vajracores.vercel.app/  
**Project type:** Network configuration security auditing and compliance analysis

VAJRA CORE is a web-based prototype for reviewing network-device configuration files against a vendor-neutral security baseline. It is designed to help administrators identify risky settings, review compliance findings, and understand possible remediation actions across heterogeneous network environments.

> **Important scope note:** “Vendor-agnostic” is the architectural goal, not a claim that every device, firmware version, or security framework is already supported. Parsing and rule coverage depend on the implemented parsers, normalized fields, and rules. Treat findings and suggested commands as recommendations that a qualified network administrator must validate before applying them to production devices.

## Live Demo and Demo Credentials

- **Live preview:** https://vajracores.vercel.app/
- **Repository-provided local demo account:**
  - **Email:** `admin@tatva.security`
  - **Password:** `admin123`

These credentials are documented in the repository's `QUICK_START.md` for the local development setup. The hosted preview may use a separate database or deployment configuration, so the local credentials are **not guaranteed to work on the live site**. If they do not work, use the **Create an account** flow on the preview. Do not reuse the sample password in any real deployment, and change/remove seeded credentials before exposing a deployment publicly.

## Problem Statement and Proposed Approach

Enterprise networks combine equipment and configuration conventions from many vendors. Manual reviews are time-consuming, while hard-coded parsers can struggle with unfamiliar syntax and firmware changes. VAJRA CORE addresses this workflow through:

1. **Configuration ingestion** — upload one or more device configuration files.
2. **Vendor detection and parsing** — use supported vendor parsers and a fallback path for unknown configurations.
3. **Normalization** — map recognized configuration properties to a unified security model.
4. **Compliance evaluation** — evaluate normalized properties against configurable security rules.
5. **Human-in-the-loop interpretation** — generate mapping candidates for unfamiliar lines and allow review/validation through the adaptive-learning workflow.
6. **Findings and remediation guidance** — show deviations, severity, evidence, and recommended corrective actions.
7. **Reporting** — generate PDF audit reports for review and record-keeping.

## Key Features in This Repository

- **Configuration upload:** `.cfg`, `.conf`, `.txt`, and `.json` are listed as supported extensions in the project configuration; the local quick-start guide documents a 10 MB upload limit.
- **Vendor parsing:** dedicated parser modules are present for Cisco, Fortinet, Juniper, and Palo Alto, plus an unknown-configuration fallback. The repository's quick-start documentation specifically highlights Cisco IOS and Fortinet examples.
- **Vendor-neutral model:** normalized fields cover areas such as remote access, management protocols, authentication, logging, and access control.
- **Rule-based compliance engine:** rules are defined in `backend/app/compliance/rules.yaml`. The included sample rules check issues such as Telnet being disabled, SSH being enabled and using version 2, HTTP management being disabled, authentication settings, logging, and session timeouts.
- **Adaptive mapping workflow:** the `backend/app/adaptive/` modules implement mapping candidates, confidence scoring, human review, and learning-related logic. Treat this as an assisted interpretation workflow, not automatic guaranteed support for arbitrary syntax.
- **Findings and remediation:** the backend contains findings, deviation, posture, and remediation modules to support risk review and corrective guidance.
- **PDF reporting:** report-generation modules use ReportLab to create audit reports with findings and remediation context.
- **Operational features:** the codebase also includes authentication/RBAC-related modules, configuration versioning, drift detection, webhooks/events, search, monitoring, and knowledge-graph modules.

## Technology Stack

| Layer | Technologies in the repository |
|---|---|
| Frontend | React 18, TypeScript, Vite, React Router, Axios, Recharts, Tailwind CSS |
| Backend API | Python, FastAPI, Uvicorn, Pydantic |
| Data layer | SQLAlchemy, Alembic; SQLite is configured as a simple development option, PostgreSQL is supported in the Docker Compose setup |
| Cache / asynchronous infrastructure | Redis and Celery-related configuration in the project |
| Parsing and compliance | Python parser modules, YAML-defined rules, normalized security schema |
| AI/ML support | Sentence Transformers and scikit-learn dependencies; adaptive mapping and confidence-scoring modules |
| PDF reporting | ReportLab and Pillow |
| Deployment / quality tooling | Docker, Docker Compose, GitHub Actions workflow files |

The repository includes integrations and modules for AI-assisted analysis, but an external LLM provider is not required to understand the basic rule-based workflow. Provider-specific features require the relevant environment variables and configuration.

## Architecture Overview

```text
Administrator
    |
    v
React + TypeScript Web UI
    |  Upload / review / audit / reports
    v
FastAPI Backend
    |
    +--> File validation and ingestion
    |
    +--> Vendor detection and configuration parsers
    |        Cisco | Fortinet | Juniper | Palo Alto | Unknown fallback
    |
    +--> Normalization --> Unified Security Model (structured fields)
    |                         |
    |                         v
    |                  Compliance Rule Engine
    |                         |
    |                         v
    |                  Findings / severity / evidence
    |
    +--> Adaptive mapping + confidence + human review
    |
    +--> Remediation guidance and PDF report generation
    |
    v
Database / optional infrastructure
SQLite for simple local development; PostgreSQL, Redis and MinIO are represented in Docker configuration
```

## Quick Start — Local Development

### Prerequisites

- Python version compatible with the backend dependencies (Python 3.11 is a sensible baseline for this project)
- Node.js and npm
- Git
- Optional: Docker and Docker Compose for the containerized infrastructure

### 1. Get the source

```bash
git clone <YOUR_REPOSITORY_URL>
cd Prototype1-main
```

Replace `<YOUR_REPOSITORY_URL>` with the repository's actual Git URL. The ZIP supplied for review does not establish a public GitHub URL, so one is not invented here.

### 2. Configure the backend

From the repository root:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Review `.env` before starting the service. The example config uses SQLite for development and defines upload/storage paths and API settings. Do not put real secrets in source control. If enabling SMTP or an external AI provider, set the corresponding credentials in your local environment.

### 3. Install backend dependencies and run the API

```bash
cd backend
python -m venv .venv
```

Activate the environment:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# Linux/macOS
source .venv/bin/activate
```

Install dependencies and start FastAPI:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

If the database schema has not been initialized in your environment, review the Alembic configuration and apply migrations as appropriate for the configured database:

```bash
alembic upgrade head
```

The repository also contains a `backend/scripts/create_admin.py` script referenced by the quick-start documentation for creating a local admin account. Use that script only after reviewing its behavior and configuring the local database.

### 4. Install frontend dependencies and run the UI

Open a second terminal from the repository root:

```bash
cd frontend
npm install
npm run dev
```

Vite normally serves the frontend at `http://localhost:5173`. Ensure the frontend's API base URL/environment configuration points to the backend at `http://127.0.0.1:8000` if required by your local setup.

### 5. Open the application

- **Frontend:** http://localhost:5173
- **FastAPI Swagger UI:** http://127.0.0.1:8000/docs
- **FastAPI ReDoc:** http://127.0.0.1:8000/redoc

Actual API routes are defined in `backend/app/api/`; use the running Swagger UI as the authoritative list for the checked-out version.

## Docker-Based Setup

The repository contains `docker-compose.yml` with PostgreSQL, Redis, MinIO, backend, and optional supporting services. Before using it:

1. Install Docker Desktop or Docker Engine with the Compose plugin.
2. Review the Compose file and environment defaults.
3. Set strong local passwords/secrets in an ignored `.env` file; never expose sample defaults publicly.
4. Start the services from the repository root:

```bash
docker compose up --build -d
```

5. Check service status and logs:

```bash
docker compose ps
docker compose logs -f backend
```

The Compose stack is more involved than the SQLite local setup. If a service fails, check its health status and environment variables before retrying. Stop the stack with `docker compose down`; add `-v` only if you intentionally want to delete persisted volumes and their data.

## How to Use the Demo

1. Open the [live preview](https://vajracores.vercel.app/) or run the project locally.
2. Sign in with the repository-provided demo credentials if accepted by the target environment; otherwise create an account in the UI.
3. Navigate to **Upload** and submit a sample network configuration file. Sample configurations are included under `demo_configs/` and in `frontend/public/demo-configs/`.
4. Open the configuration list and start an audit for the uploaded configuration.
5. Review the compliance score/findings, evidence, severity, and remediation suggestions shown by the application.
6. Use the reporting functionality to generate a PDF where available.
7. For unfamiliar configuration syntax, inspect the adaptive mapping/learning workflow and treat suggested mappings as requiring administrator review.

### Included sample configuration files

- `demo_configs/cisco/cisco_insecure.cfg`
- `demo_configs/cisco/cisco_secure.cfg`
- `demo_configs/fortinet/fortinet_insecure.conf`
- `demo_configs/fortinet/fortinet_secure.conf`
- `demo_configs/unknown/complex_proprietary.conf`
- `demo_configs/unknown/vendor_xyz.conf`

These examples are useful for a controlled demonstration of differences between secure and insecure settings. Use synthetic/sample configurations for evaluation; do not upload real production configurations containing credentials, keys, public IPs, or sensitive topology details unless your environment has been approved for that data.

## Compliance Rules and Framework Mapping

The included `backend/app/compliance/rules.yaml` defines a baseline rule set using normalized fields and expected values. Examples include:

| Example control | Normalized field | Expected condition |
|---|---|---|
| Telnet disabled | `remote_access.telnet_enabled` | `false` |
| SSH enabled | `remote_access.ssh_enabled` | `true` |
| SSH version 2 | `remote_access.ssh_version` | `2` |
| HTTP management disabled | `management.http_enabled` | `false` |
| Logging enabled | `logging.enabled` | `true` |
| Session timeout configured | `access_control.timeout_configured` | `true` |

The sample rule file references CIS and NIST 800-53 in its control metadata. The repository documentation also names PCI-DSS, NIST CSF, ISO 27001, HIPAA, and custom rules; however, the presence of a framework name does **not** prove complete, formally validated coverage of that standard. This prototype's actual evaluation scope is limited by the implemented rules and mappings. Full CIS Benchmark, NIST SP 800-53, DISA STIG, or ISO/IEC 27001 coverage requires authoritative control mappings, versioned rule packs, validation, and maintenance.

## Supported Input and Vendor Coverage

The project is structured to extend vendor support through parser modules and a normalized schema. Dedicated parser modules are present for Cisco, Fortinet, Juniper, and Palo Alto; an unknown parser/fallback is also present. Additional vendor names in the problem statement—including Check Point, Arista, Aruba, MikroTik, SONiC, cloud security groups, and SASE platforms—should be treated as **future integration targets unless a parser and tested mapping are implemented for the relevant syntax**.

A generic fallback or AI-generated suggestion is not equivalent to verified parsing. Always confirm the detected vendor, normalized fields, and evidence before using results for a compliance decision.

## Security and Operational Notes

- Use a strong, unique `JWT_SECRET_KEY` and production-grade database credentials in deployed environments.
- Change or disable the sample demo password before any public deployment.
- Keep `.env`, API keys, certificates, private keys, and production configurations out of Git.
- Restrict upload size and file types, and review any configuration file before submitting it.
- Treat generated remediation commands as recommendations: back up the device configuration, verify syntax against the exact vendor/OS version, test in a lab/change window, and maintain a rollback plan.
- Use HTTPS and appropriately restricted CORS settings in deployment.
- Do not treat an AI mapping or compliance score as a certification or substitute for a qualified security audit.

## Repository Map

```text
.
├── backend/
│   ├── app/
│   │   ├── adaptive/       # Mapping suggestions, confidence, human-in-loop workflow
│   │   ├── api/            # FastAPI route modules
│   │   ├── compliance/     # Compliance evaluator and rules.yaml
│   │   ├── detection/      # Vendor detection
│   │   ├── normalization/  # Unified security model/schema
│   │   ├── parsers/        # Vendor-specific and fallback parsers
│   │   ├── remediation/    # Remediation guidance/templates
│   │   └── reports/        # PDF report generation
│   ├── alembic/            # Database migrations
│   ├── scripts/            # Utility scripts, including local admin setup
│   └── requirements.txt
├── frontend/               # React + TypeScript + Vite application
├── demo_configs/           # Sample network configuration files
├── .env.example            # Development environment template
├── docker-compose.yml      # Containerized services
└── QUICK_START.md          # Additional local quick-start notes
```

## Testing and Build Checks

Backend tests are intended to be run with pytest where the corresponding test suite is present:

```bash
cd backend
pytest
```

Frontend production build:

```bash
cd frontend
npm run build
```

The ZIP reviewed for this README does not, by itself, establish that every test passes in a clean environment or that the hosted deployment is currently healthy. Run these checks in the target environment before presenting a release as verified.

## Known Limitations / Future Work

- Expand and validate parsers for the full range of vendors, device families, firmware versions, and cloud networking platforms listed in the problem statement.
- Maintain versioned, traceable mappings to CIS Benchmarks, NIST SP 800-53, DISA STIGs, and ISO/IEC 27001, including evidence and control identifiers.
- Add robust regression fixtures for each parser and each supported OS/version.
- Persist and govern approved human mappings with audit trails, review status, and rollback/versioning.
- Validate remediation commands against vendor/OS versions and add explicit pre-checks, post-checks, and rollback guidance.
- Add deployment-specific health checks, secret management, and documented backup/recovery procedures.

## License

The repository README currently displays an MIT license badge, but a badge alone is not a license grant. Include the full `LICENSE` file and confirm the intended licensing terms before redistributing the project.

## Project Links

- **Live preview:** https://vajracores.vercel.app/
- **Source repository:** Add the final public GitHub/Drive URL here before submission.
