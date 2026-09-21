# Phase 1 Baseline Documentation

**Multi-Vendor Network Security Compliance Auditor - Phase 1 Foundation**

**Date:** September 17, 2026  
**Phase:** 1 (Multi-Vendor Expansion)  
**Status:** Discovery Complete - Ready for Implementation

---

## Executive Summary

This document establishes the baseline for Phase 1 Multi-Vendor Expansion. Phase 0 has successfully delivered a working prototype with Cisco and Fortinet support. Phase 1 will harden existing parsers and add production-grade support for Palo Alto and Juniper platforms while maintaining the vendor-agnostic architecture.

**Current State:**
- ✅ 2 vendors supported (Cisco, Fortinet)
- ✅ 1 fallback parser (Unknown/AI-based)
- ✅ Unified Security Model (vendor-agnostic)
- ✅ 10 compliance rules (CIS/NIST baseline)
- ✅ Evidence-based findings (file/line/text)

**Phase 1 Goals:**
- 🎯 4 production-grade parsers (Cisco, Fortinet, Palo Alto, Juniper)
- 🎯 Enhanced UnifiedSecurityModel field coverage
- 🎯 Vendor-specific test suites (20+ configs per vendor)
- 🎯 Zero regression on Phase 0 functionality

---

## 1. Current Vendor Support Analysis

### 1.1 Cisco Parser (`cisco_parser.py`)

**Status:** ✅ OPERATIONAL - Needs Hardening

**Detection Signatures:**
- `interface GigabitEthernet|FastEthernet` (weight: 0.25)
- `line vty` (weight: 0.25)
- `router ospf|eigrp|bgp` (weight: 0.20)
- `ip ssh|route` (weight: 0.15)
- Confidence threshold: 0.75

**Extracted Fields:**

| Security Domain | Field | Evidence Tracking | Coverage |
|----------------|-------|------------------|----------|
| **Device Info** | hostname | ✅ Yes | ✅ Full |
| | vendor | ✅ Yes | ✅ Full |
| | version | ✅ Yes | ⚠️ Basic |
| | device_type | ❌ No | ⚠️ Static ("router") |
| **Remote Access** | ssh_enabled | ✅ Yes | ✅ Full |
| | ssh_version | ✅ Yes | ✅ Full |
| | telnet_enabled | ✅ Yes | ✅ Full |
| **Management** | http_enabled | ✅ Yes | ✅ Full |
| | https_enabled | ✅ Yes | ✅ Full |
| | snmp_enabled | ✅ Yes | ⚠️ Basic |
| **Authentication** | local_authentication | ✅ Yes | ✅ Full |
| | password_encryption | ✅ Yes | ✅ Full |
| | enable_secret_configured | ✅ Yes | ✅ Full |
| **Logging** | enabled | ✅ Yes | ✅ Full |
| | remote_server | ✅ Yes | ✅ Full |
| | buffered | ❌ No | ⚠️ Basic |
| **Access Control** | timeout_configured | ✅ Yes | ✅ Full |
| | source_filtering | ❌ No | ❌ Missing |

**Parsing Patterns:**
- `hostname \S+` - Device hostname
- `transport input (ssh|telnet)` - Remote access protocols
- `ip ssh version \d+` - SSH version
- `ip http server` / `ip http secure-server` - Web management
- `login local` - Local authentication
- `service password-encryption` - Password encryption
- `enable secret` - Privileged mode password
- `logging \d+\.\d+\.\d+\.\d+` - Syslog server
- `exec-timeout` - Session timeout

**Known Limitations:**
1. **Device Type Detection:** Hardcoded as "router" - doesn't differentiate switch/router/firewall
2. **IOS-XR Support:** Parser targets IOS/IOS-XE - IOS-XR has different syntax
3. **SNMP Coverage:** Only detects `snmp-server community` - missing v3, ACL restrictions
4. **Source Filtering:** ACLs not parsed (e.g., `access-list` statements)
5. **Buffered Logging:** Detection incomplete
6. **Version Parsing:** Only captures numeric version - missing platform info
7. **Transport Input Default:** When `transport input` absent, assumes unsafe defaults
8. **Context Awareness:** Doesn't handle hierarchical config blocks properly

**Test Coverage:**
- ✅ `cisco_ssh_compliant.cfg` - Positive test (SSH enabled, telnet disabled)
- ✅ `cisco_telnet_insecure.cfg` - Negative test (Telnet enabled)
- ❌ Missing: IOS-XR, Catalyst switches, Nexus, ASA firewall configs

---

### 1.2 Fortinet Parser (`fortinet_parser.py`)

**Status:** ✅ OPERATIONAL - Needs Hardening

**Detection Signatures:**
- `config system|firewall` (weight: 0.35)
- `edit \"?\w+\"?` (weight: 0.25)
- `set \w+` (weight: 0.20)
- `allowaccess` (weight: 0.20)
- Confidence threshold: 0.75

**Extracted Fields:**

| Security Domain | Field | Evidence Tracking | Coverage |
|----------------|-------|------------------|----------|
| **Device Info** | hostname | ✅ Yes | ✅ Full |
| | vendor | ✅ Yes | ✅ Full |
| | version | ❌ No | ❌ Missing |
| | device_type | ❌ No | ⚠️ Static ("firewall") |
| **Remote Access** | ssh_enabled | ✅ Yes | ✅ Full |
| | ssh_version | ✅ Yes | ⚠️ Assumed (2) |
| | telnet_enabled | ✅ Yes | ✅ Full |
| **Management** | http_enabled | ✅ Yes | ⚠️ Partial |
| | https_enabled | ✅ Yes | ✅ Full |
| | snmp_enabled | ✅ Yes | ⚠️ Basic |
| **Authentication** | local_authentication | ✅ Yes | ⚠️ Inferred |
| | password_encryption | ❌ No | ⚠️ N/A (auto) |
| | enable_secret_configured | ✅ Yes | ⚠️ Adapted |
| **Logging** | enabled | ✅ Yes | ⚠️ Simplified |
| | remote_server | ✅ Yes | ⚠️ Basic |
| | buffered | ❌ No | ⚠️ N/A (always) |
| **Access Control** | timeout_configured | ✅ Yes | ✅ Full |
| | source_filtering | ❌ No | ❌ Missing |

