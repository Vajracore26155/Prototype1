#!/usr/bin/env python3
"""
Phase 5 Comprehensive Test Suite
Tests: Device Management, Drift Detection, Posture Scoring, Remediation
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name):
    print(f"\n{Colors.BLUE}Testing: {name}{Colors.END}")

def print_success(msg):
    print(f"{Colors.GREEN}OK {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}ERR {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}WARN {msg}{Colors.END}")

# Test Auth
def get_auth_token():
    """Get auth token for tests"""
    print_test("Authentication Setup")
    
    # Register user
    response = requests.post(f"{BASE_URL}/api/auth/register", json={
        "email": "test@phase5.com",
        "username": "phase5test",
        "password": "TestPass123!",
        "full_name": "Phase 5 Tester",
        "organization_name": "Phase5 Test Org"
    })
    
    if response.status_code in [200, 201]:
        print_success("User registered")
    elif response.status_code == 400 and "already" in response.text.lower():
        print_warning("User already exists, continuing...")
    else:
        print_error(f"Registration failed: {response.text}")
        return None
    
    # Login
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "test@phase5.com",
        "password": "TestPass123!"
    })
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print_success(f"Logged in successfully")
        return token
    else:
        print_error(f"Login failed: {response.text}")
        return None

def test_device_management(token):
    """Test Phase 5 Device Management"""
    print_test("Device Management API")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create device
    device_data = {
        "hostname": "test-firewall-01",
        "ip_address": "192.168.1.100",
        "vendor": "CISCO",
        "device_type": "FIREWALL",
        "model": "ASA5516",
        "location": "DataCenter-A",
        "owner": "NetOps Team",
        "status": "ACTIVE"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/devices",
        headers=headers,
        json=device_data
    )
    
    if response.status_code == 200:
        device = response.json()["data"]
        device_id = device["device_id"]
        print_success(f"Device created: {device_id}")
        
        # Get device
        response = requests.get(
            f"{BASE_URL}/api/devices/{device_id}",
            headers=headers
        )
        if response.status_code == 200:
            print_success("Device retrieved successfully")
        else:
            print_error(f"Failed to get device: {response.status_code}")
        
        # List devices
        response = requests.get(
            f"{BASE_URL}/api/devices",
            headers=headers
        )
        if response.status_code == 200:
            devices = response.json()["data"]["devices"]
            print_success(f"Listed {len(devices)} devices")
        else:
            print_error(f"Failed to list devices: {response.status_code}")
        
        # Update device
        response = requests.put(
            f"{BASE_URL}/api/devices/{device_id}",
            headers=headers,
            json={"location": "DataCenter-B", "status": "MAINTENANCE"}
        )
        if response.status_code == 200:
            print_success("Device updated successfully")
        else:
            print_error(f"Failed to update device: {response.status_code}")
        
        # Device statistics
        response = requests.get(
            f"{BASE_URL}/api/devices/statistics",
            headers=headers
        )
        if response.status_code == 200:
            stats = response.json()["data"]
            print_success(f"Device stats: {stats}")
        else:
            print_error(f"Failed to get stats: {response.status_code}")
        
        return device_id
    else:
        print_error(f"Device creation failed: {response.text}")
        return None

def test_drift_detection(token, device_id):
    """Test Phase 5 Drift Detection"""
    print_test("Drift Detection")
    headers = {"Authorization": f"Bearer {token}"}
    
    if not device_id:
        print_warning("Skipping drift test - no device ID")
        return
    
    # Detect drift
    response = requests.post(
        f"{BASE_URL}/api/devices/{device_id}/detect-drift",
        headers=headers,
        json={
            "baseline_version_id": None,  # Will use latest
            "current_config": "hostname test-firewall-01\nip address 192.168.1.100\naccess-list 100 permit ip any any"
        }
    )
    
    if response.status_code == 200:
        drift = response.json()["data"]
        print_success(f"Drift detected: Score={drift.get('drift_score', 'N/A')}, Severity={drift.get('drift_severity', 'N/A')}")
        
        drift_id = drift.get("drift_id")
        if drift_id:
            # Get drift history
            response = requests.get(
                f"{BASE_URL}/api/devices/{device_id}/drift-history",
                headers=headers
            )
            if response.status_code == 200:
                history = response.json()["data"]["drift_history"]
                print_success(f"Drift history: {len(history)} entries")
            else:
                print_error(f"Failed to get drift history: {response.status_code}")
            
            # Acknowledge drift
            response = requests.post(
                f"{BASE_URL}/api/drift/{drift_id}/acknowledge",
                headers=headers,
                json={"notes": "Acknowledged for testing"}
            )
            if response.status_code == 200:
                print_success("Drift acknowledged")
            else:
                print_error(f"Failed to acknowledge drift: {response.status_code}")
            
            # Drift summary
            response = requests.get(
                f"{BASE_URL}/api/dashboard/drift-summary",
                headers=headers
            )
            if response.status_code == 200:
                summary = response.json()["data"]
                print_success(f"Drift summary: {summary}")
            else:
                print_error(f"Failed to get drift summary: {response.status_code}")
    else:
        print_warning(f"Drift detection returned: {response.status_code}")

def test_posture_scoring(token, device_id):
    """Test Phase 5 Posture Scoring"""
    print_test("Posture Scoring")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Organization posture
    response = requests.get(
        f"{BASE_URL}/api/posture/organization",
        headers=headers
    )
    if response.status_code == 200:
        posture = response.json()["data"]
        print_success(f"Org posture score: {posture.get('score', 'N/A')}/100")
    else:
        print_error(f"Failed to get org posture: {response.status_code}")
    
    # Device postures
    response = requests.get(
        f"{BASE_URL}/api/posture/devices",
        headers=headers
    )
    if response.status_code == 200:
        devices = response.json()["data"]["devices"]
        print_success(f"Device postures: {len(devices)} devices")
    else:
        print_error(f"Failed to get device postures: {response.status_code}")
    
    if device_id:
        # Single device posture
        response = requests.get(
            f"{BASE_URL}/api/posture/devices/{device_id}",
            headers=headers
        )
        if response.status_code == 200:
            posture = response.json()["data"]
            print_success(f"Device posture: {posture.get('score', 'N/A')}/100")
        else:
            print_warning(f"Device posture not available: {response.status_code}")
    
    # Posture trends
    response = requests.get(
        f"{BASE_URL}/api/posture/trends",
        headers=headers,
        params={"days": 7}
    )
    if response.status_code == 200:
        trends = response.json()["data"]["trends"]
        print_success(f"Posture trends: {len(trends)} data points")
    else:
        print_error(f"Failed to get posture trends: {response.status_code}")
    
    # Posture breakdown
    response = requests.get(
        f"{BASE_URL}/api/posture/breakdown",
        headers=headers
    )
    if response.status_code == 200:
        breakdown = response.json()["data"]
        print_success(f"Posture breakdown: {breakdown}")
    else:
        print_error(f"Failed to get posture breakdown: {response.status_code}")

def test_remediation(token, device_id):
    """Test Phase 5 Remediation"""
    print_test("Remediation Management")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create remediation plan
    plan_data = {
        "device_id": device_id,
        "title": "Test Remediation Plan",
        "description": "Fix configuration drift",
        "finding_ids": [],
        "remediation_commands": "no access-list 100\naccess-list 100 permit ip 10.0.0.0 0.255.255.255 any",
        "rollback_commands": "access-list 100 permit ip any any",
        "estimated_impact": "LOW",
        "estimated_downtime": "< 1 minute",
        "requires_approval": True
    }
    
    response = requests.post(
        f"{BASE_URL}/api/remediation/plans",
        headers=headers,
        json=plan_data
    )
    
    if response.status_code == 200:
        plan = response.json()["data"]
        plan_id = plan["plan_id"]
        print_success(f"Remediation plan created: {plan_id}")
        
        # List plans
        response = requests.get(
            f"{BASE_URL}/api/remediation/plans",
            headers=headers
        )
        if response.status_code == 200:
            plans = response.json()["data"]["plans"]
            print_success(f"Listed {len(plans)} remediation plans")
        else:
            print_error(f"Failed to list plans: {response.status_code}")
        
        # Get plan details
        response = requests.get(
            f"{BASE_URL}/api/remediation/plans/{plan_id}",
            headers=headers
        )
        if response.status_code == 200:
            print_success("Plan details retrieved")
        else:
            print_error(f"Failed to get plan details: {response.status_code}")
        
        # Pending approvals
        response = requests.get(
            f"{BASE_URL}/api/remediation/pending-approvals",
            headers=headers
        )
        if response.status_code == 200:
            pending = response.json()["data"]["pending"]
            print_success(f"Pending approvals: {len(pending)}")
        else:
            print_error(f"Failed to get pending approvals: {response.status_code}")
        
        # Approve plan
        response = requests.post(
            f"{BASE_URL}/api/remediation/plans/{plan_id}/approve",
            headers=headers,
            json={
                "decision": "APPROVE",
                "comments": "Approved for testing"
            }
        )
        if response.status_code == 200:
            print_success("Plan approved successfully")
        else:
            print_error(f"Failed to approve plan: {response.status_code}")
    else:
        print_error(f"Failed to create remediation plan: {response.text}")

def main():
    print("\n" + "="*60)
    print("  PHASE 5 COMPREHENSIVE TEST SUITE")
    print("  Testing: Device, Drift, Posture, Remediation")
    print("="*60)
    
    # Get auth token
    token = get_auth_token()
    if not token:
        print_error("Authentication failed. Cannot proceed with tests.")
        return
    
    # Test Device Management
    device_id = test_device_management(token)
    
    # Test Drift Detection
    test_drift_detection(token, device_id)
    
    # Test Posture Scoring
    test_posture_scoring(token, device_id)
    
    # Test Remediation
    test_remediation(token, device_id)
    
    print("\n" + "="*60)
    print(f"{Colors.GREEN}  PHASE 5 TESTING COMPLETE{Colors.END}")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Test interrupted by user{Colors.END}")
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to backend. Is the server running on http://localhost:8000?")
        print_warning("Start server with: cd backend && python -m uvicorn app.main:app --reload")
    except Exception as e:
        print_error(f"Test error: {str(e)}")
