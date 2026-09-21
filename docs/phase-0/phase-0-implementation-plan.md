# Phase 0 - Production MVP Implementation Plan

**Vajra Core - SIH 2026 Problem Statement 26155**  
**Date**: September 17, 2026  
**Phase**: 0 - Production MVP  
**Status**: READY TO BEGIN

---

## Executive Summary

This document provides a detailed, task-by-task implementation plan for Phase 0 based on:
1. Repository discovery audit (`phase-0-discovery.md`)
2. Baseline testing results (`baseline-test-results.md`)
3. SIH 2026 PS 26155 requirements

**Foundation Status**: ✅ SOLID - Core pipeline operational, UnifiedSecurityModel working

**Approach**: **INCREMENTAL** - Build on existing prototype, add missing components one at a time

**Timeline**: 5 weeks (assumes full-time development)

**Priority**: Functionality > Features - Complete end-to-end pipeline before polish

---

## Guiding Principles

### DO

✅ **Preserve working functionality** - Never break upload → audit → findings → report  
✅ **Test after each change** - Verify no regressions  
✅ **Incremental commits** - Small, focused changes  
✅ **Use existing patterns** - Follow established architecture  
✅ **Evidence everything** - Maintain file/line/text tracking  

### DO NOT

❌ **Rewrite working code** - If it works, leave it  
❌ **Change UnifiedSecurityModel** - This is the innovation  
❌ **Break existing tests** - Golden dataset must pass  
❌ **Add features beyond requirements** - MVP focus  
❌ **Skip testing** - Every component needs validation  

---

## Week 1: Core Pipeline Completion

**Goal**: Complete the fundamental data flow with missing components

### Task 1.1: Install AI Dependencies

**Priority**: HIGH  
**Estimated Time**: 30 minutes  
**Dependencies**: None

**Actions**:
1. Add `sentence-transformers==2.2.2` to `backend/requirements.txt`
2. Run `pip install sentence-transformers`
3. Verify import: `from sentence_transformers import SentenceTransformer`
4. Update health check to confirm model loading
5. Test UnknownParser with AI model active

**Success Criteria**:
- `GET /health/detailed` shows ai_model: "healthy"
- UnknownParser can load embedding model
- No import errors

**Files Modified**:
- `backend/requirements.txt`

---

### Task 1.2: Configuration Hashing Integration

**Priority**: HIGH  
**Estimated Time**: 2 hours  
**Dependencies**: None

**Current State**: SHA-256 hashing function exists in `storage_backend.py` but not called during upload

**Actions**:
1. Update `backend/app/api/upload.py`:
   - Import `compute_file_hash` from storage
   - Compute SHA-256 hash on upload
   - Store in `Configuration.file_hash` field (add to model if missing)
2. Add `file_hash` to Configuration model (if not present)
3. Create Alembic migration for new field
4. Update upload response to include hash
5. Add hash to configuration list/detail endpoints

**Success Criteria**:
- Every uploaded config has SHA-256 hash
- Hash stored in database
- Hash returned in API responses
- Duplicate detection possible via hash comparison

**Files Modified**:
- `backend/app/database/models.py` (if needed)
- `backend/app/api/upload.py`
- `backend/alembic/versions/[new]_add_config_hash.py`

**Testing**:
- Upload same file twice, verify same hash
- Upload different file, verify different hash

---

### Task 1.3: Parser Registry Refactor

**Priority**: MEDIUM  
**Estimated Time**: 3 hours  
**Dependencies**: None

**Current State**: Parsers exist but no formal registry

**Actions**:
1. Create `backend/app/parsers/registry.py`:
   ```python
   class ParserRegistry:
       def __init__(self):
           self._parsers = []
       
       def register(self, parser_class):
           self._parsers.append(parser_class())
       
       def get_parser(self, content: str):
           for parser in self._parsers:
               if parser.can_parse(content):
                   return parser
           return UnknownParser()  # fallback
   
   # Global registry
   registry = ParserRegistry()
   registry.register(CiscoParser)
   registry.register(FortinetParser)
   ```

2. Update vendor detection to use registry
3. Add registration decorators (optional enhancement)
4. Document parser registration process

**Success Criteria**:
- All existing parsers registered
- Parser selection automated via `can_parse()`
- UnknownParser used as fallback
- Easy to add new parsers

**Files Modified**:
- `backend/app/parsers/registry.py` (new)
- `backend/app/parsers/__init__.py`
- `backend/app/detection/vendor_detector.py`

**Testing**:
- Upload Cisco config → CiscoParser selected
- Upload Fortinet config → FortinetParser selected
- Upload unknown config → UnknownParser selected

---

### Task 1.4: Secret Sanitization Enhancement

**Priority**: HIGH  
**Estimated Time**: 4 hours  
**Dependencies**: None

**Current State**: Basic sanitization exists, needs enhancement

**Actions**:
1. Create comprehensive secret patterns:
   ```python
   SECRET_PATTERNS = {
       'cisco_enable_secret': r'enable secret \d+ \S+',
       'cisco_password': r'password \d+ \S+',
       'cisco_key': r'key \d+ \S+',
       'cisco_community': r'snmp-server community \S+',
       'fortinet_password': r'set password \S+',
       'generic_api_key': r'(?i)(api[_-]?key|apikey)\s*[:=]\s*[\'\"]?(\S+)[\'\"]?',
       'generic_token': r'(?i)(token|auth[_-]?token)\s*[:=]\s*[\'\"]?(\S+)[\'\"]?',
   }
   ```

2. Enhance `backend/app/security/masking.py`:
   - Add pattern matching for common secret types
   - Preserve enough context for parsing (e.g., "enable secret 5 [REDACTED]")
   - Track number and types of secrets masked
   - Add sanitization report

3. Update Configuration model:
   - Add `sanitization_report` JSON field
   - Store secret types found

4. Create sanitization test cases

**Success Criteria**:
- All Cisco secret types masked
- All Fortinet secret types masked
- Generic secrets (API keys, tokens) masked
- Sanitized config parseable by parser
- Report shows secret types found

**Files Modified**:
- `backend/app/security/masking.py`
- `backend/app/database/models.py`
- `backend/app/ingestion/file_handler.py`

**Testing**:
- Create test configs with various secret types
- Verify each masked correctly
- Verify parser still works after masking

---

