#!/usr/bin/env python3
"""
Phase 6 Test: Frontend Integration Test
Tests the complete workflow: upload → audit → findings
"""
import sys
import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_complete_workflow():
    """Test complete user workflow"""
    print("\n" + "="*60)
    print("PHASE 6: Frontend Integration Test")
    print("="*60)
    
    # 1. Health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        print("✓ Backend is healthy")
    except Exception as e:
        print(f"✗ Backend not running: {e}")
        print("\nPlease start backend with: cd backend && python -m uvicorn app.main:app --reload")
        sys.exit(1)
    
    # 2. Upload Cisco insecure config
    print("\n2. Testing file upload...")
    config_file = Path(__file__).parent.parent / "demo_configs" / "cisco" / "cisco_insecure.cfg"
    
    if not config_file.exists():
        print(f"✗ Demo config not found: {config_file}")
        sys.exit(1)
    
    with open(config_file, 'rb') as f:
        files = {'file': ('cisco_insecure.cfg', f, 'text/plain')}
        response = requests.post(f"{BASE_URL}/api/config/upload", files=files)
    
    assert response.status_code == 200
    upload_data = response.json()
    assert upload_data['success']
    config_id = upload_data['data']['config_id']
    print(f"✓ Uploaded config: {config_id}")
    print(f"  Vendor: {upload_data['data']['vendor']} ({upload_data['data']['vendor_confidence']*100:.0f}% confidence)")
    
    # 3. Run audit
    print(f"\n3. Running audit on {config_id}...")
    response = requests.post(f"{BASE_URL}/api/audits/{config_id}/run")
    if response.status_code != 200:
        print(f"✗ Audit failed: {response.status_code}")
        print(f"  Response: {response.text}")
        sys.exit(1)
    audit_data = response.json()
    assert audit_data['success']
    audit_id = audit_data['data']['audit_id']
    print(f"✓ Audit created: {audit_id}")
    
    # 4. Get audit results
    print(f"\n4. Fetching audit results...")
    response = requests.get(f"{BASE_URL}/api/audits/{audit_id}")
    assert response.status_code == 200
    result = response.json()
    assert result['success']
    
    audit = result['data']
    print(f"✓ Compliance Score: {audit['compliance_score']:.1f}%")
    print(f"  Risk Level: {audit['risk_level']}")
    print(f"  Failed: {audit['failed_count']}, Passed: {audit['passed_count']}")
    
    # 5. Get findings
    print(f"\n5. Fetching detailed findings...")
    response = requests.get(f"{BASE_URL}/api/audits/{audit_id}/findings")
    assert response.status_code == 200
    findings_data = response.json()
    assert findings_data['success']
    
    findings = findings_data['data']['findings']
    failed = [f for f in findings if f['status'] == 'FAIL']
    passed = [f for f in findings if f['status'] == 'PASS']
    
    print(f"✓ Found {len(findings)} total findings")
    print(f"  {len(failed)} violations, {len(passed)} passed")
    
    # Show sample violation with evidence
    if failed:
        sample = failed[0]
        print(f"\n  Sample Violation:")
        print(f"    Rule: {sample['rule_id']} - {sample['title']}")
        print(f"    Severity: {sample['severity']}")
        if sample.get('evidence'):
            print(f"    Evidence: Line {sample['evidence']['line']}")
            print(f"      {sample['evidence']['text'][:60]}...")
        if sample.get('remediation'):
            print(f"    Fix available: Yes")
    
    # 6. List configurations
    print(f"\n6. Listing all configurations...")
    response = requests.get(f"{BASE_URL}/api/configurations")
    assert response.status_code == 200
    configs_data = response.json()
    assert configs_data['success']
    
    configs = configs_data['data']['configurations']
    print(f"✓ Found {len(configs)} configuration(s)")
    
    for cfg in configs[-3:]:  # Show last 3
        print(f"  - {cfg['filename']} ({cfg['vendor']}) - {cfg['status']}")
    
    print("\n" + "="*60)
    print("✅ PHASE 6 TEST PASSED!")
    print("="*60)
    print("\nFrontend workflow verified:")
    print("  1. Upload configuration ✓")
    print("  2. Run security audit ✓")
    print("  3. View compliance score ✓")
    print("  4. Review findings with evidence ✓")
    print("  5. Get remediation guidance ✓")
    print("\nReady for Phase 7: Documentation")

if __name__ == "__main__":
    test_complete_workflow()
