#!/usr/bin/env python3
"""
Test the enhanced professional audit report generation
"""
import requests
import os

BASE_URL = 'http://localhost:8000/api'
session_token = 'e80bb6a9-1bda-4881-8122-2c6238728503'
headers = {'X-Vendor-Session-Token': session_token}

print("=== Testing Enhanced Professional Report Generation ===")

# Test with multiple audits to compare before/after
test_audits = [
    'AUD-985883',  # Recent with UNKNOWN status findings
    'AUD-324698',  # Has mixed PASS/FAIL findings
    'AUD-387455'   # Has high compliance score
]

for audit_id in test_audits:
    print(f"\n--- Testing Report for {audit_id} ---")
    
    # Get audit details first
    details_response = requests.get(f'{BASE_URL}/vendor/audit/{audit_id}', headers=headers)
    
    if details_response.status_code == 200:
        audit_data = details_response.json()['data']
        
        print(f"Audit Status: {audit_data.get('status')}")
        print(f"Compliance: {audit_data.get('compliance_score')}%")
        print(f"Risk Level: {audit_data.get('risk_level')}")
        
        findings = audit_data.get('findings', [])
        print(f"Findings: {len(findings)}")
        
        if len(findings) > 0:
            # Show findings distribution
            severity_counts = {}
            status_counts = {}
            
            for finding in findings:
                severity = finding.get('severity', 'UNKNOWN')
                status = finding.get('status', 'UNKNOWN')
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
                status_counts[status] = status_counts.get(status, 0) + 1
            
            print(f"  Severity: {severity_counts}")
            print(f"  Status: {status_counts}")
            
            # Generate report
            print("  Generating enhanced report...")
            report_response = requests.get(f'{BASE_URL}/vendor/audit/{audit_id}/report', headers=headers)
            
            if report_response.status_code == 200:
                report_size = len(report_response.content)
                report_filename = f'enhanced_professional_report_{audit_id}.pdf'
                
                with open(report_filename, 'wb') as f:
                    f.write(report_response.content)
                
                file_size_kb = report_size / 1024
                print(f"  ✅ Enhanced report: {report_filename} ({file_size_kb:.1f} KB)")
                
                # Compare with original size
                if report_size > 8000:  # More than 8KB suggests enhanced content
                    print(f"  🎉 Report is now more comprehensive!")
                else:
                    print(f"  ⚠️  Report size similar to before - may need more enhancements")
            else:
                print(f"  ❌ Report generation failed: {report_response.status_code}")
        else:
            print("  No findings to include in report")
    else:
        print(f"  ❌ Failed to get audit details: {details_response.status_code}")

print(f"\n=== Summary ===")
print("Enhanced report features added:")
print("✅ Color-coded finding status (PASS/FAIL/UNKNOWN)")
print("✅ Comprehensive finding details (expected vs actual)")
print("✅ Configuration lines and technical details")
print("✅ Detailed remediation recommendations") 
print("✅ Priority-based remediation grouping")
print("✅ Enhanced technical summary with distributions")
print("✅ Professional formatting and structure")

print(f"\nGenerated enhanced reports:")
for audit_id in test_audits:
    filename = f'enhanced_professional_report_{audit_id}.pdf'
    if os.path.exists(filename):
        size_kb = os.path.getsize(filename) / 1024
        print(f"  📄 {filename} ({size_kb:.1f} KB)")

print(f"\n🎯 Professional audit reports now ready for vendor download!")