**Parsing Patterns:**
- `set hostname "?\S+"?` - Device hostname
- `set allowaccess ... ssh` - SSH enabled
- `set allowaccess ... telnet` - Telnet enabled
- `set allowaccess ... https?` - Web management
- `config system admin` - Local authentication
- `set password` - Admin password (treated as enable_secret)
- `config log syslogd setting` - Syslog configuration
- `set admin-timeout \d+` - Session timeout

**Known Limitations:**
1. **SSH Version:** Assumes SSHv2 if SSH enabled - doesn't verify config
2. **HTTP Detection:** Regex `\bhttp\b(?!s)` may miss edge cases
3. **Password Encryption:** N/A for FortiGate (auto-encrypted) - field left None
4. **Logging Simplified:** Doesn't parse full `config log` hierarchy
5. **Version Extraction:** Not implemented - requires `get system status` output
6. **Interface Aggregation:** Parses all `allowaccess` lines but may miss interface-specific restrictions
7. **Multi-VDOM:** Doesn't handle Virtual Domain contexts
8. **Policy-Based Management:** Doesn't parse admin access policies

**Test Coverage:**
- ❌ Missing: FortiGate positive/negative test configs
- ❌ Missing: Multi-VDOM scenarios
- ❌ Missing: FortiOS 6.x vs 7.x syntax variations

---

### 1.3 Unknown Parser (`unknown_parser.py`)

**Status:** ✅ OPERATIONAL - AI-Based Fallback

**Detection:** Always returns `can_parse() = True` (last resort)

**Strategy:**
1. **Learned Mappings:** Check database for previously validated rules
2. **Heuristic Patterns:** Fast keyword matching (telnet, ssh, http, etc.)
3. **AI Interpretation:** `interpret_unknown_config()` for unrecognized lines
4. **Conservative Defaults:** Assume unsafe when uncertain

**Heuristic Patterns:**
- `telnet` + `enable|allow` → telnet_enabled = True
- `ssh` + `enable|allow|only` → ssh_enabled = True
- `ssh version 2|v2` → ssh_version = 2
- `http` + `enable` → http_enabled = True
- `https` + `enable` → https_enabled = True
- `snmp` + `enable|community` → snmp_enabled = True
- `password` + `encrypt|hash` → password_encryption = True
- `syslog|logging` + `enable` → logging.enabled = True
- `timeout|session-timeout` → timeout_configured = True

**AI Integration:**
- Uses `app/adaptive/` module (sentence-transformers)
- Generates candidate mappings with confidence scores
- Stores pending mappings for human validation
- Tracks interpretation rate (interpreted_lines / total_lines)

**Conservative Defaults (Unsafe Assumptions):**
- `ssh_enabled = True` (assume enabled)
- `telnet_enabled = True` (assume unsafe)
- `http_enabled = True` (assume unsafe)
- `password_encryption = False` (assume weak)
- `logging.enabled = False` (assume disabled)

**Known Limitations:**
1. **Low Precision:** Heuristics produce false positives
2. **AI Dependency:** Requires sentence-transformers model (optional)
3. **No Vendor Context:** Can't leverage vendor-specific semantics
4. **Pending Mapping Backlog:** Human-in-loop workflow not fully implemented
5. **Evidence Quality:** Line-level evidence but may miss context

**Test Coverage:**
- ⚠️ Tested implicitly via unknown configs
- ❌ Missing: Dedicated test suite for unknown vendors

---

## 2. UnifiedSecurityModel Field Coverage

### 2.1 Current Schema (`normalization/schema.py`)

**Architecture:** Pydantic models with evidence tracking

```
UnifiedSecurityModel
├── device: DeviceInfo
│   ├── hostname (Optional[str])
│   ├── vendor (str)
│   ├── device_type (Optional[str])
│   ├── version (Optional[str])
│   └── evidence (Optional[Evidence])
├── remote_access: RemoteAccess
│   ├── ssh_enabled (Optional[bool])
│   ├── ssh_version (Optional[int])
│   ├── telnet_enabled (Optional[bool])
│   └── [3x evidence fields]
├── management: ManagementProtocols
│   ├── http_enabled (Optional[bool])
│   ├── https_enabled (Optional[bool])
│   ├── snmp_enabled (Optional[bool])
│   └── [3x evidence fields]
├── authentication: Authentication
│   ├── local_authentication (Optional[bool])
│   ├── password_encryption (Optional[bool])
│   ├── enable_secret_configured (Optional[bool])
│   └── [3x evidence fields]
├── logging: Logging
│   ├── enabled (Optional[bool])
│   ├── remote_server (Optional[str])
│   ├── buffered (Optional[bool])
│   └── [1x evidence field]
├── access_control: AccessControl
│   ├── source_filtering (Optional[bool])
│   ├── timeout_configured (Optional[bool])
│   └── [2x evidence fields]
└── metadata
    ├── raw_config_hash (Optional[str])
    └── normalized_at (Optional[str])
```

**Total Fields:**
- Security fields: 17
- Evidence fields: 12
- Metadata fields: 2
- **Total: 31 fields**

### 2.2 Field Population by Parser

| Field | Cisco | Fortinet | Unknown | Notes |
|-------|-------|----------|---------|-------|
| **device.hostname** | ✅ | ✅ | ❌ | Unknown uses None |
| **device.vendor** | ✅ | ✅ | ✅ | All parsers |
| **device.device_type** | ⚠️ | ⚠️ | ⚠️ | Static values |
| **device.version** | ⚠️ | ❌ | ❌ | Cisco only (partial) |
| **remote_access.ssh_enabled** | ✅ | ✅ | ⚠️ | Unknown: heuristic |
| **remote_access.ssh_version** | ✅ | ⚠️ | ⚠️ | Fortinet: assumed |
| **remote_access.telnet_enabled** | ✅ | ✅ | ⚠️ | Unknown: heuristic |
| **management.http_enabled** | ✅ | ⚠️ | ⚠️ | Fortinet: regex issue |
| **management.https_enabled** | ✅ | ✅ | ⚠️ | Unknown: heuristic |
| **management.snmp_enabled** | ⚠️ | ⚠️ | ⚠️ | All: basic detection |
| **authentication.local_authentication** | ✅ | ⚠️ | ⚠️ | Fortinet: inferred |
| **authentication.password_encryption** | ✅ | ❌ | ⚠️ | Fortinet: N/A |
| **authentication.enable_secret_configured** | ✅ | ⚠️ | ⚠️ | Fortinet: adapted |
| **logging.enabled** | ✅ | ⚠️ | ⚠️ | All: simplified |
| **logging.remote_server** | ✅ | ⚠️ | ❌ | Unknown: no IP extraction |
| **logging.buffered** | ⚠️ | ❌ | ❌ | Minimal coverage |
| **access_control.source_filtering** | ❌ | ❌ | ❌ | **NOT IMPLEMENTED** |
| **access_control.timeout_configured** | ✅ | ✅ | ⚠️ | Unknown: heuristic |

