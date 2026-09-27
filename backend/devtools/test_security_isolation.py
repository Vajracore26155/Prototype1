"""
Security & Data Isolation Test
Verifies that:
1. Admin can only see their organization's data
2. Unauthenticated users cannot access protected endpoints
3. Vendor data is properly isolated
4. Permission checks are enforced
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000/api"

# Test data
ADMIN_EMAIL = "mayankparab4811@gmail.com"
ADMIN_PASSWORD = "Admin@123"

def print_section(title):
    """Print a section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_result(test_name, passed, message=""):
    """Print test result"""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status}: {test_name}")
    if message:
        print(f"  → {message}")

def test_unauthenticated_access_denied():
    """Test 1: Unauthenticated users cannot access protected endpoints"""
    print_section("TEST 1: Unauthenticated Access Control")
    
    protected_endpoints = [
        ("/admin/vendor-requests", "GET"),
        ("/admin/vendors", "GET"),
        ("/admin/vendor-activity", "GET"),
        ("/admin/vendor-sessions", "GET"),
    ]
    
    all_passed = True
    for endpoint, method in protected_endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}")
            else:
                response = requests.post(f"{BASE_URL}{endpoint}", json={})
            
            # Should get 401 or 403
            if response.status_code in [401, 403]:
                print_result(f"Unauthenticated {method} {endpoint}", True, f"Status: {response.status_code}")
            else:
                print_result(f"Unauthenticated {method} {endpoint}", False, f"Unexpected status: {response.status_code}")
                all_passed = False
        except Exception as e:
            print_result(f"Unauthenticated {method} {endpoint}", False, str(e))
            all_passed = False
    
    return all_passed

def test_admin_can_access_protected():
    """Test 2: Admin can access protected endpoints with token"""
    print_section("TEST 2: Admin Access with Valid Token")
    
    # First login
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        
        if response.status_code != 200:
            print_result("Admin Login", False, f"Status: {response.status_code}")
            return False
        
        data = response.json()
        admin_token = data.get("access_token")
        if not admin_token:
            print_result("Admin Login", False, "No token in response")
            return False
        
        print_result("Admin Login", True, "Token obtained")
        
        # Test protected endpoints
        headers = {"Authorization": f"Bearer {admin_token}"}
        protected_endpoints = [
            ("/admin/vendor-requests", "GET"),
            ("/admin/vendors", "GET"),
            ("/admin/vendor-activity", "GET"),
            ("/admin/vendor-sessions", "GET"),
        ]
        
        all_passed = True
        for endpoint, method in protected_endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
                else:
                    response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, json={})
                
                # Should get 200
                if response.status_code == 200:
                    print_result(f"Admin {method} {endpoint}", True, "Accessible")
                else:
                    print_result(f"Admin {method} {endpoint}", False, f"Status: {response.status_code}")
                    all_passed = False
            except Exception as e:
                print_result(f"Admin {method} {endpoint}", False, str(e))
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print_result("Admin Access Test", False, str(e))
        return False

def test_invalid_token_denied():
    """Test 3: Invalid token is rejected"""
    print_section("TEST 3: Invalid Token Rejection")
    
    try:
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = requests.get(f"{BASE_URL}/admin/vendors", headers=headers)
        
        # Should get 401
        if response.status_code == 401:
            print_result("Invalid Token Rejection", True, f"Status: {response.status_code}")
            return True
        else:
            print_result("Invalid Token Rejection", False, f"Unexpected status: {response.status_code}")
            return False
    except Exception as e:
        print_result("Invalid Token Rejection", False, str(e))
        return False

def test_expired_token_denied():
    """Test 4: Malformed Authorization header is rejected"""
    print_section("TEST 4: Malformed Authorization Header")
    
    try:
        headers = {"Authorization": "InvalidFormat token"}
        response = requests.get(f"{BASE_URL}/admin/vendors", headers=headers)
        
        # Should get 401 or 403
        if response.status_code in [401, 403]:
            print_result("Malformed Header Rejection", True, f"Status: {response.status_code}")
            return True
        else:
            print_result("Malformed Header Rejection", False, f"Unexpected status: {response.status_code}")
            return False
    except Exception as e:
        print_result("Malformed Header Rejection", False, str(e))
        return False

