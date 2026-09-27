#!/usr/bin/env python3
"""
Test current audit report generation functionality
"""
import requests

BASE_URL = 'http://localhost:8000/api'
session_token = 'e80bb6a9-1bda-4881-8122-2c6238728503'
headers = {'X-Vendor-Session-Token': session_token}

print("=== Testing Current Audit Report Generation ===")

# First, get the available audits
print("1. Getting available audits...")
response = requests.get(f'{BASE_URL}/vendor/audits', headers=headers)

if response.status_code == 200:
    data = response.json()
    audits = data.get('data', {}).get('audits', [])
    
    if audits:
        # Test with the most recent audit
        audit = audits[0]
        audit_id = audit.get('audit_id')
        config_id = audit.get('configuration', {}).get('config_id')
        
        print(f"2. Testing report generation for audit {audit_id} (config {config_id})")
        
        # Try to download/view audit report
        report_response = requests.get(f'{BASE_URL}/vendor/audit/{audit_id}/report', headers=headers)
        print(f"   Report endpoint status: {report_response.status_code}")
        
        if report_response.status_code == 200:
            if 'application/pdf' in report_response.headers.get('content-type', ''):
                print(f"   Report size: {len(report_response.content)} bytes (PDF)")
                print("   ✅ PDF report generated")
            else:
                print(f"   Report content: {report_response.text[:200]}...")
                print("   Report type: JSON/Text")
        else:
            print(f"   Report error: {report_response.text}")
        
        # Also test audit details endpoint
        details_response = requests.get(f'{BASE_URL}/vendor/audit/{audit_id}', headers=headers)
        print(f"   Audit details status: {details_response.status_code}")
        
        if details_response.status_code == 200:
            details = details_response.json()
            audit_data = details.get('data', {})
            
            print(f"   Audit status: {audit_data.get('status')}")
            print(f"   Risk level: {audit_data.get('risk_level')}")
            print(f"   Compliance: {audit_data.get('compliance_score')}%")
            
            findings = audit_data.get('findings', [])
            print(f"   Findings count: {len(findings)}")
            
            if findings:
                print("   Sample findings:")
                for finding in findings[:3]:
                    severity = finding.get('severity', 'N/A')
                    rule_name = finding.get('rule_name', 'N/A')
                    print(f"     - {severity}: {rule_name}")
        else:
            print(f"   Details error: {details_response.text}")
    else:
        print("   No audits found")
else:
    print(f"Error getting audits: {response.text}")

print("\n3. Checking available report formats/endpoints...")

# Check what report endpoints are available
test_endpoints = [
    '/vendor/audit/AUD-985883/report',
    '/vendor/audit/AUD-985883/report/pdf',
    '/vendor/audit/AUD-985883/download',
    '/admin/audit/AUD-985883/report'
]

for endpoint in test_endpoints:
    test_response = requests.get(f'{BASE_URL}{endpoint}', headers=headers)
    print(f"   {endpoint}: {test_response.status_code}")