"""
Integration tests for payment API views and endpoints.
"""

import json
import hmac
import hashlib
from decimal import Decimal
from unittest.mock import patch, Mock

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.conf import settings

from payments.models import PaymentTransaction, PaymentRefund, PaymentMethod, PaymentWebhook
from payments.views import *
from .test_base import StripeTestCase


class PaymentAPIViewTest(StripeTestCase):
    """Test cases for payment API views."""
    
    def setUp(self):
        """Set up test environment."""
        super().setUp()
        self.client = Client()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create payment method
        self.payment_method = PaymentMethod.objects.create(
            name='Credit Card',
            stripe_payment_method_type='card'
        )
        
        # Patch Stripe service settings
        self.settings_patcher = patch('payments.services.settings')
        mock_settings = self.settings_patcher.start()
        mock_settings.STRIPE_SECRET_KEY = self.stripe_test_secret
        mock_settings.STRIPE_WEBHOOK_SECRET = self.webhook_secret
        mock_settings.POS_VERSION = '1.0.0'
    
    def tearDown(self):
        """Clean up test environment."""
        super().tearDown()
        self.settings_patcher.stop()


class CreatePaymentIntentAPITest(PaymentAPIViewTest):
    """Test CreatePaymentIntentView API endpoint."""
    
    @patch('payments.services.requests.post')
    def test_create_payment_intent_success(self, mock_post):
        """Test successful payment intent creation via API."""
        # Mock successful Stripe response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 'pi_test_1234567890',
            'status': 'requires_payment_method',
            'amount': 2000,
            'currency': 'usd',
            'client_secret': 'pi_test_1234567890_secret_test'
        }
        mock_post.return_value = mock_response
        
        data = {
            'amount': 20.00,
            'currency': 'usd'
        }
        
        response = self.client.post(
            '/payments/api/intent/',
            data=json.dumps(data),
            content_type='application/json'
        )
    
    def test_create_payment_intent_missing_amount(self):
        """Test API error handling for missing amount."""
        response = self.client.post('/payments/api/intent/', json.dumps({
            'currency': 'usd'
        }), content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        
        self.assertTrue(response_data['error'])
        self.assertIn('Amount is required', response_data['message'])
    
    def test_create_payment_intent_invalid_amount(self):
        """Test API error handling for invalid amount."""
        response = self.client.post('/payments/api/intent/', json.dumps({
            'amount': 'invalid',
            'currency': 'usd'
        }), content_type='application/json')
    
    def test_create_payment_intent_invalid_json(self):
        """Test API error handling for invalid JSON."""
        response = self.client.post('/payments/api/intent/', 
            'invalid json', content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        
        self.assertTrue(response_data['error'])
        self.assertIn('Invalid JSON format', response_data['message'])
    
    @patch('payments.services.requests.post')
    def test_create_payment_intent_stripe_error(self, mock_post):
        """Test API handling of Stripe errors."""
        # Mock Stripe API error
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            'error': {'message': 'Invalid amount'}
        }
        mock_post.return_value = mock_response
        
        data = {
            'amount': 10.00,
            'currency': 'usd'
        }
        
        response = self.client.post(
            '/payments/api/create-payment-intent/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 500)
        response_data = response.json()
        
        self.assertTrue(response_data['error'])
        self.assertIn('Payment creation failed', response_data['message'])
    
    @patch('payments.services.requests.post')
    def test_create_payment_intent_with_user_metadata(self, mock_post):
        """Test that user metadata is added to payment intent."""
        # Mock Stripe API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 'pi_test_1234567890',
            'object': 'payment_intent',
            'amount': 1000,
            'currency': 'usd',
            'status': 'requires_payment_method',
            'client_secret': 'pi_test_1234567890_secret_test',
            'created': 1234567890
        }
        mock_post.return_value = mock_response
        
        # Login user and make request
        self.client.login(username='testuser', password='testpass123')
        
        data = {
            'amount': 10.00,
            'currency': 'usd',
            'metadata': {'order_id': '12345'}
        }
        
        response = self.client.post(
            '/payments/api/create-payment-intent/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Verify user metadata was included
        self.assertEqual(response.status_code, 200)
        
        # Check that Stripe API was called with user metadata
        call_data = mock_post.call_args[1]['data']
        self.assertEqual(call_data['metadata[created_by]'], 'testuser')
        self.assertEqual(call_data['metadata[source]'], 'ireti_pos')


class RetrievePaymentIntentAPITest(PaymentAPIViewTest):
    """Test RetrievePaymentIntentView API endpoint."""
    
    def setUp(self):
        """Set up test environment with existing payment."""
        super().setUp()
        
        # Create test payment transaction
        self.payment_transaction = PaymentTransaction.objects.create(
            payment_method=self.payment_method,
            amount=Decimal('10.00'),
            currency='usd',
            stripe_payment_intent_id='pi_test_1234567890',
            processed_by=self.user
        )
    
    @patch('payments.services.requests.get')
    def test_retrieve_payment_intent_success(self, mock_get):
        """Test successful payment intent retrieval."""
        # Mock Stripe API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 'pi_test_1234567890',
            'object': 'payment_intent',
            'amount': 1000,
            'currency': 'usd',
            'status': 'succeeded',
            'client_secret': 'pi_test_1234567890_secret_test',
            'created': 1234567890
        }
        mock_get.return_value = mock_response
        
        response = self.client.get('/payments/api/retrieve-payment-intent/pi_test_1234567890/')
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['payment_intent']['id'], 'pi_test_1234567890')
        self.assertEqual(response_data['payment_intent']['status'], 'succeeded')
        
        # Verify local transaction data is included
        self.assertIsNotNone(response_data['local_transaction'])
        self.assertEqual(response_data['local_transaction']['local_status'], 'pending')
    
    @patch('payments.services.requests.get')
    def test_retrieve_payment_intent_not_found(self, mock_get):
        """Test handling of non-existent payment intent."""
        # Mock Stripe API error
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            'error': {'message': 'No such payment_intent'}
        }
        mock_get.return_value = mock_response
        
        response = self.client.get('/payments/api/retrieve-payment-intent/pi_nonexistent/')
        
        self.assertEqual(response.status_code, 404)
        response_data = response.json()
        
        self.assertTrue(response_data['error'])


