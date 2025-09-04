"""
Unit tests for Stripe payment services.
"""

import json
import hmac
import hashlib
import requests
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal

from payments.services import StripePaymentService, stripe_service
from payments.models import PaymentMethod, PaymentTransaction, PaymentRefund, PaymentWebhook
from payments.exceptions import (
    StripeConfigurationError,
    PaymentIntentError,
    RefundError,
    ConnectionTokenError,
    PaymentAmountError,
    AuthenticationError
)
from .test_base import StripeTestCase, StripeTestData


class StripePaymentServiceTest(StripeTestCase):
    """Test cases for StripePaymentService."""
    
    def setUp(self):
        """Set up test environment."""
        super().setUp()
        
        # Patch settings to provide test configuration
        self.settings_patcher = patch('payments.services.settings')
        mock_settings = self.settings_patcher.start()
        mock_settings.STRIPE_SECRET_KEY = self.stripe_test_secret
        mock_settings.STRIPE_API_VERSION = '2024-06-20'
        mock_settings.STRIPE_WEBHOOK_SECRET = self.webhook_secret
        
        # Initialize service with mocked settings
        self.service = StripePaymentService()
    
    def tearDown(self):
        """Clean up test environment."""
        super().tearDown()
        self.settings_patcher.stop()
    
    @patch('payments.services.requests.post')
    def test_create_payment_intent_success(self, mock_post):
        """Test successful payment intent creation."""
        # Mock successful Stripe API response
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
        
        # Call service method
        result = self.service.create_payment_intent(
            amount=Decimal('10.00'),
            currency='usd',
            metadata={'order_id': '123'}
        )
        
        # Verify API call was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertIn('payment_intents', call_args[0][0])  # URL contains payment_intents
        
        # Verify request data
        sent_data = call_args[1]['data']
        self.assertEqual(sent_data['amount'], 1000)  # Converted to cents
        self.assertEqual(sent_data['currency'], 'usd')
        self.assertEqual(sent_data['metadata[order_id]'], '123')
        
        # Verify result
        self.assertEqual(result['id'], 'pi_test_1234567890')
        self.assertEqual(result['client_secret'], 'pi_test_1234567890_secret_test')
        self.assertEqual(result['amount'], 1000)
    
    @patch('payments.services.requests.post')
    def test_create_payment_intent_api_error(self, mock_post):
        """Test handling of Stripe API errors."""
        # Mock Stripe API error response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            'error': {
                'message': 'Invalid amount',
                'type': 'invalid_request_error'
            }
        }
        mock_post.return_value = mock_response
        
        # Should raise our custom exception
        with self.assertRaises(PaymentIntentError):
            self.service.create_payment_intent(amount=Decimal('10.00'))
    
    def test_create_payment_intent_invalid_amount(self):
        """Test validation of payment amount."""
        with self.assertRaises(PaymentAmountError):
            self.service.create_payment_intent(amount=Decimal('0.00'))
        
        with self.assertRaises(PaymentAmountError):
            self.service.create_payment_intent(amount=Decimal('-5.00'))
    
    @patch('payments.services.requests.get')
    def test_retrieve_payment_intent_success(self, mock_get):
        """Test successful payment intent retrieval."""
        # Mock Stripe response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 'pi_test_1234567890',
            'object': 'payment_intent',
            'amount': 1000,
            'currency': 'usd',
            'status': 'succeeded',
            'created': 1234567890
        }
        mock_get.return_value = mock_response
        
        # Call service method
        result = self.service.retrieve_payment_intent('pi_test_1234567890')
        
        # Verify API call was made correctly
        mock_get.assert_called_once()
        self.assertIn('pi_test_1234567890', mock_get.call_args[0][0])
        
        # Verify result
        self.assertEqual(result['status'], 'succeeded')
        self.assertEqual(result['id'], 'pi_test_1234567890')
    
    @patch('payments.services.requests.post')
    def test_confirm_payment_intent_success(self, mock_post):
        """Test successful payment intent confirmation."""
        # Mock Stripe response
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
        
        # Call service method
        result = self.service.confirm_payment_intent('pi_test_1234567890')
        
        # Verify API call
        mock_post.assert_called_once()
        self.assertIn('pi_test_1234567890/confirm', mock_post.call_args[0][0])
        
        # Verify result
        self.assertEqual(result['status'], 'succeeded')
    
    @patch('payments.services.requests.post')
    def test_capture_payment_intent_success(self, mock_post):
        """Test successful payment intent capture."""
        # Mock Stripe response
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
        
        # Call service method with partial capture
        result = self.service.capture_payment_intent(
            'pi_test_1234567890',
            amount_to_capture=Decimal('5.00')
        )
        
        # Verify API call
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertIn('pi_test_1234567890/capture', call_args[0][0])
        
        # Verify partial capture amount
        sent_data = call_args[1]['data']
        self.assertEqual(sent_data['amount_to_capture'], 500)  # $5.00 in cents
        
        # Verify result
        self.assertEqual(result['status'], 'succeeded')
    
    @patch('payments.services.requests.post')
    def test_create_refund_success(self, mock_post):
        """Test successful refund creation."""
        # Mock Stripe response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 're_test_1234567890',
            'object': 'refund',
            'amount': 500,
            'currency': 'usd',
            'status': 'succeeded',
            'payment_intent': 'pi_test_1234567890',
            'reason': 'requested_by_customer'
        }
        mock_post.return_value = mock_response
        
        # Call service method
        result = self.service.create_refund(
            payment_intent_id='pi_test_1234567890',
            amount=Decimal('5.00'),
            reason='requested_by_customer',
            metadata={'refund_reason': 'Customer request'}
        )
        
        # Verify API call
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertIn('refunds', call_args[0][0])
        
        # Verify request data
        sent_data = call_args[1]['data']
        self.assertEqual(sent_data['payment_intent'], 'pi_test_1234567890')
        self.assertEqual(sent_data['amount'], 500)  # Converted to cents
        self.assertEqual(sent_data['reason'], 'requested_by_customer')
        self.assertEqual(sent_data['metadata[refund_reason]'], 'Customer request')
        
        # Verify result
        self.assertEqual(result['id'], 're_test_1234567890')
        self.assertEqual(result['status'], 'succeeded')
    
    @patch('payments.services.requests.post')
    def test_create_connection_token_success(self, mock_post):
        """Test successful connection token creation."""
        # Mock Stripe response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'object': 'terminal.connection_token',
            'secret': 'pst_test_1234567890abcdef'
        }
        mock_post.return_value = mock_response
        
        # Call service method
        result = self.service.create_connection_token(location_id='tml_test_location')
        
        # Verify API call
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertIn('terminal/connection_tokens', call_args[0][0])
        
        # Verify location parameter
        sent_data = call_args[1]['data']
        self.assertEqual(sent_data['location'], 'tml_test_location')
        
        # Verify result
        self.assertEqual(result['secret'], 'pst_test_1234567890abcdef')
    
    @patch('payments.services.requests.post')
    def test_create_terminal_location_success(self, mock_post):
        """Test successful terminal location creation."""
        # Mock Stripe response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 'tml_test_1234567890',
            'object': 'terminal.location',
            'display_name': 'Test Store',
            'address': {
                'line1': '123 Main St',
                'city': 'San Francisco',
                'state': 'CA',
                'postal_code': '94105',
                'country': 'US'
            }
        }
        mock_post.return_value = mock_response
        
        address = {
            'line1': '123 Main St',
            'city': 'San Francisco',
            'state': 'CA',
            'postal_code': '94105',
            'country': 'US'
        }
        
        # Call service method
        result = self.service.create_terminal_location('Test Store', address)
        
        # Verify API call
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertIn('terminal/locations', call_args[0][0])
        
        # Verify request data
        sent_data = call_args[1]['data']
        self.assertEqual(sent_data['display_name'], 'Test Store')
        self.assertEqual(sent_data['address[line1]'], '123 Main St')
        self.assertEqual(sent_data['address[city]'], 'San Francisco')
        
        # Verify result
        self.assertEqual(result['id'], 'tml_test_1234567890')
    
    def test_amount_conversion_methods(self):
        """Test amount conversion utility methods."""
        # Test decimal to cents
        test_cases = [
            (Decimal('10.00'), 1000),
            (Decimal('0.50'), 50),
            (Decimal('123.45'), 12345),
            (Decimal('0.01'), 1),
        ]
        
        for decimal_amount, expected_cents in test_cases:
            with self.subTest(decimal_to_cents=decimal_amount):
                cents = self.service._amount_to_cents(decimal_amount)
                self.assertEqual(cents, expected_cents)
        
        # Test cents to decimal
        for expected_decimal, cents in test_cases:
            with self.subTest(cents_to_decimal=cents):
                amount = self.service._cents_to_amount(cents)
                self.assertEqual(amount, expected_decimal)
    
    def test_verify_webhook_signature_valid(self):
        """Test webhook signature verification with valid signature."""
        payload = b'{"id": "evt_test_123", "type": "payment_intent.succeeded"}'
        timestamp = str(int(timezone.now().timestamp()))
        
        # Create valid signature
        signed_payload = f"{timestamp}.{payload.decode('utf-8')}"
        signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            signed_payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        signature_header = f"t={timestamp},v1={signature}"
        
        # Should return True for valid signature
        is_valid = self.service.verify_webhook_signature(payload, signature_header)
        self.assertTrue(is_valid)
    
    def test_verify_webhook_signature_invalid(self):
        """Test webhook signature verification with invalid signature."""
        payload = b'{"id": "evt_test_123", "type": "payment_intent.succeeded"}'
        timestamp = str(int(timezone.now().timestamp()))
        
        # Create invalid signature
        signature_header = f"t={timestamp},v1=invalid_signature"
        
        # Should return False for invalid signature
        is_valid = self.service.verify_webhook_signature(payload, signature_header)
        self.assertFalse(is_valid)
    
    def test_verify_webhook_signature_old_timestamp(self):
        """Test webhook signature verification with old timestamp."""
        payload = b'{"id": "evt_test_123", "type": "payment_intent.succeeded"}'
        old_timestamp = str(int(timezone.now().timestamp()) - 600)  # 10 minutes ago
        
        # Create signature with old timestamp
        signed_payload = f"{old_timestamp}.{payload.decode('utf-8')}"
        signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            signed_payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        signature_header = f"t={old_timestamp},v1={signature}"
        
        # Should return False for old timestamp (replay attack protection)
        is_valid = self.service.verify_webhook_signature(payload, signature_header)
        self.assertFalse(is_valid)


