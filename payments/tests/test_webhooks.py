"""
Comprehensive webhook tests for Stripe integration.
Tests webhook processing with proper signatures and event handling.
"""

import json
import hashlib
import hmac
import time
from unittest.mock import patch, Mock
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.conf import settings

from payments.models import PaymentTransaction, PaymentWebhook


User = get_user_model()


class StripeWebhookTest(TestCase):
    """Test Stripe webhook processing with signed payloads."""
    
    def setUp(self):
        """Set up test environment."""
        self.client = Client()
        self.webhook_secret = 'whsec_test_secret_key_12345'
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create a test payment transaction
        self.payment_transaction = PaymentTransaction.objects.create(
            stripe_payment_intent_id='pi_test_1234567890',
            amount=25.00,
            currency='USD',
            status='pending'
        )
    
    def create_webhook_signature(self, payload, secret):
        """Create a valid Stripe webhook signature."""
        timestamp = str(int(time.time()))
        signed_payload = f"{timestamp}.{payload}"
        signature = hmac.new(
            secret.encode('utf-8'),
            signed_payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return f"t={timestamp},v1={signature}"
    
    @patch('payments.views.settings.STRIPE_WEBHOOK_SECRET', 'whsec_test_secret_key_12345')
    def test_webhook_payment_intent_succeeded(self):
        """Test processing of payment_intent.succeeded webhook."""
        payload = json.dumps({
            'id': 'evt_test_123',
            'type': 'payment_intent.succeeded',
            'data': {
                'object': {
                    'id': 'pi_test_1234567890',
                    'status': 'succeeded',
                    'amount': 2500,
                    'currency': 'usd'
                }
            },
            'created': int(time.time())
        })
        
        signature = self.create_webhook_signature(payload, self.webhook_secret)
        
        response = self.client.post(
            '/payments/webhook/',
            data=payload,
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE=signature
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['event_id'], 'evt_test_123')
        
        # Check that local transaction was updated
        self.payment_transaction.refresh_from_db()
        self.assertEqual(self.payment_transaction.status, 'succeeded')
        
        # Check that webhook record was created
        webhook = PaymentWebhook.objects.get(stripe_event_id='evt_test_123')
        self.assertEqual(webhook.event_type, 'payment_intent.succeeded')
        self.assertTrue(webhook.processed)
    
    @patch('payments.views.settings.STRIPE_WEBHOOK_SECRET', 'whsec_test_secret_key_12345')
    def test_webhook_payment_intent_failed(self):
        """Test processing of payment_intent.payment_failed webhook."""
        payload = json.dumps({
            'id': 'evt_test_456',
            'type': 'payment_intent.payment_failed',
            'data': {
                'object': {
                    'id': 'pi_test_1234567890',
                    'status': 'requires_payment_method',
                    'amount': 2500,
                    'currency': 'usd',
                    'last_payment_error': {
                        'message': 'Your card was declined.'
                    }
                }
            },
            'created': int(time.time())
        })
        
        signature = self.create_webhook_signature(payload, self.webhook_secret)
        
        response = self.client.post(
            '/payments/webhook/',
            data=payload,
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE=signature
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Check that local transaction status was updated
        self.payment_transaction.refresh_from_db()
        self.assertEqual(self.payment_transaction.status, 'requires_payment_method')
    
    @patch('payments.views.settings.STRIPE_WEBHOOK_SECRET', 'whsec_test_secret_key_12345')
    def test_webhook_duplicate_event_idempotency(self):
        """Test that duplicate webhook events are handled idempotently."""
        payload = json.dumps({
            'id': 'evt_test_789',
            'type': 'payment_intent.succeeded',
            'data': {
                'object': {
                    'id': 'pi_test_1234567890',
                    'status': 'succeeded',
                    'amount': 2500,
                    'currency': 'usd'
                }
            },
            'created': int(time.time())
        })
        
        signature = self.create_webhook_signature(payload, self.webhook_secret)
        
        # Send the same webhook twice
        for i in range(2):
            response = self.client.post(
                '/payments/webhook/',
                data=payload,
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE=signature
            )
            
            self.assertEqual(response.status_code, 200)
        
        # Should only have one webhook record
        webhook_count = PaymentWebhook.objects.filter(
            stripe_event_id='evt_test_789'
        ).count()
        self.assertEqual(webhook_count, 1)
    
    def test_webhook_invalid_signature_rejection(self):
        """Test rejection of webhooks with invalid signatures."""
        payload = json.dumps({
            'id': 'evt_test_invalid',
            'type': 'payment_intent.succeeded',
            'data': {'object': {'id': 'pi_test_1234567890'}}
        })
        
        response = self.client.post(
            '/payments/webhook/',
            data=payload,
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='invalid_signature'
        )
        
        self.assertEqual(response.status_code, 400)
        
        # Should not create any webhook records
        webhook_count = PaymentWebhook.objects.filter(
            stripe_event_id='evt_test_invalid'
        ).count()
        self.assertEqual(webhook_count, 0)
    
    @patch('payments.views.settings.STRIPE_WEBHOOK_SECRET', 'whsec_test_secret_key_12345')
    def test_webhook_unknown_event_type(self):
        """Test handling of unknown webhook event types."""
        payload = json.dumps({
            'id': 'evt_test_unknown',
            'type': 'unknown.event.type',
            'data': {
                'object': {
                    'id': 'some_stripe_object_id'
                }
            },
            'created': int(time.time())
        })
        
        signature = self.create_webhook_signature(payload, self.webhook_secret)
        
        response = self.client.post(
            '/payments/webhook/',
            data=payload,
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE=signature
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['event_id'], 'evt_test_unknown')
        
        # Should still create webhook record but note it's unhandled
        webhook = PaymentWebhook.objects.get(stripe_event_id='evt_test_unknown')
        self.assertEqual(webhook.event_type, 'unknown.event.type')
        # Unknown events are still marked as processed with status 'unhandled'
        self.assertTrue(webhook.processed)
    
    @patch('payments.views.settings.STRIPE_WEBHOOK_SECRET', 'whsec_test_secret_key_12345')
    def test_webhook_with_nonexistent_payment_intent(self):
        """Test webhook for payment intent that doesn't exist locally."""
        payload = json.dumps({
            'id': 'evt_test_nonexistent',
            'type': 'payment_intent.succeeded',
            'data': {
                'object': {
                    'id': 'pi_nonexistent_12345',
                    'status': 'succeeded',
                    'amount': 1000,
                    'currency': 'usd'
                }
            },
            'created': int(time.time())
        })
        
        signature = self.create_webhook_signature(payload, self.webhook_secret)
        
        response = self.client.post(
            '/payments/webhook/',
            data=payload,
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE=signature
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Should still create webhook record
        webhook = PaymentWebhook.objects.get(stripe_event_id='evt_test_nonexistent')
        self.assertEqual(webhook.event_type, 'payment_intent.succeeded')
        self.assertTrue(webhook.processed)  # Processed but had no local effect
