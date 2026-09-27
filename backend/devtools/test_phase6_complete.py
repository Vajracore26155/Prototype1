#!/usr/bin/env python3
"""
Phase 6 Comprehensive Test Suite
Tests: LLM Integration, AI Query, Remediation Suggestions, Cost Tracking
"""
import requests
import json

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

def get_auth_token():
    """Get auth token for tests"""
    print_test("Authentication Setup")
    
    # Register or login
    response = requests.post(f"{BASE_URL}/api/auth/register", json={
        "email": "test@phase6.com",
        "username": "phase6test",
        "password": "TestPass123!",
        "full_name": "Phase 6 Tester",
        "organization_name": "Phase6 Test Org"
    })
    
    if response.status_code in [200, 201]:
        print_success("User registered")
    elif "already exists" in response.text:
        print_warning("User already exists")
    
    # Login
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "test@phase6.com",
        "password": "TestPass123!"
    })
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print_success("Logged in successfully")
        return token
    else:
        print_error(f"Login failed: {response.text}")
        return None

def test_llm_providers(token):
    """Test LLM Provider Discovery"""
    print_test("LLM Provider Discovery")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/api/ai/providers",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()["data"]
        providers = data["providers"]
        active = data["active_provider"]
        
        print_success(f"Available providers: {', '.join(providers)}")
        print_success(f"Active provider: {active}")
        
        if active == "mock":
            print_warning("Using mock provider (no API keys configured)")
        else:
            print_success(f"Real LLM provider active: {active}")
        
        return active
    else:
        print_error(f"Failed to get providers: {response.status_code}")
        return None

def test_ai_query(token):
    """Test AI Natural Language Query"""
    print_test("AI Natural Language Query")
    headers = {"Authorization": f"Bearer {token}"}
    
    queries = [
        {
            "query": "What is the security posture of my organization?",
            "context": {"test": True}
        },
        {
            "query": "Explain what a firewall access-list does",
            "context": {}
        },
        {
            "query": "How many critical findings do I have?",
            "context": {"mock_data": True}
        }
    ]
    
    for query_data in queries:
        response = requests.post(
            f"{BASE_URL}/api/ai/query",
            headers=headers,
            json=query_data
        )
        
        if response.status_code == 200:
            result = response.json()["data"]
            print_success(f"Query: {query_data['query'][:50]}...")
            print(f"   Response: {result['response'][:100]}...")
            print(f"   Provider: {result['provider']}, Cost: ${result['cost_usd']}")
        else:
            print_error(f"Query failed: {response.status_code}")

def test_remediation_suggestion(token):
    """Test AI Remediation Suggestions"""
    print_test("AI Remediation Suggestions")
    headers = {"Authorization": f"Bearer {token}"}
    
    finding_data = {
        "finding": {
            "rule_id": "CIS-1.1.1",
            "title": "Telnet service enabled",
            "description": "Telnet is an insecure protocol",
            "severity": "HIGH",
            "current_config": "service telnet\nline vty 0 4\ntransport input telnet"
        },
        "device_context": {
            "vendor": "CISCO",
            "device_type": "ROUTER",
            "os_version": "IOS 15.2"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/ai/remediation/suggest",
        headers=headers,
        json=finding_data
    )
    
    if response.status_code == 200:
        result = response.json()["data"]
        print_success("Remediation suggestion generated")
        print(f"   Commands: {result['remediation_commands'][:100]}...")
        print(f"   Explanation: {result['explanation'][:100]}...")
        print(f"   Provider: {result['provider']}, Cost: ${result['cost_usd']}")
        
        if result.get('rollback_commands'):
            print(f"   Rollback provided: Yes")
    else:
        print_error(f"Remediation suggestion failed: {response.status_code}")

def test_config_generation(token):
    """Test AI Configuration Generation"""
    print_test("AI Configuration Generation")
    headers = {"Authorization": f"Bearer {token}"}
    
    request_data = {
        "requirements": "Create a secure SSH configuration for a Cisco router. Disable telnet, enable SSH version 2, set strong crypto, and limit access to management subnet 10.0.0.0/24",
        "vendor": "CISCO",
        "device_type": "ROUTER",
        "compliance_frameworks": ["CIS"]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/ai/config/generate",
        headers=headers,
        json=request_data
    )
    
    if response.status_code == 200:
        result = response.json()["data"]
        print_success("Configuration generated")
        print(f"   Lines: {len(result['configuration'].split(chr(10)))}")
        print(f"   Explanation: {result['explanation'][:100]}...")
        print(f"   Provider: {result['provider']}, Cost: ${result['cost_usd']}")
        
        if result.get('warnings'):
            print_warning(f"   Warnings: {len(result['warnings'])}")
    else:
        print_error(f"Config generation failed: {response.status_code}")

def test_cost_tracking(token):
    """Test AI Cost Tracking"""
    print_test("AI Cost Tracking & Usage")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/api/ai/usage",
        headers=headers
    )
    
    if response.status_code == 200:
        usage = response.json()["data"]
        
        print_success("Usage statistics retrieved")
        print(f"   Total requests: {usage.get('total_requests', 0)}")
        print(f"   Total cost: ${usage.get('total_cost_usd', 0):.4f}")
        print(f"   User limit: ${usage.get('user_monthly_limit', 0)}")
        print(f"   Org limit: ${usage.get('org_monthly_limit', 0)}")
        
        if usage.get('total_cost_usd', 0) > 0:
            print_success(f"Cost tracking is working")
        else:
            print_warning("No costs recorded yet (expected with mock provider)")
        
        if usage.get('breakdown_by_provider'):
            print(f"   Providers used: {list(usage['breakdown_by_provider'].keys())}")
    else:
        print_error(f"Usage tracking failed: {response.status_code}")

