"""
Payment models for Stripe integration.
"""

import uuid
import json
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from transaction.models import transaction


class PaymentMethod(models.Model):
    """
    Payment method configuration model for Stripe integration.
    """
    
    STRIPE_PAYMENT_METHOD_TYPES = [
        ('card', 'Credit/Debit Card'),
        ('us_bank_account', 'US Bank Account'),
        ('sepa_debit', 'SEPA Direct Debit'),
        ('ideal', 'iDEAL'),
        ('sofort', 'Sofort'),
        ('bancontact', 'Bancontact'),
        ('giropay', 'Giropay'),
        ('p24', 'Przelewy24'),
        ('eps', 'EPS'),
        ('fpx', 'FPX'),
        ('grabpay', 'GrabPay'),
        ('alipay', 'Alipay'),
        ('wechat_pay', 'WeChat Pay'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, help_text="Display name for payment method")
    stripe_payment_method_type = models.CharField(
        max_length=50, 
        choices=STRIPE_PAYMENT_METHOD_TYPES,
        help_text="Stripe payment method type identifier"
    )
    is_active = models.BooleanField(default=True, help_text="Whether this payment method is active")
    sort_order = models.PositiveIntegerField(
        default=0, 
        help_text="Sort order for display (lower numbers first)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = "Payment Method"
        verbose_name_plural = "Payment Methods"
    
    def __str__(self):
        return f"{self.name} ({self.get_stripe_payment_method_type_display()})"
    
    def clean(self):
        """Validate the payment method configuration."""
        super().clean()
        
        # Ensure unique active payment methods for same Stripe type
        if self.is_active:
            existing = PaymentMethod.objects.filter(
                stripe_payment_method_type=self.stripe_payment_method_type,
                is_active=True
            ).exclude(pk=self.pk)
            
            if existing.exists():
                raise ValidationError(
                    f"An active payment method already exists for {self.get_stripe_payment_method_type_display()}"
                )


class PaymentTransaction(models.Model):
    """
    Payment transaction model for tracking Stripe payments.
    """
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('canceled', 'Canceled'),
    ]
    
    CURRENCY_CHOICES = [
        ('usd', 'USD'),
        ('eur', 'EUR'),
        ('gbp', 'GBP'),
        ('cad', 'CAD'),
        ('aud', 'AUD'),
        ('jpy', 'JPY'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction = models.ForeignKey(
        transaction, 
        on_delete=models.CASCADE,
        related_name='payment_transactions',
        null=True,
        blank=True,
        help_text="Related POS transaction"
    )
    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.PROTECT,
        related_name='transactions',
        null=True,
        blank=True,
        help_text="Payment method used"
    )
    
    # Payment details
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Payment amount"
    )
    currency = models.CharField(
        max_length=3, 
        choices=CURRENCY_CHOICES,
        default='usd',
        help_text="Payment currency"
    )
    status = models.CharField(
        max_length=20, 
        choices=PAYMENT_STATUS_CHOICES,
        default='pending',
        help_text="Payment status"
    )
    
    # Stripe integration fields
    stripe_payment_intent_id = models.CharField(
        max_length=255, 
        unique=True, 
        null=True, 
        blank=True,
        help_text="Stripe PaymentIntent ID"
    )
    stripe_client_secret = models.CharField(
        max_length=255, 
        null=True, 
        blank=True,
        help_text="Stripe client secret for frontend"
    )
    stripe_status = models.CharField(
        max_length=50, 
        null=True, 
        blank=True,
        help_text="Status from Stripe"
    )
    last_payment_error = models.TextField(
        null=True, 
        blank=True,
        help_text="Last error message from Stripe"
    )
    
    # Audit and tracking
    processed_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='processed_payments',
        null=True,
        blank=True,
        help_text="User who processed the payment"
    )
    failure_reason = models.TextField(null=True, blank=True, help_text="Reason for payment failure")
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional payment metadata")
    idempotency_key = models.CharField(
        max_length=255, 
        unique=True, 
        null=True, 
        blank=True,
        help_text="Idempotency key for preventing duplicate charges"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True, help_text="When payment was processed")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Payment Transaction"
        verbose_name_plural = "Payment Transactions"
        indexes = [
            models.Index(fields=['stripe_payment_intent_id']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['transaction', 'status']),
        ]
    
    def __str__(self):
        return f"Payment {self.stripe_payment_intent_id or self.id} - {self.amount} {self.currency.upper()}"
    
    def save(self, *args, **kwargs):
        """Custom save method to handle status changes."""
        if self.pk:
            # Update processed_at when status changes to succeeded
            try:
                old_instance = PaymentTransaction.objects.get(pk=self.pk)
                if old_instance.status != 'succeeded' and self.status == 'succeeded':
                    self.processed_at = timezone.now()
            except PaymentTransaction.DoesNotExist:
                # This shouldn't happen, but let's be safe
                pass
        
        super().save(*args, **kwargs)
    
    @property
    def customer_name(self):
        """Get customer name from metadata or transaction."""
        if 'customer_name' in self.metadata:
            return self.metadata['customer_name']
        elif self.transaction and hasattr(self.transaction, 'customer_name'):
            return getattr(self.transaction, 'customer_name', None)
        return None
    
    @property
    def customer_email(self):
        """Get customer email from metadata or transaction."""
        if 'customer_email' in self.metadata:
            return self.metadata['customer_email']
        elif self.transaction and hasattr(self.transaction, 'customer_email'):
            return getattr(self.transaction, 'customer_email', None)
        return None
    
    @property
    def customer_phone(self):
        """Get customer phone from metadata or transaction."""
        if 'customer_phone' in self.metadata:
            return self.metadata['customer_phone']
        elif self.transaction and hasattr(self.transaction, 'customer_phone'):
            return getattr(self.transaction, 'customer_phone', None)
        return None
    
    @property
    def billing_address(self):
        """Get billing address from metadata."""
        return self.metadata.get('billing_address', None)
    
    @property
    def receipt_number(self):
        """Get receipt number from transaction or generate one."""
        if self.transaction and hasattr(self.transaction, 'receipt_number'):
            return getattr(self.transaction, 'receipt_number', None)
        elif 'receipt_number' in self.metadata:
            return self.metadata['receipt_number']
        # Generate a receipt number based on creation date and ID
        return f"R{self.created_at.strftime('%Y%m%d')}-{str(self.id)[:8].upper()}"
    
    @property
    def card_last_four(self):
        """Get last four digits of card from metadata."""
        return self.metadata.get('card_last_four', None)
    
    @property 
    def refunded_amount(self):
        """Calculate total refunded amount."""
        return self.refunds.filter(status='succeeded').aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')
    
    @property
    def refundable_amount(self):
        """Calculate remaining refundable amount."""
        if self.status != 'succeeded':
            return Decimal('0.00')
        return self.amount - self.refunded_amount
    
    @property
    def net_amount(self):
        """Calculate net amount after refunds."""
        return self.amount - self.refunded_amount
    
    @property
    def created(self):
        """Alias for created_at to match template expectations."""
        return self.created_at
    
    @property
    def updated(self):
        """Alias for updated_at to match template expectations."""
        return self.updated_at
    
    def get_status_display(self):
        """Get human readable status."""
        return dict(self.PAYMENT_STATUS_CHOICES).get(self.status, self.status.title())

    def clean(self):
        """Validate the payment transaction."""
        super().clean()
        
        # Ensure amount matches transaction total for single payments
        if self.transaction_id and self.amount:
            transaction_payments = PaymentTransaction.objects.filter(
                transaction=self.transaction,
                status__in=['succeeded', 'processing']
            ).exclude(pk=self.pk)
            
            total_paid = sum(p.amount for p in transaction_payments)
            if total_paid + self.amount > self.transaction.total_sale:
                raise ValidationError("Payment amount exceeds remaining transaction balance")


