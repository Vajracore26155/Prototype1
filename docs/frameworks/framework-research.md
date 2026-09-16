# Framework Data Sources Research - Vajra Core

**Phase 0.5 Foundation - Authoritative Compliance Framework Analysis**

**Date**: September 16, 2026  
**Status**: Research Complete  
**Purpose**: Identify authoritative framework sources for network security compliance

---

## Executive Summary

This document provides a comprehensive analysis of major cybersecurity compliance frameworks applicable to network device configuration auditing. It examines availability, licensing, machine-readable formats, and integration strategies for Vajra Core.

**Key Finding**: Multiple authoritative frameworks are available, but each has specific licensing and usage considerations that must be respected.

---

## 1. CIS Benchmarks (Center for Internet Security)

### Overview

**Authority**: Center for Internet Security (CIS)  
**Website**: https://www.cisecurity.org/cis-benchmarks  
**Focus**: Configuration best practices for IT systems and software

### Network Device Coverage

CIS provides benchmarks for multiple network vendors:

| Vendor | Product | Latest Benchmark | Availability |
|--------|---------|------------------|--------------|
| **Cisco** | IOS | Multiple versions | Download |
| **Cisco** | IOS XE | Version-specific | Download |
| **Fortinet** | FortiGate / FortiOS | Current | Download |
| **Palo Alto** | PAN-OS | Current | Download |
| **Juniper** | Junos OS | Available | Download |

### Licensing Model

**Access Levels**:

1. **Free CIS SecureSuite Membership** (Required)
   - Registration required
   - Access to PDF benchmarks
   - Terms of use apply

2. **CIS-CAT Pro** (Commercial)
   - Automated assessment tool
   - Licensing fees
   - Machine-readable formats

### Machine-Readable Formats

**Available Formats**:
- PDF (primary distribution)
- CIS-CAT Pro SCAP content (commercial)
- XCCDF/OVAL (via CIS-CAT)

**Challenge**: PDF format requires manual extraction of controls

### Benchmark Structure

CIS Benchmarks follow a standard structure:

```
Benchmark: Cisco IOS 15
├── Profile: Level 1 (Basic security)
├── Profile: Level 2 (Enhanced security)
└── Recommendations
    ├── 1. Management Plane
    │   ├── 1.1 Local Authentication
    │   ├── 1.2 Access Rules
    │   └── ...
    ├── 2. Control Plane
    └── 3. Data Plane
```

Each recommendation includes:
- **Title**
- **Description**
- **Rationale**
- **Audit procedure** (how to check)
- **Remediation** (how to fix)
- **Impact**
- **Default value**
- **CIS Control mapping**

### Integration Strategy for Vajra Core

**Approach**:
1. **Manual extraction** from PDF benchmarks (Phase 0.5)
2. Create internal control library with proper attribution
3. Map CIS control IDs to our UnifiedSecurityModel fields
4. Store control metadata with version tracking

**Legal Considerations**:
- ✅ **CAN**: Reference CIS control IDs
- ✅ **CAN**: Map our findings to CIS recommendations
- ✅ **CAN**: Display "Compliant with CIS Benchmark X.Y recommendation Z.Z"
- ❌ **CANNOT**: Redistribute CIS benchmark PDF content
- ❌ **CANNOT**: Copy large sections of benchmark text verbatim

**Attribution Requirements**:
- Cite source: "CIS Cisco IOS 15 Benchmark v4.1.0"
- Include URL to CIS website
- Note in documentation: "Benchmarks available from cisecurity.org"

### Example Control Mapping

```yaml
# Internal control definition
control_id: VAJ-NET-001
title: "SSH Version 2 Required"
description: "Enforce SSH version 2 only for remote management"
severity: HIGH
field_path: "remote_access.ssh_version"
expected: 2

# Framework mappings
frameworks:
  - framework: "CIS"
    benchmark: "Cisco IOS 15 Benchmark"
    version: "4.1.0"
    control_id: "1.2.4"
    control_title: "Set 'ip ssh version 2'"
    profile_level: 1
    source_url: "https://www.cisecurity.org/benchmark/cisco"
```

