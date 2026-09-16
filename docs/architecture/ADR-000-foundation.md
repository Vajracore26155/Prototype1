# ADR-000: Phase 0.5 Foundation Architecture

**Status**: PROPOSED  
**Date**: 2026-09-16  
**Decision Makers**: Lead Principal Engineer  
**Phase**: 0.5 - Foundation

---

## Context

Vajra Core has passed internal hackathon with a working prototype. The system demonstrates the core innovation: vendor-agnostic security configuration auditing through a unified normalization layer.

Before proceeding to full production development (Phase 0 onwards), we must establish a production-oriented foundation without destroying the working prototype.

---

## Current Architecture

### What We Have (Working Prototype)

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                             │
│                  React + TypeScript + Vite                   │
│                     Tailwind CSS + Axios                     │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/REST
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                      BACKEND API                             │
│                    FastAPI + Uvicorn                         │
│                                                              │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  Ingestion │→ │ Vendor Detect│→ │   Parser      │       │
│  └────────────┘  └──────────────┘  └──────┬───────┘       │
│                                             ↓                │
│                                    ┌────────────────┐       │
│                                    │ Normalization  │       │
│                                    │ (USM Creation) │       │
│                                    └────────┬───────┘       │
│                                             ↓                │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Compliance │← │   Findings    │← │     Risk      │       │
│  │ Evaluation │  │   Generation  │  │   Scoring     │       │
│  └────────────┘  └──────────────┘  └──────────────┘       │
│                                                              │
│  ┌────────────┐  ┌──────────────┐                          │
│  │Remediation │  │ AI Learning   │ (Human-in-Loop)         │
│  └────────────┘  └──────────────┘                          │
│                                                              │
│  ┌────────────┐                                             │
│  │  Reporting │  (PDF Generation)                           │
│  └────────────┘                                             │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER                              │
│                                                              │
│  ┌──────────────────┐       ┌──────────────────┐           │
│  │   SQLite DB      │       │  Filesystem       │           │
│  │  - Configurations│       │  - Uploads        │           │
│  │  - Audits        │       │  - Sanitized      │           │
│  │  - Findings      │       │  - Reports        │           │
│  │  - Mappings      │       │  - Normalized     │           │
│  └──────────────────┘       └──────────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

### Core Innovation: The Unified Security Model

```
VENDOR LAYER (Parser-specific)
├── Cisco Parser
│   "no ip http server" → http_enabled: false
│
├── Fortinet Parser  
│   "set allowaccess ssh" → ssh_enabled: true
│
└── Unknown Parser (AI)
    "management-access secure-shell" → ssh_enabled: true

                    ↓

NORMALIZATION LAYER (Vendor-agnostic)
{
  "device": {...},
  "remote_access": {
    "ssh_enabled": bool,
    "telnet_enabled": bool
  },
  "management": {
    "http_enabled": bool,
    "https_enabled": bool
  },
  ...
}

                    ↓

COMPLIANCE LAYER (Framework-agnostic)
Rules evaluate against normalized model:
- NET-001: remote_access.telnet_enabled == false
- NET-004: management.http_enabled == false
```

**This separation is the architectural breakthrough and MUST be preserved.**

---

## Decision: Target Production Architecture

### What We Will Add

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (Unchanged)                    │
│                  React + TypeScript + Vite                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                      API GATEWAY (New)                       │
│                  Authentication + RBAC                       │
│                     Keycloak + JWT                           │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND API (Enhanced)                    │
│                    FastAPI + Uvicorn                         │
│                                                              │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Ingestion  │→ │ Job Queue     │→ │   Workers     │       │
│  │ (Upload)   │  │ (Redis+Celery)│  │ (Background)  │       │
│  └────────────┘  └──────────────┘  └──────┬───────┘       │
│                                             ↓                │
│                            ┌────────────────────────┐       │
│                            │ Processing Pipeline    │       │
│                            │ (Same as prototype)    │       │
│                            └────────────────────────┘       │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER (Enhanced)                   │
│                                                              │
│  ┌──────────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   PostgreSQL     │  │    Redis     │  │    MinIO      │ │
│  │ - Metadata       │  │ - Queue      │  │ - Files       │ │
│  │ - Relationships  │  │ - Cache      │  │ - Reports     │ │
│  │ - Audit Logs     │  │ - Sessions   │  │ - Artifacts   │ │
│  └──────────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## Changes and Rationale

