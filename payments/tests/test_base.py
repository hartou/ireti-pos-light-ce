"""
Test configuration and utilities for Stripe integration tests.
"""

import stripe
from django.test import TestCase
from django.conf import settings
from unittest.mock import Mock, patch
from decimal import Decimal


class StripeTestCase(TestCase):
    """Base test case for Stripe integration tests."""
    
    def setUp(self):
        """Set up test environment with Stripe test configuration."""
        # Use Stripe test keys
        self.stripe_test_secret = 'sk_test_51234567890abcdef'
        self.stripe_test_public = 'pk_test_51234567890abcdef'
        self.webhook_secret = 'whsec_1234567890abcdef'
        
        # Mock Stripe configuration
        self.stripe_patcher = patch.object(stripe, 'api_key', self.stripe_test_secret)
        self.stripe_patcher.start()
        
    def tearDown(self):
        """Clean up test environment."""
        self.stripe_patcher.stop()
    
    def create_mock_payment_intent(self, amount=1000, currency='usd', status='requires_payment_method'):
        """Create a mock Stripe PaymentIntent for testing."""
        return Mock(
            id='pi_test_1234567890',
            object='payment_intent',
            amount=amount,
            currency=currency,
            status=status,
            client_secret='pi_test_1234567890_secret_test',
            payment_method=None,
            confirmation_method='automatic',
            capture_method='automatic',
            created=1234567890,
            metadata={}
        )
    
    def create_mock_refund(self, amount=1000, currency='usd', status='succeeded'):
        """Create a mock Stripe Refund for testing."""
        return Mock(
            id='re_test_1234567890',
            object='refund',
            amount=amount,
            currency=currency,
            status=status,
            payment_intent='pi_test_1234567890',
            reason='requested_by_customer',
            created=1234567890
        )
    
    def create_mock_connection_token(self):
        """Create a mock Stripe Terminal ConnectionToken for testing."""
        return Mock(
            object='terminal.connection_token',
            secret='pst_test_1234567890abcdef'
        )
    
    def create_mock_webhook_event(self, event_type='payment_intent.succeeded', payment_intent_id='pi_test_1234567890'):
        """Create a mock Stripe webhook event for testing."""
        return Mock(
            id='evt_test_1234567890',
            object='event',
            type=event_type,
            data={
                'object': {
                    'id': payment_intent_id,
                    'object': 'payment_intent',
                    'amount': 1000,
                    'currency': 'usd',
                    'status': 'succeeded'
                }
            },
            created=1234567890,
            api_version='2024-06-20'
        )


class StripeTestData:
    """Test data constants for Stripe tests."""
    
    # Test card numbers (from Stripe docs)
    VISA_SUCCESS = '4242424242424242'
    VISA_DECLINE_INSUFFICIENT_FUNDS = '4000000000009995'
    VISA_DECLINE_STOLEN_CARD = '4000000000009979'
    MASTERCARD_SUCCESS = '5555555555554444'
    AMEX_SUCCESS = '378282246310005'
    
    # Test amounts (in cents)
    AMOUNT_SUCCESS = 1000  # $10.00
    AMOUNT_DECLINE = 2000  # $20.00
    
    # Test currencies
    CURRENCY_USD = 'usd'
    CURRENCY_EUR = 'eur'
    
    # Test metadata
    TEST_METADATA = {
        'order_id': '12345',
        'customer_id': 'cust_test_123',
        'store_location': 'downtown'
    }