**Coverage Summary:**
- ✅ Full Coverage: 8 fields (47%)
- ⚠️ Partial Coverage: 8 fields (47%)
- ❌ No Coverage: 1 field (6%)

### 2.3 Missing Capabilities

**Critical Gaps:**
1. **Source Filtering:** ACLs, firewall policies, trusted sources not parsed
2. **Device Type Detection:** Static values instead of runtime detection
3. **Version Parsing:** Incomplete across vendors
4. **SNMP Security:** v2c vs v3, community ACLs not extracted
5. **Buffered Logging:** Inconsistent detection

**Vendor-Specific Fields Not Captured:**
- Cisco: AAA configuration, VTY ACLs, exec timeout values
- Fortinet: Admin profiles, access policies, VDOM isolation
- Palo Alto: Zone-based policies (not yet parsed)
- Juniper: Firewall filters, login classes (not yet parsed)

---

## 3. Compliance Framework Support

### 3.1 Current Rules (`compliance/rules.yaml`)

**Total Rules:** 10  
**Frameworks Referenced:** CIS Benchmark, NIST 800-53  
**Rule Distribution:**

| Category | Count | Severity Breakdown |
|----------|-------|-------------------|
| Remote Access | 3 | HIGH: 2, MEDIUM: 1 |
| Management | 2 | HIGH: 1, MEDIUM: 1 |
| Authentication | 3 | HIGH: 1, MEDIUM: 1, LOW: 1 |
| Logging | 1 | MEDIUM: 1 |
| Access Control | 1 | LOW: 1 |

**Framework Coverage:**

| Rule ID | Field | CIS | NIST | STIG | ISO |
|---------|-------|-----|------|------|-----|
| NET-001 | telnet_enabled | ✅ | ✅ SC-8 | ❌ | ❌ |
| NET-002 | ssh_enabled | ✅ | ❌ | ❌ | ❌ |
| NET-003 | ssh_version | ✅ | ❌ | ❌ | ❌ |
| NET-004 | http_enabled | ✅ | ❌ | ❌ | ❌ |
| NET-005 | https_enabled | ✅ | ❌ | ❌ | ❌ |
| NET-006 | local_authentication | ✅ | ❌ | ❌ | ❌ |
| NET-007 | enable_secret_configured | ✅ | ❌ | ❌ | ❌ |
| NET-008 | password_encryption | ✅ | ❌ | ❌ | ❌ |
| NET-009 | logging.enabled | ✅ | ❌ | ❌ | ❌ |
| NET-010 | timeout_configured | ✅ | ❌ | ❌ | ❌ |

**Observations:**
- CIS Benchmark: 10/10 rules reference CIS (generic)
- NIST 800-53: 1/10 rules reference specific control (SC-8)
- STIG: 0/10 rules mapped
- ISO 27001: 0/10 rules mapped

**Limitation:** Rules reference frameworks by name but don't include:
- Specific control IDs (e.g., CIS v8 4.3.1)
- STIG Rule IDs (e.g., SRG-NET-000019)
- ISO 27001 control numbers (e.g., A.9.4.1)

---

## 4. Vendor Detection Engine

### 4.1 Current Detection (`detection/vendor_detector.py`)

**Supported Vendors:** Cisco, Fortinet, AWS, Unknown

**Detection Algorithm:**
1. Pattern matching with weighted signatures
2. Score aggregation per vendor
3. Confidence threshold: 0.75
4. Highest score wins (if >= threshold)
5. Falls back to "Unknown" if below threshold

**Signature Weights:**

**Cisco (7 signatures, max score: 1.0+):**
- `version \d+\.\d+` (0.30)
- `interface GigabitEthernet` (0.25)
- `line vty` (0.25)
- `router ospf|eigrp` (0.20)
- `ip route|ssh` (0.15)
- `transport input` (0.15)
- `enable secret` (0.15)

**Fortinet (9 signatures, max score: 1.0+):**
- `config system|firewall` (0.35)
- `edit "?\w+"?` (0.25)
- `set \w+` (0.20)
- `allowaccess` (0.20)
- `next` (0.15)

**AWS (6 signatures, max score: 1.0+):**
- `"GroupId":` (0.40)
- `"IpPermissions":` (0.30)
- `"SecurityGroups":` (0.30)
- `"VpcId":` (0.20)

**Performance:** ✅ Fast (regex-based, deterministic)

**Limitations:**
1. **No Palo Alto Signatures:** Will classify as Unknown
2. **No Juniper Signatures:** Will classify as Unknown
3. **IOS-XR vs IOS:** Can't differentiate Cisco variants
4. **Palo Alto XML vs Set:** Multiple config formats not handled
5. **Vendor Confidence:** Binary decision (>= 0.75 or Unknown)

---

## 5. New Vendor Research: Palo Alto Networks

### 5.1 Config Format Overview

**Platform:** PAN-OS (Palo Alto Networks Operating System)  
**Device Types:** Next-Generation Firewalls (PA-Series, VM-Series)  
**Config Formats:**

1. **Set Format** (CLI-style):
   ```
   set mgt-config users admin phash <hash>
   set zone L3-Trust network layer3 ethernet1/3
   set rulebase security rules rule1 action allow
   ```

2. **XML Format** (API export):
   ```xml
   <config>
     <mgt-config>
       <users>
         <entry name="admin">
           <phash>hash</phash>
         </entry>
       </users>
     </mgt-config>
   </config>
   ```

**Primary Focus:** Set format (CLI) - more common for audits

### 5.2 Key Security Settings

**Management Access:**
```
set deviceconfig system service disable-telnet yes
set deviceconfig system service disable-http yes
set deviceconfig system ssh-cipher-list <cipher-list>
```

**Administrative Users:**
```
set mgt-config users <username> phash <password-hash>
set mgt-config users <username> permissions role-based <role>
```

**Session Timeout:**
```
set deviceconfig system idle-timeout <minutes>
```