class StripeServiceWebhookTest(StripeTestCase):
    """Test webhook processing functionality."""
    
    def setUp(self):
        """Set up test environment."""
        super().setUp()
        
        # Patch settings
        self.settings_patcher = patch('payments.services.settings')
        mock_settings = self.settings_patcher.start()
        mock_settings.STRIPE_SECRET_KEY = self.stripe_test_secret
        mock_settings.STRIPE_WEBHOOK_SECRET = self.webhook_secret
        
        self.service = StripePaymentService()
        
        # Create test payment transaction
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.payment_method = PaymentMethod.objects.create(
            name='Credit Card',
            stripe_payment_method_type='card'
        )
        
        self.payment_transaction = PaymentTransaction.objects.create(
            payment_method=self.payment_method,
            amount=Decimal('10.00'),
            currency='usd',
            processed_by=self.user,
            stripe_payment_intent_id='pi_test_1234567890'
        )
    
    def tearDown(self):
        """Clean up test environment."""
        super().tearDown()
        self.settings_patcher.stop()
    
    def test_process_payment_intent_succeeded_webhook(self):
        """Test processing payment_intent.succeeded webhook."""
        event_data = {
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
        }
        
        result = self.service.process_webhook_event(event_data)
        
        # Verify webhook was processed
        self.assertEqual(result['status'], 'processed')
        self.assertEqual(result['event_type'], 'payment_intent.succeeded')
        
        # Verify payment transaction was updated
        self.payment_transaction.refresh_from_db()
        self.assertEqual(self.payment_transaction.status, 'succeeded')
        self.assertIsNotNone(self.payment_transaction.processed_at)
        
        # Verify webhook record was created
        webhook = PaymentWebhook.objects.get(stripe_event_id='evt_test_123')
        self.assertTrue(webhook.processed)
        self.assertEqual(webhook.event_type, 'payment_intent.succeeded')
    
    def test_process_duplicate_webhook_event(self):
        """Test that duplicate webhook events are handled properly."""
        # Create existing webhook record
        PaymentWebhook.objects.create(
            stripe_event_id='evt_test_123',
            event_type='payment_intent.succeeded',
            processed=True
        )
        
        event_data = {
            'id': 'evt_test_123',
            'type': 'payment_intent.succeeded',
            'data': {'object': {'id': 'pi_test_1234567890'}}
        }
        
        result = self.service.process_webhook_event(event_data)
        
        # Should skip processing
        self.assertEqual(result['status'], 'already_processed')
    
    def test_process_refund_webhook(self):
        """Test processing refund webhook events."""
        event_data = {
            'id': 'evt_test_refund_123',
            'type': 'refund.created',
            'data': {
                'object': {
                    'id': 're_test_1234567890',
                    'object': 'refund',
                    'amount': 500,
                    'currency': 'usd',
                    'status': 'succeeded',
                    'payment_intent': 'pi_test_1234567890',
                    'reason': 'requested_by_customer'
                }
            }
        }
        
        result = self.service.process_webhook_event(event_data)
        
        # Verify processing result
        self.assertEqual(result['status'], 'processed')
        self.assertEqual(result['event_type'], 'refund.created')
        
        # Verify refund record was created
        refund = PaymentRefund.objects.get(stripe_refund_id='re_test_1234567890')
        self.assertEqual(refund.payment_transaction, self.payment_transaction)
        self.assertEqual(refund.amount, Decimal('5.00'))
        self.assertEqual(refund.reason, 'requested_by_customer')


