#!/usr/bin/env python3
"""
Legacy copy of test_payment_api
"""

...existing code...
#!/usr/bin/env python
"""
Test script for Payment API endpoints (legacy copy).
"""

import os
import sys
import json
import django
from decimal import Decimal

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onlineretailpos.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from payments.models import PaymentTransaction

class PaymentAPITester:
    def __init__(self):
        self.client = Client()
        self.base_url = 'http://localhost:8000'
        self.test_user = None
        self.created_payment_intent = None
    
    def setup_test_user(self):
        try:
            self.test_user = User.objects.get(username='test_payment_user')
        except User.DoesNotExist:
            self.test_user = User.objects.create_user(
                username='test_payment_user',
                password='testpass123',
                email='test@example.com'
            )
        print(f"✅ Test user set up: {self.test_user.username}")

    # ... (rest of tests preserved in legacy file)

if __name__ == '__main__':
    tester = PaymentAPITester()
    success = tester.run_all_tests() if hasattr(tester, 'run_all_tests') else False
    sys.exit(0 if success else 1)