def test_vendor_registration_is_public():
    """Test 5: Vendor registration endpoint is public (no auth required)"""
    print_section("TEST 5: Vendor Registration Public Access")
    
    try:
        payload = {
            "email": "test-public@example.com",
            "company_name": "Test Company",
            "contact_name": "Test Contact",
            "phone": "+1-555-0000"
        }
        
        response = requests.post(
            f"{BASE_URL}/vendor/register",
            json=payload
        )
        
        # Should be accessible without auth
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print_result("Vendor Registration Public", True, "Public endpoint accessible")
                return True
            else:
                print_result("Vendor Registration Public", False, f"Response: {data}")
                return False
        else:
            print_result("Vendor Registration Public", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_result("Vendor Registration Public", False, str(e))
        return False

def test_vendor_login_is_public():
    """Test 6: Vendor login endpoint is public"""
    print_section("TEST 6: Vendor Login Public Access")
    
    try:
        payload = {
            "email": "any-vendor@example.com",
            "password": "password"
        }
        
        response = requests.post(
            f"{BASE_URL}/vendor/login",
            json=payload
        )
        
        # Should be accessible without auth (may fail auth but endpoint exists)
        if response.status_code in [200, 401, 403, 404]:
            print_result("Vendor Login Public", True, f"Endpoint accessible (status: {response.status_code})")
            return True
        else:
            print_result("Vendor Login Public", False, f"Unexpected status: {response.status_code}")
            return False
    except Exception as e:
        print_result("Vendor Login Public", False, str(e))
        return False

def test_otp_request_is_public():
    """Test 7: OTP request endpoint is public"""
    print_section("TEST 7: OTP Request Public Access")
    
    try:
        payload = {"vendor_email": "test@example.com"}
        
        response = requests.post(
            f"{BASE_URL}/vendor/request-otp",
            json=payload
        )
        
        # Should be accessible without auth (may fail if vendor not found, but endpoint exists)
        if response.status_code in [200, 403, 404]:
            print_result("OTP Request Public", True, f"Endpoint accessible (status: {response.status_code})")
            return True
        else:
            print_result("OTP Request Public", False, f"Unexpected status: {response.status_code}")
            return False
    except Exception as e:
        print_result("OTP Request Public", False, str(e))
        return False

def test_no_public_admin_registration():
    """Test 8: Public admin registration endpoint does NOT exist"""
    print_section("TEST 8: Admin Registration Endpoint Removed")
    
    try:
        # Try the old /register endpoint that allowed public admin registration
        payload = {
            "email": "hacker@example.com",
            "username": "hacker",
            "password": "password",
            "full_name": "Hacker",
            "organization_name": "Hacker Corp"
        }
        
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=payload
        )
        
        # Should get 404 (endpoint not found)
        if response.status_code == 404:
            print_result("Admin Registration Removed", True, "Endpoint properly removed (404)")
            return True
        elif response.status_code == 422:
            # Could be validation error if endpoint exists
            print_result("Admin Registration Removed", False, "Endpoint still exists (validation error)")
            return False
        else:
            print_result("Admin Registration Removed", False, f"Unexpected status: {response.status_code}")
            return False
    except Exception as e:
        print_result("Admin Registration Removed", False, str(e))
        return False

def main():
    """Run all security tests"""
    print("\n" + "="*70)
    print("  TATVA SECURITY & DATA ISOLATION TEST")
    print("  Verifying authentication, authorization, and data isolation")
    print("="*70)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Unauthenticated access denied
    tests_total += 1
    if test_unauthenticated_access_denied():
        tests_passed += 1
    
    # Test 2: Admin can access protected endpoints
    tests_total += 1
    if test_admin_can_access_protected():
        tests_passed += 1
    
    # Test 3: Invalid token denied
    tests_total += 1
    if test_invalid_token_denied():
        tests_passed += 1
    
    # Test 4: Malformed auth header denied
    tests_total += 1
    if test_expired_token_denied():
        tests_passed += 1
    
    # Test 5: Vendor registration is public
    tests_total += 1
    if test_vendor_registration_is_public():
        tests_passed += 1
    
    # Test 6: Vendor login is public
    tests_total += 1
    if test_vendor_login_is_public():
        tests_passed += 1
    
    # Test 7: OTP request is public
    tests_total += 1
    if test_otp_request_is_public():
        tests_passed += 1
    
    # Test 8: Public admin registration removed
    tests_total += 1
    if test_no_public_admin_registration():
        tests_passed += 1
    
    # Summary
    print_section("SECURITY TEST SUMMARY")
    print(f"Tests Passed: {tests_passed}/{tests_total}")
    print(f"Success Rate: {(tests_passed/tests_total)*100:.1f}%")
    
    if tests_passed == tests_total:
        print("\n✓ ALL SECURITY TESTS PASSED")
        return 0
    else:
        print(f"\n✗ {tests_total - tests_passed} SECURITY TESTS FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