### Task 1.5: Framework Data Loading - Foundation

**Priority**: HIGH  
**Estimated Time**: 6 hours  
**Dependencies**: None

**Current State**: Rules reference CIS/NIST but no actual data loaded

**Actions**:
1. Create framework data directory:
   ```
   backend/data/frameworks/
   ├── cis/
   │   ├── cisco-ios-benchmark.yaml
   │   └── fortinet-fortigate-benchmark.yaml
   ├── nist/
   │   └── oscal-catalog.json
   └── disa/
       └── stig-mappings.yaml
   ```

2. Define framework data schema:
   ```yaml
   # Example: cisco-ios-benchmark.yaml
   framework: CIS
   vendor: Cisco
   product: IOS
   version: 1.0
   controls:
     - id: CIS-2.1.1
       title: Ensure Telnet is Disabled
       description: ...
       mapped_rules:
         - NET-001
       severity: HIGH
   ```

3. Create framework loader:
   ```python
   class FrameworkLoader:
       def load_framework(self, framework_type, vendor):
           # Load YAML/JSON
           # Parse controls
           # Map to existing rules
           # Store in database or cache
   ```

4. Add framework metadata to ComplianceRule model:
   ```python
   class ComplianceRule:
       ...
       framework_mappings = Column(JSON)  # {"CIS": "2.1.1", "NIST": "SC-8"}
   ```

5. Update rules.yaml to include framework mappings

**Phase 1 Goal**: Foundation only - load 5 sample controls for Cisco

**Success Criteria**:
- Framework data structure defined
- Loader can parse YAML/JSON
- Sample CIS controls loaded for Cisco
- Rules show framework mappings

**Files Modified**:
- `backend/data/frameworks/` (new directory)
- `backend/app/compliance/framework_loader.py` (new)
- `backend/app/database/models.py`
- `backend/app/compliance/rules.yaml`

**Testing**:
- Load sample framework data
- Verify mappings in database
- Verify rule references correct controls

**Note**: Full framework integration (50+ controls) deferred to Week 3

---

### Week 1 Deliverables

✅ AI dependencies installed and working  
✅ SHA-256 hashing integrated in upload pipeline  
✅ Parser registry implemented and tested  
✅ Secret sanitization enhanced with comprehensive patterns  
✅ Framework data foundation established (5 sample controls)  

**Testing**: All baseline tests still passing + new functionality verified

---

## Week 2: Deviation & Remediation Engines

**Goal**: Implement configuration comparison and automated fix generation

### Task 2.1: Deviation Engine - Data Model

**Priority**: HIGH  
**Estimated Time**: 2 hours  
**Dependencies**: None

**Actions**:
1. Create `ConfigurationComparison` model:
   ```python
   class ConfigurationComparison(Base):
       __tablename__ = "configuration_comparisons"
       
       id = Column(Integer, primary_key=True)
       comparison_id = Column(String(50), unique=True)  # CMP-000001
       baseline_config_id = Column(Integer, ForeignKey("configurations.id"))
       current_config_id = Column(Integer, ForeignKey("configurations.id"))
       baseline_audit_id = Column(Integer, ForeignKey("audits.id"))
       current_audit_id = Column(Integer, ForeignKey("audits.id"))
       
       # Deviation metrics
       compliance_drift = Column(Float)  # % change in compliance
       new_violations = Column(Integer)
       resolved_violations = Column(Integer)
       risk_drift = Column(Float)  # Change in risk score
       
       # Detailed deviations
       deviations = Column(JSON)  # Field-by-field comparison
       created_at = Column(DateTime, default=datetime.utcnow)
   ```

2. Create Alembic migration

**Success Criteria**:
- ConfigurationComparison table created
- Schema supports before/after comparison
- Supports deviation metrics storage

**Files Modified**:
- `backend/app/database/models.py`
- `backend/alembic/versions/[new]_add_comparison_model.py`

---

### Task 2.2: Deviation Engine - Comparison Logic

**Priority**: HIGH  
**Estimated Time**: 6 hours  
**Dependencies**: Task 2.1

**Actions**:
1. Create `backend/app/deviation/engine.py`:
   ```python
   class DeviationEngine:
       def compare_audits(self, baseline_audit_id, current_audit_id):
           # Load both audits
           # Load both normalized models (JSON from audit.normalized_data)
           # Compare field by field
           # Calculate drift metrics
           # Identify new/resolved violations
           # Generate deviation report
           
       def compare_findings(self, baseline_findings, current_findings):
           # Group by rule_id
           # Detect status changes (PASS→FAIL, FAIL→PASS)
           # Track new failures
           # Track resolved failures
           
       def calculate_compliance_drift(self, baseline_score, current_score):
           return current_score - baseline_score
   ```

2. Implement field-level comparison:
   ```python
   def compare_fields(self, baseline_model, current_model):
       deviations = []
       baseline_dict = baseline_model.to_flat_dict()
       current_dict = current_model.to_flat_dict()
       
       all_keys = set(baseline_dict.keys()) | set(current_dict.keys())
       for key in all_keys:
           baseline_val = baseline_dict.get(key)
           current_val = current_dict.get(key)
           if baseline_val != current_val:
               deviations.append({
                   "field": key,
                   "baseline": baseline_val,
                   "current": current_val,
                   "severity": self._assess_deviation_severity(key, baseline_val, current_val)
               })
       return deviations
   ```

3. Create deviation API endpoint:
   ```python
   @router.post("/api/comparisons/create")
   async def create_comparison(
       baseline_audit_id: str,
       current_audit_id: str
   ):
       # Run comparison
       # Store results
       # Return comparison_id
   ```

**Success Criteria**:
- Can compare two audits
- Detects field-level changes
- Calculates drift metrics
- Identifies new/resolved violations
- Stores comparison results

**Files Modified**:
- `backend/app/deviation/` (new directory)
- `backend/app/deviation/engine.py` (new)
- `backend/app/deviation/__init__.py` (new)
- `backend/app/api/comparisons.py` (new)
- `backend/app/main.py` (register router)

**Testing**:
- Upload baseline config (compliant)
- Run audit A
- Upload modified config (add violation)
- Run audit B
- Compare A vs B
- Verify deviation detected
- Verify drift metrics correct

---

### Task 2.3: Remediation Engine - Integration