class StripeConfigurationTest(TestCase):
    """Test Stripe service configuration."""
    
    @patch('payments.services.settings')
    def test_missing_stripe_secret_key_raises_error(self, mock_settings):
        """Test that missing STRIPE_SECRET_KEY raises configuration error."""
        # Mock missing secret key
        mock_settings.STRIPE_SECRET_KEY = None
        
        with self.assertRaises(StripeConfigurationError):
            StripePaymentService()
    
    @patch('payments.services.settings')
    def test_empty_stripe_secret_key_raises_error(self, mock_settings):
        """Test that empty STRIPE_SECRET_KEY raises configuration error."""
        # Mock empty secret key
        mock_settings.STRIPE_SECRET_KEY = ''
        
        with self.assertRaises(StripeConfigurationError):
            StripePaymentService()
    
    @patch('payments.services.settings')
    def test_invalid_stripe_key_format_raises_error(self, mock_settings):
        """Test that invalid key format raises configuration error."""
        # Mock invalid key format
        mock_settings.STRIPE_SECRET_KEY = 'invalid_key_format'
        
        with self.assertRaises(StripeConfigurationError):
            StripePaymentService()
    
    @patch('payments.services.settings')
    def test_valid_test_key_configuration(self, mock_settings):
        """Test that valid test keys are accepted."""
        mock_settings.STRIPE_SECRET_KEY = 'sk_test_1234567890abcdef'
        mock_settings.STRIPE_API_VERSION = '2024-06-20'
        
        # Should not raise any exceptions
        service = StripePaymentService()
        self.assertIsNotNone(service)
    
    @patch('payments.services.settings')
    def test_valid_live_key_configuration(self, mock_settings):
        """Test that valid live keys are accepted."""
        mock_settings.STRIPE_SECRET_KEY = 'sk_live_1234567890abcdef'
        mock_settings.STRIPE_API_VERSION = '2024-06-20'
        
        # Should not raise any exceptions
        service = StripePaymentService()
        self.assertIsNotNone(service)


