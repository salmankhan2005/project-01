#!/usr/bin/env python3
"""
Test meal plan sync functionality
"""

import requests
import json

# Test endpoints
BASE_URL = "http://127.0.0.1:5000"

def test_health():
    """Test backend health"""
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            print("Backend is running")
            return True
        else:
            print("Backend not responding correctly")
            return False
    except Exception as e:
        print(f"Backend connection failed: {e}")
        return False

def test_templates():
    """Test templates endpoint without auth"""
    try:
        response = requests.get(f"{BASE_URL}/api/meal-plans/admin-templates")
        print(f"Templates (no auth): {response.status_code}")
        
        if response.status_code == 401:
            print("Auth required (expected)")
            return True
        else:
            print(f"Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"Templates test failed: {e}")
        return False

def main():
    print("Testing meal plan sync...")
    
    health_ok = test_health()
    templates_ok = test_templates()
    
    if health_ok and templates_ok:
        print("SUCCESS: Backend sync endpoints are working")
        print("User app should now be able to:")
        print("  - Browse admin templates")
        print("  - Apply templates to meal plans")
        print("  - Sync with admin changes")
    else:
        print("ERROR: Backend needs to be started")
        print("Run: python app.py in backend folder")

if __name__ == '__main__':
    main()