**Priority**: HIGH  
**Estimated Time**: 4 hours  
**Dependencies**: None

**Current State**: Templates exist in `backend/app/remediation/templates.yaml` but not integrated

**Actions**:
1. Review existing remediation templates
2. Enhance templates with vendor-specific syntax:
   ```yaml
   remediations:
     - rule_id: NET-001
       title: Disable Telnet
       cisco:
         commands:
           - "line vty 0 4"
           - "transport input ssh"
           - "no transport input telnet"
       fortinet:
         commands:
           - "config system global"
           - "set admin-telnet disable"
           - "end"
   ```

3. Create `backend/app/remediation/engine.py`:
   ```python
   class RemediationEngine:
       def __init__(self):
           self.templates = self._load_templates()
       
       def generate_remediation(self, finding: Finding, vendor: str):
           template = self.templates.get(finding.rule_id)
           if not template:
               return None
           
           vendor_commands = template.get(vendor.lower(), {}).get('commands', [])
           return {
               "rule_id": finding.rule_id,
               "vendor": vendor,
               "commands": vendor_commands,
               "explanation": template.get('explanation'),
               "risk": template.get('risk')  # Risk of applying fix
           }
   ```

4. Integrate into audit flow:
   - Generate remediation for each FAIL finding
   - Store in Finding.remediation field (already exists)
   - Include in PDF report

**Success Criteria**:
- Remediation generated for each failed finding
- Commands are vendor-specific
- Remediation stored in database
- Remediation included in PDF report

**Files Modified**:
- `backend/app/remediation/templates.yaml`
- `backend/app/remediation/engine.py` (new)
- `backend/app/remediation/__init__.py`
- `backend/app/findings/engine.py` (integrate remediation)

**Testing**:
- Run audit with failures
- Verify remediation commands generated
- Verify vendor-specific syntax
- Check PDF includes remediation

---

### Task 2.4: Corrected Configuration Generation

**Priority**: HIGH  
**Estimated Time**: 8 hours  
**Dependencies**: Task 2.3

**Actions**:
1. Create `backend/app/remediation/config_generator.py`:
   ```python
   class CorrectedConfigGenerator:
       def generate(self, original_config: str, audit: Audit, vendor: str):
           # Parse original config
           # Get all failed findings
           # For each finding, get remediation commands
           # Apply commands to config
           # Validate new config parseable
           # Return corrected config
           
       def apply_remediation_cisco(self, config_lines, commands):
           # Cisco-specific logic
           # Find relevant section
           # Apply commands
           # Preserve structure
           
       def apply_remediation_fortinet(self, config_lines, commands):
           # Fortinet-specific logic
   ```

2. Add config generation endpoint:
   ```python
   @router.post("/api/audits/{audit_id}/generate-corrected-config")
   async def generate_corrected_config(audit_id: str):
       # Load audit, findings, original config
       # Generate corrected config
       # Store corrected config
       # Return config_id for corrected version
   ```

3. Store corrected configs:
   - Save to `backend/data/corrected/`
   - Link to original audit in database
   - Add `corrected_config_id` field to Audit model

**Success Criteria**:
- Corrected config generated from failed findings
- Vendor syntax correct
- Original structure preserved where possible
- Corrected config parseable
- Corrected config stored and linked to audit

**Files Modified**:
- `backend/app/remediation/config_generator.py` (new)
- `backend/app/api/audit.py`
- `backend/app/database/models.py`
- `backend/alembic/versions/[new]_add_corrected_config.py`

**Testing**:
- Audit insecure config (telnet enabled)
- Generate corrected config
- Verify telnet disabled in corrected config
- Parse corrected config
- Verify syntax valid

---

### Week 2 Deliverables

✅ Deviation engine implemented and tested  
✅ Configuration comparison functional  
✅ Remediation engine integrated into audit flow  
✅ Corrected configuration generation working  
✅ Vendor-specific command generation validated  

**Testing**: Can compare before/after configs, generate fixes, produce corrected configs

---

## Week 3: Re-assessment & Bulk Upload

**Goal**: Complete the feedback loop and enable batch processing

### Task 3.1: Re-assessment Workflow

**Priority**: HIGH  
**Estimated Time**: 4 hours  
**Dependencies**: Task 2.4

**Actions**:
1. Create re-assessment endpoint:
   ```python
   @router.post("/api/audits/{original_audit_id}/reassess")
   async def reassess_after_remediation(
       original_audit_id: str,
       corrected_config_file: UploadFile
   ):
       # Upload corrected config
       # Run new audit
       # Compare with original audit
       # Generate before/after report
       # Return reassessment_id
   ```

2. Create `Reassessment` model:
   ```python
   class Reassessment(Base):
       __tablename__ = "reassessments"
       
       id = Column(Integer, primary_key=True)
       reassessment_id = Column(String(50), unique=True)  # RAS-000001
       original_audit_id = Column(Integer, ForeignKey("audits.id"))
       corrected_audit_id = Column(Integer, ForeignKey("audits.id"))
       comparison_id = Column(Integer, ForeignKey("configuration_comparisons.id"))
       
       # Improvement metrics
       compliance_improvement = Column(Float)  # % improvement
       violations_fixed = Column(Integer)
       violations_remaining = Column(Integer)
       risk_reduction = Column(Float)
       
       status = Column(String(50))  # IMPROVED, DEGRADED, NO_CHANGE
       created_at = Column(DateTime, default=datetime.utcnow)
   ```

3. Implement automatic comparison on reassessment
4. Generate before/after PDF report

**Success Criteria**:
- Can upload corrected config
- Runs new audit automatically
- Compares with original audit
- Shows improvement metrics
- Generates before/after report

**Files Modified**:
- `backend/app/database/models.py`
- `backend/app/api/audit.py`
- `backend/app/reports/pdf_generator.py` (add before/after template)

**Testing**:
- Audit insecure config (33% compliance)
- Generate corrected config
- Re-assess corrected config
- Verify compliance improved (should be ~100%)
- Verify improvement metrics correct
- Check before/after report

---

### Task 3.2: Bulk Upload API - Data Model

**Priority**: HIGH  
**Estimated Time**: 2 hours  
**Dependencies**: None