**Logging:**
```
set deviceconfig system server <server-name> address <ip>
set deviceconfig system server <server-name> protocol <udp|tcp>
set shared log-settings syslog <profile-name> server <server-name>
```

**Zone-Based Security:**
```
set zone <zone-name> network layer3 <interface>
set rulebase security rules <rule-name> from <zone>
set rulebase security rules <rule-name> to <zone>
set rulebase security rules <rule-name> action <allow|deny>
```

**SNMP:**
```
set deviceconfig system snmp-setting access-setting version v2c
set deviceconfig system snmp-setting snmp-system location <location>
```

### 5.3 Detection Signatures (Proposed)

**High Confidence (weight >= 0.25):**
- `set deviceconfig system` (0.30)
- `set mgt-config` (0.30)
- `set rulebase security` (0.25)
- `set zone .* network layer3` (0.25)

**Medium Confidence (weight 0.10-0.24):**
- `set shared log-settings` (0.20)
- `set network interface` (0.15)
- `phash` (0.15) - PAN-OS password hash
- `role-based superuser` (0.10)

**Minimum Score for Detection:** 0.75

### 5.4 Mapping to UnifiedSecurityModel

| UnifiedSecurityModel Field | PAN-OS Config Pattern | Notes |
|---------------------------|----------------------|-------|
| **device.hostname** | `set deviceconfig system hostname <name>` | Direct mapping |
| **device.vendor** | Detected → "Palo Alto" | Constant |
| **device.device_type** | Static: "firewall" | Could parse from model |
| **device.version** | `set deviceconfig system sw-version` | If present |
| **remote_access.ssh_enabled** | Absence of `disable-ssh yes` | Default enabled |
| **remote_access.telnet_enabled** | `disable-telnet yes` | Inverted logic |
| **remote_access.ssh_version** | Parse `ssh-cipher-list` | Infer from ciphers |
| **management.http_enabled** | `disable-http yes` | Inverted logic |
| **management.https_enabled** | Default enabled | Always available |
| **management.snmp_enabled** | `set deviceconfig system snmp-setting` | Presence check |
| **authentication.local_authentication** | `set mgt-config users` | Presence check |
| **authentication.password_encryption** | N/A | Always hashed (phash) |
| **authentication.enable_secret_configured** | `phash` present | Adapted concept |
| **logging.enabled** | `set shared log-settings syslog` | Presence check |
| **logging.remote_server** | `server <name> address <ip>` | Extract IP |
| **access_control.timeout_configured** | `idle-timeout <minutes>` | Direct mapping |
| **access_control.source_filtering** | `set rulebase security rules` | Parse rules |

**Challenges:**
1. **Inverted Logic:** `disable-telnet yes` means telnet_enabled = False
2. **Hierarchical Refs:** Rules reference zones/profiles defined elsewhere
3. **Multiple Formats:** Must support both set and XML formats
4. **Zone Complexity:** Security policies are zone-based (new concept)
5. **SSH Version:** Not explicit - must infer from cipher list

---

## 6. New Vendor Research: Juniper Networks

### 6.1 Config Format Overview

**Platform:** Junos OS (Juniper Networks Operating System)  
**Device Types:** Routers (MX-Series), Switches (EX-Series), Firewalls (SRX-Series)  
**Config Format:** Hierarchical, curly-brace syntax

**Example:**
```
system {
    host-name CORE-ROUTER;
    root-authentication {
        encrypted-password "$1$hash$...";
    }
    services {
        ssh;
        telnet;
    }
}

interfaces {
    ge-0/0/0 {
        unit 0 {
            family inet {
                address 192.168.1.1/24;
            }
        }
    }
}

firewall {
    filter limit-mgmt-access {
        term block_non_manager {
            from {
                source-prefix-list {
                    manager-ip except;
                }
                protocol [ tcp ];
                destination-port [ ssh telnet ];
            }
            then {
                discard;
                log;
            }
        }
        term accept_everything_else {
            then accept;
        }
    }
}
```

**Command to View:** `show configuration | display set` (flattened format)

**Flattened Format:**
```
set system host-name CORE-ROUTER
set system root-authentication encrypted-password "$1$hash$..."
set system services ssh
set system services telnet
set interfaces ge-0/0/0 unit 0 family inet address 192.168.1.1/24
set firewall filter limit-mgmt-access term block_non_manager from protocol tcp
```

### 6.2 Key Security Settings

**Management Access:**
```
system {
    services {
        ssh;                           # SSH enabled
        telnet;                        # Telnet enabled (insecure)
        web-management {
            http;                      # HTTP enabled
            https {
                system-generated-certificate;
            }
        }
    }
}
```

**SSH Configuration:**
```
system {
    services {
        ssh {
            protocol-version v2;       # SSHv2 only
            ciphers [ aes256-cbc ];
        }
    }
}
```

**Authentication:**
```
system {
    root-authentication {
        encrypted-password "$1$...";
    }
    login {
        user admin {
            uid 2000;
            class super-user;
            authentication {
                encrypted-password "$6$...";
            }
        }
    }
}
```

**Logging:**
```
system {
    syslog {
        host 10.10.10.10 {
            any any;
            facility-override local7;
        }
        file messages {
            any any;
        }
    }
}
```

**Access Control (Firewall Filters):**
```
firewall {
    filter limit-mgmt-access {
        term block_telnet {
            from {
                protocol tcp;
                destination-port telnet;
            }
            then {
                reject;
            }
        }
    }
}

interfaces {
    lo0 {
        unit 0 {
            family inet {
                filter {
                    input limit-mgmt-access;
                }
            }
        }
    }
}
```

**Session Timeout:**
```
system {
    login {
        idle-timeout 10;               # Minutes
        authentication {
            no-challenge-response;
        }
    }
}
```

**SNMP:**
```
snmp {
    community public {
        authorization read-only;
    }
    trap-group all-traps {
        targets {
            10.10.10.10;
        }
    }
}
```

### 6.3 Detection Signatures (Proposed)

**High Confidence (weight >= 0.25):**
- `system \{` (0.30)
- `set system host-name` (0.30)
- `interfaces \{` (0.25)
- `firewall \{` (0.25)
- `set interfaces [a-z]{2}-\d+/\d+/\d+` (0.25) - Juniper interface naming

**Medium Confidence (weight 0.10-0.24):**
- `protocols \{` (0.20)
- `routing-options \{` (0.20)
- `encrypted-password "\$` (0.15) - Juniper password format
- `class super-user` (0.15)
- `family inet \{` (0.10)

