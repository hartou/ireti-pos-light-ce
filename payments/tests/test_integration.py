"""
Integration tests for Stripe payment flows.
"""

import stripe
from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal

from payments.services import StripePaymentService
from payments.models import PaymentMethod, PaymentTransaction, PaymentRefund, PaymentWebhook
from .test_base import StripeTestCase, StripeTestData


class StripeIntegrationFlowTest(StripeTestCase):
    """Test complete Stripe payment flows end-to-end."""
    
    def setUp(self):
        """Set up test environment."""
        super().setUp()
        self.service = StripePaymentService()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test payment method
        self.payment_method = PaymentMethod.objects.create(
            name='Credit Card',
            stripe_payment_method_type='card'
        )
    
    @patch('payments.services.stripe.PaymentIntent.create')
    @patch('payments.services.stripe.PaymentIntent.retrieve')
    def test_successful_payment_flow(self, mock_retrieve, mock_create):
        """Test complete successful payment flow."""
        # 1. Mock payment intent creation
        mock_intent_created = self.create_mock_payment_intent(
            status='requires_payment_method'
        )
        mock_create.return_value = mock_intent_created
        
        # 2. Mock payment intent confirmation (after card collection)
        mock_intent_succeeded = self.create_mock_payment_intent(
            status='succeeded'
        )
        mock_retrieve.return_value = mock_intent_succeeded
        
        # 3. Create payment intent
        intent_result = self.service.create_payment_intent(
            amount=Decimal('10.00'),
            currency='usd',
            metadata={'order_id': '123'}
        )
        
        self.assertEqual(intent_result['status'], 'requires_payment_method')
        
        # 4. Simulate payment confirmation by retrieving updated intent
        confirmed_intent = self.service.retrieve_payment_intent(
            intent_result['id']
        )
        
        self.assertEqual(confirmed_intent['status'], 'succeeded')
    
    @patch('payments.services.stripe.PaymentIntent.create')
    @patch('payments.services.stripe.Refund.create')
    def test_payment_and_refund_flow(self, mock_refund, mock_create):
        """Test payment creation followed by refund."""
        # 1. Mock successful payment
        mock_intent = self.create_mock_payment_intent(status='succeeded')
        mock_create.return_value = mock_intent
        
        # 2. Mock successful refund
        mock_refund_obj = self.create_mock_refund(status='succeeded')
        mock_refund.return_value = mock_refund_obj
        
        # 3. Create payment
        payment_result = self.service.create_payment_intent(
            amount=Decimal('10.00'),
            currency='usd'
        )
        
        # 4. Create refund
        refund_result = self.service.create_refund(
            payment_intent_id=payment_result['id'],
            amount=Decimal('5.00'),
            reason='requested_by_customer'
        )
        
        self.assertEqual(refund_result['status'], 'succeeded')
        self.assertEqual(refund_result['payment_intent'], payment_result['id'])
    
    @patch('payments.services.stripe.terminal.ConnectionToken.create')
    def test_terminal_connection_flow(self, mock_create):
        """Test terminal connection token creation."""
        # Mock connection token
        mock_token = self.create_mock_connection_token()
        mock_create.return_value = mock_token
        
        # Create connection token
        token_result = self.service.create_connection_token()
        
        self.assertIn('secret', token_result)
        self.assertEqual(token_result['secret'], 'pst_test_1234567890abcdef')


class StripeWebhookIntegrationTest(StripeTestCase):
    """Test Stripe webhook processing integration."""
    
    def test_webhook_event_processing(self):
        """Test webhook event record creation."""
        # Create webhook event record
        webhook = PaymentWebhook.objects.create(
            stripe_event_id='evt_test_1234567890',
            event_type='payment_intent.succeeded'
        )
        
        self.assertFalse(webhook.processed)
        
        # Mark as processed
        webhook.mark_processed()
        
        self.assertTrue(webhook.processed)
        self.assertIsNotNone(webhook.processed_at)
    
    def test_webhook_event_error_handling(self):
        """Test webhook event error processing."""
        # Create webhook event record
        webhook = PaymentWebhook.objects.create(
            stripe_event_id='evt_test_1234567890',
            event_type='payment_intent.payment_failed'
        )
        
        # Mark as processed with error
        error_message = 'Payment processing failed'
        webhook.mark_processed(error=error_message)
        
        self.assertFalse(webhook.processed)
        self.assertEqual(webhook.processing_error, error_message)
        self.assertIsNotNone(webhook.processed_at)


class StripeErrorHandlingTest(StripeTestCase):
    """Test Stripe error scenarios and handling."""
    
    def setUp(self):
        """Set up test environment."""
        super().setUp()
        self.service = StripePaymentService()
    
    @patch('payments.services.stripe.PaymentIntent.create')
    def test_insufficient_funds_error(self, mock_create):
        """Test handling of insufficient funds error."""
        # Mock Stripe error
        mock_create.side_effect = stripe.error.CardError(
            message='Your card has insufficient funds.',
            param='amount',
            code='insufficient_funds',
            decline_code='insufficient_funds'
        )
        
        with self.assertRaises(Exception):  # Would be specific payment exception
            self.service.create_payment_intent(amount=Decimal('10.00'))
    
    @patch('payments.services.stripe.PaymentIntent.create')
    def test_api_connection_error(self, mock_create):
        """Test handling of API connection errors."""
        # Mock connection error
        mock_create.side_effect = stripe.error.APIConnectionError(
            message='Network communication with Stripe failed'
        )
        
        with self.assertRaises(Exception):  # Would be specific connection exception
            self.service.create_payment_intent(amount=Decimal('10.00'))
    
    @patch('payments.services.stripe.PaymentIntent.create')
    def test_authentication_error(self, mock_create):
        """Test handling of authentication errors."""
        # Mock auth error
        mock_create.side_effect = stripe.error.AuthenticationError(
            message='Invalid API key provided'
        )
        
        with self.assertRaises(Exception):  # Would be specific auth exception
            self.service.create_payment_intent(amount=Decimal('10.00'))


class StripeRealAPITest(TestCase):
    """
    Tests using real Stripe Test API (commented out by default).
    
    These tests require actual Stripe test API keys and should only be run
    when testing against the real Stripe API in test mode.
    """
    
    def setUp(self):
        """Set up for real API testing."""
        # Uncomment and configure for real API testing
        # stripe.api_key = 'sk_test_your_actual_test_key_here'
        pass
    
    def test_real_payment_intent_creation(self):
        """Test creating real payment intent (commented out)."""
        # Uncomment for real API testing
        # intent = stripe.PaymentIntent.create(
        #     amount=1000,
        #     currency='usd',
        #     payment_method_types=['card'],
        # )
        # self.assertIsNotNone(intent.id)
        # self.assertEqual(intent.amount, 1000)
        pass
    
    def test_real_connection_token_creation(self):
        """Test creating real terminal connection token (commented out)."""
        # Uncomment for real API testing
        # token = stripe.terminal.ConnectionToken.create()
        # self.assertIsNotNone(token.secret)
        pass
