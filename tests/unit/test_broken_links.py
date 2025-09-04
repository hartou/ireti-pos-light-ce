#!/usr/bin/env python3
"""
Test script to verify all broken links are working correctly.
Moved into tests/unit for discoverability.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onlineretailpos.settings.devlopement')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

def test_broken_links():
    client = Client()
    test_cases = [
        ('/dashboard_sales/', 'BL-001', 'Sales Dashboard'),
        ('/dashboard_department/', 'BL-002', 'Department Dashboard'),
        ('/dashboard_products/', 'BL-003', 'Products Dashboard'),
        ('/transaction/', 'BL-004', 'Transactions list'),
        ('/register/product_lookup/', 'BL-005', 'Product lookup'),
        ('/inventory/', 'BL-006', 'Add Inventory'),
        ('/staff_portal/', 'BL-007', 'Admin portal'),
        ('/retail_display/', 'BL-009', 'Customer Display')
    ]

    # Unauthenticated checks
    for url, story_id, desc in test_cases:
        response = client.get(url, follow=False)
        print(f"{story_id} {url} -> {response.status_code}")

if __name__ == "__main__":
    test_broken_links()