### Recommendation

**For Phase 0.5**:
- Download relevant CIS benchmarks (requires free account)
- Extract key controls manually for Cisco, Fortinet
- Create internal control library with CIS mappings
- Document source and version
- DO NOT redistribute PDF content

**For Phase 0**:
- Consider CIS-CAT Pro for automated SCAP content (if budget available)
- Build comprehensive mapping for all network device benchmarks
- Implement benchmark version management

---

## 2. NIST SP 800-53 (National Institute of Standards and Technology)

### Overview

**Authority**: National Institute of Standards and Technology (NIST)  
**Website**: https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final  
**Focus**: Security and privacy controls for information systems

### Current Version

**NIST SP 800-53 Revision 5** (September 2020)
- 20 control families
- 1000+ controls and enhancements
- Technology-neutral framework

### Licensing

**PUBLIC DOMAIN** - U.S. Government work
- ✅ Free to use
- ✅ Free to redistribute
- ✅ No registration required
- ✅ Machine-readable formats available

### Machine-Readable Formats (OSCAL)

**OSCAL** (Open Security Controls Assessment Language)

NIST provides official OSCAL representations:

**Available Formats**:
- JSON
- XML
- YAML

**Repository**: https://github.com/usnistgov/oscal-content

```json
{
  "control": {
    "id": "ac-2",
    "class": "SP800-53",
    "title": "Account Management",
    "params": [...],
    "props": [
      {"name": "label", "value": "AC-2"},
      {"name": "sort-id", "value": "ac-02"}
    ],
    "parts": [
      {
        "id": "ac-2_smt",
        "name": "statement",
        "prose": "..."
      }
    ]
  }
}
```

### Applicability to Network Devices

NIST SP 800-53 is **technology-neutral**, so controls apply conceptually:

**Relevant Control Families**:
- **AC** (Access Control)
- **AU** (Audit and Accountability)
- **IA** (Identification and Authentication)
- **SC** (System and Communications Protection)
- **SI** (System and Information Integrity)

**Example Mappings**:

| NIST Control | Network Device Implementation |
|--------------|-------------------------------|
| AC-17 (Remote Access) | SSH configuration, VPN settings |
| AU-2 (Event Logging) | Syslog configuration |
| IA-5 (Authenticator Management) | Password policies, key management |
| SC-8 (Transmission Confidentiality) | TLS/SSH encryption |
| AC-2 (Account Management) | Local user accounts |

### Integration Strategy for Vajra Core

**Approach**:
1. Download OSCAL JSON catalog
2. Store in `data/frameworks/nist/sp800-53-rev5.json`
3. Create mapping table: Technical setting → NIST control
4. Display NIST control coverage in reports

**Technical Implementation**:

```python
# NIST control mapping model
class NISTControlMapping:
    control_id: str  # "AC-17"
    control_title: str
    technical_field: str  # "remote_access.ssh_enabled"
    mapping_type: str  # "SUPPORTS", "IMPLEMENTS", "CONTRIBUTES_TO"
    rationale: str
```

**Attribution**:
- Source: "NIST SP 800-53 Rev. 5"
- No restrictions on use or redistribution

### Recommendation

**For Phase 0.5**:
- ✅ Download OSCAL JSON catalog from GitHub
- ✅ Store in version-controlled location
- ✅ Create initial mapping for key controls
- ✅ Display NIST control IDs in findings

**For Phase 0**:
- Build comprehensive mapping table
- Implement control selection by impact level (LOW/MODERATE/HIGH)
- Support control tailoring

---

## 3. DISA STIGs (Security Technical Implementation Guides)

### Overview

**Authority**: Defense Information Systems Agency (DISA)  
**Website**: https://public.cyber.mil/stigs/  
**Focus**: Configuration standards for DoD information systems

