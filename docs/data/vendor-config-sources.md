# Vendor Configuration Sources Research

**Phase 0.5 Foundation - Real-World Configuration Data Strategy**

**Date**: September 16, 2026  
**Status**: Research Complete  
**Purpose**: Identify legitimate sources for real vendor configuration examples

---

## Executive Summary

This document identifies legitimate, legal sources for obtaining real-world network device configuration examples for testing and validation of Vajra Core parsers and compliance engines.

**Key Finding**: Public, vendor-provided configuration examples are limited. A hybrid strategy combining public examples, vendor documentation, and synthetic generation is required.

---

## Legal and Ethical Guidelines

### ✅ Acceptable Sources

1. **Vendor documentation** - Configuration examples from official docs
2. **Vendor-provided samples** - Example configs from vendor websites
3. **Public training materials** - Educational resources
4. **Open-source repositories** - Publicly shared configs (check licensing)
5. **Standardization bodies** - Sample configs from RFC/standards
6. **Our own synthetic generation** - Created configs for testing

### ❌ Unacceptable Sources

1. ❌ **Leaked configurations** - From data breaches or unauthorized sources
2. ❌ **Customer configurations** - Without explicit written permission
3. ❌ **Scraped configurations** - From private networks or unauthorized access
4. ❌ **Pastebin/GitHub leaks** - Even if publicly posted
5. ❌ **Vendor-confidential** - Internal-only documentation

---

## 1. Cisco

### Official Documentation Sources

**Cisco Configuration Guides**:
- URL: https://www.cisco.com/c/en/us/support/index.html
- Content: Configuration examples in official guides
- License: For reference and documentation purposes

**Cisco Learning Network**:
- URL: https://learningnetwork.cisco.com/
- Content: Lab exercises with sample configurations
- License: Educational use

**Cisco DevNet**:
- URL: https://developer.cisco.com/
- Content: API examples, automation samples
- License: DevNet terms of use

### Available Configuration Examples

**From Documentation**:
```
Location: IOS Configuration Guides
Example Topics:
- Basic router configuration
- Security hardening examples
- VPN configuration samples
- ACL examples
- Routing protocol configs
```

**Characteristics**:
- ✅ Legally obtained
- ✅ Vendor-approved
- ⚠️ Often simplified/minimal
- ⚠️ May not represent full enterprise configs

### GNS3/EVE-NG Lab Configs

**Community Labs**:
- Many public GNS3 labs include Cisco configs
- Check individual repository licenses
- Usually educational purpose

### CML (Cisco Modeling Labs)

**Official Lab Platform**:
- Includes sample topologies
- Requires subscription
- Educational/development license

### Recommendation

**For Phase 0.5**:
1. Extract examples from Cisco IOS Configuration Guides
2. Use CIS Benchmark example configurations
3. Reference DISA STIG example snippets
4. Create synthetic configurations based on real command syntax

**Synthetic Generation Strategy**:
- Study Cisco IOS command reference
- Build configuration templates
- Generate variations (secure, insecure, mixed)
- Validate syntax with Cisco documentation

---

## 2. Fortinet

### Official Documentation Sources

**Fortinet Documentation Library**:
- URL: https://docs.fortinet.com/
- Content: FortiGate configuration guides
- License: For reference and documentation

**Fortinet Cookbook**:
- URL: https://docs.fortinet.com/fortigate-cookbook
- Content: Step-by-step configuration recipes
- License: Documentation license

**FortiGate Knowledge Base**:
- URL: https://kb.fortinet.com/
- Content: Configuration examples for specific use cases

### Available Configuration Examples

**Configuration Snippets**:
```
config system global
    set hostname "FortiGate-Example"
    set timezone 04
end

config system admin
    edit "admin"
        set password ENC <encrypted>
    next
end
```

**Cookbook Examples**:
- SSL VPN setup
- Firewall policies
- High availability configurations
- IPsec VPN tunnels

### FortiGate Training

**Fortinet Training Institute**:
- NSE (Network Security Expert) training
- Lab configurations included
- Educational license

### Recommendation

