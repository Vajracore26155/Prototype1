#!/usr/bin/env python3
"""
Download and examine current audit report
"""
import requests
import os

BASE_URL = 'http://localhost:8000/api'
session_token = 'e80bb6a9-1bda-4881-8122-2c6238728503'
headers = {'X-Vendor-Session-Token': session_token}

print("=== Downloading Current Audit Report ===")

audit_id = 'AUD-985883'
response = requests.get(f'{BASE_URL}/vendor/audit/{audit_id}/report', headers=headers)

if response.status_code == 200:
    # Save the PDF report
    report_path = f'current_report_{audit_id}.pdf'
    with open(report_path, 'wb') as f:
        f.write(response.content)
    
    file_size = os.path.getsize(report_path)
    print(f"✅ Report saved: {report_path} ({file_size} bytes)")
    
    # Also get the detailed audit data to understand what should be in the report
    details_response = requests.get(f'{BASE_URL}/vendor/audit/{audit_id}', headers=headers)
    
    if details_response.status_code == 200:
        details = details_response.json()
        audit_data = details.get('data', {})
        
        print(f"\n=== Current Audit Content ===")
        print(f"Audit ID: {audit_data.get('audit_id')}")
        print(f"Status: {audit_data.get('status')}")
        print(f"Risk Level: {audit_data.get('risk_level')}")
        print(f"Compliance Score: {audit_data.get('compliance_score')}%")
        print(f"Started: {audit_data.get('started_at')}")
        print(f"Completed: {audit_data.get('completed_at')}")
        
        configuration = audit_data.get('configuration', {})
        print(f"\nConfiguration:")
        print(f"  ID: {configuration.get('config_id')}")
        print(f"  Filename: {configuration.get('filename')}")
        print(f"  Vendor: {configuration.get('vendor')}")
        print(f"  File Size: {configuration.get('file_size')} bytes")
        
        findings = audit_data.get('findings', [])
        print(f"\nFindings: {len(findings)}")
        
        if findings:
            for i, finding in enumerate(findings):
                print(f"  {i+1}. {finding.get('severity', 'N/A')}: {finding.get('rule_name', 'N/A')}")
                print(f"     Description: {finding.get('description', 'N/A')[:100]}...")
        else:
            print("  No findings (this might be why compliance is 0%)")
        
        # Check assessment summary
        summary = audit_data.get('assessment_summary', {})
        if summary:
            print(f"\nAssessment Summary:")
            print(f"  Passed: {summary.get('passed_count', 0)}")
            print(f"  Failed: {summary.get('failed_count', 0)}")
            print(f"  Warnings: {summary.get('warning_count', 0)}")
            print(f"  Total Rules: {summary.get('total_rules', 0)}")
        
    else:
        print(f"Error getting audit details: {details_response.text}")
    
else:
    print(f"Error downloading report: {response.text}")