### Network Device STIG Coverage

DISA provides STIGs for multiple network platforms:

| Vendor | Product | STIG Availability | Current Version |
|--------|---------|-------------------|-----------------|
| **Cisco** | IOS XE Router | Available | Current |
| **Cisco** | IOS XE Switch | Available | Current |
| **Cisco** | IOS-XR | Available | Current |
| **Juniper** | Router | Available | Current |
| **Palo Alto** | Firewall | Available | Current |

### Licensing

**PUBLIC RELEASE**
- ✅ Free to download
- ✅ No registration required (since recent policy change)
- ✅ Redistributable
- Published under U.S. Government policy

### Machine-Readable Formats

**STIG Viewer Format** (XML-based):
- XCCDF (Extensible Configuration Checklist Description Format)
- Includes rule IDs, severity, check content, fix text

**SCAP Content** (available for some STIGs):
- Automated compliance checking
- OVAL definitions

### STIG Structure

```xml
<Rule id="SV-123456r1_rule" severity="high">
  <title>Network device must enforce SSH version 2</title>
  <description>
    SSHv1 has known vulnerabilities...
  </description>
  <check system="C-12345r1_chk">
    <check-content>
      Verify SSH version with: show ip ssh
      If "version 2" is not displayed, this is a finding.
    </check-content>
  </check>
  <fix id="F-12345r1_fix">
    <fixtext>
      Configure: ip ssh version 2
    </fixtext>
  </fix>
</Rule>
```

### CAT (Category) Severity Levels

- **CAT I**: High severity (immediate threat)
- **CAT II**: Medium severity (degraded security)
- **CAT III**: Low severity (minor security concerns)

### Integration Strategy for Vajra Core

**Approach**:
1. Download STIG XML files from public.cyber.mil
2. Parse XCCDF to extract rules
3. Map STIG Rule IDs to technical controls
4. Store with version tracking

**Mapping Example**:

```yaml
control_id: VAJ-NET-002
title: "Telnet Must Be Disabled"
frameworks:
  - framework: "STIG"
    stig_name: "Cisco IOS XE Router STIG"
    version: "2R3"
    rule_id: "SV-123789r1_rule"
    vuln_id: "V-123789"
    severity: "CAT I"
    cci: "CCI-000068"  # NIST Control Correlation Identifier
```

### Recommendation

**For Phase 0.5**:
- ✅ Download Cisco IOS XE Router/Switch STIGs
- ✅ Download Fortinet/Palo Alto STIGs if available
- ✅ Parse XCCDF XML for rule extraction
- ✅ Create STIG mapping table

**For Phase 0**:
- Implement full STIG parser
- Support CCI (Control Correlation Identifier) mapping to NIST
- Generate STIG compliance reports

---

## 4. ISO/IEC 27001:2022

### Overview

**Authority**: International Organization for Standardization (ISO)  
**Standard**: ISO/IEC 27001:2022 - Information Security Management Systems  
**Website**: https://www.iso.org/standard/27001

### Nature of Standard

ISO/IEC 27001 is an **ISMS certification standard**, not a technical configuration guide.

**Key Point**: ISO 27001 does NOT specify technical configurations directly.

### Structure

**Clauses 4-10**: Management system requirements  
**Annex A**: 93 controls organized in 4 themes:
- Organizational controls (37)
- People controls (8)
- Physical controls (14)
- Technological controls (34)

### Licensing

**PROPRIETARY STANDARD**
- ❌ Not freely available
- ❌ Must purchase from ISO or national standards body
- ❌ Copyright protected
- ❌ Cannot redistribute control text

**Cost**: ~$150-200 USD per copy

### Machine-Readable Formats

**None officially available**

Third-party representations exist but may violate copyright.

### Applicability to Network Devices

ISO 27001 Annex A controls are **high-level** and require interpretation:

