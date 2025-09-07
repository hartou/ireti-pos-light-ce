#!/usr/bin/env python
"""
Simple API test (moved to tests/unit)
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iretilightpos.settings')
django.setup()

from django.test import Client
import json

def main():
    client = Client()
    print("🔎 Running simple API smoke checks")
    response = client.get('/payments/api/recent/')
    print(f"Recent API status: {response.status_code}")

if __name__ == '__main__':
    main()