**Low Confidence (weight < 0.10):**
- `unit \d+` (0.05)
- `apply-groups` (0.05)

**Minimum Score for Detection:** 0.75

### 6.4 Mapping to UnifiedSecurityModel

| UnifiedSecurityModel Field | Junos Config Pattern | Notes |
|---------------------------|---------------------|-------|
| **device.hostname** | `system { host-name <name>; }` | Direct mapping |
| **device.vendor** | Detected → "Juniper" | Constant |
| **device.device_type** | Infer from model/interface | ge- = router, xe- = switch |
| **device.version** | Parse from `show version` | Not in config |
| **remote_access.ssh_enabled** | `system services ssh` | Presence check |
| **remote_access.ssh_version** | `ssh { protocol-version v2; }` | Parse version |
| **remote_access.telnet_enabled** | `system services telnet` | Presence check |
| **management.http_enabled** | `web-management { http; }` | Presence check |
| **management.https_enabled** | `web-management { https }` | Presence check |
| **management.snmp_enabled** | `snmp { community }` | Presence check |
| **authentication.local_authentication** | `login { user }` | Presence check |
| **authentication.password_encryption** | N/A | Always encrypted |
| **authentication.enable_secret_configured** | `root-authentication` | Adapted concept |
| **logging.enabled** | `syslog { host }` | Presence check |
| **logging.remote_server** | `syslog { host <ip> }` | Extract IP |
| **logging.buffered** | `syslog { file }` | Presence check |
| **access_control.timeout_configured** | `login { idle-timeout }` | Direct mapping |
| **access_control.source_filtering** | `firewall { filter }` | Parse filters |

**Challenges:**
1. **Hierarchical Parsing:** Curly braces create nested contexts
2. **Flattened vs Hierarchical:** Must support both formats
3. **Service Presence = Enabled:** Unlike Cisco's explicit enable/disable
4. **Firewall Filters:** Complex ACL-like structures on interfaces
5. **Device Type Inference:** Interface naming patterns (ge-, xe-, fxp-)
6. **Version Not in Config:** Requires operational command output

---

## 7. Parser Gaps & Hardening Requirements

### 7.1 Cisco Parser Hardening

**Priority 1 (Critical):**
1. **Device Type Detection:**
   - Parse `version` output for platform info (Catalyst, ASR, ISR)
   - Interface naming: FastEthernet = old, GigabitEthernet = router/switch
   - Presence of `vlan database` → switch
   
2. **IOS-XR Support:**
   - Different syntax: `telnet ipv4 server` vs `transport input telnet`
   - Hierarchical config with indentation (not flat like IOS)
   - Pattern: `ssh server v2` vs `ip ssh version 2`

3. **Source Filtering (ACLs):**
   - Parse `access-list` statements
   - Check `line vty` for `access-class` restrictions
   - Populate `access_control.source_filtering`

4. **Enhanced SNMP:**
   - Parse SNMP version (v2c vs v3)
   - Check for `snmp-server community <string> ro` (read-only)
   - Extract access-list restrictions

5. **Transport Input Defaults:**
   - When `transport input` absent, check global `transport preferred`
   - Better heuristics for implicit defaults

**Priority 2 (Important):**
6. **Buffered Logging:** Detect `logging buffered <level>`
7. **Version Parsing:** Extract platform (e.g., "IOS-XE 16.9.3")
8. **AAA Configuration:** Parse `aaa authentication login` for centralized auth
9. **VTY Timeout Values:** Extract actual timeout numbers (not just presence)
10. **Context-Aware Parsing:** Track hierarchical blocks (line vty 0 4, interface, etc.)

**Priority 3 (Nice-to-Have):**
11. **Crypto Map Detection:** SSH key strength, SSL cert validation
12. **BGP/OSPF Auth:** Routing protocol authentication settings
13. **NTP Authentication:** Time sync security

### 7.2 Fortinet Parser Hardening

**Priority 1 (Critical):**
1. **Version Extraction:**
   - Parse `get system status` output (if included in file)
   - Look for `# config-version=` comments
   
2. **SSH Version Verification:**
   - Don't assume SSHv2 - check `config system global` for `ssh-enc-algo`
   - If modern ciphers (aes256-cbc), infer SSHv2

3. **HTTP Regex Fix:**
   - Current: `\bhttp\b(?!s)` may fail on edge cases
   - Better: Separate parsing for `http` and `https` in allowaccess

4. **Multi-VDOM Support:**
   - Detect `config global` vs `config vdom`
   - Parse each VDOM separately
   - Aggregate findings by VDOM

5. **Source Filtering (Admin Policies):**
   - Parse `config system admin` → `set trusthost1` (trusted IPs)
   - Parse firewall policies for management zone restrictions

**Priority 2 (Important):**
6. **Full Logging Hierarchy:** Parse `config log` blocks completely
7. **Admin Profiles:** Extract permission levels beyond superuser
8. **Password Complexity:** Parse `config system global` → `admin-password-policy`
9. **Certificate-Based Auth:** Detect PKI authentication for admins

**Priority 3 (Nice-to-Have):**
10. **HA Configuration:** Parse high-availability settings
11. **VPN Settings:** IPSec/SSL VPN security configs
12. **Antivirus/IPS Profiles:** Parse security profiles

### 7.3 Unknown Parser Improvements

**Priority 1 (Critical):**
1. **Vendor Hint Detection:**
   - Analyze config for vendor-specific keywords (PAN-OS, JunOS)
   - Suggest "Run vendor detection again" if strong hints found

2. **IP Address Extraction:**
   - Regex for IPv4 in logging lines
   - Populate `logging.remote_server`

3. **Confidence Scoring:**
   - Add interpretation confidence to findings
   - Flag low-confidence findings for human review

**Priority 2 (Important):**
4. **Learned Mapping Database:** Implement storage/retrieval fully
5. **Batch Learning:** Apply approved mappings retroactively
6. **Vendor Migration:** Auto-suggest known vendor parser if learned mappings cluster

### 7.4 New Parser Requirements

**Palo Alto Parser:**
1. Support both set and XML formats
2. Handle inverted logic (disable-* flags)
3. Parse zone-based security rules
4. Extract cipher lists to infer SSH version
5. Parse logging server configurations
6. Detect idle-timeout settings

