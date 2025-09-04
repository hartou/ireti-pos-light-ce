#!/usr/bin/env python
"""
Integration tests for Stripe webhook handlers (moved from repo root).
"""

import os
import sys
import json
import hashlib
import hmac
import time

# Set up Django environment for integration tests
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onlineretailpos.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django
django.setup()

from django.test import Client
from django.conf import settings

class WebhookTester:
    def __init__(self):
        self.client = Client()
        self.webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', 'whsec_test')

    def create_webhook_signature(self, payload: str, timestamp: int = None) -> str:
        if timestamp is None:
            timestamp = int(time.time())
        signed_payload = f"{timestamp}.{payload}"
        signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            signed_payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return f"t={timestamp},v1={signature}"

    def create_test_event(self, event_type: str, event_data: dict) -> dict:
        return {
            "id": f"evt_test_{int(time.time())}",
            "object": "event",
            "api_version": "2024-06-20",
            "created": int(time.time()),
            "data": {"object": event_data},
            "livemode": False,
            "pending_webhooks": 1,
            "request": {"id": f"req_test_{int(time.time())}", "idempotency_key": None},
            "type": event_type
        }

    def test_payment_intent_succeeded(self):
        payment_intent_data = {
            "id": "pi_test_webhook_123",
            "object": "payment_intent",
            "amount": 1234,
            "currency": "usd",
            "status": "succeeded",
            "created": int(time.time()),
            "client_secret": "pi_test_webhook_123_secret",
            "metadata": {"test_webhook": "true"}
        }
        event = self.create_test_event("payment_intent.succeeded", payment_intent_data)
        payload = json.dumps(event)
        signature = self.create_webhook_signature(payload)
        response = self.client.post('/payments/webhook/', data=payload, content_type='application/json', HTTP_STRIPE_SIGNATURE=signature)
        return response.status_code == 200

if __name__ == '__main__':
    tester = WebhookTester()
    success = tester.test_payment_intent_succeeded()
    sys.exit(0 if success else 1)
