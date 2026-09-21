# VAJRA CORE API Reference

**Version:** 1.0.0  
**Base URL:** `https://api.vajra.example.com`  
**Authentication:** Bearer Token (JWT)

---

## Table of Contents

1. [Authentication](#authentication)
2. [Configuration Management](#configuration-management)
3. [Security Audits](#security-audits)
4. [Findings](#findings)
5. [Devices](#devices)
6. [Compliance Frameworks](#compliance-frameworks)
7. [Drift Detection](#drift-detection)
8. [Reporting](#reporting)
9. [Webhooks](#webhooks)
10. [Knowledge Graph](#knowledge-graph)
11. [Search](#search)
12. [Monitoring](#monitoring)

---

## Authentication

### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 3600
  }
}
```

### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "newuser@example.com",
  "username": "newuser",
  "password": "SecurePassword123!",
  "full_name": "New User"
}
```

### Refresh Token
```http
POST /api/auth/refresh
Authorization: Bearer <token>
```

---

## Configuration Management

### Upload Configuration
```http
POST /api/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <configuration_file.cfg>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "config_id": "CFG-00000123",
    "filename": "router1.cfg",
    "vendor": "cisco",
    "vendor_confidence": 0.95,
    "status": "UPLOADED"
  }
}
```

### Get Configuration
```http
GET /api/configurations/{config_id}
Authorization: Bearer <token>
```

### List Configurations
```http
GET /api/configurations?limit=50&status=COMPLETED
Authorization: Bearer <token>
```

### Delete Configuration
```http
DELETE /api/configurations/{config_id}
Authorization: Bearer <token>
```

---

## Security Audits

### Create Audit
```http
POST /api/audits
Authorization: Bearer <token>
Content-Type: application/json

{
  "config_id": "CFG-00000123",
  "frameworks": ["CIS", "PCI-DSS"],
  "device_id": "DEV-000456"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "audit_id": "AUD-00000789",
    "status": "PROCESSING",
    "config_id": "CFG-00000123",
    "started_at": "2026-09-18T10:30:00Z"
  }
}
```

### Get Audit Status
```http
GET /api/audits/{audit_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "audit_id": "AUD-00000789",
    "status": "COMPLETED",
    "compliance_score": 85.5,
    "risk_score": 25.0,
    "risk_level": "MEDIUM",
    "passed_count": 85,
    "failed_count": 15,
    "warning_count": 5,
    "completed_at": "2026-09-18T10:35:00Z"
  }
}
```

### List Audits
```http
GET /api/audits?limit=50&status=COMPLETED
Authorization: Bearer <token>
```

---

## Findings

### Get Audit Findings
```http
GET /api/audits/{audit_id}/findings
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "findings": [
      {
        "finding_id": "FND-001",
        "title": "SSH version 1 enabled",
        "severity": "HIGH",
        "category": "AUTHENTICATION",
        "status": "OPEN",
        "description": "Device is using insecure SSH version 1",
        "line_number": 42,
        "config_snippet": "ssh version 1",
        "remediation": "Disable SSH version 1 and enable version 2"
      }
    ],
    "total": 15
  }
}
```

### Update Finding Status
```http
PATCH /api/findings/{finding_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "ACKNOWLEDGED",
  "notes": "Remediation scheduled for next maintenance window"
}
```

---

## Devices

### Register Device
```http
POST /api/devices
Authorization: Bearer <token>
Content-Type: application/json

{
  "device_id": "DEV-CUSTOM-001",
  "vendor": "cisco",
  "model": "ISR4451",
  "hostname": "router-prod-01",
  "ip_address": "192.168.1.1",
  "location": "Data Center A"
}
```

### Get Device
```http
GET /api/devices/{device_id}
Authorization: Bearer <token>
```

### List Devices
```http
GET /api/devices?vendor=cisco&status=ACTIVE
Authorization: Bearer <token>
```

---

## Reporting

### List Templates
```http
GET /api/reports/templates
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "templates": [
      {
        "template_id": "TMPL-001",
        "name": "Executive Summary Report",
        "report_type": "executive_summary",
        "description": "High-level overview for executives"
      }
    ]
  }
}
```

### Generate Report
```http
POST /api/reports/generate
Authorization: Bearer <token>
Content-Type: application/json

{
  "template_id": "TMPL-001",
  "name": "Monthly Security Report",
  "format": "PDF",
  "filters": {
    "date_range": "30d"
  }
}
```

### Schedule Report
```http
POST /api/reports/scheduled
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Weekly Security Report",
  "template_id": "TMPL-001",
  "report_type": "executive_summary",
  "format": "PDF",
  "schedule_type": "WEEKLY",
  "schedule_time": "09:00",
  "schedule_day_of_week": 1,
  "recipients": ["admin@example.com"]
}
```

---

## Webhooks

### Create Webhook
```http
POST /api/webhooks
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Audit Completion Webhook",
  "url": "https://example.com/webhook",
  "secret": "webhook_secret_123",
  "events": ["audit.completed", "finding.critical"],
  "is_active": true
}
```

### List Webhooks
```http
GET /api/webhooks
Authorization: Bearer <token>
```

### Test Webhook
```http
POST /api/webhooks/{webhook_id}/test
Authorization: Bearer <token>
```

---

## Knowledge Graph

### Get Graph Statistics
```http
GET /api/knowledge-graph
Authorization: Bearer <token>
```

### Get Entity Details
```http
GET /api/knowledge-graph/entity/{entity_id}
Authorization: Bearer <token>
```

### Analyze Impact
```http
GET /api/knowledge-graph/impact/{entity_id}?max_depth=3
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "source_entity": {
      "entity_id": "DEV-001",
      "entity_type": "device"
    },
    "affected_entities": [
      {
        "entity_id": "CFG-123",
        "entity_type": "configuration",
        "depth": 1
      }
    ],
    "total_affected": 5
  }
}
```

---

## Search

### Universal Search
```http
GET /api/search?q=firewall&types=findings,devices&severity=HIGH
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "id": "FND-001",
        "_type": "findings",
        "title": "Firewall policy misconfiguration",
        "severity": "HIGH"
      }
    ],
    "total": 25,
    "facets": {
      "severity": {"HIGH": 10, "MEDIUM": 15}
    }
  }
}
```

### Auto-suggest
```http
GET /api/search/suggest?q=fire&entity_type=findings&limit=10
Authorization: Bearer <token>
```

---

## Monitoring

### Get Dashboard
```http
GET /api/monitoring/dashboard
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "metrics": {
      "total_devices": 50,
      "total_audits": 1250,
      "critical_findings": 5,
      "compliance_score": 85.5
    },
    "trends": {
      "audit_trend": "improving",
      "finding_trend": "decreasing"
    }
  }
}
```

### Get System Metrics
```http
GET /api/monitoring/metrics/system
Authorization: Bearer <token>
```

---

## Rate Limits

- **Default:** 60 requests/minute, 1000 requests/hour
- **Authentication:** 5 requests/minute, 100 requests/hour
- **Upload:** 10 requests/minute, 100 requests/hour

**Rate Limit Headers:**
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1632825600
```

---

## Error Responses

### Standard Error Format
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "email",
      "issue": "Invalid email format"
    }
  }
}
```

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `429` - Too Many Requests
- `500` - Internal Server Error

---

## Webhooks

### Event Types
- `audit.created`
- `audit.completed`
- `audit.failed`
- `finding.created`
- `finding.critical`
- `device.registered`
- `device.drift_detected`
- `report.generated`

### Webhook Payload
```json
{
  "event_id": "EVT-123",
  "event_type": "audit.completed",
  "timestamp": "2026-09-18T10:35:00Z",
  "data": {
    "audit_id": "AUD-789",
    "compliance_score": 85.5,
    "risk_level": "MEDIUM"
  }
}
```

### Signature Verification
```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)
```

---

## Pagination

All list endpoints support pagination:

```http
GET /api/audits?page=2&limit=50
```

**Response includes:**
```json
{
  "data": [...],
  "pagination": {
    "page": 2,
    "limit": 50,
    "total": 250,
    "pages": 5
  }
}
```

---

## OpenAPI Specification

Interactive API documentation available at:
- Swagger UI: `https://api.vajra.example.com/docs`
- ReDoc: `https://api.vajra.example.com/redoc`
- OpenAPI JSON: `https://api.vajra.example.com/openapi.json`