**Actions**:
1. Create `BulkUploadJob` model:
   ```python
   class BulkUploadJob(Base):
       __tablename__ = "bulk_upload_jobs"
       
       id = Column(Integer, primary_key=True)
       job_id = Column(String(50), unique=True)  # BULK-000001
       status = Column(String(50))  # PROCESSING, COMPLETED, PARTIAL_FAILURE, FAILED
       total_files = Column(Integer)
       processed_files = Column(Integer, default=0)
       successful_uploads = Column(Integer, default=0)
       failed_uploads = Column(Integer, default=0)
       started_at = Column(DateTime, default=datetime.utcnow)
       completed_at = Column(DateTime)
       error_summary = Column(JSON)  # List of failures with reasons
   ```

2. Create Alembic migration

**Success Criteria**:
- BulkUploadJob table created
- Schema supports job tracking
- Supports partial failure tracking

**Files Modified**:
- `backend/app/database/models.py`
- `backend/alembic/versions/[new]_add_bulk_upload.py`

---

### Task 3.3: Bulk Upload API - Implementation

**Priority**: HIGH  
**Estimated Time**: 6 hours  
**Dependencies**: Task 3.2

**Actions**:
1. Create bulk upload endpoint:
   ```python
   @router.post("/api/configurations/bulk-upload")
   async def bulk_upload_configurations(
       files: List[UploadFile] = File(...),
       auto_audit: bool = False,  # Auto-run audit on each
       db: Session = Depends(get_db)
   ):
       # Create BulkUploadJob
       # Process each file
       # Track success/failure
       # Optionally run audit on each
       # Update job status
       # Return job_id
   ```

2. Implement file processing:
   ```python
   async def process_bulk_upload(job_id: str, files: List[UploadFile]):
       job = get_job(job_id)
       results = []
       
       for file in files:
           try:
               # Upload using existing single upload logic
               config = upload_single_file(file)
               job.successful_uploads += 1
               results.append({"file": file.filename, "status": "success", "config_id": config.config_id})
           except Exception as e:
               job.failed_uploads += 1
               results.append({"file": file.filename, "status": "failed", "error": str(e)})
           finally:
               job.processed_files += 1
               db.commit()
       
       job.status = "COMPLETED" if job.failed_uploads == 0 else "PARTIAL_FAILURE"
       job.error_summary = [r for r in results if r["status"] == "failed"]
       job.completed_at = datetime.utcnow()
       db.commit()
   ```

3. Create job status endpoint:
   ```python
   @router.get("/api/bulk-uploads/{job_id}")
   async def get_bulk_upload_status(job_id: str):
       # Return job status and progress
       # Return list of successful/failed uploads
   ```

4. Add progress tracking (optional - use Redis if available)

**Success Criteria**:
- Can upload multiple files in one request
- Each file processed individually
- Partial failures handled gracefully
- Job status trackable
- Optionally runs audit on each upload

**Files Modified**:
- `backend/app/api/upload.py`
- `backend/app/ingestion/bulk_handler.py` (new)

**Testing**:
- Upload 5 valid configs → all succeed
- Upload 3 valid + 2 invalid → partial failure handled
- Verify job status shows progress
- With auto_audit=true, verify audits run

---

### Task 3.4: Framework Data - Full Integration

**Priority**: MEDIUM  
**Estimated Time**: 8 hours  
**Dependencies**: Task 1.5

**Actions**:
1. Expand framework data:
   - CIS Cisco IOS Benchmark: 20+ controls
   - CIS Fortinet FortiGate Benchmark: 15+ controls
   - NIST 800-53 mappings: Core security controls
   - DISA STIG mappings (if available)

2. Load framework data on startup:
   ```python
   @app.on_event("startup")
   async def load_frameworks():
       loader = FrameworkLoader()
       loader.load_all_frameworks()
       logger.info("✓ Framework data loaded")
   ```

3. Add framework filter to findings:
   ```python
   @router.get("/api/audits/{audit_id}/findings")
   async def get_findings(
       audit_id: str,
       framework: Optional[str] = None  # Filter by CIS, NIST, STIG
   ):
       # Get findings
       # If framework specified, filter to rules mapped to that framework
   ```

4. Add framework compliance view:
   ```python
   @router.get("/api/audits/{audit_id}/frameworks/{framework}")
   async def get_framework_compliance(audit_id: str, framework: str):
       # Get all findings
       # Group by framework controls
       # Calculate framework-specific compliance score
       # Return framework view
   ```

**Success Criteria**:
- 50+ framework controls loaded
- Rules mapped to CIS/NIST controls
- Framework filtering works
- Framework-specific compliance scores calculated

**Files Modified**:
- `backend/data/frameworks/` (expand data)
- `backend/app/compliance/framework_loader.py`
- `backend/app/api/findings.py`
- `backend/app/main.py`

**Testing**:
- Run audit
- Get findings filtered by CIS
- Get findings filtered by NIST
- Verify framework compliance scores

---

### Week 3 Deliverables

✅ Re-assessment workflow functional  
✅ Before/after comparison automated  
✅ Bulk upload API operational  
✅ Partial failure handling working  
✅ Framework data fully integrated (50+ controls)  
✅ Framework filtering and reporting working  

**Testing**: Can bulk upload configs, reassess after remediation, filter by framework

---

## Week 4: Authentication & Testing

**Goal**: Secure the application and expand test coverage

### Task 4.1: Keycloak Integration - Basic Setup

**Priority**: HIGH  
**Estimated Time**: 4 hours  
**Dependencies**: Docker services running

**Actions**:
1. Start Keycloak container:
   ```bash
   docker-compose up -d keycloak
   ```

2. Configure Keycloak realm:
   - Create `vajra-core` realm
   - Create clients: `vajra-backend`, `vajra-frontend`
   - Create roles: `admin`, `auditor`, `viewer`, `vendor`

3. Install FastAPI OAuth dependencies:
   ```bash
   pip install python-jose[cryptography] python-multipart
   ```

4. Create authentication module:
   ```python
   # backend/app/auth/keycloak.py
   from fastapi import Depends, HTTPException, status
   from fastapi.security import OAuth2AuthorizationCodeBearer
   from jose import JWTError, jwt
   
   oauth2_scheme = OAuth2AuthorizationCodeBearer(
       authorizationUrl=f"{KEYCLOAK_URL}/auth",
       tokenUrl=f"{KEYCLOAK_URL}/token"
   )
   
   async def get_current_user(token: str = Depends(oauth2_scheme)):
       # Verify JWT token
       # Extract user info
       # Return user object
   ```