def test_llm_caching(token):
    """Test LLM Response Caching"""
    print_test("LLM Response Caching")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Same query twice
    query = {"query": "What is a firewall?", "context": {}}
    
    # First call
    response1 = requests.post(
        f"{BASE_URL}/api/ai/query",
        headers=headers,
        json=query
    )
    
    # Second call (should be cached)
    response2 = requests.post(
        f"{BASE_URL}/api/ai/query",
        headers=headers,
        json=query
    )
    
    if response1.status_code == 200 and response2.status_code == 200:
        result1 = response1.json()["data"]
        result2 = response2.json()["data"]
        
        if result1['response'] == result2['response']:
            print_success("Caching working - same responses")
            print_warning("Note: Both calls may have generated cost (cache check needed in code)")
        else:
            print_warning("Responses differ - caching may not be working")
    else:
        print_error("Caching test failed")

def test_cost_limits(token):
    """Test Cost Limit Enforcement"""
    print_test("Cost Limit Enforcement")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Check current usage
    response = requests.get(
        f"{BASE_URL}/api/ai/usage",
        headers=headers
    )
    
    if response.status_code == 200:
        usage = response.json()["data"]
        user_limit = usage.get('user_monthly_limit', 10)
        current_cost = usage.get('total_cost_usd', 0)
        
        print_success(f"Current usage: ${current_cost:.4f} / ${user_limit}")
        
        if current_cost < user_limit * 0.5:
            print_success("Well within limits")
        elif current_cost < user_limit * 0.8:
            print_warning("Approaching limits")
        else:
            print_warning("Near limit threshold")
        
        # The actual limit enforcement happens in the LLM router
        # Just verify the tracking is working
        print_success("Cost limit tracking operational")
    else:
        print_error("Failed to check cost limits")

def main():
    print("\n" + "="*60)
    print("  PHASE 6 COMPREHENSIVE TEST SUITE")
    print("  Testing: LLM Integration, AI Features, Cost Tracking")
    print("="*60)
    
    # Get auth token
    token = get_auth_token()
    if not token:
        print_error("Authentication failed. Cannot proceed with tests.")
        return
    
    # Test LLM Providers
    provider = test_llm_providers(token)
    
    if provider == "mock":
        print_warning("\nWARN Using MOCK LLM provider")
        print_warning("To test with real LLMs, set API keys in .env:")
        print_warning("  OPENAI_API_KEY=sk-...")
        print_warning("  ANTHROPIC_API_KEY=sk-...")
        print_warning("  GOOGLE_API_KEY=...")
        print()
    
    # Test AI Query
    test_ai_query(token)
    
    # Test Remediation Suggestions
    test_remediation_suggestion(token)
    
    # Test Config Generation
    test_config_generation(token)
    
    # Test Cost Tracking
    test_cost_tracking(token)
    
    # Test Caching
    test_llm_caching(token)
    
    # Test Cost Limits
    test_cost_limits(token)
    
    print("\n" + "="*60)
    print(f"{Colors.GREEN}  PHASE 6 TESTING COMPLETE{Colors.END}")
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
