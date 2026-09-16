# Golden Test Dataset

**Purpose**: Regression testing with known expected outcomes

## Structure

```
golden/
├── positive/          # Compliant configurations (should pass)
├── negative/          # Non-compliant configurations (should fail)
└── test_cases.json    # Expected outcomes for each test
```

## Test Case Format

Each test case includes:
1. **Input**: Configuration file
2. **Expected**: JSON file with expected outcomes

```json
{
  "test_case_id": "GOLD-001",
  "name": "Cisco IOS - Compliant SSH Configuration",
  "config_file": "cisco_ssh_compliant.cfg",
  "vendor": "Cisco",
  "expected_vendor": "Cisco",
  "expected_vendor_confidence": ">0.8",
  "expected_findings": [
    {
      "rule_id": "NET-002",
      "status": "PASS",
      "title": "SSH Must Be Enabled"
    },
    {
      "rule_id": "NET-003",
      "status": "PASS",
      "title": "SSH Version 2 Required"
    },
    {
      "rule_id": "NET-001",
      "status": "PASS",
      "title": "Telnet Must Be Disabled"
    }
  ],
  "expected_compliance_score": ">0.9",
  "expected_risk_level": "LOW"
}
```

## Usage

Run golden tests:
```bash
python scripts/run_golden_tests.py
```

## Test Categories

### 1. Vendor Detection Tests
- Cisco IOS recognition
- Fortinet FortiGate recognition
- Unknown vendor handling

### 2. Compliance Tests
- Fully compliant config (all rules pass)
- Partially compliant config (some rules fail)
- Non-compliant config (multiple critical failures)

### 3. Parser Tests
- Valid syntax
- Edge cases
- Unusual formatting

### 4. Evidence Tracking Tests
- Line number accuracy
- Text extraction
- Evidence attachment

### 5. Remediation Tests
- Remediation generation
- Command syntax correctness

## Adding New Test Cases

1. Create configuration file in positive/ or negative/
2. Add expected outcomes to test_cases.json
3. Run golden tests to verify
4. Commit both input and expected output

## Maintenance

- Review quarterly
- Update when compliance rules change
- Add tests for bug fixes
- Expand vendor coverage

---

**Version**: 1.0  
**Last Updated**: 2026-09-16