5. Add authentication to sensitive endpoints:
   ```python
   @router.post("/api/config/upload")
   async def upload_configuration(
       file: UploadFile,
       current_user: User = Depends(get_current_user)  # Added
   ):
       ...
   ```

**Success Criteria**:
- Keycloak running and configured
- JWT token verification working
- Protected endpoints require authentication
- User information extracted from token

**Files Modified**:
- `backend/app/auth/` (new directory)
- `backend/app/auth/keycloak.py` (new)
- `backend/app/auth/models.py` (new - User model)
- `backend/app/api/upload.py` (add auth)
- `backend/app/api/audit.py` (add auth)
- `backend/requirements.txt`

**Testing**:
- Access protected endpoint without token → 401
- Get valid token from Keycloak
- Access endpoint with token → success
- Invalid token → 401

**Note**: Frontend integration deferred to separate task

---

### Task 4.2: Role-Based Access Control (RBAC)

**Priority**: MEDIUM  
**Estimated Time**: 3 hours  
**Dependencies**: Task 4.1

**Actions**:
1. Define permission model:
   ```python
   PERMISSIONS = {
       "admin": ["*"],  # All permissions
       "auditor": ["upload", "audit", "view", "generate_report"],
       "viewer": ["view"],
       "vendor": ["view_own_configs", "reassess"]  # Limited scope
   }
   ```

2. Create permission checker:
   ```python
   def require_permission(permission: str):
       def permission_checker(user: User = Depends(get_current_user)):
           if not user.has_permission(permission):
               raise HTTPException(status_code=403, detail="Insufficient permissions")
           return user
       return permission_checker
   ```

3. Apply to endpoints:
   ```python
   @router.post("/api/config/upload")
   async def upload_configuration(
       file: UploadFile,
       user: User = Depends(require_permission("upload"))
   ):
       ...
   ```

4. Add data isolation for vendors:
   - Vendors can only see their own configurations
   - Filter queries by user organization

**Success Criteria**:
- Admins can access everything
- Auditors can upload and audit
- Viewers can only view
- Vendors see only their data

**Files Modified**:
- `backend/app/auth/permissions.py` (new)
- All API endpoints (add permission checks)

**Testing**:
- Login as admin → access all endpoints
- Login as viewer → upload fails (403)
- Login as vendor → see only own configs

---

### Task 4.3: Expand Golden Test Dataset

**Priority**: MEDIUM  
**Estimated Time**: 4 hours  
**Dependencies**: None

**Current State**: 2 golden test cases (GOLD-001, GOLD-002)

**Actions**:
1. Create 20+ golden test cases:
   - **Cisco**: 8 test cases
     - Fully compliant
     - Telnet enabled (NET-001 fail)
     - HTTP enabled (NET-004 fail)
     - SSHv1 (NET-003 fail)
     - No logging (NET-009 fail)
     - Multiple violations
     - Edge cases (partial config, unusual syntax)
     - Complex enterprise config
   
   - **Fortinet**: 6 test cases
     - Fully compliant
     - Insecure protocols
     - Weak authentication
     - Multiple violations
     - Edge cases
     - Complex firewall rules
   
   - **Unknown/Synthetic**: 6 test cases
     - Generic router config (test AI learning)
     - Juniper-like syntax
     - HPE/Aruba-like syntax
     - Palo Alto-like syntax
     - Malformed config (error handling test)
     - Empty config (error handling test)

2. Document expected results:
   ```yaml
   # backend/data/golden/test-cases.yaml
   test_cases:
     - id: GOLD-003
       file: cisco_http_insecure.cfg
       vendor: Cisco
       expected:
         compliance_score: 88.89
         risk_level: MEDIUM
         failed_rules:
           - NET-004
   ```

3. Create automated test runner:
   ```python
   # backend/tests/test_golden_dataset.py
   @pytest.mark.parametrize("test_case", load_golden_test_cases())
   def test_golden_case(test_case):
       # Upload config
       # Run audit
       # Verify compliance score matches expected
       # Verify failed rules match expected
       # Verify risk level matches expected
   ```

**Success Criteria**:
- 20+ golden test cases created
- All expected results documented
- Automated test suite runs all cases
- All tests pass

**Files Modified**:
- `backend/data/golden/positive/` (new configs)
- `backend/data/golden/negative/` (new configs)
- `backend/data/golden/unknown/` (new directory + configs)
- `backend/data/golden/test-cases.yaml` (new)
- `backend/tests/test_golden_dataset.py` (new)

**Testing**:
- Run: `pytest backend/tests/test_golden_dataset.py`
- Verify all 20+ tests pass

---

### Task 4.4: Unit Tests for Core Components

**Priority**: MEDIUM  
**Estimated Time**: 6 hours  
**Dependencies**: None

**Actions**:
1. Create parser unit tests:
   ```python
   # backend/tests/test_parsers.py
   def test_cisco_parser_telnet_detection():
       config = "line vty 0 4\n transport input telnet"
       parser = CiscoParser()
       model = parser.parse(config, "test.cfg")
       assert model.remote_access.telnet_enabled == True
   
   def test_cisco_parser_ssh_version():
       config = "ip ssh version 2"
       parser = CiscoParser()
       model = parser.parse(config, "test.cfg")
       assert model.remote_access.ssh_version == 2
   ```

2. Create compliance engine tests:
   ```python
   # backend/tests/test_compliance.py
   def test_telnet_rule_fail():
       model = UnifiedSecurityModel(...)
       model.remote_access.telnet_enabled = True
       evaluator = ComplianceEvaluator()
       results = evaluator.evaluate(model)
       telnet_result = [r for r in results if r.rule_id == "NET-001"][0]
       assert telnet_result.status == ComplianceStatus.FAIL
   ```

3. Create deviation engine tests:
   ```python
   # backend/tests/test_deviation.py
   def test_compliance_drift_calculation():
       engine = DeviationEngine()
       drift = engine.calculate_compliance_drift(80.0, 60.0)
       assert drift == -20.0
   ```

4. Create remediation engine tests:
   ```python
   # backend/tests/test_remediation.py
   def test_cisco_telnet_remediation():
       finding = Finding(rule_id="NET-001", ...)
       engine = RemediationEngine()
       remediation = engine.generate_remediation(finding, "Cisco")
       assert "transport input ssh" in remediation["commands"]
   ```

