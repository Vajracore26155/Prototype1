# VAJRA CORE : AI-Driven Multi-Vendor Network Security Compliance Auditor

**Problem statement / organization:** National Technical Research Organisation (NTRO)  
**Live preview:** https://vajracores.vercel.app/  
**Project type:** Network configuration auditing, security compliance, and AI-assisted configuration mapping.

## Table of Contents

1. [Overview](#1-overview)
2. [Problem Statement](#2-problem-statement)
3. [Solution and Workflow](#3-solution-and-workflow)
4. [Features in the Repository](#4-features-in-the-repository)
5. [Live Preview and Demo Credentials](#5-live-preview-and-demo-credentials)
6. [Technology Stack](#6-technology-stack)
7. [Architecture](#7-architecture)
8. [Repository Structure](#8-repository-structure)
9. [Vendor Detection and Parser Coverage](#9-vendor-detection-and-parser-coverage)
10. [Compliance Frameworks and Rules](#10-compliance-frameworks-and-rules)
11. [Local Installation](#11-local-installation)
12. [Docker Setup](#12-docker-setup)
13. [Using the Application](#13-using-the-application)
14. [Sample Configurations](#14-sample-configurations)
15. [Adaptive Mapping](#15-adaptive-mapping)
16. [Audit Reports and Remediation](#16-audit-reports-and-remediation)
17. [Security Notes](#17-security-notes)
18. [Testing and Build Commands](#18-testing-and-build-commands)
19. [Current Scope and Limitations](#19-current-scope-and-limitations)
20. [NTRO Submission Deliverables](#20-ntro-submission-deliverables)
21. [Project Links](#21-project-links)

---

## 1. Overview

VAJRA CORE is a web application for reviewing network-device configuration files and identifying security settings that may violate a defined baseline. It combines a React/TypeScript frontend with a Python FastAPI backend. The backend contains vendor detection, vendor-specific parsers, a vendor-neutral security model, compliance rules, adaptive mapping components, remediation templates, and PDF report generators.

The project addresses a common network-security challenge: devices from different vendors represent similar security controls using different configuration syntax. By mapping recognized settings into a common model, the application can evaluate them against shared rules instead of requiring each rule to understand every vendor's syntax.

### Objectives

- Provide a single interface for uploading and reviewing network configuration files.
- Detect known configuration vendors and route them to the corresponding parser.
- Normalize recognized settings into a shared security model.
- Evaluate normalized settings against configured security controls.
- Present audit findings and remediation context.
- Provide an assisted workflow for reviewing unfamiliar configuration patterns.
- Generate PDF audit reports.

## 2. Problem Statement

Enterprise environments combine routers, switches, firewalls, cloud networking, and security appliances from multiple manufacturers. Their command-line syntax and configuration structures differ, making centralized security review difficult. Manual audits are time-consuming, while vendor-specific tools may not cover a mixed environment.

The NTRO problem statement highlights two central challenges:

1. **Syntactic diversity:** The same security objective can be represented differently across vendor operating systems.
2. **Adaptability:** New or changed configuration formats can exceed the coverage of existing parsers.

VAJRA CORE addresses these challenges through parser-based extraction, normalization, configurable compliance evaluation, and an adaptive mapping workflow with human review.

## 3. Solution and Workflow

The intended processing flow is:

1. **Upload:** An administrator submits a configuration file through the web interface.
2. **Validate:** The backend checks the upload against supported file types and size limits.
3. **Detect:** Vendor detection uses configuration signatures to classify known formats or return an unknown result.
4. **Parse:** The matching parser extracts security-relevant settings.
5. **Normalize:** Extracted values are represented in the `UnifiedSecurityModel` defined in `backend/app/normalization/schema.py`.
6. **Evaluate:** Compliance rules compare normalized fields with expected values.
7. **Review:** The application exposes audit results and findings through its UI/API.
8. **Remediate:** Remediation-related modules provide guidance associated with detected issues.
9. **Report:** ReportLab-based modules generate PDF audit reports.
10. **Adapt:** Unrecognized patterns can be reviewed through the adaptive mapping and human-in-the-loop components.

The quality of the result depends on the parser's coverage, the evidence extracted, the configured rules, and the correctness of any accepted mapping.

## 4. Features in the Repository

The repository contains code for the following capabilities:

- **Configuration upload:** API routes and frontend pages for configuration upload.
- **Bulk/vendor upload workflows:** Additional upload routes for vendor-oriented processing.
- **Vendor detection:** Signature-based detection for Cisco, Fortinet, Palo Alto, Juniper, AWS-related security-group JSON, and unknown formats.
- **Dedicated parsers:** Cisco, Fortinet, Juniper, Palo Alto, and unknown-format parser modules.
- **Unified security model:** Typed fields for device information, remote access, management protocols, authentication, logging, and access control, including evidence fields.
- **Compliance evaluation:** YAML-based network security rules and a multi-framework engine.
- **Audit findings and risk/posture components:** Modules for findings, risk scoring, posture, and drift analysis.
- **Adaptive mapping:** Candidate mapping, embeddings, confidence scoring, vocabulary, learning, and human-in-the-loop components.
- **Remediation support:** Remediation API/module and YAML templates.
- **PDF reports:** Standard and enhanced PDF report generators implemented with ReportLab.
- **Application security/infrastructure components:** Authentication, role/permission logic, request middleware, rate limiting, database integration, Redis/Celery tasks, object-storage integration, monitoring, and webhooks.

The presence of a module means code is present; the complete end-to-end behavior and deployment configuration should still be tested in the environment being demonstrated.

## 5. Live Preview and Demo Credentials

### Live Preview

**Application:** https://vajracores.vercel.app/

The live link is supplied as the project's frontend preview. The frontend API client uses relative `/api` paths, so successful end-to-end operations also depend on the deployed API and routing configuration. Live backend connectivity and the credentials below have not been verified from this repository inspection.

### Local Development Demo Account

The repository's `QUICK_START.md` and `backend/scripts/create_admin.py` document these local development credentials:

| Field | Value |
|---|---|
| Email | `admin@tatva.security` |
| Password | `admin123` |
| Intended use | Local development only |

The `create_admin.py` script creates this account only when the database contains no users. Run it from the `backend` directory after installing dependencies and configuring the database. The application startup code also supports environment-configured default-admin creation using `DEFAULT_ADMIN_EMAIL` and `DEFAULT_ADMIN_PASSWORD`.

**These credentials are not confirmed to work on the hosted Vercel preview.** Do not use the sample password in a public or production deployment. Change it immediately if used locally.

## 6. Technology Stack

| Layer | Technologies found in the repository | Purpose |
|---|---|---|
| Frontend | React 18, TypeScript, Vite | Web interface and production build |
| UI and navigation | React Router, Tailwind CSS, Lucide React | Navigation, styling, icons |
| API client and upload | Axios, React Dropzone | HTTP requests and file selection |
| Charts | Recharts | Dashboard visualizations |
| Backend API | Python 3.11, FastAPI, Uvicorn | REST API and application services |
| Validation/settings | Pydantic, python-dotenv | Request/data validation and environment configuration |
| Database | SQLAlchemy, Alembic; SQLite for development and optional PostgreSQL | Persistence and schema management |
| Compliance/configuration | PyYAML | Declarative rules and remediation templates |
| AI/ML dependencies | Sentence Transformers, scikit-learn; provider integrations are present in the project dependency configuration | Embedding-based mapping and supporting AI/ML workflows |
| Async/background work | Redis, Celery, APScheduler | Queued tasks, caching/broker-related functions, scheduling |
| Object storage | MinIO client | S3-compatible storage integration |
| Reports | ReportLab, Pillow | PDF report generation and image handling |
| Monitoring | Prometheus client, psutil, structured logging dependencies | Metrics and operational visibility |
| Security | JWT-related `python-jose`, bcrypt dependency, validation and rate-limiting modules | Authentication and request protection |
| Containers | Docker, Docker Compose | Multi-service development/deployment |
| CI workflows | GitHub Actions workflow files | CI/CD and security workflow configuration |

Not every optional service or AI provider is required for a basic local run. Some integrations require environment variables and separate services.

## 7. Architecture

```text
+----------------------------+
| Administrator / Reviewer   |
+--------------+-------------+
               |
               v
+----------------------------+
| React + TypeScript Frontend|
+--------------+-------------+
               | HTTP API
               v
+----------------------------+
| FastAPI Backend            |
| Upload / Audit / Findings  |
| Auth / Reports / Learning  |
+--------------+-------------+
               |
               v
+----------------------------+
| Vendor Detection           |
| Cisco / Fortinet / Juniper |
| Palo Alto / AWS / Unknown  |
+--------------+-------------+
               |
               v
+----------------------------+
| Vendor-Specific Parsers    |
+--------------+-------------+
               |
               v
+----------------------------+
| UnifiedSecurityModel       |
| Device + Security Settings |
| + Evidence                 |
+--------------+-------------+
               |
               v
+----------------------------+
| Compliance Rules / Engine  |
+--------------+-------------+
               |
        +------+------+
        |             |
        v             v
+---------------+ +----------------+
| Findings, Risk| | Remediation and|
| / Posture     | | PDF Reports    |
+---------------+ +----------------+

Supporting components include database persistence, optional Redis/Celery,
MinIO object storage, monitoring, webhooks, and adaptive mapping/review.
```

### Main architectural components

- **Detection:** `backend/app/detection/vendor_detector.py`
- **Parsers:** `backend/app/parsers/`
- **Normalization model:** `backend/app/normalization/schema.py`
- **Rule-based compliance:** `backend/app/compliance/evaluator.py` and `rules.yaml`
- **Multi-framework mappings:** `backend/app/compliance/framework_engine.py`
- **Adaptive mapping:** `backend/app/adaptive/`
- **Remediation:** `backend/app/remediation/`
- **PDF reports:** `backend/app/reports/`
- **API routes:** `backend/app/api/`

## 8. Repository Structure

```text
Prototype1-main/
├── .github/workflows/       # CI, CD, and security workflows
├── backend/
│   ├── app/
│   │   ├── adaptive/        # Candidate mapping, confidence, learning, review
│   │   ├── api/             # FastAPI route modules
│   │   ├── compliance/      # Rule evaluation and framework engine
│   │   ├── detection/       # Vendor detection
│   │   ├── normalization/   # Unified security model
│   │   ├── parsers/         # Vendor and unknown-format parsers
│   │   ├── remediation/     # Remediation logic/templates
│   │   ├── reports/         # PDF report generators
│   │   ├── drift/           # Configuration drift components
│   │   ├── posture/         # Posture scoring/trends
│   │   └── main.py          # FastAPI application entry point
│   ├── alembic/             # Database migration files
│   ├── scripts/             # Setup utilities, including create_admin.py
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/
│   ├── src/                 # React/TypeScript application
│   ├── public/demo-configs/ # Public demo configuration samples
│   └── package.json
├── demo_configs/            # Sample Cisco, Fortinet, and unknown configs
├── docs/                    # Architecture, deployment, and implementation docs
├── infrastructure/          # Infrastructure setup resources
├── monitoring/              # Prometheus and Grafana configuration
├── docker-compose.yml
├── docker-compose.production.yml
├── .env.example
├── QUICK_START.md
└── README.md
```

## 9. Vendor Detection and Parser Coverage

### Detection coverage

The detector defines signatures for:

- Cisco IOS/IOS-XE/IOS-XR-style configurations
- Fortinet FortiGate
- Palo Alto PAN-OS
- Juniper JunOS
- AWS Security Groups represented as JSON
- Unknown formats

### Dedicated parser modules

The parser package provides modules for Cisco, Fortinet, Palo Alto, Juniper, and unknown configurations. The parser dispatch function selects a parser for these vendor labels and falls back to the unknown parser when no matching label is supplied.

| Vendor / format | Code found | Qualification |
|---|---|---|
| Cisco | Detector signatures and parser | Coverage depends on the commands implemented in the parser |
| Fortinet | Detector signatures and parser | Coverage depends on the configuration syntax/version |
| Palo Alto | Parser and detector support | Validate with representative PAN-OS exports |
| Juniper | Parser and detector support | Parser includes Juniper-specific handling; validate target syntax/version |
| AWS security-group JSON | Detector support | A detector signature does not imply a full cloud API collector or complete AWS audit implementation |
| Unknown / proprietary | Fallback parser and adaptive modules | Unknown syntax may require manual mapping and validation |

The repository does **not** establish universal support for every device listed in the NTRO problem statement. Cisco Firepower/Meraki, Check Point, Aruba, Arista, MikroTik, SONiC, Azure, GCP, and the other listed products should be treated as future integration targets unless individually tested and documented.

### File types and size

The primary upload API and frontend support `.cfg`, `.conf`, `.txt`, and `.json` files, with a default 10 MB limit. Some enhanced validation code also mentions `.xml`; accepted formats can vary by endpoint, so the primary upload flow should be used for a consistent demonstration.

## 10. Compliance Frameworks and Rules

### Framework engine

`backend/app/compliance/framework_engine.py` defines framework types for:

- CIS Benchmarks
- NIST SP 800-53
- DISA STIG
- ISO 27001

The engine includes framework control metadata and cross-framework mappings. The repository's `backend/app/compliance/rules.yaml` contains 10 network-security rules that evaluate normalized fields.

**Important scope distinction:** Framework identifiers and mappings in code do not prove full, official benchmark coverage or certification. The rules should be treated as a prototype baseline and validated against the specific benchmark version and device platform before being used for formal compliance claims.

### Examples from `rules.yaml`

| Rule ID | Control | Field checked | Expected value | Severity in rule file |
|---|---|---|---|---|
| NET-001 | Telnet must be disabled | `remote_access.telnet_enabled` | `false` | HIGH |
| NET-002 | SSH must be enabled | `remote_access.ssh_enabled` | `true` | HIGH |
| NET-003 | SSH version 2 required | `remote_access.ssh_version` | `2` | MEDIUM |
| NET-004 | HTTP management must be disabled | `management.http_enabled` | `false` | HIGH |
| NET-005 | HTTPS management should be enabled | `management.https_enabled` | `true` | MEDIUM; optional |
| NET-006 | Local authentication should be enabled | `authentication.local_authentication` | `true` | MEDIUM |
| NET-007 | Enable secret should be configured | `authentication.enable_secret_configured` | `true` | HIGH |
| NET-008 | Password encryption should be enabled | `authentication.password_encryption` | `true` | LOW; optional |
| NET-009 | Logging should be enabled | `logging.enabled` | `true` | MEDIUM |
| NET-010 | Session timeout should be configured | `access_control.timeout_configured` | `true` | LOW; optional |

Rules are evaluated against the normalized model. If a value is not extracted, the system's result depends on the evaluator's handling of missing/unknown values; missing evidence should not automatically be interpreted as proof that a control is compliant.

## 11. Local Installation

### Prerequisites

- Python **3.11** (the `backend/pyproject.toml` specifies `>=3.11,<3.12`)
- Node.js and npm
- Git
- Optional: Docker and Docker Compose for the multi-service setup

### Step 1 — Get the code

```bash
git clone <YOUR_REPOSITORY_URL>
cd Prototype1-main
```

Replace `<YOUR_REPOSITORY_URL>` with the repository URL. If you downloaded the ZIP instead, extract it and open the `Prototype1-main` directory.

### Step 2 — Configure environment

From the repository root:

**Windows PowerShell**

```powershell
Copy-Item .env.example .env
```

**Linux/macOS**

```bash
cp .env.example .env
```

Review `.env` before starting services. The example uses SQLite for development and sets default local paths for uploads, normalized files, and reports. Do not commit `.env` or real credentials.

### Step 3 — Install backend dependencies

```bash
cd backend
python -m venv .venv
```

Activate the environment:

**Windows PowerShell**

```powershell
.venv\Scripts\Activate.ps1
```

**Linux/macOS**

```bash
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

The backend's declared Python range is 3.11.x. If dependency installation fails under another Python version, use Python 3.11 and consult `backend/pyproject.toml`.

### Step 4 — Initialize the local administrator (optional)

From the `backend` directory, with the virtual environment activated:

```bash
python scripts/create_admin.py
```

This creates the local demo account only if the database has no existing users. The script uses the sample credentials listed in [Live Preview and Demo Credentials](#5-live-preview-and-demo-credentials). Do not run it against a production database without reviewing the script and changing the credentials.

### Step 5 — Start the backend

From the `backend` directory:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The FastAPI application is configured in `backend/app/main.py`. The development database defaults to SQLite, based on the environment configuration and database settings.

### Step 6 — Start the frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Vite normally serves the frontend at `http://localhost:5173`.

### Local URLs

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend root | http://127.0.0.1:8000/ |
| FastAPI Swagger UI | http://127.0.0.1:8000/docs |
| FastAPI ReDoc | http://127.0.0.1:8000/redoc |
| Health endpoint | http://127.0.0.1:8000/health |

The frontend API service uses relative `/api` URLs. Ensure that the local frontend's development proxy or deployment routing is configured to route API requests to the backend. If API calls fail while the frontend loads, inspect the browser network panel and `frontend/vite.config.ts`.

## 12. Docker Setup

The repository includes a `docker-compose.yml` describing a multi-service setup with PostgreSQL, Redis, MinIO, the backend, and Celery-related services. It also defines supporting services such as Keycloak in the Compose configuration. These services require Docker and may need environment adjustments for your machine.

From the repository root:

```bash
cp .env.example .env
```

On Windows PowerShell, use `Copy-Item .env.example .env` instead. Review and replace default secrets before starting containers.

Start services:

```bash
docker compose up --build -d
```

Inspect service status and logs:

```bash
docker compose ps
docker compose logs -f backend
```

Stop services:

```bash
docker compose down
```

To remove named volumes as well:

```bash
docker compose down -v
```

**Warning:** `docker compose down -v` deletes persisted service data. The Compose file has multiple services and environment dependencies; verify the configuration and service health before relying on this setup for a demonstration or deployment.

## 13. Using the Application

The repository's `QUICK_START.md` describes the basic local workflow:

1. Open the frontend.
2. Sign in using the local demo account or register if appropriate for the environment.
3. Open the upload page.
4. Upload a sample configuration file.
5. Open the configurations view and run an audit.
6. Review the audit findings.
7. Download a PDF report if the report endpoint is available and functioning in the running environment.

The repository contains separate general and vendor-oriented upload/dashboard flows. The exact UI path depends on the route and environment being used. For a reviewer demo, use one known sample file and confirm that the audit and report steps complete successfully before recording the demonstration.

## 14. Sample Configurations

Sample files are included in `demo_configs/`:

| Path | Purpose |
|---|---|
| `demo_configs/cisco/cisco_insecure.cfg` | Cisco configuration intended to exercise insecure-setting checks |
| `demo_configs/cisco/cisco_secure.cfg` | Cisco configuration intended to represent a more secure baseline |
| `demo_configs/fortinet/fortinet_insecure.conf` | Fortinet insecure-configuration example |
| `demo_configs/fortinet/fortinet_secure.conf` | Fortinet secure-configuration example |
| `demo_configs/unknown/complex_proprietary.conf` | Unfamiliar/proprietary-format example |
| `demo_configs/unknown/vendor_xyz.conf` | Unknown-vendor example |

Some samples are also published under `frontend/public/demo-configs/` for frontend access.

### Suggested demo

1. Upload `cisco_insecure.cfg`.
2. Run the audit and review the findings.
3. Upload `cisco_secure.cfg` and compare results.
4. Repeat with the Fortinet examples.
5. Try an unknown-format sample to show the fallback/adaptive-mapping concept, if that workflow is available in the running UI.
6. Generate a PDF report.

Use the repository's sample files rather than real customer configurations during a public demonstration.

## 15. Adaptive Mapping

The repository contains adaptive components in `backend/app/adaptive/`, including candidate mapping, confidence scoring, an embedding engine, vocabulary handling, learning logic, and a human-in-the-loop workflow. Learning-related API routes are also present.

The intended workflow is:

1. A parser or detector encounters content it cannot confidently interpret.
2. The adaptive components help produce or rank possible mappings.
3. A reviewer examines the raw configuration evidence and proposed normalized field.
4. A reviewer accepts or rejects the mapping through the available learning workflow.
5. Accepted mappings can be reused to the extent supported by the implementation and persistence layer.

For example, a vendor-specific command that controls an administrative timeout could be mapped to `access_control.timeout_configured` after its meaning has been validated.

This is an assisted-learning design, not a guarantee that the system can automatically interpret every proprietary command. Mapping quality, confidence thresholds, persistence, and reuse should be verified with test cases before claiming that a new vendor is fully supported.

## 16. Audit Reports and Remediation

The repository includes `backend/app/reports/pdf_generator.py` and `backend/app/reports/enhanced_pdf_generator.py`, which use ReportLab. Report API routes are located in `backend/app/api/reports.py` and audit routes are in `backend/app/api/audit.py`.

The code is intended to provide audit reports and findings with compliance and remediation context. The exact report fields depend on the data available to the application and the report template. Device serial number, hardware model, or firmware details can only be reported when collected or extracted; do not assume those fields are always available in text configuration files.

### Remediation safety

Generated remediation guidance must be checked against the actual device model, OS version, and current configuration before use. Before applying changes:

1. Review the relevant finding and evidence.
2. Confirm the vendor command and syntax for the exact platform/version.
3. Back up the device configuration.
4. Test in a lab or staging environment where possible.
5. Follow change-management approval and prepare a rollback plan.

The application should be used as an auditing aid, not as an unreviewed automatic production configuration changer.

## 17. Security Notes

Network configuration files may contain sensitive data. For development and demonstrations:

- Use the included sample configurations or sanitized files.
- Never commit `.env`, API keys, database passwords, JWT secrets, or real credentials.
- Change the local default admin password before any shared or deployed use.
- Replace default Docker service passwords and restrict exposed ports.
- Use HTTPS and appropriate CORS settings in a public deployment.
- Restrict access to uploaded configurations, reports, and administrative endpoints.
- Review file validation, upload size limits, and rate limiting.
- Avoid exposing detailed errors or sensitive configuration contents in logs.
- Review AI/LLM provider configuration before enabling external services; do not send confidential configurations to a third party without authorization.
- Validate all suggested mappings and remediation commands.

Compliance findings depend on the implemented parser, rule set, mapping, and available evidence. The project is a prototype and is not a guarantee of formal certification or complete compliance with a framework.

## 18. Testing and Build Commands

### Backend tests

The dependency list includes `pytest` and `pytest-asyncio`. From the backend directory, after installing dependencies:

```bash
pytest
```

To run a specific test file if present:

```bash
pytest path/to/test_file.py
```

Confirm the repository's current test files before using a specific path. No claim is made here that the complete test suite has passed.

### Frontend production build

From the frontend directory:

```bash
npm install
npm run build
```

The `build` script runs TypeScript compilation followed by Vite's production build. The frontend package also defines `npm run lint` for ESLint checks.

### Recommended validation cases

- Upload an allowed file and reject a disallowed file.
- Verify vendor detection for each included vendor sample.
- Confirm that parser output contains expected normalized fields and evidence.
- Verify each compliance rule against known secure/insecure examples.
- Test missing or unknown fields without treating missing evidence as a pass.
- Exercise unknown-format fallback and the mapping review flow.
- Confirm that generated reports contain the findings returned by the audit.
- Verify unauthenticated requests are rejected for protected routes.
- Test the live preview's API connectivity separately from its frontend loading.

These are recommended tests, not a claim that all cases have already passed.

## 19. Current Scope and Limitations

### Implemented code areas

- Frontend pages for login, registration, dashboards, uploads, configurations, audit views, and vendor-oriented workflows.
- FastAPI route modules for upload, audit, findings, frameworks, reports, learning, remediation, configuration versions, drift, monitoring, and related functions.
- Four dedicated vendor parser modules plus an unknown parser.
- Vendor detection signatures that also include AWS security-group JSON detection.
- A normalized security schema with evidence fields.
- Ten YAML-based network security rules.
- A multi-framework engine with CIS, NIST 800-53, DISA STIG, and ISO 27001 identifiers/mappings.
- Adaptive mapping and human-review modules.
- PDF report generation modules.

### Limitations to communicate clearly

- The code does not prove complete support for every vendor, device model, firmware release, or configuration command.
- AWS detection does not by itself mean full AWS API collection or complete cloud security-group compliance auditing.
- Framework mappings and sample rules should not be represented as complete official benchmark coverage without additional validation.
- Serial numbers and hardware details may not be present in text configuration exports.
- Adaptive mapping suggestions need human validation and regression testing.
- Live deployment functionality and credentials are not confirmed by inspecting the ZIP alone.
- A successful frontend build or running API does not, on its own, prove that every workflow works end-to-end.

### Future improvements

- Add parsers and fixtures for additional vendors and network operating systems.
- Build version-specific tests for every parser and compliance rule.
- Maintain traceable mappings to exact benchmark versions and controls.
- Improve mapping approval history, versioning, rollback, and regression protection.
- Validate remediation commands against device and OS versions.
- Add broader cloud-native auditing integrations for AWS, Azure, and GCP.
- Add signed or versioned audit artifacts and stronger report provenance.

## 20. NTRO Submission Deliverables

The problem statement requests the following evaluation deliverables:

| Deliverable | Action before submission |
|---|---|
| Source code link | Add the public GitHub/Drive URL below |
| README with setup instructions | This README |
| Architecture document (maximum 2 pages) | Prepare and link a separate document |
| Demo video (maximum 2 minutes) | Record the working workflow and link it |
| Technical presentation (maximum 5 slides) | Prepare and link the slides |
| Live preview | https://vajracores.vercel.app/ |

### Suggested two-minute demo sequence

- **0:00–0:15:** Introduce the problem and VAJRA CORE.
- **0:15–0:35:** Show the dashboard and upload page.
- **0:35–1:00:** Upload a sample configuration and run the audit.
- **1:00–1:25:** Explain a finding, its evidence, and remediation context.
- **1:25–1:45:** Show adaptive mapping if it works in the deployed environment.
- **1:45–2:00:** Generate/show the PDF report and summarize the outcome.

Only demonstrate capabilities that have been tested in the version being presented.

## 21. Project Links

- **Live preview:** https://vajracores.vercel.app/
- **Source repository:** _Add your GitHub/Drive URL here._
- **Architecture document:** _Add link before submission._
- **Demo video:** _Add link before submission._
- **Technical presentation:** _Add link before submission._

---

## Conclusion

VAJRA CORE provides a modular prototype for network configuration security auditing. Its codebase brings together vendor detection, vendor-specific parsers, a unified security model, configurable compliance rules, adaptive mapping components, remediation support, and PDF reporting. The design provides a foundation for expanding heterogeneous network audits, while reliable enterprise use requires continued parser coverage, benchmark validation, end-to-end testing, and human review of uncertain mappings and remediation actions.

**Project:** VAJRA CORE — AI-Driven Multi-Vendor Network Security Compliance Auditor  
**Organization:** National Technical Research Organisation (NTRO)  
**Live preview:** https://vajracores.vercel.app/