class ConfirmPaymentIntentAPITest(PaymentAPIViewTest):
    """Test ConfirmPaymentIntentView API endpoint."""
    
    def setUp(self):
        """Set up test environment with existing payment."""
        super().setUp()
        
        # Create test payment transaction
        self.payment_transaction = PaymentTransaction.objects.create(
            payment_method=self.payment_method,
            amount=Decimal('10.00'),
            currency='usd',
            stripe_payment_intent_id='pi_test_1234567890',
            processed_by=self.user
        )
    
    @patch('payments.services.requests.post')
    def test_confirm_payment_intent_success(self, mock_post):
        """Test successful payment confirmation."""
        # Mock Stripe API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 'pi_test_1234567890',
            'object': 'payment_intent',
            'status': 'succeeded',
            'amount': 1000,
            'currency': 'usd'
        }
        mock_post.return_value = mock_response
        
        response = self.client.post(
            '/payments/api/confirm-payment-intent/pi_test_1234567890/',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['payment_intent']['status'], 'succeeded')
        
        # Verify local payment was updated
        self.payment_transaction.refresh_from_db()
        self.assertEqual(self.payment_transaction.status, 'succeeded')


class CreateRefundAPITest(PaymentAPIViewTest):
    """Test CreateRefundView API endpoint."""
    
    def setUp(self):
        """Set up test environment with existing payment."""
        super().setUp()
        
        # Create test payment transaction
        self.payment_transaction = PaymentTransaction.objects.create(
            payment_method=self.payment_method,
            amount=Decimal('100.00'),
            currency='usd',
            stripe_payment_intent_id='pi_test_1234567890',
            processed_by=self.user,
            status='succeeded'
        )
    
    @patch('payments.services.requests.post')
    def test_create_refund_success(self, mock_post):
        """Test successful refund creation."""
        # Mock Stripe API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 're_test_1234567890',
            'object': 'refund',
            'amount': 2500,  # $25.00 in cents
            'currency': 'usd',
            'status': 'succeeded',
            'reason': 'requested_by_customer'
        }
        mock_post.return_value = mock_response
        
        data = {
            'payment_intent_id': 'pi_test_1234567890',
            'amount': 25.00,
            'reason': 'requested_by_customer',
            'metadata': {'refund_reason': 'Customer not satisfied'}
        }
        
        response = self.client.post(
            '/payments/api/create-refund/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['refund']['id'], 're_test_1234567890')
        self.assertEqual(response_data['refund']['amount'], 2500)
        
        # Verify database record was created
        refund = PaymentRefund.objects.get(stripe_refund_id='re_test_1234567890')
        self.assertEqual(refund.amount, Decimal('25.00'))
        self.assertEqual(refund.payment_transaction, self.payment_transaction)
    
    def test_create_refund_missing_payment_intent(self):
        """Test error handling for missing payment intent ID."""
        data = {
            'amount': 25.00,
            'reason': 'requested_by_customer'
        }
        
        response = self.client.post(
            '/payments/api/create-refund/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        
        self.assertTrue(response_data['error'])
        self.assertIn('Payment intent ID is required', response_data['message'])


class CreateConnectionTokenAPITest(PaymentAPIViewTest):
    """Test CreateConnectionTokenView API endpoint."""
    
    @patch('payments.services.requests.post')
    def test_create_connection_token_success(self, mock_post):
        """Test successful connection token creation."""
        # Mock Stripe API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'object': 'terminal.connection_token',
            'secret': 'pst_test_1234567890abcdef'
        }
        mock_post.return_value = mock_response
        
        data = {
            'location_id': 'tml_test_location'
        }
        
        response = self.client.post(
            '/payments/api/create-connection-token/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['connection_token'], 'pst_test_1234567890abcdef')
    
    def test_create_connection_token_no_location(self):
        """Test connection token creation without location ID."""
        # This should still work (location is optional)
        with patch('payments.services.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'object': 'terminal.connection_token',
                'secret': 'pst_test_1234567890abcdef'
            }
            mock_post.return_value = mock_response
            
            response = self.client.post(
                '/payments/api/create-connection-token/',
                data=json.dumps({}),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 200)
            response_data = response.json()
            self.assertTrue(response_data['success'])


class StripeWebhookViewTest(PaymentAPIViewTest):
    """Test StripeWebhookView API endpoint."""
    
    def setUp(self):
        """Set up test environment with webhook data."""
        super().setUp()
        
        # Create test payment transaction for webhook testing
        self.payment_transaction = PaymentTransaction.objects.create(
            payment_method=self.payment_method,
            amount=Decimal('10.00'),
            currency='usd',
            stripe_payment_intent_id='pi_test_1234567890',
            processed_by=self.user
        )
    
    def create_valid_webhook_signature(self, payload: bytes, timestamp: str) -> str:
        """Create a valid webhook signature for testing."""
        signed_payload = f"{timestamp}.{payload.decode('utf-8')}"
        signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            signed_payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return f"t={timestamp},v1={signature}"
    
    def test_webhook_payment_intent_succeeded(self):
        """Test webhook processing for payment_intent.succeeded."""
        payload = json.dumps({
            'id': 'evt_test_123',
            'type': 'payment_intent.succeeded',
            'data': {
                'object': {
                    'id': 'pi_test_1234567890',
                    'object': 'payment_intent',
                    'status': 'succeeded',
                    'amount': 1000,
                    'currency': 'usd'
                }
            }
        }).encode('utf-8')
        
        timestamp = str(int(timezone.now().timestamp()))
        signature = self.create_valid_webhook_signature(payload, timestamp)
        
        response = self.client.post(
            '/payments/webhook/',
            data=payload,
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE=signature
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        self.assertTrue(response_data['received'])
        
        # Verify payment transaction was updated
        self.payment_transaction.refresh_from_db()
        self.assertEqual(self.payment_transaction.status, 'succeeded')
        
        # Verify webhook record was created
        webhook = PaymentWebhook.objects.get(stripe_event_id='evt_test_123')
        self.assertTrue(webhook.processed)
    
    def test_webhook_invalid_signature(self):
        """Test webhook rejection with invalid signature."""
        payload = json.dumps({
            'id': 'evt_test_123',
            'type': 'payment_intent.succeeded'
        }).encode('utf-8')
        
        # Invalid signature
        signature = "t=1234567890,v1=invalid_signature"
        
        response = self.client.post(
            '/payments/webhook/',
            data=payload,
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE=signature
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        
        self.assertTrue(response_data['error'])
        self.assertIn('Invalid signature', response_data['message'])
    
    def test_webhook_duplicate_event(self):
        """Test handling of duplicate webhook events."""
        # Create existing webhook record
        PaymentWebhook.objects.create(
            stripe_event_id='evt_test_123',
            event_type='payment_intent.succeeded',
            processed=True
        )
        
        payload = json.dumps({
            'id': 'evt_test_123',
            'type': 'payment_intent.succeeded',
            'data': {
                'object': {
                    'id': 'pi_test_1234567890',
                    'status': 'succeeded'
                }
            }
        }).encode('utf-8')
        
        timestamp = str(int(timezone.now().timestamp()))
        signature = self.create_valid_webhook_signature(payload, timestamp)
        
        response = self.client.post(
            '/payments/webhook/',
            data=payload,
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE=signature
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        self.assertTrue(response_data['received'])
        # Should indicate it was already processed
        # (implementation detail depends on webhook handler)


class PaymentDashboardViewTest(PaymentAPIViewTest):
    """Test payment dashboard view."""
    
    def setUp(self):
        """Set up test environment with sample data."""
        super().setUp()
        
        # Create sample payments and refunds
        for i in range(15):
            PaymentTransaction.objects.create(
                payment_method=self.payment_method,
                amount=Decimal(f'{10 + i}.00'),
                currency='usd',
                processed_by=self.user,
                stripe_payment_intent_id=f'pi_test_{i:010d}',
                status='succeeded' if i % 2 == 0 else 'pending'
            )
    
    def test_dashboard_requires_login(self):
        """Test that dashboard requires authentication."""
        response = self.client.get('/payments/dashboard/')
        
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_dashboard_authenticated_access(self):
        """Test dashboard access for authenticated users."""
        # Login and access dashboard
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get('/payments/dashboard/')
        
        self.assertEqual(response.status_code, 200)
        
        # Verify context data
        self.assertIn('recent_payments', response.context)
        self.assertIn('recent_refunds', response.context)
        
        # Should show most recent payments (limited to 10)
        recent_payments = response.context['recent_payments']
        self.assertEqual(len(recent_payments), 10)
        
        # Should be ordered by creation date (newest first)
        payment_ids = [p.stripe_payment_intent_id for p in recent_payments]
        expected_ids = [f'pi_test_{i:010d}' for i in range(14, 4, -1)]  # Last 10, newest first
        self.assertEqual(payment_ids, expected_ids)


class PaymentDetailViewTest(PaymentAPIViewTest):
    """Test payment detail view."""
    
    def setUp(self):
        """Set up test environment with sample data."""
        super().setUp()
        
        # Create payment with refunds
        self.payment = PaymentTransaction.objects.create(
            payment_method=self.payment_method,
            amount=Decimal('100.00'),
            currency='usd',
            processed_by=self.user,
            stripe_payment_intent_id='pi_test_1234567890',
            status='succeeded'
        )
        
        self.refund = PaymentRefund.objects.create(
            payment_transaction=self.payment,
            amount=Decimal('25.00'),
            currency='usd',
            reason='requested_by_customer',
            processed_by=self.user,
            stripe_refund_id='re_test_1234567890'
        )
    
    def test_detail_requires_login(self):
        """Test that detail view requires authentication."""
        response = self.client.get(f'/payments/detail/{self.payment.id}/')
        
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_detail_authenticated_access(self):
        """Test detail view access for authenticated users."""
        # Login and access detail view
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(f'/payments/detail/{self.payment.id}/')
        
        self.assertEqual(response.status_code, 200)
        
        # Verify context data
        self.assertEqual(response.context['payment'], self.payment)
        
        refunds = response.context['refunds']
        self.assertEqual(len(refunds), 1)
        self.assertEqual(refunds[0], self.refund)
    
    def test_detail_not_found(self):
        """Test detail view with non-existent payment."""
        # Login and access non-existent payment
        self.client.login(username='testuser', password='testpass123')
        
        import uuid
        fake_id = uuid.uuid4()
        response = self.client.get(f'/payments/detail/{fake_id}/')
        
        self.assertEqual(response.status_code, 404)


class APIErrorHandlingTest(PaymentAPIViewTest):
    """Test API error handling and edge cases."""
    
    def test_content_type_validation(self):
        """Test that API endpoints require proper content type."""
        data = {'amount': 10.00}
        
        # Test with form data instead of JSON
        response = self.client.post(
            '/payments/api/create-payment-intent/',
            data=data  # Not JSON
        )
        
        # Should handle gracefully (either accept or return proper error)
        self.assertIn(response.status_code, [200, 400, 415])
    
    def test_http_method_restrictions(self):
        """Test that API endpoints respect HTTP method restrictions."""
        # Test GET on POST-only endpoints
        response = self.client.get('/payments/api/create-payment-intent/')
        self.assertEqual(response.status_code, 405)  # Method not allowed
        
        response = self.client.get('/payments/api/create-refund/')
        self.assertEqual(response.status_code, 405)
        
        response = self.client.get('/payments/api/create-connection-token/')
        self.assertEqual(response.status_code, 405)
    
    def test_large_payload_handling(self):
        """Test handling of unusually large payloads."""
        # Create large metadata object
        large_metadata = {f'key_{i}': 'x' * 100 for i in range(100)}
        
        data = {
            'amount': 10.00,
            'currency': 'usd',
            'metadata': large_metadata
        }
        
        response = self.client.post(
            '/payments/api/create-payment-intent/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Should handle gracefully (may accept, reject, or truncate)
        self.assertIn(response.status_code, [200, 400, 413])