**Juniper Parser:**
1. Parse hierarchical (curly-brace) format
2. Support flattened (`display set`) format
3. Detect device type from interface naming
4. Parse firewall filters (ACL equivalent)
5. Extract syslog host configurations
6. Handle `encrypted-password` hashes
7. Parse login idle-timeout
8. Detect service presence (ssh, telnet, web-management)

---

## 8. Test Coverage Gaps

### 8.1 Current Test Inventory

**Golden Test Configs:**
- ✅ `cisco_ssh_compliant.cfg` - Positive (Cisco)
- ✅ `cisco_telnet_insecure.cfg` - Negative (Cisco)
- ❌ **No Fortinet tests**
- ❌ **No Palo Alto tests**
- ❌ **No Juniper tests**
- ❌ **No Unknown vendor tests**

**Test Coverage:** 2/4 supported vendors (50%)

### 8.2 Required Test Configs

**Cisco:**
- ✅ SSH compliant (exists)
- ✅ Telnet insecure (exists)
- ❌ IOS-XR secure config
- ❌ Catalyst switch config
- ❌ ASR router config
- ❌ Config with ACLs
- ❌ Config with SNMP v3
- ❌ Config with AAA

**Fortinet:**
- ❌ FortiGate compliant config (SSH only, HTTPS, logging)
- ❌ FortiGate insecure config (Telnet, HTTP)
- ❌ Multi-VDOM config
- ❌ Config with admin trusthosts
- ❌ Config with admin profiles

**Palo Alto (New):**
- ❌ Compliant config (set format) - telnet disabled, SSH enabled
- ❌ Insecure config (set format) - telnet enabled, HTTP enabled
- ❌ Config with zone-based rules
- ❌ Config with logging servers
- ❌ XML format sample

**Juniper (New):**
- ❌ Compliant config (hierarchical) - telnet disabled, SSH v2
- ❌ Insecure config (hierarchical) - telnet enabled
- ❌ Flattened format config (`display set`)
- ❌ Config with firewall filters
- ❌ Config with syslog hosts

**Unknown Vendor:**
- ❌ Generic secure config (for heuristic testing)
- ❌ Generic insecure config (for heuristic testing)
- ❌ Config with learned mappings

**Target:** 20+ configs per vendor × 4 vendors = 80+ test configs

---

## 9. Vendor-Agnostic Architecture Validation

### 9.1 UnifiedSecurityModel Sufficiency

**Question:** Can the current UnifiedSecurityModel represent all vendor concepts?

**Analysis:**

| Vendor Concept | Current Model | Status | Action |
|----------------|---------------|--------|--------|
| **Cisco VTY ACLs** | `access_control.source_filtering` | ⚠️ Boolean | Extend |
| **Fortinet VDOMs** | N/A | ❌ Missing | Add metadata |
| **Palo Alto Zones** | N/A | ❌ Missing | Add domain |
| **Juniper Filters** | `access_control.source_filtering` | ⚠️ Boolean | Extend |
| **SNMP Versions** | `management.snmp_enabled` | ⚠️ Boolean | Add version field |
| **Logging Levels** | N/A | ❌ Missing | Add logging.level |
| **Auth Mechanisms** | `authentication.local_authentication` | ⚠️ Boolean | Add type field |
| **Session Timeout Values** | `access_control.timeout_configured` | ⚠️ Boolean | Add timeout_minutes |

**Recommendations:**

**Phase 1 Immediate:**
1. Keep current schema UNCHANGED (preserve Phase 0 compatibility)
2. Use evidence.text to capture additional details
3. Store vendor-specific metadata in parser-private fields

**Phase 1 Optional (if time permits):**
4. Add `snmp_version` field (v2c, v3)
5. Add `timeout_minutes` field (integer)
6. Add `device._vendor_context` (dict for vendor-specific data)

**Phase 2 (Multi-Framework):**
7. Extend schema with framework-specific fields
8. Add `authentication.method` (local, radius, tacacs+, ldap)
9. Add `logging.level` (emergency, alert, critical, etc.)
10. Add `access_control.acl_count` (number of ACL entries)

### 9.2 Evidence Tracking Sufficiency

**Current:** Single evidence per field (file, line, text)

**Scenarios:**

1. **Multiple Matches:**
   - Fortinet: Multiple `set allowaccess` lines across interfaces
   - **Current:** Store first occurrence only
   - **Improvement:** Store array of evidence

2. **Inferred Values:**
   - Fortinet: SSH version assumed if SSH enabled
   - **Current:** Use same evidence as ssh_enabled
   - **Improvement:** Mark as inferred in evidence

3. **Negative Evidence:**
   - Config lacks `no ip telnet` → telnet_enabled = None (unknown)
   - **Current:** No evidence stored
   - **Improvement:** Store "absence evidence"

**Recommendation:** Keep single-evidence model for Phase 1 (KISS principle)

---

## 10. Implementation Roadmap

### 10.1 Phase 1 Scope Definition

**IN SCOPE:**
1. ✅ Palo Alto parser (set format)
2. ✅ Juniper parser (hierarchical + flattened)
3. ✅ Enhanced Cisco parser (IOS-XR, ACLs, device type)
4. ✅ Enhanced Fortinet parser (VDOM, version, SSH verification)
5. ✅ Enhanced vendor detection (add PAN-OS, JunOS signatures)
6. ✅ Golden test dataset expansion (20+ configs per vendor)
7. ✅ UnifiedSecurityModel validation (no breaking changes)
8. ✅ Regression testing (Phase 0 audits must still pass)

**OUT OF SCOPE (Deferred to Phase 2/3):**
1. ❌ Schema extensions (snmp_version, timeout_minutes, etc.)
2. ❌ Multi-framework control mapping (STIG, ISO)
3. ❌ Human-in-loop learning workflow enhancements
4. ❌ Multi-VDOM/multi-context full support
5. ❌ XML format for Palo Alto (set format only)
6. ❌ Operational command output parsing (show version, etc.)

### 10.2 Implementation Phases

**Week 1: Research & Planning (COMPLETE)**
- ✅ Current state analysis
- ✅ Vendor research (Palo Alto, Juniper)
- ✅ Gap identification
- ✅ Baseline documentation (this document)

**Week 2: Vendor Detection Enhancement**
- Add Palo Alto signatures to `vendor_detector.py`
- Add Juniper signatures to `vendor_detector.py`
- Test detection with sample configs
- Update confidence thresholds if needed

