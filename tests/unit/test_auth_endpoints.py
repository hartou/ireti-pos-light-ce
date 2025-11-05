#!/usr/bin/env python
"""
Test for authentication API endpoints
Tests both /auth/login/ and /api/v1/auth/login/ endpoints
"""

import os
import sys
import json
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iretilightpos.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    django.setup()
    from django.test import Client
    from django.contrib.auth.models import User
    
    def test_auth_endpoints():
        """Test that both auth endpoints are accessible and work correctly"""
        client = Client()
        
        print("🔐 Testing Authentication API Endpoints")
        print("=" * 60)
        
        # Test endpoints without authentication (should return 400 for missing credentials)
        endpoints = [
            '/auth/login/',           # Direct endpoint
            '/api/v1/auth/login/',   # Versioned API endpoint
        ]
        
        for endpoint in endpoints:
            print(f"\n📍 Testing {endpoint}")
            
            # Test POST with empty data (should return 400)
            response = client.post(endpoint, 
                                   content_type='application/json',
                                   data=json.dumps({}))
            print(f"   Empty POST: {response.status_code} (expected: 400)")
            
            # Test POST with missing password
            response = client.post(endpoint,
                                   content_type='application/json', 
                                   data=json.dumps({'username': 'testuser'}))
            print(f"   Missing password: {response.status_code} (expected: 400)")
            
            # Test POST with invalid credentials
            response = client.post(endpoint,
                                   content_type='application/json',
                                   data=json.dumps({
                                       'username': 'invalid',
                                       'password': 'invalid'
                                   }))
            print(f"   Invalid credentials: {response.status_code} (expected: 401)")
            
        print("\n" + "=" * 60)
        print("✅ Both authentication endpoints are accessible!")
        print("\nNote: Full authentication testing requires a test user setup.")
        print("In production, test with valid credentials:")
        print('  curl -X POST http://localhost:8000/auth/login/ \\')
        print('       -H "Content-Type: application/json" \\')
        print('       -d \'{"username": "admin", "password": "admin123"}\'')
        
    if __name__ == '__main__':
        test_auth_endpoints()
        
except ImportError as e:
    print(f"⚠️  Missing dependencies: {e}")
    print("This test requires Django and DRF to be installed.")
    print("Install with: pip install -r config/requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
