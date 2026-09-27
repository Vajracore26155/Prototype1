#!/usr/bin/env python3
"""
Test the enhanced vendor audit details endpoint with findings
"""
import requests

BASE_URL = 'http://localhost:8000/api'
session_token = 'e80bb6a9-1bda-4881-8122-2c6238728503'
headers = {'X-Vendor-Session-Token': session_token}

print("=== Testing Enhanced Audit Details ===")

# Test with an audit that has findings
audit_id = 'AUD-985883'
response = requests.get(f'{BASE_URL}/vendor/audit/{audit_id}', headers=headers)

if response.status_code == 200:
    data = response.json()
    audit_data = data.get('data', {})
    
    print(f"✅ Audit Details Retrieved Successfully!")
    print(f"Audit ID: {audit_data.get('audit_id')}")
    print(f"Status: {audit_data.get('status')}")
    print(f"Compliance: {audit_data.get('compliance_score')}%")
    print(f"Risk Level: {audit_data.get('risk_level')}")
    
    findings = audit_data.get('findings', [])
    print(f"\nFindings: {len(findings)}")
    
    if findings:
        print("✅ Findings now included in API response!")
        
        # Show summary by severity and status
        findings_summary = audit_data.get('findings_summary', {})
        by_severity = findings_summary.get('by_severity', {})
        by_status = findings_summary.get('by_status', {})
        
        print(f"\nFindings by Severity:")
        for severity, count in by_severity.items():
            print(f"  {severity.upper()}: {count}")
        
        print(f"\nFindings by Status:")
        for status, count in by_status.items():
            print(f"  {status.upper()}: {count}")
        
        print(f"\nSample Findings:")
        for i, finding in enumerate(findings[:3]):
            print(f"  {i+1}. [{finding.get('severity')}] {finding.get('rule_name')}")
            print(f"     Status: {finding.get('status')}")
            print(f"     Description: {finding.get('description', '')[:80]}...")
            if finding.get('remediation'):
                print(f"     Remediation: {finding.get('remediation', '')[:80]}...")
        
        # Now the reports should be much more comprehensive!
        print(f"\n=== Testing Enhanced Report Generation ===")
        report_response = requests.get(f'{BASE_URL}/vendor/audit/{audit_id}/report', headers=headers)
        
        if report_response.status_code == 200:
            report_size = len(report_response.content)
            print(f"✅ Enhanced report generated: {report_size} bytes")
            
            # Save the enhanced report
            with open(f'enhanced_report_{audit_id}.pdf', 'wb') as f:
                f.write(report_response.content)
            print(f"✅ Enhanced report saved: enhanced_report_{audit_id}.pdf")
            
            if report_size > 7300:
                print(f"🎉 Report is now larger and more comprehensive!")
        else:
            print(f"❌ Report generation failed: {report_response.text}")
    else:
        print("❌ No findings in response - something is still wrong")
else:
    print(f"❌ Failed to get audit details: {response.text}")