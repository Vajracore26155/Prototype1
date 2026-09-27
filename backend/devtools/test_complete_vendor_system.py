#!/usr/bin/env python3
"""
Complete End-to-End Vendor System Testing
Tests the entire workflow from registration to report download
"""
import requests
import tempfile
import os
import time
import json

BASE_URL = "http://localhost:8000/api"

class VendorSystemTester:
    def __init__(self):
        self.test_results = {
            "registration": False,
            "admin_approval": False,
            "otp_login": False,
            "dashboard_access": False,
            "file_upload": False,
            "audit_execution": False,
            "report_generation": False,
            "report_download": False
        }
        self.vendor_email = f"test_vendor_{int(time.time())}@testcompany.com"
        self.company_name = f"Test Company {int(time.time())}"
        self.session_token = None
        self.config_id = None
        self.audit_id = None
        
    def log_step(self, step_name, success, details=""):
        """Log test step results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {step_name}")
        if details:
            print(f"   {details}")
        self.test_results[step_name] = success
        return success
    
    def test_vendor_registration(self):
        """Test 1: Vendor Registration"""
        print("\n=== STEP 1: Vendor Registration ===")
        
        registration_data = {
            "email": self.vendor_email,
            "company_name": self.company_name,
            "contact_name": "Test Contact",
            "phone": "+1-555-0123",
            "organization_id": 1
        }
        
        try:
            response = requests.post(f"{BASE_URL}/vendor/register", json=registration_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    vendor_id = data["data"]["vendor_id"]
                    request_id = data["data"]["request_id"]
                    return self.log_step("registration", True, f"Vendor ID: {vendor_id}, Request ID: {request_id}")
                else:
                    return self.log_step("registration", False, f"Registration failed: {data}")
            else:
                return self.log_step("registration", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            return self.log_step("registration", False, f"Exception: {str(e)}")
    
    def test_admin_approval(self):
        """Test 2: Admin Approval Process"""
        print("\n=== STEP 2: Admin Approval Simulation ===")
        
        try:
            # Simulate admin approval by directly updating the database
            from app.database import get_db_session, VendorUser, VendorApprovalRequest
            from datetime import datetime
            
            with get_db_session() as db:
                # Find the vendor we just registered
                vendor = db.query(VendorUser).filter(VendorUser.email == self.vendor_email).first()
                
                if vendor:
                    # Update vendor status
                    vendor.approval_status = "APPROVED"
                    vendor.approved_by = "test@admin.com"
                    vendor.approved_at = datetime.utcnow()
                    vendor.is_active = True
                    
                    # Update approval request
                    request = db.query(VendorApprovalRequest).filter(
                        VendorApprovalRequest.vendor_id == vendor.id
                    ).first()
                    
                    if request:
                        request.status = "APPROVED"
                        request.reviewed_by = "test@admin.com"
                        request.reviewed_at = datetime.utcnow()
                        request.review_notes = "Approved for testing"
                    
                    db.commit()
                    return self.log_step("admin_approval", True, f"Vendor {vendor.vendor_id} approved")
                else:
                    return self.log_step("admin_approval", False, "Vendor not found for approval")
        except Exception as e:
            return self.log_step("admin_approval", False, f"Exception: {str(e)}")
    
    def test_otp_login(self):
        """Test 3: OTP Login Process"""
        print("\n=== STEP 3: OTP Login ===")
        
        try:
            # Step 3a: Request OTP
            otp_request = {"vendor_email": self.vendor_email}
            response = requests.post(f"{BASE_URL}/vendor/request-otp", json=otp_request)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print("   OTP request sent successfully")
                    
                    # Step 3b: Get OTP from database (in real system, this would be from email)
                    from app.database import get_db_session, VendorOTP, VendorUser
                    
                    with get_db_session() as db:
                        vendor = db.query(VendorUser).filter(VendorUser.email == self.vendor_email).first()
                        if vendor:
                            latest_otp = db.query(VendorOTP).filter(
                                VendorOTP.vendor_id == vendor.id
                            ).order_by(VendorOTP.created_at.desc()).first()
                            
                            if latest_otp:
                                otp_code = latest_otp.otp_code
                                print(f"   Retrieved OTP: {otp_code}")
                                
                                # Step 3c: Verify OTP
                                verify_data = {
                                    "vendor_email": self.vendor_email,
                                    "otp_code": otp_code
                                }
                                
                                verify_response = requests.post(f"{BASE_URL}/vendor/verify-otp", json=verify_data)
                                
                                if verify_response.status_code == 200:
                                    verify_data = verify_response.json()
                                    if verify_data.get("success"):
                                        self.session_token = verify_data["data"]["session_token"]
                                        session_id = verify_data["data"]["session_id"]
                                        return self.log_step("otp_login", True, f"Session: {session_id}")
                                    else:
                                        return self.log_step("otp_login", False, f"OTP verification failed: {verify_data}")
                                else:
                                    return self.log_step("otp_login", False, f"OTP verification HTTP {verify_response.status_code}")
                            else:
                                return self.log_step("otp_login", False, "No OTP found in database")
                        else:
                            return self.log_step("otp_login", False, "Vendor not found for OTP retrieval")
                else:
                    return self.log_step("otp_login", False, f"OTP request failed: {data}")
            else:
                return self.log_step("otp_login", False, f"OTP request HTTP {response.status_code}")
        except Exception as e:
            return self.log_step("otp_login", False, f"Exception: {str(e)}")
    
    def test_dashboard_access(self):
        """Test 4: Dashboard Access"""
        print("\n=== STEP 4: Dashboard Access ===")
        
        if not self.session_token:
            return self.log_step("dashboard_access", False, "No session token available")
        
        headers = {"X-Vendor-Session-Token": self.session_token}
        
        try:
            # Test session info
            response = requests.get(f"{BASE_URL}/vendor/upload/session", headers=headers)
            
            if response.status_code == 200:
                session_data = response.json()
                vendor_info = session_data["data"]["vendor"]
                
                # Test configurations endpoint
                configs_response = requests.get(f"{BASE_URL}/vendor/configurations", headers=headers)
                
                if configs_response.status_code == 200:
                    # Test audits endpoint
                    audits_response = requests.get(f"{BASE_URL}/vendor/audits", headers=headers)
                    
                    if audits_response.status_code == 200:
                        return self.log_step("dashboard_access", True, f"Company: {vendor_info['company']}")
                    else:
                        return self.log_step("dashboard_access", False, f"Audits endpoint failed: {audits_response.status_code}")
                else:
                    return self.log_step("dashboard_access", False, f"Configurations endpoint failed: {configs_response.status_code}")
            else:
                return self.log_step("dashboard_access", False, f"Session endpoint failed: {response.status_code}")
        except Exception as e:
            return self.log_step("dashboard_access", False, f"Exception: {str(e)}")
    
    def test_file_upload(self):
        """Test 5: File Upload"""
        print("\n=== STEP 5: File Upload ===")
        
        if not self.session_token:
            return self.log_step("file_upload", False, "No session token available")
        
        headers = {"X-Vendor-Session-Token": self.session_token}
        
        try:
            # Create test configuration file
            test_config = f"""version 15.1
