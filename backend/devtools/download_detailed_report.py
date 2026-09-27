#!/usr/bin/env python3
"""
Download and examine detailed audit report with findings
"""
import requests

BASE_URL = 'http://localhost:8000/api'
session_token = 'e80bb6a9-1bda-4881-8122-2c6238728503'
headers = {'X-Vendor-Session-Token': session_token}

print("=== Examining Audit with Findings ===")

# Test with audit that has findings (AUD-324698 showed 22.22% compliance)
audit_id = 'AUD-324698'
print(f"Testing audit: {audit_id}")

details_response = requests.get(f'{BASE_URL}/vendor/audit/{audit_id}', headers=headers)

if details_response.status_code == 200:
    details = details_response.json()
    audit_data = details.get('data', {})
    
    print(f"\n=== Audit Content Analysis ===")
    print(f"Audit ID: {audit_data.get('audit_id')}")
    print(f"Status: {audit_data.get('status')}")
    print(f"Risk Level: {audit_data.get('risk_level')}")
    print(f"Compliance Score: {audit_data.get('compliance_score')}%")
    
    configuration = audit_data.get('configuration', {})
    print(f"\nConfiguration: {configuration.get('config_id')} - {configuration.get('filename')}")
    
    findings = audit_data.get('findings', [])
    print(f"\nFindings: {len(findings)}")
    
    if findings:
        for i, finding in enumerate(findings[:5]):  # Show first 5 findings
            print(f"\n  Finding {i+1}:")
            print(f"    Severity: {finding.get('severity')}")
            print(f"    Rule: {finding.get('rule_name')}")
            print(f"    Description: {finding.get('description')}")
            print(f"    Impact: {finding.get('impact')}")
            print(f"    Recommendation: {finding.get('recommendation')}")
            
            # Show configuration lines if available
            config_lines = finding.get('configuration_lines', [])
            if config_lines:
                print(f"    Config Lines: {config_lines[:2]}")  # Show first 2 lines
    
    # Download the report for this audit
    print(f"\n=== Downloading Report for {audit_id} ===")
    report_response = requests.get(f'{BASE_URL}/vendor/audit/{audit_id}/report', headers=headers)
    
    if report_response.status_code == 200:
        report_path = f'detailed_report_{audit_id}.pdf'
        with open(report_path, 'wb') as f:
            f.write(report_response.content)
        
        import os
        file_size = os.path.getsize(report_path)
        print(f"✅ Detailed report saved: {report_path} ({file_size} bytes)")
        
        # Compare sizes to see if this report is more comprehensive
        if file_size > 7300:
            print(f"   This report is larger than the previous one - likely more detailed!")
    else:
        print(f"Error downloading report: {report_response.text}")

else:
    print(f"Error getting audit details: {details_response.text}")