### 1. Database: SQLite → PostgreSQL

**Why Change**:
- SQLite is single-writer, blocking
- No connection pooling
- Not suitable for multi-user production
- Limited concurrent access

**Migration Strategy**:
- SQLAlchemy abstracts database
- Keep existing models
- Use Alembic for migrations
- No breaking schema changes

**Risk**: Low (ORM abstraction layer protects us)

**Benefit**: Production-grade concurrency, ACID guarantees, better tooling

---

### 2. Storage: Filesystem → MinIO (S3-compatible)

**Why Change**:
- Configuration files should not be in database
- Filesystem doesn't scale horizontally
- No versioning, replication, or backup built-in
- Need object storage for future cloud deployment

**Migration Strategy**:
- Add MinIO via Docker Compose
- Create storage abstraction layer
- Keep file references in PostgreSQL
- Migrate existing files gradually

**Risk**: Low (new layer, doesn't affect existing logic)

**Benefit**: Scalable storage, versioning, S3-compatible API

---

### 3. Processing: Synchronous → Asynchronous (Celery + Redis)

**Why Change**:
- Bulk uploads block API
- No progress tracking
- Timeouts on large files
- Poor user experience for long operations

**Migration Strategy**:
- Add Redis + Celery via Docker Compose
- Create job model
- Wrap existing processing logic as tasks
- API returns job ID, client polls for results

**Risk**: Medium (architectural change, but existing logic preserved)

**Benefit**: Non-blocking uploads, progress tracking, scalability

---

### 4. Authentication: None → Keycloak + JWT

**Why Change**:
- No user management
- No access control
- No audit trail of who did what
- Not production-ready

**Migration Strategy**:
- Add Keycloak via Docker Compose
- Create user/role models
- Protect API endpoints with JWT middleware
- Add audit logging

**Risk**: Medium (new layer, affects all endpoints)

**Benefit**: Enterprise-grade authentication, RBAC, SSO-ready, MFA-ready

---

### 5. Framework Data: Custom Rules → Structured Framework Integration

**Why Change**:
- 10 custom rules insufficient
- No CIS Benchmark integration
- No NIST mapping
- No STIG references
- Not traceable to authoritative sources

**Migration Strategy**:
- Research authoritative sources (CIS, NIST, DISA)
- Create framework metadata models
- Add framework versioning
- Map existing rules to frameworks
- DO NOT fabricate control mappings

**Risk**: Low (additive, doesn't affect existing rules)

**Benefit**: Credibility, completeness, traceability

---

### 6. Data Provenance: Implicit → Explicit

**Why Change**:
- Unknown source of test configurations
- No hash tracking
- No version history
- Not audit-ready

**Migration Strategy**:
- Add SHA-256 hashing to ingestion
- Create data manifest (CSV/JSON)
- Document source for every file
- Add provenance fields to models

**Risk**: Low (metadata addition)

**Benefit**: Traceability, audit compliance, reproducibility

---

## What We Will NOT Change

### Preserved Architecture

1. **UnifiedSecurityModel** - Core innovation
2. **Parser abstraction** - Clean separation
3. **Evidence tracking** - File/line/text references
4. **API contracts** - Existing endpoints preserved
5. **Frontend structure** - React components unchanged
6. **Compliance evaluation logic** - Rule engine preserved
7. **AI learning workflow** - Human-in-loop preserved
8. **Test configurations** - 23 files preserved

---

## Technology Stack Decision

### Backend

| Technology | Version | Purpose | Decision |
|------------|---------|---------|----------|
| **Python** | 3.11+ | Backend language | KEEP - already works |
| **FastAPI** | 0.104.1+ | Web framework | KEEP - excellent choice |
| **Pydantic** | 2.5.0+ | Validation | KEEP - integral to FastAPI |
| **SQLAlchemy** | 2.0.23+ | ORM | KEEP - abstracts database |
| **Alembic** | Latest | Migrations | ADD - for schema versioning |
| **PostgreSQL** | 15+ | Database | ADD - production-ready RDBMS |
| **Redis** | 7+ | Queue/cache | ADD - for Celery and caching |
| **Celery** | 5+ | Task queue | ADD - async processing |
| **MinIO** | Latest | Object storage | ADD - S3-compatible storage |

### Authentication

| Technology | Version | Purpose | Decision |
|------------|---------|---------|----------|
| **Keycloak** | 23+ | Identity provider | ADD - enterprise auth |
| **python-jose** | Latest | JWT handling | ADD - token validation |
| **cryptography** | Latest | Security primitives | ADD - for key management |

### Frontend

| Technology | Version | Purpose | Decision |
|------------|---------|---------|----------|
| **React** | 18.2+ | UI framework | KEEP - works well |
| **TypeScript** | 5.2+ | Type safety | KEEP - essential |
| **Vite** | 5.0+ | Build tool | KEEP - fast builds |
| **Tailwind CSS** | 3.3+ | Styling | KEEP - consistent design |
| **Axios** | 1.6+ | HTTP client | KEEP - works well |

### Parsing & Analysis

| Technology | Version | Purpose | Decision |
|------------|---------|---------|----------|
| **sentence-transformers** | 2.2.2+ | Embeddings | KEEP - AI learning |
| **PyYAML** | 6.0.1+ | YAML parsing | KEEP - rules/config |
| **ciscoconfparse2** | TBD | Cisco parsing | EVALUATE - may enhance parsers |
| **TextFSM** | TBD | Template-based parsing | EVALUATE - may add later |

### Reporting

| Technology | Version | Purpose | Decision |
|------------|---------|---------|----------|
| **ReportLab** | 4.0.7+ | PDF generation | KEEP - works well |

### Development

| Technology | Version | Purpose | Decision |
|------------|---------|---------|----------|
| **Docker** | Latest | Containerization | ADD - infrastructure |
| **Docker Compose** | Latest | Multi-container | ADD - local development |
| **pytest** | 7.4.3+ | Testing | KEEP - Python standard |

---

## Rejected Alternatives

### Why Not Kubernetes?
- Premature optimization
- Docker Compose sufficient for development
- Add in later phase if needed

### Why Not MongoDB?
- Relational data model fits better
- PostgreSQL has JSON support
- No need for schema-less
- ACID guarantees important

### Why Not GraphQL?
- REST API works fine
- No complex nested queries needed
- Adds complexity without benefit
- Can add later if needed

### Why Not Microservices?
- Monolith appropriate for this scale
- Clear module boundaries sufficient
- Deployment complexity not justified
- Can split later if needed

### Why Not Custom Parser Library?
- Existing regex parsers work
- Adding library must provide clear benefit
- Evaluate ciscoconfparse2 on merit
- Don't add dependencies blindly

---

## Migration Strategy

### Phase 0.5 Incremental Approach

```
WEEK 1: Infrastructure
├── Docker Compose setup
├── PostgreSQL container
├── Redis container
├── MinIO container
├── Keycloak container (optional start)
└── Health checks

WEEK 1-2: Database Migration
├── Alembic setup
├── Migration scripts
├── Schema verification
├── Data migration from SQLite
└── Testing

WEEK 2: Storage Migration
├── MinIO configuration
├── Storage abstraction layer
├── File migration
├── Reference updates
└── Testing

WEEK 2-3: Async Processing
├── Celery worker setup
├── Job model creation
├── Task wrapper for existing logic
├── API update for job handling
└── Testing

WEEK 3: Data Foundation
├── Configuration analysis
├── Provenance documentation
├── Hashing implementation
├── Manifest creation
└── Golden dataset creation

WEEK 3-4: Framework Research
├── CIS Benchmark source identification
├── NIST OSCAL retrieval
├── STIG source identification
├── Framework metadata model
└── Documentation

WEEK 4: Authentication (Foundation)
├── Keycloak setup
├── User model
├── JWT middleware (optional enable)
├── Protected endpoints
└── Testing

WEEK 4: Validation & Documentation
├── End-to-end testing
├── Performance testing
├── Documentation completion
└── Final report
```

---

## Success Criteria

Phase 0.5 is successful when:

### Infrastructure
- [ ] Docker Compose starts all services
- [ ] PostgreSQL accepts connections
- [ ] Redis accessible
- [ ] MinIO S3 API working
- [ ] All health checks passing

### Functionality Preservation
- [ ] All existing features work
- [ ] File upload works
- [ ] Vendor detection works
- [ ] Parsing works (Cisco, Fortinet, Unknown)
- [ ] Compliance evaluation works
- [ ] Findings generation works
- [ ] PDF reports generate
- [ ] AI learning works
- [ ] Dashboard displays correctly

### New Capabilities
- [ ] Files stored in MinIO
- [ ] Metadata in PostgreSQL
- [ ] Async job processing works
- [ ] Job status polling works
- [ ] Configuration hashes generated
- [ ] Data provenance recorded

### Documentation
- [ ] All architecture decisions documented
- [ ] Technology stack justified
- [ ] Framework sources identified
- [ ] Data sources documented
- [ ] Migration strategy clear

### Testing
- [ ] Existing tests pass
- [ ] New integration tests pass
- [ ] Performance acceptable
- [ ] No regressions

---

## Risks and Mitigations

### Risk: Breaking Existing Functionality

**Mitigation**:
- Git checkpoint created
- Incremental migration
- Test after each change
- Rollback procedure documented

### Risk: Complex Docker Setup

**Mitigation**:
- Start simple (PostgreSQL only)
- Add services incrementally
- Document configuration
- Provide troubleshooting guide

### Risk: Database Migration Issues

**Mitigation**:
- SQLAlchemy provides abstraction
- Alembic handles migrations
- Test with sample data first
- Backup before migration

### Risk: Storage Migration Complexity

**Mitigation**:
- New layer, doesn't affect logic
- Reference existing files initially
- Migrate gradually
- Test thoroughly

### Risk: Celery Learning Curve

**Mitigation**:
- Simple task wrapper first
- Existing logic unchanged
- Good documentation
- Start with one task type

---

## Open Questions

1. **Keycloak Timeline**: Should we fully implement auth in Phase 0.5 or just foundation?
   - **Decision**: Foundation only (setup + optional enable)

2. **ciscoconfparse2**: Should we integrate this library?
   - **Decision**: Evaluate on merit, not required for Phase 0.5

3. **Framework Data**: Can we legally use CIS Benchmarks?
   - **Decision**: Research required, document licensing

4. **Test Data**: Should we generate more synthetic configs?
   - **Decision**: Yes, after cataloguing existing 23 files

5. **Configuration Versioning**: Implement in Phase 0.5?
   - **Decision**: Design in Phase 0.5, implement in Phase 0

---

## Approval

**Status**: PROPOSED - Awaiting validation  
**Review Date**: 2026-09-16  
**Next Review**: After infrastructure setup  

---

## References

- Prototype Baseline Documentation (docs/prototype-baseline.md)
- SIH 2026 Problem Statement 26155
- Phase 0.5 Requirements Document
- Existing README.md

---

**Decision Record**: ADR-000  
**Phase**: 0.5 - Foundation  
**Author**: Lead Principal Engineer  
**Date**: 2026-09-16