hostname TestDevice-E2E-{int(time.time())}
!
interface GigabitEthernet0/0
 description Management Interface
 ip address 192.168.100.1 255.255.255.0
 no shutdown
!
ip ssh version 2
ip ssh time-out 60
!
line vty 0 4
 transport input ssh
 login local
!
username admin privilege 15 secret 5 $1$salt$hashedpassword
!
end"""
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as f:
                f.write(test_config)
                temp_file = f.name
            
            try:
                with open(temp_file, 'rb') as f:
                    files = {'file': (f'e2e_test_{int(time.time())}.cfg', f, 'text/plain')}
                    data = {'device_id': f'E2E-TEST-{int(time.time())}'}
                    
                    response = requests.post(
                        f"{BASE_URL}/vendor/upload/configuration",
                        files=files,
                        data=data,
                        headers=headers
                    )
                
                if response.status_code == 200:
                    upload_data = response.json()
                    if upload_data.get("success") and not upload_data.get("data", {}).get("duplicate", False):
                        self.config_id = upload_data["data"]["config_id"]
                        
                        # Check if audit was automatically created
                        audit_info = upload_data["data"].get("audit")
                        if audit_info:
                            self.audit_id = audit_info["audit_id"]
                            return self.log_step("file_upload", True, f"Config: {self.config_id}, Auto-audit: {self.audit_id}")
                        else:
                            return self.log_step("file_upload", True, f"Config: {self.config_id} (no auto-audit)")
                    else:
                        return self.log_step("file_upload", False, f"Upload failed or duplicate: {upload_data}")
                else:
                    return self.log_step("file_upload", False, f"Upload HTTP {response.status_code}: {response.text}")
            finally:
                os.unlink(temp_file)
        except Exception as e:
            return self.log_step("file_upload", False, f"Exception: {str(e)}")
    
    def test_audit_execution(self):
        """Test 6: Audit Execution"""
        print("\n=== STEP 6: Audit Execution ===")
        
        if not self.session_token or not self.config_id:
            return self.log_step("audit_execution", False, "Missing session token or config ID")
        
        headers = {"X-Vendor-Session-Token": self.session_token}
        
        try:
            if not self.audit_id:
                # Trigger manual audit if not auto-created
                response = requests.post(f"{BASE_URL}/vendor/audit/{self.config_id}", headers=headers)
                
                if response.status_code == 200:
                    audit_data = response.json()
                    if audit_data.get("success"):
                        self.audit_id = audit_data["data"]["audit_id"]
                    else:
                        return self.log_step("audit_execution", False, f"Manual audit failed: {audit_data}")
                else:
                    return self.log_step("audit_execution", False, f"Manual audit HTTP {response.status_code}")
            
            # Wait a moment for audit to complete
            time.sleep(2)
            
            # Check audit status
            audit_response = requests.get(f"{BASE_URL}/vendor/audit/{self.audit_id}", headers=headers)
            
            if audit_response.status_code == 200:
                audit_details = audit_response.json()["data"]
                status = audit_details.get("status")
                compliance = audit_details.get("compliance_score", 0)
                findings_count = len(audit_details.get("findings", []))
                
                if status in ["COMPLETED", "NEEDS_REVIEW"]:
                    return self.log_step("audit_execution", True, f"Status: {status}, Compliance: {compliance}%, Findings: {findings_count}")
                else:
                    return self.log_step("audit_execution", False, f"Audit status: {status}")
            else:
                return self.log_step("audit_execution", False, f"Audit details HTTP {audit_response.status_code}")
        except Exception as e:
            return self.log_step("audit_execution", False, f"Exception: {str(e)}")
    
    def test_report_generation(self):
        """Test 7: Report Generation"""
        print("\n=== STEP 7: Report Generation ===")
        
        if not self.session_token or not self.audit_id:
            return self.log_step("report_generation", False, "Missing session token or audit ID")
        
        headers = {"X-Vendor-Session-Token": self.session_token}
        
        try:
            response = requests.get(f"{BASE_URL}/vendor/audit/{self.audit_id}/report", headers=headers)
            
            if response.status_code == 200:
                report_size = len(response.content)
                
                if report_size > 5000:  # Reasonable size for a professional report
                    return self.log_step("report_generation", True, f"Report size: {report_size / 1024:.1f} KB")
                else:
                    return self.log_step("report_generation", False, f"Report too small: {report_size} bytes")
            else:
                return self.log_step("report_generation", False, f"Report HTTP {response.status_code}: {response.text}")
        except Exception as e:
            return self.log_step("report_generation", False, f"Exception: {str(e)}")
    
    def test_report_download(self):
        """Test 8: Report Download and Validation"""
        print("\n=== STEP 8: Report Download & Validation ===")
        
        if not self.session_token or not self.audit_id:
            return self.log_step("report_download", False, "Missing session token or audit ID")
        
        headers = {"X-Vendor-Session-Token": self.session_token}
        
        try:
            response = requests.get(f"{BASE_URL}/vendor/audit/{self.audit_id}/report", headers=headers)
            
            if response.status_code == 200:
                # Save report for validation
                report_filename = f"e2e_test_report_{self.audit_id}.pdf"
                with open(report_filename, 'wb') as f:
                    f.write(response.content)
                
                file_size = os.path.getsize(report_filename)
                
                # Validate PDF header
                with open(report_filename, 'rb') as f:
                    pdf_header = f.read(4)
                
                if pdf_header == b'%PDF':
                    return self.log_step("report_download", True, f"Valid PDF saved: {report_filename} ({file_size / 1024:.1f} KB)")
                else:
                    return self.log_step("report_download", False, "Downloaded file is not a valid PDF")
            else:
                return self.log_step("report_download", False, f"Download HTTP {response.status_code}")
        except Exception as e:
            return self.log_step("report_download", False, f"Exception: {str(e)}")
    
    def run_complete_test(self):
        """Run complete end-to-end test suite"""
        print("🚀 STARTING COMPLETE VENDOR SYSTEM END-TO-END TEST")
        print("=" * 60)
        
        test_steps = [
            self.test_vendor_registration,
            self.test_admin_approval,
            self.test_otp_login,
            self.test_dashboard_access,
            self.test_file_upload,
            self.test_audit_execution,
            self.test_report_generation,
            self.test_report_download
        ]
        
        for step in test_steps:
            if not step():
                break  # Stop on first failure
        
        # Results summary
        print("\n" + "=" * 60)
        print("📊 COMPLETE VENDOR SYSTEM TEST RESULTS")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results.values() if result)
        total = len(self.test_results)
        
        for step_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {step_name.replace('_', ' ').title()}")
        
        print(f"\n📈 Overall Result: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 SUCCESS: Complete vendor system is fully operational!")
            print("✅ Registration → Approval → Login → Upload → Audit → Report")
            print("✅ All vendor workflow components working correctly")
            print("✅ Professional audit reports generating successfully")
            return True
        else:
            print(f"\n⚠️  PARTIAL SUCCESS: {total - passed} issues need attention")
            return False

def main():
    """Main test execution"""
    tester = VendorSystemTester()
    success = tester.run_complete_test()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())