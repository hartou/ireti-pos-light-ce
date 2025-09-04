"""
Tests for Stripe payment integration with transactions.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.conf import settings
from decimal import Decimal
from datetime import datetime
import json
from unittest.mock import patch, MagicMock

from transaction.models import transaction
from payments.models import PaymentTransaction, PaymentMethod
from payments.services import StripePaymentService


class StripeTransactionIntegrationTest(TestCase):
    """Test Stripe payment integration with POS transactions."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        # Create a payment method for testing
        self.payment_method = PaymentMethod.objects.create(
            name='Test Card',
            stripe_payment_method_type='card',
            is_active=True
        )
    
    @patch('payments.services.StripePaymentService._make_stripe_request')
    def test_stripe_payment_service_integration(self, mock_stripe_request):
        """Test that StripePaymentService integration methods work."""
        # Mock Stripe API response
        mock_stripe_request.return_value = {
            'id': 'pi_test_123456',
            'amount': 2198,  # cents
            'currency': 'usd',
            'status': 'requires_payment_method',
            'client_secret': 'pi_test_123456_secret',
            'metadata': {'transaction_id': 'TEST001'}
        }
        
        # Create a test transaction with minimal data (bypass inventory requirements)
        test_transaction = transaction(
            transaction_id='TEST001',
            transaction_dt=datetime(2025, 9, 2, 12, 0, 0),
            user=self.user,
            total_sale=Decimal('21.98'),
            sub_total=Decimal('20.00'),
            tax_total=Decimal('1.98'),
            deposit_total=Decimal('0.00'),
            payment_type='STRIPE',
            receipt='Test receipt',
            products='[]'  # Empty products to avoid inventory lookup
        )
        
        # Override save method to skip product processing
        with patch.object(test_transaction, 'save', wraps=lambda *args, **kwargs: super(transaction, test_transaction).save(*args, **kwargs)):
            test_transaction.save()
        
        # Test payment intent data
        mock_intent_data = {
            'id': 'pi_test_123456',
            'amount': 2198,  # cents
            'currency': 'usd',
            'status': 'requires_payment_method',
            'client_secret': 'pi_test_123456_secret',
            'metadata': {'transaction_id': 'TEST001'}
        }
        
        # Test linking transaction to payment
        stripe_service = StripePaymentService()
        payment_transaction = stripe_service.link_transaction_to_payment(
            test_transaction, 
            mock_intent_data
        )
        
        # Verify payment transaction was created correctly
        self.assertEqual(payment_transaction.transaction, test_transaction)
        self.assertEqual(payment_transaction.amount, Decimal('21.98'))
        self.assertEqual(payment_transaction.currency, 'usd')
        self.assertEqual(payment_transaction.stripe_payment_intent_id, 'pi_test_123456')
        self.assertEqual(payment_transaction.status, 'pending')
        
        # Test transaction properties
        self.assertTrue(test_transaction.has_stripe_payment)
        self.assertEqual(test_transaction.stripe_payment_status, 'pending')
        
        # Test status update
        updated_transaction = stripe_service.update_transaction_payment_status(test_transaction)
        self.assertEqual(updated_transaction, test_transaction)
    
    def test_transaction_model_properties(self):
        """Test transaction model Stripe-related properties."""
        # Create transactions without triggering the save method inventory checks
        with patch('transaction.models.transaction.save', new=lambda self, *args, **kwargs: super(transaction, self).save(*args, **kwargs)):
            # Create a non-Stripe transaction
            cash_transaction = transaction.objects.create(
                transaction_id='CASH001',
                transaction_dt=datetime(2025, 9, 2, 12, 0, 0),
                user=self.user,
                total_sale=Decimal('21.98'),
                sub_total=Decimal('20.00'),
                tax_total=Decimal('1.98'),
                deposit_total=Decimal('0.00'),
                payment_type='CASH',
                receipt='Cash receipt',
                products='[]'
            )
            
            # Test that cash transaction doesn't have Stripe payment
            self.assertFalse(cash_transaction.has_stripe_payment)
            self.assertIsNone(cash_transaction.stripe_payment_status)
            
            # Create a Stripe transaction
            stripe_transaction = transaction.objects.create(
                transaction_id='STRIPE001',
                transaction_dt=datetime(2025, 9, 2, 12, 0, 0),
                user=self.user,
                total_sale=Decimal('21.98'),
                sub_total=Decimal('20.00'),
                tax_total=Decimal('1.98'),
                deposit_total=Decimal('0.00'),
                payment_type='STRIPE',
                receipt='Stripe receipt',
                products='[]'
            )
            
            # Test that Stripe transaction without payment records returns pending
            self.assertEqual(stripe_transaction.stripe_payment_status, 'pending')

    def test_stripe_status_mapping(self):
        """Test the Stripe status mapping functionality."""
        stripe_service = StripePaymentService()
        
        # Test various Stripe statuses
        test_cases = [
            ('requires_payment_method', 'pending'),
            ('requires_confirmation', 'pending'),
            ('requires_action', 'pending'),
            ('processing', 'processing'),
            ('succeeded', 'succeeded'),
            ('canceled', 'canceled'),
            ('unknown_status', 'unknown_status'),  # Should pass through unknown statuses
        ]
        
        for stripe_status, expected_internal_status in test_cases:
            with self.subTest(stripe_status=stripe_status):
                result = stripe_service._map_stripe_status(stripe_status)
                self.assertEqual(result, expected_internal_status)


if __name__ == '__main__':
    import unittest
    unittest.main()
