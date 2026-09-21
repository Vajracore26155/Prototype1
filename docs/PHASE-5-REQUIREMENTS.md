# PHASE 5: ADVANCED SECURITY INTELLIGENCE & GOVERNANCE

**Project:** SIH 2026 PS 26155 - AI-Driven Multi-Vendor Network Security Compliance Auditor  
**Phase:** 5 of 6  
**Focus:** Device Management, Drift Detection, Posture Scoring, Remediation Workflows

---

## OVERVIEW

Phase 5 transforms Vajra Core from a configuration auditing tool into a comprehensive security posture management platform with device tracking, configuration drift detection, continuous compliance monitoring, and automated remediation workflows.

---

## OBJECTIVES

1. **Device Inventory Management** - Track all network devices and their configurations
2. **Configuration History & Versioning** - Track configuration changes over time
3. **Drift Detection** - Identify configuration drift from baselines
4. **Security Posture Scoring** - Quantify organization security posture
5. **Remediation Workflows** - Automate remediation with approval workflows
6. **Advanced Reporting** - Executive dashboards and trend analysis

---

## FEATURES

### 1. Device Inventory Management

**Capabilities:**
- Register network devices (routers, switches, firewalls)
- Device metadata (hostname, IP, type, vendor, location, owner)
- Device grouping and tagging
- Device-to-configuration mapping
- Device lifecycle tracking (active, maintenance, decommissioned)
- Bulk device import from CSV

**Data Model:**
```python
Device:
    - device_id (UUID)
    - organization_id (FK)
    - hostname
    - ip_address
    - device_type (ROUTER, SWITCH, FIREWALL, WAF, IDS, IPS, etc.)
    - vendor
    - model
    - os_version
    - location
    - owner
    - tags (JSON array)
    - status (ACTIVE, MAINTENANCE, DECOMMISSIONED)
    - last_seen
    - created_at, updated_at
```

**API Endpoints:**
```
POST   /api/devices                - Create device
GET    /api/devices                - List devices (with filters)
GET    /api/devices/{device_id}    - Get device details
PATCH  /api/devices/{device_id}    - Update device
DELETE /api/devices/{device_id}    - Delete device
POST   /api/devices/bulk-import    - Bulk import from CSV
GET    /api/devices/{device_id}/configurations - Get device config history
```

### 2. Configuration History & Versioning

**Capabilities:**
- Track configuration versions over time
- Link configurations to devices
- Configuration comparison (diff view)
- Rollback capability (generate commands)
- Change annotations and metadata
- Automated configuration collection scheduling

**Data Model:**
```python
ConfigurationVersion:
    - id
    - configuration_id (FK)
    - device_id (FK) 
    - version_number
    - content_hash (SHA-256)
    - uploaded_at
    - uploaded_by
    - change_summary
    - is_baseline (bool)
    - parent_version_id (FK, self-reference)
```

**API Endpoints:**
```
GET  /api/configurations/{config_id}/versions - List versions
GET  /api/configurations/{config_id}/versions/{version} - Get version
POST /api/configurations/{config_id}/versions/{v1}/compare/{v2} - Compare versions
POST /api/configurations/{config_id}/set-baseline - Mark as baseline
GET  /api/devices/{device_id}/configuration-timeline - Get timeline
```

### 3. Drift Detection

**Capabilities:**
- Detect drift from baseline configuration
- Baseline management (set, update, clear)
- Drift scoring (severity of drift)
- Field-level drift analysis
- Automated drift alerts
- Drift remediation suggestions

**Data Model:**
```python
DriftAnalysis:
    - id
    - drift_id (UUID)
    - device_id (FK)
    - baseline_version_id (FK)
    - current_version_id (FK)
    - drift_score (0-100)
    - drift_severity (NONE, LOW, MEDIUM, HIGH, CRITICAL)
    - field_drifts (JSON array)
    - detected_at
    - acknowledged (bool)
    - acknowledged_by
    - acknowledged_at

FieldDrift:
    - field_path (e.g., "security.ssh_enabled")
    - baseline_value
    - current_value
    - drift_type (ADDED, REMOVED, MODIFIED)
    - severity (LOW, MEDIUM, HIGH, CRITICAL)
    - security_impact
```

**API Endpoints:**
```
POST /api/devices/{device_id}/detect-drift - Detect drift
GET  /api/devices/{device_id}/drift-history - Drift history
POST /api/drift/{drift_id}/acknowledge - Acknowledge drift
GET  /api/dashboard/drift-summary - Organization drift summary
```

### 4. Security Posture Scoring

**Capabilities:**
- Organization-level posture score (0-100)
- Device-level compliance scores
- Trend analysis (daily, weekly, monthly)
- Risk factor breakdown
- Compliance by framework
- Score comparison across devices/groups

**Scoring Factors:**
- Compliance score (40%)
- Configuration drift (20%)
- Critical findings count (15%)
- High findings count (10%)
- Remediation velocity (10%)
- Configuration age (5%)

