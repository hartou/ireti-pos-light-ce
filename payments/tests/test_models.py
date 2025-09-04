"""
Unit tests for Stripe payment models.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from unittest.mock import patch, Mock
from datetime import timedelta

from payments.models import PaymentMethod, PaymentTransaction, PaymentRefund, PaymentWebhook
from transaction.models import transaction
from .test_base import StripeTestCase


class PaymentMethodModelTest(TestCase):
    """Test cases for PaymentMethod model."""
    
    def test_create_payment_method(self):
        """Test creating a payment method."""
        payment_method = PaymentMethod.objects.create(
            name='Credit Card',
            stripe_payment_method_type='card'
        )
        
        self.assertEqual(payment_method.name, 'Credit Card')
        self.assertEqual(payment_method.stripe_payment_method_type, 'card')
        self.assertTrue(payment_method.is_active)
        self.assertEqual(payment_method.sort_order, 0)
    
    def test_payment_method_str(self):
        """Test string representation of payment method."""
        payment_method = PaymentMethod.objects.create(
            name='Credit Card',
            stripe_payment_method_type='card'
        )
        
        expected = 'Credit Card (Credit/Debit Card)'
        self.assertEqual(str(payment_method), expected)
    
    def test_unique_active_payment_method_validation(self):
        """Test validation prevents duplicate active payment methods."""
        # Create first payment method
        PaymentMethod.objects.create(
            name='Credit Card 1',
            stripe_payment_method_type='card',
            is_active=True
        )
        
        # Try to create another active payment method of same type
        duplicate_method = PaymentMethod(
            name='Credit Card 2',
            stripe_payment_method_type='card',
            is_active=True
        )
        
        with self.assertRaises(ValidationError):
            duplicate_method.clean()
    
    def test_inactive_payment_methods_allowed(self):
        """Test that multiple inactive payment methods are allowed."""
        PaymentMethod.objects.create(
            name='Credit Card 1',
            stripe_payment_method_type='card',
            is_active=False
        )
        
        # This should not raise an error
        duplicate_method = PaymentMethod.objects.create(
            name='Credit Card 2',
            stripe_payment_method_type='card',
            is_active=False
        )
        
        self.assertIsNotNone(duplicate_method.pk)


class PaymentTransactionModelTest(StripeTestCase):
    """Test cases for PaymentTransaction model."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        
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
        
        # Create a mock transaction for testing
        # We'll create this in memory since we can't guarantee transaction model availability
        self.mock_transaction = Mock()
        self.mock_transaction.id = 1
        self.mock_transaction.total_sale = Decimal('25.00')
        self.mock_transaction.payment_transactions = Mock()
        
    def test_create_payment_transaction(self):
        """Test creating a payment transaction."""
        payment = PaymentTransaction.objects.create(
            payment_method=self.payment_method,
            amount=Decimal('10.00'),
            currency='usd',
            processed_by=self.user,
            stripe_payment_intent_id='pi_test_1234567890'
        )
        
        self.assertEqual(payment.amount, Decimal('10.00'))
        self.assertEqual(payment.currency, 'usd')
        self.assertEqual(payment.status, 'pending')  # default status
        self.assertEqual(payment.processed_by, self.user)
        self.assertEqual(payment.stripe_payment_intent_id, 'pi_test_1234567890')
    
    def test_payment_transaction_str(self):
        """Test string representation of payment transaction."""
        payment = PaymentTransaction.objects.create(
            payment_method=self.payment_method,
            amount=Decimal('10.00'),
            currency='usd',
            processed_by=self.user,
            stripe_payment_intent_id='pi_test_1234567890'
        )
        
        expected = 'Payment pi_test_1234567890 - 10.00 USD'
        self.assertEqual(str(payment), expected)
    
    def test_payment_transaction_str_without_stripe_id(self):
        """Test string representation when no Stripe ID is present."""
        payment = PaymentTransaction.objects.create(
            payment_method=self.payment_method,
            amount=Decimal('10.00'),
            currency='usd',
            processed_by=self.user
        )
        
        expected = f'Payment {payment.id} - 10.00 USD'
        self.assertEqual(str(payment), expected)
    
    def test_payment_status_change_updates_processed_at(self):
        """Test that changing status to succeeded updates processed_at."""
        payment = PaymentTransaction.objects.create(
            payment_method=self.payment_method,
            amount=Decimal('10.00'),
            currency='usd',
            processed_by=self.user,
            stripe_payment_intent_id='pi_test_1234567890'
        )
        
        # Initially, processed_at should be None
        self.assertIsNone(payment.processed_at)
        
        # Change status to succeeded
        payment.status = 'succeeded'
        payment.save()
        
        # Refresh from database to get updated processed_at
        payment.refresh_from_db()
        
        # Now processed_at should be set
        self.assertIsNotNone(payment.processed_at)
    
    def test_payment_amount_validation(self):
        """Test payment amount validation."""
        # Test minimum amount validation
        with self.assertRaises(ValidationError):
            payment = PaymentTransaction(
                payment_method=self.payment_method,
                amount=Decimal('0.00'),  # Should fail validation
                currency='usd',
                processed_by=self.user
            )
            payment.full_clean()
    
    def test_payment_metadata_default(self):
        """Test that metadata defaults to empty dict."""
        payment = PaymentTransaction.objects.create(
            payment_method=self.payment_method,
            amount=Decimal('10.00'),
            currency='usd',
            processed_by=self.user
        )
        
        self.assertEqual(payment.metadata, {})
    
    def test_payment_customer_properties(self):
        """Test customer-related properties."""
        metadata = {
            'customer_name': 'John Doe',
            'customer_email': 'john@example.com',
            'customer_phone': '+1234567890',
            'billing_address': {'line1': '123 Main St', 'city': 'Anytown'},
            'card_last_four': '4242'
        }
        
        payment = PaymentTransaction.objects.create(
            payment_method=self.payment_method,
            amount=Decimal('10.00'),
            currency='usd',
            processed_by=self.user,
            metadata=metadata
        )
        
        self.assertEqual(payment.customer_name, 'John Doe')
        self.assertEqual(payment.customer_email, 'john@example.com')
        self.assertEqual(payment.customer_phone, '+1234567890')
        self.assertEqual(payment.billing_address['line1'], '123 Main St')
        self.assertEqual(payment.card_last_four, '4242')
    
    def test_payment_receipt_number_generation(self):
        """Test receipt number generation."""
        payment = PaymentTransaction.objects.create(
            payment_method=self.payment_method,
            amount=Decimal('10.00'),
            currency='usd',
            processed_by=self.user
        )
        
        receipt_number = payment.receipt_number
        # Should start with R and today's date
        today_str = timezone.now().strftime('%Y%m%d')
        self.assertTrue(receipt_number.startswith(f'R{today_str}'))
        
    def test_refunded_amount_property(self):
        """Test refunded amount calculation."""
        payment = PaymentTransaction.objects.create(
            payment_method=self.payment_method,
            amount=Decimal('10.00'),
            currency='usd',
            processed_by=self.user
        )
        
        # Initially should be 0
        self.assertEqual(payment.refunded_amount, Decimal('0.00'))
    
    def test_refundable_amount_property(self):
        """Test refundable amount calculation."""
        payment = PaymentTransaction.objects.create(
            payment_method=self.payment_method,
            amount=Decimal('10.00'),
            currency='usd',
            processed_by=self.user,
            status='succeeded'
        )
        
        # Should be equal to payment amount for succeeded payment
        self.assertEqual(payment.refundable_amount, Decimal('10.00'))
        
        # Should be 0 for non-succeeded payment
        payment.status = 'failed'
        payment.save()
        self.assertEqual(payment.refundable_amount, Decimal('0.00'))
    
    def test_net_amount_property(self):
        """Test net amount calculation."""
        payment = PaymentTransaction.objects.create(
            payment_method=self.payment_method,
            amount=Decimal('10.00'),
            currency='usd',
            processed_by=self.user
        )
        
        # Should equal payment amount minus refunded amount
        self.assertEqual(payment.net_amount, Decimal('10.00'))


