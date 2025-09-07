#!/usr/bin/env python
"""
Payment API tests (moved to tests/unit)
"""

import os
import sys
import json
from decimal import Decimal
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iretilightpos.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from django.test import Client

def main():
    client = Client()
    response = client.get('/payments/api/recent/')
    print(f"Recent payments API: {response.status_code}")

if __name__ == '__main__':
    main()
