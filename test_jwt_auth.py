#!/usr/bin/env python3
"""
JWT Authentication Test Script
Tests the enhanced JWT authentication system for the Home Management System.
"""

import requests
import json
import os
from datetime import datetime

class JWTAuthTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token = None
        self.refresh_token = None
    
    def test_health(self):
        """Test health endpoint"""
        print("🔍 Testing health endpoint...")
        response = self.session.get(f"{self.base_url}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    
    def test_register(self, username, email, full_name, password):
        """Test user registration"""
        print(f"📝 Testing registration for {username}...")
        data = {
            "username": username,
            "email": email,
            "full_name": full_name,
            "password": password
        }
        response = self.session.post(f"{self.base_url}/register", data=data, allow_redirects=False)
        print(f"Status: {response.status_code}")
        return response.status_code == 303
    
    def test_login_api(self, username, password):
        """Test API login (OAuth2)"""
        print(f"🔐 Testing API login for {username}...")
        data = {
            "username": username,
            "password": password
        }
        response = self.session.post(f"{self.base_url}/token", data=data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data.get("access_token")
            self.refresh_token = token_data.get("refresh_token")
            print(f"Access token received: {self.access_token[:20]}...")
            print(f"Refresh token received: {self.refresh_token[:20]}...")
            print(f"Expires in: {token_data.get('expires_in')} seconds")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    
    def test_authenticated_request(self):
        """Test authenticated API request"""
        if not self.access_token:
            print("❌ No access token available")
            return False
        
        print("🔒 Testing authenticated request...")
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = self.session.get(f"{self.base_url}/me", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"User info: {user_data}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    
    def test_token_info(self):
        """Test token info endpoint"""
        if not self.access_token:
            print("❌ No access token available")
            return False
        
        print("ℹ️ Testing token info...")
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = self.session.get(f"{self.base_url}/token-info", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            token_info = response.json()
            print(f"Token info: {token_info}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    
    def test_refresh_token(self):
        """Test token refresh"""
        if not self.refresh_token:
            print("❌ No refresh token available")
            return False
        
        print("🔄 Testing token refresh...")
        data = {"refresh_token": self.refresh_token}
        response = self.session.post(f"{self.base_url}/refresh", json=data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            old_token = self.access_token[:20] if self.access_token else "None"
            self.access_token = token_data.get("access_token")
            new_token = self.access_token[:20] if self.access_token else "None"
            print(f"Old token: {old_token}...")
            print(f"New token: {new_token}...")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    
    def test_logout(self):
        """Test logout"""
        if not self.access_token:
            print("❌ No access token available")
            return False
        
        print("🚪 Testing logout...")
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = self.session.post(f"{self.base_url}/logout", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"Logout response: {response.json()}")
            # Clear tokens
            self.access_token = None
            self.refresh_token = None
            return True
        else:
            print(f"Error: {response.text}")
            return False
    
    def test_invalid_token(self):
        """Test request with invalid token"""
        print("🚫 Testing invalid token...")
        headers = {"Authorization": "Bearer invalid_token_here"}
        response = self.session.get(f"{self.base_url}/me", headers=headers)
        print(f"Status: {response.status_code}")
        return response.status_code == 401
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 Starting JWT Authentication Tests")
        print("=" * 50)
        
        test_user = {
            "username": f"testuser_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "email": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com",
            "full_name": "Test User",
            "password": "TestPass123!"
        }
        
        tests = [
            ("Health Check", self.test_health),
            ("User Registration", lambda: self.test_register(**test_user)),
            ("API Login", lambda: self.test_login_api(test_user["username"], test_user["password"])),
            ("Authenticated Request", self.test_authenticated_request),
            ("Token Info", self.test_token_info),
            ("Token Refresh", self.test_refresh_token),
            ("Invalid Token", self.test_invalid_token),
            ("Logout", self.test_logout),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n--- {test_name} ---")
            try:
                if test_func():
                    print(f"✅ {test_name} PASSED")
                    passed += 1
                else:
                    print(f"❌ {test_name} FAILED")
            except Exception as e:
                print(f"💥 {test_name} ERROR: {e}")
        
        print("\n" + "=" * 50)
        print(f"🏁 Tests completed: {passed}/{total} passed")
        
        if passed == total:
            print("🎉 All tests passed! JWT authentication is working correctly.")
        else:
            print(f"⚠️ {total - passed} tests failed. Check the output above for details.")
        
        return passed == total

if __name__ == "__main__":
    import sys
    
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    tester = JWTAuthTester(base_url)
    
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)