**Week 3: Palo Alto Parser**
- Create `palo_alto_parser.py`
- Implement `can_parse()` with PAN-OS patterns
- Implement `parse()` for set format
- Map to UnifiedSecurityModel
- Handle inverted logic (disable-* flags)
- Write unit tests

**Week 4: Juniper Parser**
- Create `juniper_parser.py`
- Implement hierarchical config parser
- Implement flattened format support
- Map to UnifiedSecurityModel
- Parse firewall filters for source_filtering
- Write unit tests

**Week 5: Cisco Parser Hardening**
- Add IOS-XR pattern detection
- Implement device type detection
- Parse ACLs for source_filtering
- Enhanced SNMP parsing (v2c vs v3)
- Improve buffered logging detection
- Update unit tests

**Week 6: Fortinet Parser Hardening**
- Add version extraction logic
- Implement SSH version verification
- Fix HTTP regex edge cases
- Add basic VDOM awareness
- Parse admin trusthost restrictions
- Update unit tests

**Week 7: Test Dataset Creation**
- Create 5+ Cisco test configs (compliant + insecure)
- Create 5+ Fortinet test configs
- Create 5+ Palo Alto test configs
- Create 5+ Juniper test configs
- Create 2+ Unknown vendor configs
- Document test case expectations

**Week 8: Integration & Regression Testing**
- Run all Phase 0 tests (must pass)
- Run new vendor tests
- Test vendor detection accuracy
- Test UnifiedSecurityModel field population
- Test compliance rule evaluation
- Fix bugs and edge cases

**Week 9: Documentation & Completion**
- Update parser documentation
- Create Phase 1 completion report
- Document known limitations
- Create Phase 2 handoff document
- Code review and cleanup

### 10.3 Success Criteria

**Functional:**
1. ✅ 4 production-grade parsers (Cisco, Fortinet, Palo Alto, Juniper)
2. ✅ Vendor detection accuracy >= 95% for known vendors
3. ✅ UnifiedSecurityModel field coverage >= 80% for each vendor
4. ✅ 20+ test configs per vendor (80+ total)
5. ✅ Phase 0 regression tests: 100% pass rate
6. ✅ New vendor tests: >= 90% pass rate

**Non-Functional:**
1. ✅ No breaking changes to UnifiedSecurityModel
2. ✅ No breaking changes to compliance rules
3. ✅ No breaking changes to API contracts
4. ✅ Parser performance: < 500ms per config
5. ✅ Evidence tracking maintained for all fields
6. ✅ Code coverage: >= 70% for new parsers

**Documentation:**
1. ✅ Phase 1 baseline document (this document)
2. ✅ Phase 1 implementation plan (separate doc)
3. ✅ Parser development guide (per-vendor)
4. ✅ Test case documentation (expected results)
5. ✅ Phase 1 completion report (at end)

---

## 11. Risk Analysis

### 11.1 Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|------------|-----------|
| **Parser Regex Complexity** | HIGH | MEDIUM | Incremental testing, golden datasets |
| **UnifiedSecurityModel Insufficient** | HIGH | LOW | Evidence.text escape hatch, Phase 2 extension |
| **Vendor Config Variations** | MEDIUM | HIGH | Multiple test cases per vendor, graceful degradation |
| **Performance Degradation** | MEDIUM | LOW | Benchmark tests, optimize hot paths |
| **Evidence Tracking Breaks** | HIGH | LOW | Extensive regression testing |
| **IOS-XR Syntax Mismatch** | MEDIUM | MEDIUM | Separate detection, conditional parsing |
| **Palo Alto XML Complexity** | MEDIUM | LOW | Defer XML to Phase 2, focus on set format |
| **Juniper Hierarchical Parsing** | HIGH | MEDIUM | Tokenizer/state machine, test with real configs |

### 11.2 Project Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|------------|-----------|
| **Scope Creep (Schema Changes)** | HIGH | MEDIUM | Strict scope enforcement, defer to Phase 2 |
| **Insufficient Test Configs** | MEDIUM | MEDIUM | Request vendor configs early, generate if needed |
| **Phase 0 Regression** | HIGH | LOW | CI/CD with Phase 0 test suite, frequent testing |
| **Timeline Overrun** | MEDIUM | MEDIUM | 9-week buffer, prioritize critical features |
| **Vendor Documentation Gaps** | LOW | HIGH | Rely on real configs, reverse engineer if needed |

### 11.3 Mitigation Strategies

**1. Incremental Development:**
- Implement one vendor at a time
- Test after each vendor completion
- Don't proceed until tests pass

**2. Regression Testing:**
- Run Phase 0 tests before starting Phase 1
- Run Phase 0 tests after each vendor addition
- Automated test suite in CI/CD

**3. Vendor Config Library:**
- Request sample configs from users
- Generate synthetic configs based on vendor docs
- Maintain diverse test cases (IOS vs IOS-XR, FortiOS 6 vs 7)

**4. Graceful Degradation:**
- Unknown Parser catches all unsupported vendors
- Parsers return partial results if some fields fail
- Evidence tracking enables manual review

**5. Documentation-Driven:**
- Document expected behavior before coding
- Create test cases before parsers
- Update docs as implementation evolves

---

## 12. Dependencies & Prerequisites

### 12.1 External Dependencies

**Python Libraries:**
- ✅ `pydantic` - Schema validation (already installed)
- ✅ `PyYAML` - Compliance rules (already installed)
- ✅ `re` - Regex parsing (stdlib)
- ⚠️ `lxml` - XML parsing for Palo Alto (optional, Phase 2)
- ⚠️ `pyparsing` - Hierarchical parsing for Juniper (optional, alternative to regex)

**Data:**
- ❌ Palo Alto sample configs (need 5+)
- ❌ Juniper sample configs (need 5+)
- ⚠️ Enhanced Cisco configs (IOS-XR, ACLs)
- ⚠️ Enhanced Fortinet configs (VDOM, v7)

### 12.2 Knowledge Prerequisites

**Team Knowledge Required:**
1. Palo Alto PAN-OS CLI syntax
2. Juniper JunOS configuration hierarchy
3. Cisco IOS-XR differences from IOS
4. Fortinet FortiOS version differences
5. Regex pattern matching (advanced)
6. Pydantic schema design

### 12.3 Infrastructure

**Development:**
- ✅ Python 3.11+ environment
- ✅ SQLite database (Phase 0)
- ✅ pytest testing framework
- ✅ Git version control