**Success Criteria**:
- 50+ unit tests created
- All parsers tested
- Compliance engine tested
- Deviation engine tested
- Remediation engine tested
- All tests pass
- Code coverage > 70%

**Files Modified**:
- `backend/tests/test_parsers.py` (new)
- `backend/tests/test_compliance.py` (new)
- `backend/tests/test_deviation.py` (new)
- `backend/tests/test_remediation.py` (new)

**Testing**:
- Run: `pytest backend/tests/ --cov=app --cov-report=html`
- Review coverage report

---

### Week 4 Deliverables

✅ Keycloak authentication integrated  
✅ JWT token verification working  
✅ RBAC implemented with 4 roles  
✅ Golden dataset expanded to 20+ test cases  
✅ Automated golden test suite created  
✅ 50+ unit tests implemented  
✅ Code coverage > 70%  

**Testing**: Authentication enforced, RBAC working, comprehensive test suite passing

---

## Week 5: Polish, Documentation & Production Readiness

**Goal**: Final touches, documentation, and production validation

### Task 5.1: Structured Logging

**Priority**: MEDIUM  
**Estimated Time**: 3 hours  
**Dependencies**: None

**Actions**:
1. Install structured logging:
   ```bash
   pip install structlog
   ```

2. Configure logging:
   ```python
   # backend/app/core/logging.py
   import structlog
   
   def configure_logging():
       structlog.configure(
           processors=[
               structlog.stdlib.filter_by_level,
               structlog.stdlib.add_logger_name,
               structlog.stdlib.add_log_level,
               structlog.stdlib.PositionalArgumentsFormatter(),
               structlog.processors.TimeStamper(fmt="iso"),
               structlog.processors.StackInfoRenderer(),
               structlog.processors.format_exc_info,
               structlog.processors.UnicodeDecoder(),
               structlog.processors.JSONRenderer()
           ],
           ...
       )
   ```

3. Add request logging middleware:
   ```python
   @app.middleware("http")
   async def log_requests(request: Request, call_next):
       logger.info("request_started",
           method=request.method,
           path=request.url.path,
           client=request.client.host
       )
       
       start_time = time.time()
       response = await call_next(request)
       duration = time.time() - start_time
       
       logger.info("request_completed",
           method=request.method,
           path=request.url.path,
           status_code=response.status_code,
           duration_ms=int(duration * 1000)
       )
       
       return response
   ```

4. Add component logging:
   - Parser selection: `logger.info("parser_selected", vendor=vendor, confidence=confidence)`
   - Audit execution: `logger.info("audit_started", config_id=config_id)`
   - Finding generation: `logger.info("finding_created", rule_id=rule_id, status=status)`

**Success Criteria**:
- All requests logged with timing
- Key operations logged
- JSON structured format
- Logs include context (config_id, audit_id, user_id)

**Files Modified**:
- `backend/app/core/logging.py` (new)
- `backend/app/main.py` (add middleware)
- All major components (add logging)
- `backend/requirements.txt`

---

### Task 5.2: Error Handling Enhancement

**Priority**: MEDIUM  
**Estimated Time**: 2 hours  
**Dependencies**: None

**Actions**:
1. Create structured error model:
   ```python
   # backend/app/core/errors.py
   class APIError(Exception):
       def __init__(self, code: str, message: str, details: dict = None):
           self.code = code
           self.message = message
           self.details = details or {}
   
   class ValidationError(APIError):
       pass
   
   class NotFoundError(APIError):
       pass
   ```

2. Add global exception handler:
   ```python
   @app.exception_handler(APIError)
   async def api_error_handler(request: Request, exc: APIError):
       logger.error("api_error",
           code=exc.code,
           message=exc.message,
           details=exc.details,
           path=request.url.path
       )
       
       return JSONResponse(
           status_code=400,
           content={
               "success": False,
               "error": {
                   "code": exc.code,
                   "message": exc.message,
                   "details": exc.details
               }
           }
       )
   ```

3. Replace generic exceptions with structured errors

**Success Criteria**:
- All errors have error codes
- User-friendly error messages
- Consistent error format across all endpoints
- Errors logged with context

**Files Modified**:
- `backend/app/core/errors.py` (new)
- `backend/app/main.py` (add handlers)
- All API endpoints (use structured errors)

---

### Task 5.3: API Documentation

**Priority**: MEDIUM  
**Estimated Time**: 3 hours  
**Dependencies**: None

**Actions**:
1. Add comprehensive OpenAPI documentation:
   ```python
   @router.post("/api/config/upload",
       summary="Upload Network Configuration",
       description="""
       Upload a network device configuration file for security auditing.
       
       Supported vendors: Cisco, Fortinet, Unknown (AI-assisted)
       Supported formats: .cfg, .conf, .txt, .json
       Max file size: 10MB
       
       The upload process includes:
       1. File validation
       2. Vendor detection (AI-powered)
       3. Secret sanitization
       4. Storage
       5. SHA-256 hashing
       
       Returns configuration metadata including vendor confidence score.
       """,
       responses={
           200: {"description": "Configuration uploaded successfully"},
           400: {"description": "Invalid file or format"},
           413: {"description": "File too large"},
           500: {"description": "Server error during processing"}
       },
       tags=["Configuration Management"]
   )
   async def upload_configuration(...):
       ...
   ```

2. Add request/response examples:
   ```python
   class ConfigUploadResponse(BaseModel):
       success: bool
       data: dict
       
       class Config:
           schema_extra = {
               "example": {
                   "success": True,
                   "data": {
                       "config_id": "CFG-813169",
                       "filename": "router-01.cfg",
                       "vendor": "Cisco",
                       "vendor_confidence": 1.0,
                       "masked_secrets": 4
                   }
               }
           }
   ```

3. Document all endpoints with:
   - Summary
   - Description
   - Parameters
   - Request body schema
   - Response schemas
   - Example requests/responses
   - Error codes

4. Create API documentation page:
   - Access at `/docs` (Swagger UI)
   - Access at `/redoc` (ReDoc)

**Success Criteria**:
- All endpoints documented
- Examples provided
- Error codes documented
- Swagger UI functional
- ReDoc functional

**Files Modified**:
- All API endpoint files (add OpenAPI docs)

