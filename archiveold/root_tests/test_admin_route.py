#!/usr/bin/env python3
"""
Test script to verify admin routes are properly registered
"""

import requests
import json

# Base URL
BASE_URL = "http://localhost:8000"

def test_admin_routes():
    """Test if admin routes are accessible"""
    
    routes_to_test = [
        "/ui/admin/maintenance",
        "/ui/admin/image-jobs",
        "/ui/admin/users",
        "/ui/admin/billing"
    ]
    
    print("Testing admin routes...\n")
    
    for route in routes_to_test:
        url = f"{BASE_URL}{route}"
        try:
            response = requests.get(url, allow_redirects=False, timeout=5)
            print(f"Route: {route}")
            print(f"  Status: {response.status_code}")
            print(f"  Content-Type: {response.headers.get('content-type', 'N/A')}")
            
            if response.status_code == 302:
                print(f"  Redirect to: {response.headers.get('location', 'N/A')}")
            elif response.status_code == 200:
                print(f"  ✅ Page accessible")
            
            print()
            
        except Exception as e:
            print(f"Route: {route}")
            print(f"  ❌ Error: {e}\n")

def test_api_endpoints():
    """Test if API endpoints are available"""
    
    api_endpoints = [
        "/api/v1/generate-image/jobs",
        "/api/v1/maintenance/status"
    ]
    
    print("\nTesting API endpoints...\n")
    
    for endpoint in api_endpoints:
        url = f"{BASE_URL}{endpoint}"
        try:
            response = requests.get(url, timeout=5)
            print(f"Endpoint: {endpoint}")
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✅ API accessible")
                data = response.json()
                print(f"  Response: {json.dumps(data, indent=2)[:200]}...")
            
            print()
            
        except Exception as e:
            print(f"Endpoint: {endpoint}")
            print(f"  ❌ Error: {e}\n")

if __name__ == "__main__":
    print("=== Admin Route Testing ===\n")
    print(f"Testing server at: {BASE_URL}\n")
    
    test_admin_routes()
    test_api_endpoints()
    
    print("\nNote: 302 redirects usually mean authentication is required.")
    print("200 status means the page is accessible.")
    print("\nMake sure you're logged in as an admin user to access admin pages.")