# PDF Report Visual Structure Guide

## Professional Layout Preview

---

## Page 1: Cover Page

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                                                             │
│  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  │ ← Indigo accent bar
│                                                             │
│          SECURITY COMPLIANCE AUDIT REPORT                   │ ← Small caps, spaced
│                                                             │
│                     Tatva                                   │ ← Large, bold (36pt)
│         Network Security Compliance Auditor                 │ ← Subtitle (14pt)
│                                                             │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Configuration File   cisco_router_config.cfg         │ │
│  │  Vendor               Cisco IOS                       │ │ ← Light gray box
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│                                                             │
│     Report ID:     AUD-998777                              │
│     Status:        COMPLETED                               │ ← Metadata table
│     Generated:     September 9, 2026 at 14:32 UTC         │
│                                                             │
│                   ┌─────────────────┐                      │
│                   │   COMPLETED     │                      │ ← Status badge
│                   └─────────────────┘                      │
│                                                             │
│  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  │ ← Bottom accent
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Page 2: Executive Summary

```
─────────────────────────────────────────────────────────────
Tatva                      Security Compliance Audit Report   ← Header
─────────────────────────────────────────────────────────────

Executive Summary                                              ← Section title (20pt)
══════════════                                                 ← Underline accent

This report presents the comprehensive security audit 
results for cisco_router_config.cfg (Cisco IOS). The 
automated analysis evaluated 24 security controls across       ← Body text (10pt)
multiple compliance domains, identifying 8 violations          justified
that require remediation.

The configuration achieved a compliance score of 67.0% 
with an overall risk rating of HIGH.

┌─────────────────────────────────────────────────────────┐
│ Critical Findings:                                      │
│ • 2 CRITICAL severity issues requiring immediate       │  ← Red alert box
│   attention                                             │
│ • 3 HIGH severity issues requiring prompt remediation  │
└─────────────────────────────────────────────────────────┘


─────────────────────────────────────────────────────────────
Report ID: AUD-998777        Generated: September 9, 2026     Page 2 of 12
                                                               ← Footer
```

---

## Page 3: Key Performance Indicators

```
─────────────────────────────────────────────────────────────
Tatva                      Security Compliance Audit Report
─────────────────────────────────────────────────────────────

Key Performance Indicators
══════════════════════════

┌─────────────┬─────────────┬─────────────┬─────────────┐
│             │             │             │             │
│     67%     │    HIGH     │     16      │      8      │ ← Large numbers
│             │             │             │             │
│ Compliance  │    Risk     │   Passed    │   Failed    │ ← Small labels
│   Score     │    Level    │  Controls   │  Controls   │
│             │             │             │             │
└─────────────┴─────────────┴─────────────┴─────────────┘


┌─────────────┬─────────────┬─────────────┬─────────────┐
│      2      │      3      │      2      │      1      │ ← Smaller KPIs
│  Critical   │    High     │   Medium    │     Low     │
└─────────────┴─────────────┴─────────────┴─────────────┘


─────────────────────────────────────────────────────────────
Report ID: AUD-998777        Generated: September 9, 2026     Page 3 of 12
```

---

## Page 4: Compliance Analysis

```
─────────────────────────────────────────────────────────────
Tatva                      Security Compliance Audit Report
─────────────────────────────────────────────────────────────

Compliance Analysis
═══════════════════

              Control Status Distribution
┌──────────────────────────────────────────────────────────┐
│ ████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │ ← Bar chart
│  Passed: 16 (67%)           Failed: 8 (33%)              │   Green & red
└──────────────────────────────────────────────────────────┘

Overall Risk Assessment: HIGH
Risk Score: 7.25 out of 10.0

The risk level is determined by the severity and quantity 
of failed controls. Critical and high-severity findings 
significantly impact the overall risk rating.


[IF HUMAN REVIEW NEEDED:]
┌───────────────────────────────────────────────────────────┐
│  ⚠ MANUAL REVIEW REQUIRED                                │ ← Yellow header
├───────────────────────────────────────────────────────────┤
│  Reason: Proprietary syntax detected                     │
│  Interpretation Confidence: 72.5%                        │ ← Details
│  Uninterpreted Lines: 45 of 230 (19.6%)                 │
└───────────────────────────────────────────────────────────┘


─────────────────────────────────────────────────────────────
Report ID: AUD-998777        Generated: September 9, 2026     Page 4 of 12
```

---

## Page 5: Detailed Findings

```
─────────────────────────────────────────────────────────────
Tatva                      Security Compliance Audit Report
─────────────────────────────────────────────────────────────

Detailed Security Findings
══════════════════════════

Found 8 total violations: 2 CRITICAL, 3 HIGH, 2 MEDIUM, 1 LOW.


CRITICAL Severity Findings                                    ← Subsection

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 1. Weak SSH Encryption Algorithm Configured              ┃ ← Red tinted
┃ Rule: NET-SEC-001  |  CRITICAL                           ┃   header
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
┌─────────────────────────────────────────────────────────┐
│ Issue:                                                   │
│ The SSH service is configured to accept weak encryption │
│ algorithms that are vulnerable to cryptographic attacks.│
│                                                          │
│ Expected Configuration: aes256-ctr or aes192-ctr        │
│ Actual Configuration: 3des-cbc                          │
│                                                          │
│ Evidence:                                               │ ← White body
│   ip ssh server algorithm encryption 3des-cbc           │   Courier font
│   Location: config.cfg, Line 142                        │
│                                                          │
│ Recommended Solution:                                    │
│   ip ssh server algorithm encryption aes256-ctr         │ ← Code block
│                                                          │
│ Risk Impact Score: 9.2/10.0                             │
└─────────────────────────────────────────────────────────┘


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 2. Telnet Service Enabled                               ┃
┃ Rule: NET-SEC-002  |  CRITICAL                          ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
[... similar structure ...]


─────────────────────────────────────────────────────────────
Report ID: AUD-998777        Generated: September 9, 2026     Page 5 of 12
```

