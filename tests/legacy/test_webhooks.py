#!/usr/bin/env python
"""
Legacy webhook endpoint tester.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onlineretailpos.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.conf import settings

def create_signature(payload: str, secret: str):
    import hashlib, hmac, time
    ts = int(time.time())
    signed = f"{ts}.{payload}"
    sig = hmac.new(secret.encode(), signed.encode(), hashlib.sha256).hexdigest()
    return f"t={ts},v1={sig}"

print('Legacy webhook tester added')