class PaymentRefundModelTest(StripeTestCase):
    """Test cases for PaymentRefund model."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        
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
        
        # Create test payment transaction
        self.payment_transaction = PaymentTransaction.objects.create(
            payment_method=self.payment_method,
            amount=Decimal('100.00'),
            currency='usd',
            processed_by=self.user,
            stripe_payment_intent_id='pi_test_1234567890',
            status='succeeded'
        )
    
    def test_create_payment_refund(self):
        """Test creating a payment refund."""
        refund = PaymentRefund.objects.create(
            payment_transaction=self.payment_transaction,
            amount=Decimal('25.00'),
            currency='usd',
            reason='requested_by_customer',
            processed_by=self.user,
            stripe_refund_id='re_test_1234567890'
        )
        
        self.assertEqual(refund.amount, Decimal('25.00'))
        self.assertEqual(refund.currency, 'usd')
        self.assertEqual(refund.reason, 'requested_by_customer')
        self.assertEqual(refund.status, 'pending')  # default status
        self.assertEqual(refund.processed_by, self.user)
    
    def test_refund_str_representation(self):
        """Test string representation of refund."""
        refund = PaymentRefund.objects.create(
            payment_transaction=self.payment_transaction,
            amount=Decimal('25.00'),
            currency='usd',
            reason='requested_by_customer',
            processed_by=self.user,
            stripe_refund_id='re_test_1234567890'
        )
        
        expected = 'Refund re_test_1234567890 - 25.00 USD'
        self.assertEqual(str(refund), expected)
    
    def test_refund_without_stripe_id(self):
        """Test string representation when no Stripe ID is present."""
        refund = PaymentRefund.objects.create(
            payment_transaction=self.payment_transaction,
            amount=Decimal('25.00'),
            currency='usd',
            reason='requested_by_customer',
            processed_by=self.user
        )
        
        expected = f'Refund {refund.id} - 25.00 USD'
        self.assertEqual(str(refund), expected)
    
    def test_refund_amount_validation(self):
        """Test that refund amount cannot exceed payment amount."""
        # This should fail validation during clean()
        refund = PaymentRefund(
            payment_transaction=self.payment_transaction,
            amount=Decimal('150.00'),  # More than payment amount
            currency='usd',
            reason='requested_by_customer',
            processed_by=self.user
        )
        
        with self.assertRaises(ValidationError):
            refund.clean()
    
    def test_refund_status_change_updates_processed_at(self):
        """Test that changing status to succeeded updates processed_at."""
        refund = PaymentRefund.objects.create(
            payment_transaction=self.payment_transaction,
            amount=Decimal('25.00'),
            currency='usd',
            reason='requested_by_customer',
            processed_by=self.user
        )
        
        # Initially, processed_at should be None
        self.assertIsNone(refund.processed_at)
        
        # Change status to succeeded
        refund.status = 'succeeded'
        refund.save()
        
        # Refresh from database to get updated processed_at
        refund.refresh_from_db()
        
        # Now processed_at should be set
        self.assertIsNotNone(refund.processed_at)
    
    def test_refund_currency_inheritance(self):
        """Test that currency is inherited from payment transaction if not set."""
        refund = PaymentRefund(
            payment_transaction=self.payment_transaction,
            amount=Decimal('25.00'),
            reason='requested_by_customer',
            processed_by=self.user
        )
        
        # Before save, currency should not be set
        self.assertEqual(refund.currency, 'usd')  # Default from model
        
        refund.currency = ''  # Clear currency to test inheritance
        refund.save()
        
        # After save, currency should be inherited from payment transaction
        refund.refresh_from_db()
        self.assertEqual(refund.currency, self.payment_transaction.currency)
    
    def test_refund_metadata_default(self):
        """Test that metadata defaults to empty dict."""
        refund = PaymentRefund.objects.create(
            payment_transaction=self.payment_transaction,
            amount=Decimal('25.00'),
            currency='usd',
            reason='requested_by_customer',
            processed_by=self.user
        )
        
        self.assertEqual(refund.metadata, {})
    
    def test_multiple_refunds_validation(self):
        """Test validation prevents refunds exceeding payment amount."""
        # Create first refund
        PaymentRefund.objects.create(
            payment_transaction=self.payment_transaction,
            amount=Decimal('60.00'),
            currency='usd',
            reason='requested_by_customer',
            processed_by=self.user,
            status='succeeded'
        )
        
        # Try to create second refund that would exceed payment amount
        refund2 = PaymentRefund(
            payment_transaction=self.payment_transaction,
            amount=Decimal('50.00'),  # 60 + 50 = 110 > 100
            currency='usd',
            reason='requested_by_customer',
            processed_by=self.user
        )
        
        with self.assertRaises(ValidationError):
            refund2.clean()
    
    def test_get_reason_display(self):
        """Test get_reason_display method."""
        refund = PaymentRefund.objects.create(
            payment_transaction=self.payment_transaction,
            amount=Decimal('25.00'),
            currency='usd',
            reason='requested_by_customer',
            processed_by=self.user
        )
        
        self.assertEqual(refund.get_reason_display(), 'Requested by Customer')
    
    def test_original_payment_property(self):
        """Test original_payment property alias."""
        refund = PaymentRefund.objects.create(
            payment_transaction=self.payment_transaction,
            amount=Decimal('25.00'),
            currency='usd',
            reason='requested_by_customer',
            processed_by=self.user
        )
        
        self.assertEqual(refund.original_payment, self.payment_transaction)


class PaymentWebhookModelTest(TestCase):
    """Test cases for PaymentWebhook model."""
    
    def test_create_webhook_event(self):
        """Test creating a webhook event record."""
        webhook = PaymentWebhook.objects.create(
            stripe_event_id='evt_test_1234567890',
            event_type='payment_intent.succeeded'
        )
        
        self.assertEqual(webhook.stripe_event_id, 'evt_test_1234567890')
        self.assertEqual(webhook.event_type, 'payment_intent.succeeded')
        self.assertFalse(webhook.processed)
        self.assertIsNone(webhook.processed_at)
    
    def test_webhook_str_representation(self):
        """Test string representation shows processing status."""
        webhook = PaymentWebhook.objects.create(
            stripe_event_id='evt_test_1234567890',
            event_type='payment_intent.succeeded'
        )
        
        # Unprocessed webhook
        expected = '⏳ payment_intent.succeeded (evt_test_1234567890)'
        self.assertEqual(str(webhook), expected)
        
        # Mark as processed
        webhook.mark_processed()
        expected = '✓ payment_intent.succeeded (evt_test_1234567890)'
        self.assertEqual(str(webhook), expected)
    
    def test_mark_processed_method(self):
        """Test mark_processed method updates status and timestamp."""
        webhook = PaymentWebhook.objects.create(
            stripe_event_id='evt_test_1234567890',
            event_type='payment_intent.succeeded'
        )
        
        # Mark as processed successfully
        webhook.mark_processed()
        
        self.assertTrue(webhook.processed)
        self.assertIsNone(webhook.processing_error)
        self.assertIsNotNone(webhook.processed_at)
        
        # Mark as processed with error
        webhook.mark_processed(error='Test error')
        
        self.assertFalse(webhook.processed)
        self.assertEqual(webhook.processing_error, 'Test error')
        self.assertIsNotNone(webhook.processed_at)
    
    def test_webhook_event_data_storage(self):
        """Test storing event data in webhook."""
        event_data = {
            'id': 'evt_test_1234567890',
            'type': 'payment_intent.succeeded',
            'data': {
                'object': {
                    'id': 'pi_test_1234567890',
                    'amount': 1000,
                    'currency': 'usd',
                    'status': 'succeeded'
                }
            }
        }
        
        webhook = PaymentWebhook.objects.create(
            stripe_event_id='evt_test_1234567890',
            event_type='payment_intent.succeeded',
            event_data=event_data
        )
        
        self.assertEqual(webhook.event_data, event_data)
        self.assertEqual(webhook.event_data['data']['object']['amount'], 1000)
    
    def test_webhook_unique_stripe_event_id(self):
        """Test that Stripe event IDs are unique."""
        PaymentWebhook.objects.create(
            stripe_event_id='evt_test_1234567890',
            event_type='payment_intent.succeeded'
        )
        
        # Try to create another webhook with same Stripe event ID
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            PaymentWebhook.objects.create(
                stripe_event_id='evt_test_1234567890',
                event_type='payment_intent.payment_failed'
            )
    
    def test_webhook_ordering(self):
        """Test that webhooks are ordered by creation date (newest first)."""
        # Create webhooks with slight time differences
        webhook1 = PaymentWebhook.objects.create(
            stripe_event_id='evt_test_1',
            event_type='payment_intent.created'
        )
        
        webhook2 = PaymentWebhook.objects.create(
            stripe_event_id='evt_test_2',
            event_type='payment_intent.succeeded'
        )
        
        # Latest should be first
        webhooks = list(PaymentWebhook.objects.all())
        self.assertEqual(webhooks[0], webhook2)
        self.assertEqual(webhooks[1], webhook1)