class StripeServiceErrorHandlingTest(StripeTestCase):
    """Test error handling in Stripe service."""
    
    def setUp(self):
        """Set up test environment."""
        super().setUp()
        
        # Patch settings
        self.settings_patcher = patch('payments.services.settings')
        mock_settings = self.settings_patcher.start()
        mock_settings.STRIPE_SECRET_KEY = self.stripe_test_secret
        
        self.service = StripePaymentService()
    
    def tearDown(self):
        """Clean up test environment."""
        super().tearDown()
        self.settings_patcher.stop()
    
    @patch('payments.services.requests.post')
    def test_network_error_handling(self, mock_post):
        """Test handling of network errors."""
        # Mock network error
        mock_post.side_effect = requests.exceptions.ConnectionError('Network error')
        
        with self.assertRaises(PaymentIntentError) as context:
            self.service.create_payment_intent(amount=Decimal('10.00'))
        
        self.assertIn('Network error', str(context.exception))
    
    @patch('payments.services.requests.post')
    def test_timeout_error_handling(self, mock_post):
        """Test handling of timeout errors."""
        # Mock timeout error
        mock_post.side_effect = requests.exceptions.Timeout('Request timeout')
        
        with self.assertRaises(PaymentIntentError) as context:
            self.service.create_payment_intent(amount=Decimal('10.00'))
        
        self.assertIn('Request timeout', str(context.exception))
    
    @patch('payments.services.requests.post')
    def test_http_error_response_handling(self, mock_post):
        """Test handling of various HTTP error responses."""
        error_cases = [
            (400, 'Bad Request'),
            (401, 'Unauthorized'),
            (402, 'Payment Required'),
            (404, 'Not Found'),
            (429, 'Too Many Requests'),
            (500, 'Internal Server Error')
        ]
        
        for status_code, error_type in error_cases:
            with self.subTest(status_code=status_code):
                mock_response = Mock()
                mock_response.status_code = status_code
                mock_response.json.return_value = {
                    'error': {'message': f'{error_type} error'}
                }
                mock_post.return_value = mock_response
                
                with self.assertRaises(PaymentIntentError):
                    self.service.create_payment_intent(amount=Decimal('10.00'))
