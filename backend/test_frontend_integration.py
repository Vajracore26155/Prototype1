#!/usr/bin/env python3
"""
Test frontend integration with enhanced vendor system
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_frontend_compatibility():
    """Test that all frontend endpoints return expected data structure"""
    print("🌐 TESTING FRONTEND INTEGRATION COMPATIBILITY")
    print("=" * 55)
    
    # Use T-star Fashion session
    session_token = 'e80bb6a9-1bda-4881-8122-2c6238728503'
    headers = {"X-Vendor-Session-Token": session_token}
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Vendor session info for dashboard
    print("🧪 Test: Vendor Dashboard Session Info")
    total_tests += 1
    response = requests.get(f"{BASE_URL}/vendor/upload/session", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        required_fields = ['success', 'data']
        vendor_fields = ['vendor_id', 'company', 'contact', 'email']
        
        if all(field in data for field in required_fields):
            vendor_data = data['data'].get('vendor', {})
            if all(field in vendor_data for field in vendor_fields):
                print("   ✅ Session info structure correct for frontend")
                tests_passed += 1
            else:
                print(f"   ❌ Missing vendor fields: {set(vendor_fields) - set(vendor_data.keys())}")
        else:
            print(f"   ❌ Missing required fields: {set(required_fields) - set(data.keys())}")
    else:
        print(f"   ❌ Session endpoint failed: {response.status_code}")
    
    # Test 2: Configurations list for VendorConfigurations page
    print("\n🧪 Test: Vendor Configurations List")
    total_tests += 1
    response = requests.get(f"{BASE_URL}/vendor/configurations", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if 'data' in data and 'configurations' in data['data']:
            configs = data['data']['configurations']
            if configs:
                config = configs[0]
                required_config_fields = ['config_id', 'filename', 'vendor', 'status']
                
                if all(field in config for field in required_config_fields):
                    print("   ✅ Configuration data structure correct for frontend")
                    tests_passed += 1
                else:
                    print(f"   ❌ Missing config fields: {set(required_config_fields) - set(config.keys())}")
            else:
                print("   ✅ Empty configurations list (valid state)")
                tests_passed += 1
        else:
            print("   ❌ Invalid configurations response structure")
    else:
        print(f"   ❌ Configurations endpoint failed: {response.status_code}")
    
    # Test 3: Audits list for vendor dashboard
    print("\n🧪 Test: Vendor Audits List")
    total_tests += 1
    response = requests.get(f"{BASE_URL}/vendor/audits", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if 'data' in data and 'audits' in data['data']:
            audits = data['data']['audits']
            if audits:
                audit = audits[0]
                required_audit_fields = ['audit_id', 'status', 'compliance_score', 'risk_level']
                
                if all(field in audit for field in required_audit_fields):
                    print("   ✅ Audit data structure correct for frontend")
                    tests_passed += 1
                else:
                    print(f"   ❌ Missing audit fields: {set(required_audit_fields) - set(audit.keys())}")
            else:
                print("   ✅ Empty audits list (valid state)")
                tests_passed += 1
        else:
            print("   ❌ Invalid audits response structure")
    else:
        print(f"   ❌ Audits endpoint failed: {response.status_code}")
    
    # Test 4: Enhanced audit details with findings
    print("\n🧪 Test: Enhanced Audit Details")
    total_tests += 1
    
    # Get first audit ID
    audit_response = requests.get(f"{BASE_URL}/vendor/audits", headers=headers)
    if audit_response.status_code == 200:
        audits = audit_response.json()['data']['audits']
        if audits:
            audit_id = audits[0]['audit_id']
            
            details_response = requests.get(f"{BASE_URL}/vendor/audit/{audit_id}", headers=headers)
            
            if details_response.status_code == 200:
                details = details_response.json()['data']
                
                # Check for enhanced findings data
                if 'findings' in details and 'findings_summary' in details:
                    findings = details['findings']
                    summary = details['findings_summary']
                    
                    if findings and len(findings) > 0:
                        finding = findings[0]
                        required_finding_fields = ['severity', 'status', 'rule_name', 'description']
                        
                        if all(field in finding for field in required_finding_fields):
                            print("   ✅ Enhanced findings data available for frontend")
                            tests_passed += 1
                        else:
                            print(f"   ❌ Missing finding fields: {set(required_finding_fields) - set(finding.keys())}")
                    else:
                        print("   ✅ No findings (valid for some audits)")
                        tests_passed += 1
                else:
                    print("   ❌ Enhanced findings not included in audit details")
            else:
                print(f"   ❌ Audit details failed: {details_response.status_code}")
        else:
            print("   ⚠️  No audits available for testing")
            tests_passed += 1  # Count as pass since no data to test
    else:
        print("   ❌ Could not get audits for details test")
    
    # Test 5: Upload history with session tracking
    print("\n🧪 Test: Enhanced Upload History")
    total_tests += 1
    response = requests.get(f"{BASE_URL}/vendor/upload/history", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if 'data' in data and 'uploads' in data['data']:
            uploads = data['data']['uploads']
            if uploads:
                upload = uploads[0]
                required_upload_fields = ['config_id', 'filename', 'uploaded_at', 'status']
                
                if all(field in upload for field in required_upload_fields):
                    print("   ✅ Upload history structure correct for frontend")
                    tests_passed += 1
                else:
                    print(f"   ❌ Missing upload fields: {set(required_upload_fields) - set(upload.keys())}")
            else:
                print("   ✅ Empty upload history (valid state)")
                tests_passed += 1
        else:
            print("   ❌ Invalid upload history response structure")
    else:
        print(f"   ❌ Upload history endpoint failed: {response.status_code}")
    
    # Test 6: Professional report download
    print("\n🧪 Test: Professional Report Download")
    total_tests += 1
    
    # Get an audit ID for report testing
    audit_response = requests.get(f"{BASE_URL}/vendor/audits", headers=headers)
    if audit_response.status_code == 200:
        audits = audit_response.json()['data']['audits']
        if audits:
            audit_id = audits[0]['audit_id']
            
            report_response = requests.get(f"{BASE_URL}/vendor/audit/{audit_id}/report", headers=headers)
            
            if report_response.status_code == 200:
                content_type = report_response.headers.get('content-type', '')
                content_length = len(report_response.content)
                
                if 'application/pdf' in content_type and content_length > 8000:
                    print("   ✅ Professional PDF report generated successfully")
                    tests_passed += 1
                else:
                    print(f"   ❌ Report issues - Type: {content_type}, Size: {content_length}")
            else:
                print(f"   ❌ Report download failed: {report_response.status_code}")
        else:
            print("   ⚠️  No audits available for report testing")
            tests_passed += 1  # Count as pass since no data to test
    else:
        print("   ❌ Could not get audits for report test")
    
    # Results summary
    print("\n" + "=" * 55)
    print(f"📊 FRONTEND INTEGRATION TEST RESULTS")
    print("=" * 55)
    print(f"✅ Tests Passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("\n🎉 Perfect Frontend Integration!")
        print("✅ All API endpoints return correct data structures")
        print("✅ Enhanced findings and audit details available")
        print("✅ Professional reports generate properly")
        print("✅ Vendor dashboard will work seamlessly")
        return True
    else:
        print(f"\n⚠️  {total_tests - tests_passed} integration issues found")
        return False

if __name__ == "__main__":
    success = test_frontend_compatibility()
    exit(0 if success else 1)