**Example**:
- **A.5.15** (Access Control)
  - "Access to networks and network services shall be controlled"
  - Implementation could include: SSH-only access, ACLs, segmentation

**This is NOT the same as**:
- "Configure `ip ssh version 2`" (CIS Benchmark)
- "Set transport input ssh" (STIG)

### Integration Strategy for Vajra Core

**IMPORTANT**: We CANNOT create technical checks that claim to "verify ISO 27001 compliance."

**What We CAN Do**:
1. Map our technical controls to Annex A control **concepts**
2. Show that technical configurations **support** ISO 27001 objectives
3. Help prepare for ISO 27001 audits by demonstrating security controls

**Mapping Example**:

```yaml
control_id: VAJ-NET-001
title: "SSH Version 2 Required"
frameworks:
  - framework: "ISO27001"
    version: "2022"
    annex_a_control: "A.5.15"
    control_title: "Access Control"
    relationship: "SUPPORTS"
    rationale: "SSH v2 encryption supports secure network access control"
    note: "Technical implementation supporting ISO 27001 objectives"
```

**Disclaimer Required**:
> "Vajra Core checks technical security configurations that support ISO/IEC 27001:2022 Annex A control objectives. These technical checks do not constitute ISO 27001 certification, which requires organizational processes, documentation, and third-party audit."

### Recommendation

**For Phase 0.5**:
- ✅ Create conceptual mappings to Annex A (public domain information)
- ✅ Use control numbers (A.5.15) without reproducing control text
- ✅ Clearly state relationship as "SUPPORTS" not "IMPLEMENTS"
- ❌ Do NOT claim our tool "performs ISO 27001 audits"
- ❌ Do NOT reproduce copyrighted control descriptions

**For Phase 0**:
- Optionally purchase ISO 27001 standard for reference
- Create detailed mapping documentation (internal use only)
- Generate reports showing "ISO 27001 support coverage"

---

## 5. OSCAL (Open Security Controls Assessment Language)

### Overview

**Authority**: NIST  
**Website**: https://pages.nist.gov/OSCAL/  
**Purpose**: Machine-readable representation of security controls

### Benefits

**Standardized Format** for:
- Control catalogs
- Control baselines
- System security plans
- Assessment plans
- Assessment results

### Adoption

OSCAL is used for:
- NIST SP 800-53
- FedRAMP baselines
- Growing industry adoption

### Integration Strategy

**Long-term Vision**:
- Export Vajra Core findings in OSCAL Assessment Results format
- Import OSCAL control catalogs
- Support custom OSCAL-based frameworks

**Phase 0.5**:
- Use OSCAL for NIST SP 800-53 import
- Study OSCAL assessment results schema

---

## 6. Framework Comparison Matrix

| Framework | Prescriptive | Machine-Readable | Cost | Redistribution | Network Device Coverage |
|-----------|--------------|------------------|------|----------------|------------------------|
| **CIS Benchmarks** | ✅ High | ⚠️ Limited | Free* | ❌ No | ✅ Excellent |
| **NIST SP 800-53** | ⚠️ Conceptual | ✅ Yes (OSCAL) | ✅ Free | ✅ Yes | ⚠️ Requires mapping |
| **DISA STIGs** | ✅ High | ✅ Yes (XCCDF) | ✅ Free | ✅ Yes | ✅ Good |
| **ISO 27001** | ⚠️ High-level | ❌ No | ❌ Paid | ❌ No | ⚠️ Conceptual only |

*Requires free registration

---

## 7. Recommended Framework Implementation Priority

### Phase 0.5 (Foundation)

1. **CIS Benchmarks** - Manual extraction for Cisco, Fortinet
2. **NIST SP 800-53** - Download OSCAL JSON catalog
3. **DISA STIGs** - Download and parse Cisco IOS XE STIG

### Phase 0 (Production MVP)

4. **Expand CIS** - All supported network vendors
5. **Expand STIGs** - All available network device STIGs
6. **ISO 27001 Mapping** - Conceptual support mappings