---

## Page 6+: Continued Findings

```
─────────────────────────────────────────────────────────────
Tatva                      Security Compliance Audit Report
─────────────────────────────────────────────────────────────

HIGH Severity Findings                                        ← New severity

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 3. No Banner Message Configured                          ┃ ← Orange tint
┃ Rule: NET-POL-005  |  HIGH                               ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
[... finding details ...]


MEDIUM Severity Findings                                      ← Yellow tint

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 6. NTP Server Not Configured                             ┃
┃ Rule: NET-CFG-012  |  MEDIUM                             ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
[... finding details ...]


LOW Severity Findings                                         ← Green tint

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 8. Hostname Uses Default Value                           ┃
┃ Rule: NET-CFG-020  |  LOW                                ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
[... finding details ...]


─────────────────────────────────────────────────────────────
Report ID: AUD-998777        Generated: September 9, 2026     Page 8 of 12
```

---

## Last Page: Recommendations

```
─────────────────────────────────────────────────────────────
Tatva                      Security Compliance Audit Report
─────────────────────────────────────────────────────────────

Recommendations
═══════════════

Based on the security audit findings, the following actions 
are recommended to improve the security posture and compliance 
of this network configuration:

Immediate Action Required (2 items):
• Address all CRITICAL severity findings within 24 hours
• These issues present significant security risks that could
  be exploited
• Implement recommended fixes and re-audit to verify 
  remediation

Priority Action (3 items):
• Resolve HIGH severity findings within 1 week
• These issues represent serious security weaknesses
• Schedule remediation activities and track progress

General Recommendations:
• Review all findings with your security team
• Test all configuration changes in a non-production 
  environment first
• Document all changes made for compliance audit trails
• Schedule regular security audits to maintain compliance
• Consider implementing automated configuration monitoring


─────────────────────────────────────────────────────────────
Report ID: AUD-998777        Generated: September 9, 2026     Page 12 of 12
```

---

## Color Legend

### Primary Colors
- **▓** Indigo (#4f46e5) - Accent bars, primary KPIs
- **█** Green (#10b981) - Passed controls, success
- **█** Red (#dc2626) - Failed controls, critical
- **█** Orange (#ea580c) - High severity
- **█** Amber (#d97706) - Medium severity, warnings
- **█** Green (#16a34a) - Low severity

### Background Colors
- Light gray (#f8fafc) - KPI cards, tables
- White - Finding bodies, main content
- Red tint (rgba red, 8%) - Critical findings
- Orange tint - High findings
- Yellow tint - Medium findings, alerts
- Green tint - Low findings, success boxes

### Text Colors
- Dark (#1e293b) - Main text, headers
- Medium (#475569) - Body text
- Light (#64748b) - Labels, metadata
- Lightest (#94a3b8) - Captions, footer

---

## Typography Scale

```
Cover Title:          36pt  Helvetica-Bold
KPI Number (large):   32pt  Helvetica-Bold
KPI Number (small):   24pt  Helvetica-Bold
Section Title:        20pt  Helvetica-Bold
Subsection:           15pt  Helvetica-Bold
Finding Title:        13pt  Helvetica-Bold
Body Standard:        10pt  Helvetica
Body Small:            9pt  Helvetica
Header/Footer:         8pt  Helvetica
Caption:               8pt  Helvetica
Code:                  8pt  Courier
```

---

## Page Elements

### Header (Every page except cover)
```
─────────────────────────────────────────────────────────────
Tatva                      Security Compliance Audit Report
─────────────────────────────────────────────────────────────
```

### Footer (Every page except cover)
```
─────────────────────────────────────────────────────────────
Report ID: AUD-XXXXXX        Generated: Date          Page X of Y
```

### Section Title
```
Section Name
════════════  ← Implied underline through styling
```

### KPI Card
```
┌─────────────┐
│             │
│     67%     │ ← Large colored number
│             │
│ Compliance  │ ← Small label
│   Score     │
│             │
└─────────────┘
```

### Finding Card
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓  ← Colored header
┃ N. Finding Title                        ┃
┃ Rule: XXX  |  SEVERITY                  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
┌──────────────────────────────────────────┐  ← White body
│ Issue: ...                               │
│ Evidence: ...                            │
│ Solution: ...                            │
└──────────────────────────────────────────┘
```

---

## Print Layout

### Margins
```
┌─────────────────────────────────────────┐
│  0.75"                                  │
│  ┌───────────────────────────────────┐ │
│  │                                   │ │
│  │         7" wide                   │ │
0.75"│         9.3" tall                 │0.75"
│  │         Printable Area            │ │
│  │                                   │ │
│  └───────────────────────────────────┘ │
│                 0.75"                   │
└─────────────────────────────────────────┘
     8.5" × 11" (Letter size)
```

---

## Design Principles

✅ **Clean & Minimal** - No unnecessary decoration
✅ **Strong Hierarchy** - Clear visual organization
✅ **Consistent Identity** - Tatva branding throughout
✅ **Readable** - Professional typography
✅ **Print-Friendly** - Works in color and grayscale
✅ **Executive-Quality** - Appropriate for stakeholders
✅ **Data-Focused** - Information is primary
✅ **Actionable** - Clear recommendations

---

**Report System Version:** 2.0.0  
**Design Standard:** Enterprise Professional  
**Last Updated:** September 9, 2026