**For Phase 0.5**:
1. Use Fortinet Cookbook configurations
2. Extract examples from official documentation
3. Generate synthetic FortiGate configs
4. Test with FortiGate VM (trial license available)

---

## 3. Palo Alto Networks

### Official Documentation Sources

**Palo Alto Networks TechDocs**:
- URL: https://docs.paloaltonetworks.com/
- Content: PAN-OS configuration guides
- License: Documentation license

**PAN-OS Administrator's Guide**:
- Comprehensive configuration examples
- Best practices documentation
- Security policy examples

**Knowledge Base**:
- URL: https://knowledgebase.paloaltonetworks.com/
- Content: Configuration how-tos

### Available Configuration Examples

**XML Configuration Format**:
```xml
<config>
  <devices>
    <entry name="localhost.localdomain">
      <deviceconfig>
        <system>
          <hostname>PA-Firewall</hostname>
        </system>
      </deviceconfig>
    </entry>
  </devices>
</config>
```

**Best Practice Examples**:
- Security profiles
- NAT policies
- Zone protection
- App-ID configuration

### PAN-OS API

**Configuration via API**:
- REST API documentation includes examples
- XML/JSON configuration snippets
- Developer documentation

### Recommendation

**For Phase 0.5**:
1. Extract examples from TechDocs
2. Use Best Practice Assessment (BPA) recommendations
3. Generate synthetic PAN-OS XML configs
4. Test with PAN-OS VM (trial available)

---

## 4. Juniper

### Official Documentation Sources

**Juniper TechLibrary**:
- URL: https://www.juniper.net/documentation/
- Content: Junos OS configuration guides
- License: Documentation license

**Day One Books**:
- URL: https://www.juniper.net/us/en/training/jnbooks/day-one/
- Content: Free ebooks with configuration examples
- License: Free with registration

**Junos Examples**:
- Configuration snippets in documentation
- Sample configurations by feature

### Available Configuration Examples

**Junos Configuration Format**:
```
system {
    host-name juniper-router;
    time-zone America/New_York;
    root-authentication {
        encrypted-password "$1$...";
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
```

### Juniper Open Learning

**Free Training**:
- Juniper Open Learning platform
- Lab configurations
- Educational resources

### Recommendation

**For Phase 0.5**:
1. Use Day One book examples
2. Extract from Junos documentation
3. Generate synthetic Junos configs
4. Validate syntax with Junos documentation

---

## 5. Open Source and Community Resources

### GitHub Repositories

**Network Configuration Examples**:

**Approach**:
1. Search for: "cisco config example", "network device config"
2. **Verify licensing** - check repository LICENSE file
3. **Verify authenticity** - ensure examples are intentional shares
4. **Avoid** - repositories with "leaked", "dump", "backup" in description

**Example Search Strategy**:
```
site:github.com "cisco ios" "config" "example" -leaked -dump
site:github.com "fortigate" "config" "example" license:mit
```

**Caution**:
- Many GitHub configs are accidental uploads (secrets exposed)
- Some may be from unauthorized sources
- Always check if intentionally shared as examples

### Network Automation Repositories

**Ansible/Python Network Automation**:
- Automation repositories often include sample configs
- Usually synthetic/test configurations
- Check repository license

**Example Repositories** (verify current status):
- napalm-automation (network automation)
- nornir examples
- netmiko examples

### Educational Platforms

**Cisco Packet Tracer**:
- Lab configurations from Packet Tracer exercises
- Educational purpose
- Simplified but realistic

**GNS3 Labs**:
- Public lab repositories
- Community-contributed
- Educational focus

---

## 6. RFC and Standards Documents

### Network Protocol RFCs

**IETF RFCs** include configuration examples:

**Examples**:
- RFC 4271 (BGP) - includes config snippets
- RFC 2328 (OSPF) - configuration examples
- RFC 4443 (ICMPv6) - implementation notes

**License**: Public domain / IETF Trust

### Standards Bodies

**IEEE Standards**:
- 802.1X authentication examples
- Network management examples

---

## 7. Vendor Certification Programs

### Cisco Certifications

**CCNA/CCNP Labs**:
- Official curriculum includes configs
- Lab exercises with sample configurations
- Educational license

**Cisco Press Books**:
- Published configuration examples
- Used with permission for educational purposes