---

### Task 5.4: PostgreSQL Production Testing

**Priority**: HIGH  
**Estimated Time**: 4 hours  
**Dependencies**: Docker Compose

**Actions**:
1. Update `.env`:
   ```
   USE_POSTGRES=true
   DATABASE_URL=postgresql://vajra:vajra_dev_password@localhost:5432/vajra_core
   ```

2. Start PostgreSQL:
   ```bash
   docker-compose up -d postgres
   ```

3. Run Alembic migrations:
   ```bash
   cd backend
   alembic upgrade head
   ```

4. Test full pipeline with PostgreSQL:
   - Upload configuration
   - Run audit
   - Generate PDF
   - Bulk upload
   - Re-assessment
   - Deviation comparison

5. Performance testing:
   - Measure audit time with PostgreSQL
   - Compare to SQLite baseline
   - Test concurrent requests

6. Backup/restore testing:
   ```bash
   # Backup
   docker exec vajra-postgres pg_dump -U vajra vajra_core > backup.sql
   
   # Restore
   docker exec -i vajra-postgres psql -U vajra vajra_core < backup.sql
   ```

**Success Criteria**:
- All migrations apply successfully
- All baseline tests pass with PostgreSQL
- Performance acceptable (< 50ms audit time)
- Backup/restore works
- No data loss

**Files Modified**:
- `.env` (switch to PostgreSQL)

**Testing**:
- Run full baseline test suite
- Verify all tests pass
- Check performance metrics

---

### Task 5.5: MinIO Storage Testing

**Priority**: MEDIUM  
**Estimated Time**: 2 hours  
**Dependencies**: Docker Compose

**Actions**:
1. Update `.env`:
   ```
   USE_MINIO=true
   MINIO_ENDPOINT=localhost:9000
   MINIO_ACCESS_KEY=minioadmin
   MINIO_SECRET_KEY=minioadmin
   MINIO_BUCKET=vajra-core-configs
   ```

2. Start MinIO:
   ```bash
   docker-compose up -d minio
   ```

