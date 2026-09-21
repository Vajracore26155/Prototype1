import requests
import sys

try:
    r = requests.get('http://127.0.0.1:8000/health', timeout=2)
    print(f"✓ Backend is UP - HTTP {r.status_code}")
    print(f"Response: {r.text[:200]}")
except ConnectionRefusedError:
    print("✗ Backend is DOWN - Connection refused")
    sys.exit(1)
except Exception as e:
    print(f"✗ Backend error: {type(e).__name__}: {str(e)[:100]}")
    sys.exit(1)