class PaymentRefund(models.Model):
    """
    Payment refund model for tracking Stripe refunds.
    """
    
    REFUND_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('canceled', 'Canceled'),
    ]
    
    REFUND_REASON_CHOICES = [
        ('duplicate', 'Duplicate'),
        ('fraudulent', 'Fraudulent'),
        ('requested_by_customer', 'Requested by Customer'),
        ('expired_uncaptured_charge', 'Expired Uncaptured Charge'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment_transaction = models.ForeignKey(
        PaymentTransaction,
        on_delete=models.CASCADE,
        related_name='refunds',
        help_text="Related payment transaction"
    )
    
    # Refund details
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Refund amount"
    )
    currency = models.CharField(max_length=3, default='usd', help_text="Refund currency")
    reason = models.CharField(
        max_length=50, 
        choices=REFUND_REASON_CHOICES,
        help_text="Reason for refund"
    )
    description = models.TextField(null=True, blank=True, help_text="Refund description")
    status = models.CharField(
        max_length=20, 
        choices=REFUND_STATUS_CHOICES,
        default='pending',
        help_text="Refund status"
    )
    
    # Stripe integration
    stripe_refund_id = models.CharField(
        max_length=255, 
        unique=True, 
        null=True, 
        blank=True,
        help_text="Stripe Refund ID"
    )
    
    # Authorization and processing
    processed_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='processed_refunds',
        null=True,
        blank=True,
        help_text="User who processed the refund"
    )
    authorized_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='authorized_refunds',
        null=True,
        blank=True,
        help_text="User who authorized the refund (if different from processor)"
    )
    
    # Additional fields for payment history
    notes = models.TextField(null=True, blank=True, help_text="Additional notes about the refund")
    
    # Audit and tracking
    failure_reason = models.TextField(null=True, blank=True, help_text="Reason for refund failure")
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional refund metadata")
    idempotency_key = models.CharField(
        max_length=255, 
        unique=True, 
        null=True, 
        blank=True,
        help_text="Idempotency key for preventing duplicate refunds"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True, help_text="When refund was processed")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Payment Refund"
        verbose_name_plural = "Payment Refunds"
        indexes = [
            models.Index(fields=['stripe_refund_id']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['payment_transaction', 'status']),
        ]
    
    def __str__(self):
        return f"Refund {self.stripe_refund_id or self.id} - {self.amount} {self.currency.upper()}"
    
    @property
    def created(self):
        """Alias for created_at to match template expectations."""
        return self.created_at
    
    @property
    def original_payment(self):
        """Alias for payment_transaction to match template expectations."""
        return self.payment_transaction
    
    def get_status_display(self):
        """Get human readable status."""
        return dict(self.REFUND_STATUS_CHOICES).get(self.status, self.status.title())
    
    def get_reason_display(self):
        """Get human readable reason."""
        return dict(self.REFUND_REASON_CHOICES).get(self.reason, self.reason.replace('_', ' ').title())
    
    def save(self, *args, **kwargs):
        """Custom save method to handle status changes."""
        if self.pk:
            # Update processed_at when status changes to succeeded
            try:
                old_instance = PaymentRefund.objects.get(pk=self.pk)
                if old_instance.status != 'succeeded' and self.status == 'succeeded':
                    self.processed_at = timezone.now()
            except PaymentRefund.DoesNotExist:
                # This shouldn't happen, but let's be safe
                pass
        
        # Set currency from parent payment transaction if not specified
        if not self.currency and self.payment_transaction:
            self.currency = self.payment_transaction.currency
            
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validate the refund."""
        super().clean()
        
        if self.payment_transaction and self.amount:
            # Ensure refund amount doesn't exceed remaining refundable amount
            existing_refunds = PaymentRefund.objects.filter(
                payment_transaction=self.payment_transaction,
                status__in=['succeeded', 'pending']
            ).exclude(pk=self.pk)
            
            total_refunded = sum(r.amount for r in existing_refunds)
            if total_refunded + self.amount > self.payment_transaction.amount:
                raise ValidationError("Refund amount exceeds remaining refundable balance")


class PaymentWebhook(models.Model):
    """
    Webhook event model for tracking Stripe webhook events.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stripe_event_id = models.CharField(
        max_length=255, 
        unique=True,
        help_text="Stripe event ID"
    )
    event_type = models.CharField(
        max_length=100,
        help_text="Type of Stripe event"
    )
    processed = models.BooleanField(
        default=False,
        help_text="Whether the webhook has been processed"
    )
    processing_error = models.TextField(
        null=True, 
        blank=True,
        help_text="Error message if processing failed"
    )
    event_data = models.JSONField(
        null=True, 
        blank=True,
        help_text="Raw event data from Stripe"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Payment Webhook"
        verbose_name_plural = "Payment Webhooks"
        indexes = [
            models.Index(fields=['stripe_event_id']),
            models.Index(fields=['event_type', 'processed']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        status = "✓" if self.processed else "⏳"
        return f"{status} {self.event_type} ({self.stripe_event_id})"
    
    def mark_processed(self, error=None):
        """Mark webhook as processed."""
        self.processed = error is None
        self.processing_error = error
        self.processed_at = timezone.now()
        self.save(update_fields=['processed', 'processing_error', 'processed_at'])


class PaymentMetric(models.Model):
    """
    Payment metrics model for tracking payment performance and observability.
    Used to collect data for monitoring payment success rates, latency, and error analysis.
    """
    
    METRIC_EVENT_TYPES = [
        ('payment_attempt', 'Payment Attempt'),
        ('payment_success', 'Payment Success'),
        ('payment_failure', 'Payment Failure'),
        ('refund_success', 'Refund Success'),
        ('refund_failure', 'Refund Failure'),
        ('webhook_received', 'Webhook Received'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(
        max_length=20, 
        choices=METRIC_EVENT_TYPES,
        help_text="Type of payment metric event"
    )
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Payment amount (if applicable)"
    )
    currency = models.CharField(
        max_length=3, 
        default='USD',
        help_text="ISO currency code"
    )
    metadata = models.JSONField(
        default=dict,
        help_text="Additional metric metadata (processing time, error codes, etc.)"
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        help_text="When this metric event occurred"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Payment Metric"
        verbose_name_plural = "Payment Metrics"
        indexes = [
            models.Index(fields=['event_type', 'timestamp']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['currency', 'timestamp']),
        ]
    
    def __str__(self):
        if self.amount:
            return f"{self.get_event_type_display()} - {self.amount} {self.currency}"
        return f"{self.get_event_type_display()}"
    
    @property
    def processing_time_ms(self):
        """Get processing time in milliseconds from metadata."""
        return self.metadata.get('processing_time_ms')
    
    @property
    def error_code(self):
        """Get error code from metadata."""
        return self.metadata.get('error_code')
    
    def clean(self):
        """Validate the metric data."""
        super().clean()
        
        # Payment and refund events should have amounts
        if self.event_type in ['payment_attempt', 'payment_success', 'payment_failure', 
                              'refund_success', 'refund_failure']:
            if self.amount is None:
                raise ValidationError("Amount is required for payment and refund events")
        
        # Webhook events should not have amounts
        if self.event_type == 'webhook_received':
            if self.amount is not None:
                raise ValidationError("Amount should not be set for webhook events")