### Fortinet NSE Certification

**Training Materials**:
- Lab configurations
- Example scenarios
- Educational use

### Palo Alto Networks Certifications

**PCNSA/PCNSE**:
- Training configurations
- Lab scenarios
- Educational focus

---

## 8. Synthetic Configuration Generation

### Why Synthetic Configs Are Necessary

**Limitations of Real Configs**:
- Limited availability
- May not cover all scenarios
- Licensing restrictions
- Privacy concerns

**Benefits of Synthetic**:
- ✅ Complete control over content
- ✅ No licensing issues
- ✅ Can test edge cases
- ✅ Can create deliberately insecure configs for testing

### Synthetic Generation Strategy

**Approach**:
1. Study vendor command reference documentation
2. Understand syntax rules and validation
3. Create configuration templates
4. Generate variations:
   - Secure baseline
   - Insecure (for testing detection)
   - Mixed security posture
   - Edge cases and unusual syntax

**Example Generation**:
```python
# Generate Cisco IOS config with specific security posture
def generate_cisco_config(security_level='medium'):
    config = []
    config.append(f"hostname ROUTER-{random_id()}")
    
    if security_level in ['high', 'medium']:
        config.append("ip ssh version 2")
        config.append("no ip http server")
    else:
        config.append("ip http server")  # Insecure
        config.append("transport input telnet ssh")  # Allows telnet
    
    # ... generate full config
    return "\n".join(config)
```

### Validation

**Syntax Validation**:
1. Compare against vendor documentation
2. Test with vendor parser/simulator if available
3. Validate command structure
4. Check for realistic patterns

---

## 9. Dataset Composition Strategy

### Recommended Mix

For comprehensive testing, create a balanced dataset:

| Category | Percentage | Purpose |
|----------|-----------|---------|
| **Vendor Documentation Examples** | 20% | Verify parser handles official syntax |
| **Synthetic Secure Configs** | 30% | Test compliant configurations |
| **Synthetic Insecure Configs** | 30% | Test finding detection |
| **Synthetic Edge Cases** | 10% | Test parser robustness |
| **Unknown/Custom Syntax** | 10% | Test AI learning system |

### Dataset Labeling

**Essential Metadata**:
```json
{
  "source_type": "vendor_documentation|synthetic|community|certification",
  "vendor": "Cisco|Fortinet|PaloAlto|Juniper|Unknown",
  "authenticity": "vendor_provided|generated|community_verified",
  "security_posture": "secure|insecure|mixed|unknown",
  "expected_findings": ["NET-001", "NET-004"],
  "license": "public_domain|documentation_use|educational",
  "provenance": "Cisco IOS 15 Config Guide, Chapter 3",
  "generated_by": null|"synthetic_generator_v1.0"
}
```

---

## 10. Current Dataset Analysis

### Existing Vajra Core Configs (46 files)

**From catalogue_configurations.py results**:
- Cisco: 22 files (47.8%)
- Fortinet: 10 files (21.7%)
- Unknown/Synthetic: 14 files (30.4%)

**Analysis**:
- 14 synthetic configurations already present
- 16 files with redacted content (sanitized)
- Good starting point for testing

**Recommendations**:
1. Document provenance for each existing file
2. Classify as: vendor_example, synthetic, or community
3. Add more vendor variety (Palo Alto, Juniper)
4. Create golden test set with known expected outcomes

---

## 11. Configuration Acquisition Workflow

### Step-by-Step Process

**1. Identify Need**
- Specific vendor/product
- Specific feature/configuration type
- Security posture (secure vs insecure)

**2. Search Legitimate Sources**
```
Priority Order:
1. Official vendor documentation
2. Vendor training materials
3. Published certification resources
4. Community-licensed examples
5. Generate synthetic
```

**3. Evaluate Source**
- ✅ Is it legally obtained?
- ✅ Is it intentionally public?
- ✅ Are licensing terms acceptable?
- ✅ Is authenticity verifiable?

