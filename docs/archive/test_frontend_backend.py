#!/usr/bin/env python3
"""
Test frontend-backend connectivity through Vite proxy
"""

import requests
import json

def test_frontend_proxy():
    """Test if frontend proxy can reach backend"""
    print("Testing frontend proxy to backend...")
    
    # Test through Vite proxy (frontend port 5174)
    try:
        response = requests.get("http://localhost:5174/api/health")
        if response.status_code == 200:
            print("✅ Frontend proxy working!")
            print(f"Health check response: {response.json()}")
            return True
        else:
            print(f"❌ Frontend proxy failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend proxy error: {e}")
        return False

def test_direct_backend():
    """Test direct backend access"""
    print("\nTesting direct backend access...")
    
    try:
        response = requests.get("http://localhost:8000/api/health")
        if response.status_code == 200:
            print("✅ Direct backend working!")
            print(f"Health check response: {response.json()}")
            return True
        else:
            print(f"❌ Direct backend failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Direct backend error: {e}")
        return False

def test_vendor_login_through_proxy():
    """Test vendor login through frontend proxy"""
    print("\nTesting vendor login through frontend proxy...")
    
    try:
        response = requests.post("http://localhost:5174/api/vendor/login", json={
            "email": "kingmp142@gmail.com",
            "password": "Enhanced@123"
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ Vendor login through proxy working!")
                return True
            else:
                print(f"❌ Vendor login failed: {data}")
                return False
        else:
            print(f"❌ Vendor login request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Vendor login error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Frontend-Backend Integration")
    print("=" * 40)
    
    backend_ok = test_direct_backend()
    proxy_ok = test_frontend_proxy()
    login_ok = test_vendor_login_through_proxy()
    
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    print(f"  Direct Backend: {'✓' if backend_ok else '✗'}")
    print(f"  Frontend Proxy: {'✓' if proxy_ok else '✗'}")
    print(f"  Vendor Login:   {'✓' if login_ok else '✗'}")
    
    if all([backend_ok, proxy_ok, login_ok]):
        print("🎉 All tests passed! Frontend ready for use.")
    else:
        print("❌ Some tests failed. Check configuration.")