### Phase 1+ (Future)

7. **Custom frameworks** - User-defined control sets
8. **OSCAL export** - Assessment results in OSCAL format
9. **Framework versioning** - Track and compare across versions

---

## 8. Framework Data Storage Structure

```
data/frameworks/
├── cis/
│   ├── metadata.json
│   ├── cisco_ios_15_v4.1.0/
│   │   ├── benchmark_metadata.json
│   │   └── controls.yaml
│   └── fortinet_fortios_v1.0.0/
│       ├── benchmark_metadata.json
│       └── controls.yaml
│
├── nist/
│   ├── sp800-53-rev5.json  (OSCAL)
│   └── mappings/
│       └── network_devices.yaml
│
├── stig/
│   ├── metadata.json
│   ├── cisco_ios_xe_router_v2r3.xml  (XCCDF)
│   └── cisco_ios_xe_switch_v2r3.xml
│
└── iso27001/
    ├── 2022_annex_a_controls.json  (control numbers only)
    └── mappings/
        └── technical_mappings.yaml
```

---

## 9. Legal and Compliance Summary

### ✅ Safe to Use / Redistribute

- NIST SP 800-53 (public domain)
- NIST OSCAL catalogs (public domain)
- DISA STIGs (public release)
- Framework **metadata** (titles, IDs, structure)
- Our own **mappings** to frameworks

### ⚠️ Requires Care

- CIS Benchmarks (free access, but terms apply)
  - Can reference by ID
  - Cannot redistribute PDF
  - Can create internal derived works for tool use
- ISO 27001 (copyrighted)
  - Can reference control numbers (A.5.15)
  - Cannot reproduce control text without license

### ❌ Do Not

- Copy/paste large sections of copyrighted content
- Redistribute restricted PDFs
- Claim certification/compliance without proper process
- Misrepresent scope (technical checks ≠ organizational compliance)

---

## 10. Attribution Requirements

### CIS Benchmarks

```
Source: CIS Cisco IOS 15 Benchmark v4.1.0
Published by: Center for Internet Security (CIS)
Available from: https://www.cisecurity.org/cis-benchmarks
License: Available under CIS SecureSuite Membership
```

### NIST SP 800-53

```
Source: NIST Special Publication 800-53 Revision 5
Published by: National Institute of Standards and Technology
Available from: https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final
License: Public Domain (U.S. Government work)
```

### DISA STIGs

```
Source: Cisco IOS XE Router Security Technical Implementation Guide
Published by: Defense Information Systems Agency (DISA)
Available from: https://public.cyber.mil/stigs/
License: Public Release
```

---

## 11. Next Steps

### Immediate (Phase 0.5)

1. ✅ Register for CIS SecureSuite (free)
2. ✅ Download Cisco IOS & Fortinet benchmarks
3. ✅ Clone NIST OSCAL GitHub repository
4. ✅ Download relevant DISA STIGs from public.cyber.mil
5. ✅ Create framework storage structure
6. ✅ Extract initial control set (20-30 controls)

### Phase 0

1. Comprehensive control extraction
2. Framework version management system
3. Automated STIG XCCDF parsing
4. Mapping validation
5. Multi-framework reporting

---

## Conclusion

Multiple authoritative frameworks are available for network device security compliance. Each has different characteristics:

- **CIS Benchmarks**: Most prescriptive, device-specific, requires careful licensing compliance
- **NIST SP 800-53**: Technology-neutral, freely available, requires interpretation
- **DISA STIGs**: Government-focused, very prescriptive, freely available
- **ISO 27001**: Organizational focus, high-level, proprietary

**Vajra Core Strategy**: Multi-framework approach with proper attribution, respecting licensing, and clearly communicating the scope and limitations of automated technical checks.

---

**Document Version**: 1.0  
**Last Updated**: September 16, 2026  
**Status**: Research Complete  
**Phase**: 0.5 - Foundation