**4. Document Provenance**
```yaml
config_file: cisco_ios_example_001.cfg
source_type: vendor_documentation
source_url: https://www.cisco.com/c/en/us/td/docs/...
source_title: "Cisco IOS Security Configuration Guide"
retrieval_date: "2026-09-16"
license: "Documentation reference use"
modifications: "Redacted IP addresses and hostnames"
```

**5. Sanitize If Needed**
- Remove real IP addresses
- Redact secrets/passwords
- Remove identifying information
- Preserve syntax and structure

**6. Add to Repository**
- Store in appropriate directory
- Update manifest
- Calculate hash
- Tag with metadata

---

## 12. Vendor-Specific Recommendations

### Cisco

**Priority Sources**:
1. ✅ Cisco.com Configuration Guides
2. ✅ CIS Cisco IOS Benchmark examples
3. ✅ DISA STIG Cisco examples
4. ✅ Cisco Press book examples (with attribution)

**Gap**: Need IOS-XR and NX-OS examples

### Fortinet

**Priority Sources**:
1. ✅ Fortinet Cookbook
2. ✅ docs.fortinet.com examples
3. ✅ Knowledge Base articles

**Gap**: Need more complex FortiGate configurations

### Palo Alto

**Priority Sources**:
1. ✅ PAN-OS Administrator's Guide
2. ✅ TechDocs configuration examples
3. ✅ Best Practice Assessment examples

**Gap**: Need initial dataset (currently 0 files)

### Juniper

**Priority Sources**:
1. ✅ Day One books
2. ✅ Junos documentation
3. ✅ Junos Genius examples

**Gap**: Need initial dataset (currently 0 files)

---

## 13. Ethical Considerations

### Data Privacy

**Never Include**:
- Real customer data
- Live IP addresses from production networks
- Actual passwords or secrets
- Identifying organization information

**If Using Real Configs** (with permission):
- Sanitize thoroughly
- Get written authorization
- Document sanitization process
- Respect confidentiality agreements

### Responsible Disclosure

**If You Find**:
- Accidentally exposed configurations online
- Security vulnerabilities in examples

**Do**:
- Report to vendor security team
- Do not exploit
- Do not publicize until patched
- Follow responsible disclosure

---

## 14. Legal Checklist

Before adding any configuration to Vajra Core dataset:

- [ ] Is the source legitimate and legal?
- [ ] Have I verified licensing terms?
- [ ] If from documentation, am I using for permitted purpose?
- [ ] If synthetic, is it based only on public documentation?
- [ ] Have I documented provenance?
- [ ] Have I sanitized sensitive information?
- [ ] Can I legally redistribute this (if open source)?
- [ ] Have I avoided any leaked/unauthorized sources?

---

## 15. Next Steps for Phase 0.5

### Immediate Actions

1. **Document existing 46 configs**:
   - Classify each by source type
   - Add provenance metadata
   - Update manifest

2. **Acquire vendor documentation examples**:
   - Cisco IOS Configuration Guide (10 examples)
   - Fortinet Cookbook (5 examples)

3. **Generate synthetic configs**:
   - 10 Cisco synthetic (various security levels)
   - 5 Fortinet synthetic
   - 5 Palo Alto synthetic (new vendor)
   - 5 Juniper synthetic (new vendor)

4. **Create golden test set**:
   - 10 configs with known expected outcomes
   - Document expected findings for each
   - Cover key compliance rules

### Phase 0 Goals

- 200+ configurations across 4+ vendors
- Full provenance tracking
- Balanced secure/insecure mix
- Comprehensive vendor coverage
- Golden test suite (50+ cases)

---

## Conclusion

Real-world vendor configuration data is limited and must be obtained ethically and legally. Vajra Core's strategy combines:

1. **Vendor documentation examples** (20%) - For authenticity
2. **Synthetic generation** (70%) - For scale and control
3. **Community sources** (10%) - For variety

This balanced approach ensures:
- ✅ Legal compliance
- ✅ Ethical data acquisition
- ✅ Comprehensive test coverage
- ✅ Reproducible benchmarks
- ✅ No privacy violations

**Key Principle**: When in doubt about a source, generate synthetic instead.

---

**Document Version**: 1.0  
**Last Updated**: September 16, 2026  
**Status**: Research Complete  
**Phase**: 0.5 - Foundation
