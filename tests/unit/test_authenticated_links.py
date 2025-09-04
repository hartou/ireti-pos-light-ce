#!/usr/bin/env python
"""
Test authenticated access to broken links URLs (moved under tests/unit).
"""

import os
import django
from django.test import Client
from django.contrib.auth.models import User
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onlineretailpos.settings.devlopement')
django.setup()

def test_authenticated_access():
    client = Client()
    try:
        user = User.objects.get(username='testuser')
    except User.DoesNotExist:
        user = User.objects.create_superuser('testuser', 'test@example.com', 'testpass123')

    login_success = client.login(username='testuser', password='testpass123')
    if not login_success:
        print("❌ Failed to login test user")
        return

    urls_to_test = [
        '/dashboard_sales/',
        '/dashboard_department/',
        '/dashboard_products/',
        '/transaction/',
        '/register/product_lookup/',
        '/inventory/',
        '/staff_portal/',
        '/staff_portal/auth/group/',
        '/retail_display/',
    ]

    for url in urls_to_test:
        response = client.get(url)
        print(f"{url} -> {response.status_code}")

if __name__ == '__main__':
    test_authenticated_access()