3. Create bucket via MinIO console (http://localhost:9001)

4. Test storage operations:
   - Upload config → stored in MinIO
   - Retrieve config for parsing
   - Store corrected configs
   - Store PDF reports

5. Verify file structure in MinIO:
   ```
   vajra-core-configs/
   ├── uploads/
   ├── sanitized/
   ├── corrected/
   └── reports/
   ```

**Success Criteria**:
- Files stored in MinIO
- Files retrievable for processing
- S3-compatible interface works
- Bucket organization correct

**Files Modified**:
- `.env` (switch to MinIO)

**Testing**:
- Upload config
- Verify file in MinIO bucket
- Run audit (requires reading from MinIO)
- Verify audit succeeds

---

### Task 5.6: Comprehensive Documentation

**Priority**: MEDIUM  
**Estimated Time**: 6 hours  
**Dependencies**: All features complete

**Actions**:
1. Create user documentation:
   - `docs/user-guide/upload-guide.md`
   - `docs/user-guide/audit-guide.md`
   - `docs/user-guide/remediation-guide.md`
   - `docs/user-guide/bulk-upload-guide.md`

2. Create API documentation:
   - `docs/api/authentication.md`
   - `docs/api/endpoints.md`
   - `docs/api/error-codes.md`

3. Create developer documentation:
   - `docs/developer/architecture.md` (update with Phase 0 changes)
   - `docs/developer/adding-parsers.md`
   - `docs/developer/adding-rules.md`
   - `docs/developer/testing-guide.md`

4. Create operations documentation:
   - `docs/operations/deployment.md`
   - `docs/operations/docker-compose-guide.md`
   - `docs/operations/backup-restore.md`
   - `docs/operations/monitoring.md`
   - `docs/operations/troubleshooting.md`

5. Update README.md with Phase 0 status

**Success Criteria**:
- Complete user guides
- Complete API docs
- Complete developer docs
- Complete operations docs
- README updated

**Files Created**:
- `docs/user-guide/*.md` (4 files)
- `docs/api/*.md` (3 files)
- `docs/developer/*.md` (4 files)
- `docs/operations/*.md` (5 files)

---

### Task 5.7: Final Integration Testing

**Priority**: HIGH  
**Estimated Time**: 4 hours  
**Dependencies**: All features complete

**Actions**:
1. End-to-end workflow test:
   ```
   1. Upload 5 configs (bulk)
   2. Run audits on all
   3. Generate corrected configs for failed audits
   4. Re-assess corrected configs
   5. Compare before/after
   6. Generate PDF reports
   7. Verify deviation metrics
   8. Check authentication enforcement
   9. Test RBAC restrictions
   10. Validate framework filtering
   ```

2. Load testing:
   - 50 concurrent uploads
   - 100 audits queued
   - Measure throughput
   - Check for memory leaks

3. Security testing:
   - Attempt SQL injection
   - Attempt path traversal
   - Test secret exposure
   - Verify authentication bypass impossible

4. Cross-browser testing (if frontend integrated)

**Success Criteria**:
- All workflows complete successfully
- Performance acceptable under load
- No security vulnerabilities found
- No memory leaks
- All features working together

**Testing**:
- Document all test results
- Create `docs/phase-0/final-test-report.md`

---

### Week 5 Deliverables

✅ Structured logging implemented  
✅ Error handling enhanced with codes  
✅ API documentation complete (OpenAPI)  
✅ PostgreSQL tested and validated  
✅ MinIO storage tested and validated  
✅ Comprehensive documentation created  
✅ Final integration testing complete  
✅ Production readiness validated  

**Final Status**: Phase 0 Production MVP **COMPLETE**

---

## Testing Strategy

### Continuous Testing

After **every task**:
1. Run baseline tests: `pytest backend/tests/test_golden_dataset.py`
2. Verify no regressions in existing functionality
3. Add new tests for new features
4. Update test documentation

### Test Pyramid

**Unit Tests** (50+ tests):
- Parser logic
- Compliance rules
- Deviation calculations
- Remediation generation
- Evidence tracking

**Integration Tests** (20+ tests):
- Upload → audit flow
- Deviation → remediation flow
- Bulk upload → multiple audits
- Re-assessment workflow
- Authentication flow

**End-to-End Tests** (10+ tests):
- Complete workflows
- Golden dataset validation
- Before/after scenarios
- Multi-user scenarios

---

## Git Strategy

### Branching

```
main (protected)
├── phase-0-week-1
│   ├── feature/ai-dependencies
│   ├── feature/config-hashing
│   ├── feature/parser-registry
│   ├── feature/secret-sanitization
│   └── feature/framework-foundation
├── phase-0-week-2
│   ├── feature/deviation-engine
│   ├── feature/remediation-integration
│   └── feature/config-generator
├── phase-0-week-3
│   ├── feature/reassessment
│   ├── feature/bulk-upload
│   └── feature/framework-full
├── phase-0-week-4
│   ├── feature/authentication
│   ├── feature/rbac
│   ├── feature/golden-tests
│   └── feature/unit-tests
└── phase-0-week-5
    ├── feature/logging
    ├── feature/documentation
    └── feature/production-testing
```

### Commit Messages

Format: `[TYPE] Brief description`

Types:
- `[FEAT]` - New feature
- `[FIX]` - Bug fix
- `[TEST]` - Test additions
- `[DOCS]` - Documentation
- `[REFACTOR]` - Code refactoring
- `[PERF]` - Performance improvement

Examples:
- `[FEAT] Add SHA-256 hashing to upload pipeline`
- `[TEST] Add golden test case GOLD-003 for HTTP insecure`
- `[DOCS] Document deviation engine API`

### Merge Strategy

1. Feature branch → Week branch (PR with review)
2. Week branch → main (PR with full testing)
3. Tag each week completion: `phase-0-week-1`, etc.
4. Tag Phase 0 completion: `phase-0-complete`

---

## Success Criteria - Phase 0 Complete

### Functional Requirements

✅ Bulk upload API operational  
✅ Deviation engine functional (before/after comparison)  
✅ Remediation engine integrated (vendor-specific commands)  
✅ Corrected configuration generation working  
✅ Re-assessment workflow complete  
✅ Framework data loaded (CIS, NIST, 50+ controls)  
✅ Authentication enabled (Keycloak + JWT)  
✅ RBAC enforced (4 roles: admin, auditor, viewer, vendor)  
✅ Evidence tracking maintained (file/line/text)  

### Quality Requirements

✅ 20+ golden test cases passing  
✅ 50+ unit tests passing  
✅ Code coverage > 70%  
✅ Performance: Audit time < 50ms (PostgreSQL)  
✅ API documentation complete (OpenAPI)  
✅ User documentation complete  
✅ Operations documentation complete  

### Production Requirements

✅ PostgreSQL tested and working  
✅ MinIO tested and working  
✅ Docker Compose stack validated  
✅ Backup/restore tested  
✅ Security audit passed  
✅ Load testing passed (50 concurrent users)  
✅ No memory leaks  

### Preservation Requirements

✅ All baseline tests still passing  
✅ UnifiedSecurityModel unchanged  
✅ Existing parsers working  
✅ Evidence tracking preserved  
✅ PDF generation working  

---

## Risk Mitigation

### High Risks

1. **Breaking existing functionality**  
   - Mitigation: Test after every change, maintain golden dataset
   
2. **Performance degradation with PostgreSQL**  
   - Mitigation: Early PostgreSQL testing, query optimization
   
3. **Authentication breaking existing APIs**  
   - Mitigation: Phased rollout, maintain backward compatibility option
   
4. **Framework data quality**  
   - Mitigation: Start with verified CIS benchmarks, validate mappings

### Medium Risks

1. **AI model dependency issues**  
   - Mitigation: Graceful degradation if model unavailable
   
2. **Bulk upload memory issues**  
   - Mitigation: Process files sequentially, add file count limit
   
3. **Corrected config generation errors**  
   - Mitigation: Extensive testing, validation before saving

---

## Dependencies

### External

- sentence-transformers (AI model)
- PostgreSQL 15 (production database)
- MinIO (object storage)
- Keycloak 23 (authentication)
- Redis 7 (caching - optional)

### Internal

- UnifiedSecurityModel (core - must not break)
- Existing parsers (Cisco, Fortinet, Unknown)
- Compliance engine (10 rules)
- Evidence tracking system

---

## Deliverables Checklist

### Code

- [ ] Bulk upload API
- [ ] Deviation engine
- [ ] Remediation engine integration
- [ ] Corrected config generator
- [ ] Re-assessment workflow
- [ ] Framework data loader
- [ ] Authentication module
- [ ] RBAC implementation
- [ ] Structured logging
- [ ] Enhanced error handling

### Tests

- [ ] 20+ golden test cases
- [ ] 50+ unit tests
- [ ] 20+ integration tests
- [ ] 10+ end-to-end tests
- [ ] Load testing results
- [ ] Security testing results

### Documentation

- [ ] 4 user guides
- [ ] 3 API documentation files
- [ ] 4 developer guides
- [ ] 5 operations guides
- [ ] Updated README
- [ ] OpenAPI/Swagger complete

### Infrastructure

- [ ] Docker Compose validated
- [ ] PostgreSQL production-ready
- [ ] MinIO configured
- [ ] Keycloak configured
- [ ] Alembic migrations applied

---

## Timeline Summary

| Week | Focus | Key Deliverables |
|------|-------|------------------|
| 1 | Core Pipeline | AI deps, hashing, parser registry, secrets, framework foundation |
| 2 | Deviation & Remediation | Comparison engine, remediation integration, config generator |
| 3 | Re-assessment & Bulk | Re-assessment workflow, bulk upload, full framework integration |
| 4 | Authentication & Testing | Keycloak, RBAC, 20+ golden tests, 50+ unit tests |
| 5 | Polish & Production | Logging, docs, PostgreSQL/MinIO testing, final validation |

**Total Duration**: 5 weeks (full-time development)

---

## Next Steps

1. **Review this plan** with stakeholders
2. **Set up development environment** (Docker, dependencies)
3. **Create Week 1 branch** (`phase-0-week-1`)
4. **Start with Task 1.1** (Install AI dependencies)
5. **Daily standup** to track progress
6. **Weekly review** at end of each week
7. **Final demo** at Phase 0 completion

---

**Plan Status**: ✅ READY TO BEGIN  
**Created**: September 17, 2026  
**Phase**: 0 - Production MVP  
**Approach**: Incremental, test-driven, preservation-focused