**Data Model:**
```python
PostureScore:
    - id
    - organization_id (FK)
    - device_id (FK, nullable - null = org level)
    - score (0-100)
    - compliance_score
    - drift_score
    - risk_score
    - factor_breakdown (JSON)
    - calculated_at

PostureTrend:
    - id
    - organization_id (FK)
    - date
    - score
    - trend (IMPROVING, DECLINING, STABLE)
    - score_change
```

**API Endpoints:**
```
GET /api/posture/organization - Org posture score
GET /api/posture/devices - Device posture scores
GET /api/posture/trends - Posture trends
GET /api/posture/breakdown - Score breakdown
GET /api/posture/compare - Compare devices/groups
```

### 5. Remediation Workflows

**Capabilities:**
- Generate remediation commands per vendor
- Remediation approval workflow
- Batch remediation for multiple findings
- Remediation templates
- Change request tracking
- Remediation history and rollback

**Data Model:**
```python
RemediationPlan:
    - id
    - plan_id (UUID)
    - organization_id (FK)
    - device_id (FK)
    - audit_id (FK)
    - finding_ids (JSON array)
    - remediation_commands (text)
    - estimated_impact (LOW, MEDIUM, HIGH)
    - requires_approval (bool)
    - status (DRAFT, PENDING_APPROVAL, APPROVED, REJECTED, APPLIED, FAILED)
    - created_by
    - created_at
    - approved_by
    - approved_at
    - applied_at
    - rollback_commands (text)

RemediationApproval:
    - id
    - plan_id (FK)
    - approver_id (FK)
    - decision (APPROVE, REJECT, REQUEST_CHANGES)
    - comments
    - created_at
```

**API Endpoints:**
```
POST   /api/remediation/plans - Create plan
GET    /api/remediation/plans - List plans
GET    /api/remediation/plans/{plan_id} - Get plan
POST   /api/remediation/plans/{plan_id}/approve - Approve plan
POST   /api/remediation/plans/{plan_id}/reject - Reject plan
POST   /api/remediation/plans/{plan_id}/apply - Apply plan
GET    /api/remediation/pending-approvals - Pending approvals
```

### 6. Advanced Reporting & Dashboards

**Capabilities:**
- Executive dashboard (high-level metrics)
- Compliance dashboard (by framework)
- Drift dashboard (organization-wide)
- Device health dashboard
- Custom report builder
- Scheduled reports (email delivery)
- Export to PDF, CSV, JSON

**Reports:**
- Executive Security Posture Report
- Compliance Status Report (by framework)
- Drift Analysis Report
- Risk Assessment Report
- Remediation Status Report
- Trend Analysis Report

**API Endpoints:**
```
GET  /api/dashboards/executive - Executive dashboard
GET  /api/dashboards/compliance - Compliance dashboard
GET  /api/dashboards/drift - Drift dashboard
GET  /api/dashboards/devices - Device health
POST /api/reports/generate - Generate custom report
GET  /api/reports/templates - List templates
POST /api/reports/schedule - Schedule report
```

---

## IMPLEMENTATION PLAN

### Week 1: Device Management
- [ ] Device model and CRUD operations
- [ ] Device API endpoints
- [ ] Device grouping and tagging
- [ ] Bulk import from CSV
- [ ] Device-configuration linking

### Week 2: Configuration History
- [ ] Configuration versioning
- [ ] Version comparison engine
- [ ] Timeline API
- [ ] Baseline management
- [ ] Diff visualization support

### Week 3: Drift Detection
- [ ] Drift detection algorithm
- [ ] Field-level drift analysis
- [ ] Drift scoring engine
- [ ] Alert system
- [ ] Drift API endpoints

### Week 4: Posture Scoring
- [ ] Scoring algorithm
- [ ] Trend tracking
- [ ] Score breakdown
- [ ] Comparison engine
- [ ] Posture API endpoints

### Week 5: Remediation Workflows
- [ ] Remediation plan generation
- [ ] Approval workflow
- [ ] Command templates
- [ ] Rollback support
- [ ] Remediation API endpoints

### Week 6: Advanced Reporting
- [ ] Dashboard APIs
- [ ] Report templates
- [ ] PDF generation
- [ ] Scheduled reports
- [ ] Email delivery

---

## SUCCESS CRITERIA

- ✅ Device inventory with 100+ devices manageable
- ✅ Configuration history with version comparison
- ✅ Drift detection with <1 min latency
- ✅ Posture score accuracy >95%
- ✅ Remediation plans generated in <5s
- ✅ All reports generate in <10s
- ✅ API response time <500ms
- ✅ Multi-tenant data isolation maintained

---

## DEPENDENCIES

**Phase 4 (Complete):**
- Authentication & RBAC
- Multi-tenancy
- Async processing
- Storage abstraction

**New Dependencies:**
- difflib (Python stdlib - for config diff)
- APScheduler (for scheduled reports)
- reportlab (for advanced PDF generation)

---

**Phase 5 Status:** 🔄 **IN PROGRESS**