**Testing:**
- ❌ Vendor config repository (to be created)
- ❌ CI/CD pipeline (optional)
- ⚠️ Performance benchmarking tools

---

## 13. Phase 0 Compatibility Matrix

### 13.1 Preserved Components

**MUST NOT CHANGE:**
- ✅ `UnifiedSecurityModel` schema (fields, types, structure)
- ✅ `Evidence` schema
- ✅ `BaseParser` interface (`can_parse()`, `parse()`, `vendor_name()`)
- ✅ Compliance rule YAML structure
- ✅ API response formats (audit, findings, etc.)
- ✅ Database schema (Configuration, Audit, Finding tables)

**MAY EXTEND (Non-Breaking):**
- ✅ Add new parsers (Palo Alto, Juniper)
- ✅ Add vendor detection signatures
- ✅ Add parser helper methods
- ✅ Add optional schema fields (with defaults)
- ✅ Add new compliance rules (NET-011+)

**MAY MODIFY (With Care):**
- ⚠️ Existing parser logic (if fixes bugs without changing output schema)
- ⚠️ Vendor detection confidence thresholds (if improves accuracy)
- ⚠️ Evidence text formatting (if improves readability)

### 13.2 Regression Test Requirements

**Phase 0 Tests That MUST Pass:**
1. ✅ Cisco compliant config → 100% compliance
2. ✅ Cisco insecure config → 33.33% compliance (3/9 rules pass)
3. ✅ Vendor detection: Cisco → confidence >= 0.75
4. ✅ Vendor detection: Fortinet → confidence >= 0.75
5. ✅ UnifiedSecurityModel validation: All configs parse without errors
6. ✅ Evidence tracking: All findings have valid evidence
7. ✅ API /upload: Returns 201 with config ID
8. ✅ API /audit: Returns audit ID and findings

**Additional Regression Checks:**
1. ✅ Parser selection: Correct parser chosen for each vendor
2. ✅ Field population: No previously-populated fields become None
3. ✅ Compliance scoring: Same rules produce same results
4. ✅ Database writes: All entities persist correctly
5. ✅ SHA-256 hashing: File hashes consistent

---

## 14. Next Steps

### 14.1 Immediate Actions (Week 1)

**Done:**
1. ✅ Document current state (this document)
2. ✅ Research Palo Alto config format
3. ✅ Research Juniper config format
4. ✅ Identify parser gaps
5. ✅ Define Phase 1 scope

**Next:**
6. ⏭️ Create Phase 1 implementation plan document
7. ⏭️ Set up vendor config test directory structure
8. ⏭️ Request sample configs from users (if available)
9. ⏭️ Review and approve Phase 1 scope with stakeholders

### 14.2 Decision Points

**Decisions Needed:**
1. **XML Support for Palo Alto:** Include in Phase 1 or defer to Phase 2?
   - **Recommendation:** Defer to Phase 2 (set format sufficient for MVP)

2. **Multi-VDOM for Fortinet:** Full support or basic awareness?
   - **Recommendation:** Basic awareness (detect VDOM, warn user, parse global config)

3. **IOS-XR Priority:** Must-have or nice-to-have?
   - **Recommendation:** Must-have (common in enterprise, distinct syntax)

4. **Schema Extensions:** Add new fields or use evidence.text?
   - **Recommendation:** Use evidence.text for Phase 1, extend schema in Phase 2

5. **Test Config Source:** Real configs or synthetic?
   - **Recommendation:** Mix of both (prefer real if available, generate if needed)

### 14.3 Stakeholder Communication

**Phase 1 Kickoff:**
- Present baseline findings
- Review vendor priorities (Palo Alto vs Juniper first?)
- Confirm success criteria
- Align on timeline (9 weeks)

**Weekly Updates:**
- Parser completion status
- Test coverage progress
- Blocker identification
- Risk assessment updates

**Phase 1 Completion:**
- Demo all 4 vendors parsing correctly
- Show test coverage metrics
- Present Phase 1 completion report
- Handoff to Phase 2 planning

---

## 15. Glossary

**Terms:**

- **UnifiedSecurityModel:** Vendor-agnostic security representation (core innovation)
- **Evidence:** Source reference (file, line, text) for each security finding
- **Parser:** Vendor-specific configuration interpreter
- **Golden Test:** Known-good/known-bad config for validation
- **Vendor Detection:** Fingerprinting to identify config vendor
- **Compliance Rule:** Security policy evaluated against UnifiedSecurityModel
- **IOS-XR:** Cisco's carrier-grade OS (different syntax from IOS)
- **VDOM:** Virtual Domain (Fortinet's multi-tenancy feature)
- **PAN-OS:** Palo Alto Networks Operating System
- **JunOS:** Juniper Networks Operating System
- **Set Format:** CLI-style flat config (Palo Alto, Juniper)
- **Hierarchical Format:** Curly-brace nested config (Juniper)

**Acronyms:**

- **CIS:** Center for Internet Security
- **NIST:** National Institute of Standards and Technology
- **STIG:** Security Technical Implementation Guide
- **ISO:** International Organization for Standardization
- **ACL:** Access Control List
- **SNMP:** Simple Network Management Protocol
- **SSH:** Secure Shell
- **HTTPS:** HTTP Secure
- **AAA:** Authentication, Authorization, Accounting
- **VLAN:** Virtual Local Area Network
- **BGP:** Border Gateway Protocol
- **OSPF:** Open Shortest Path First

---

## 16. Document Metadata

**Document Control:**
- **Version:** 1.0
- **Date:** September 17, 2026
- **Author:** Vajra Core Team
- **Status:** Final - Approved for Phase 1 Implementation
- **Next Review:** Phase 1 Week 5 (mid-point check)

**Change History:**
- 2026-09-17: Initial creation (v1.0)

**Related Documents:**
- `docs/PHASE-0-SUMMARY.md` - Phase 0 completion summary
- `docs/phase-0/PHASE-0-COMPLETION-REPORT.md` - Phase 0 detailed report
- `docs/phase-0/baseline-test-results.md` - Phase 0 test results
- `docs/phase-1/phase-1-implementation-plan.md` - Phase 1 execution plan (to be created)

**Approval:**
- [ ] Technical Lead Review
- [ ] Architecture Review
- [ ] Stakeholder Sign-off

---

**END OF PHASE 1 BASELINE DOCUMENTATION**
