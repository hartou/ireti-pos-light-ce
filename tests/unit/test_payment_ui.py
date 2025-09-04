#!/usr/bin/env python
"""
Payment UI component tests (moved from repo root to tests/unit).
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onlineretailpos.settings.devlopement')
django.setup()

from django.test import Client

def main():
    client = Client()
    response = client.get('/payments/')
    print(f"/payments/ -> {response.status_code}")
    response = client.get('/payments/terminal/')
    print(f"/payments/terminal/ -> {response.status_code}")

if __name__ == '__main__':
    main()
