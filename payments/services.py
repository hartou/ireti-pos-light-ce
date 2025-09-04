"""
Stripe payment service integration.

This module provides a service layer for interacting with the Stripe API
to process payments, handle refunds, and manage terminal connections.
All operations follow PCI DSS compliance standards.

Uses direct HTTP requests to the Stripe API for maximum compatibility.
"""

import logging
import requests
import json
import hashlib
import hmac
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from typing import Dict, Any, Optional, List

from .models import PaymentTransaction, PaymentRefund, PaymentMethod, PaymentWebhook
from .logging_utils import secure_log_payment_event, create_audit_trail, redact_sensitive_data
from .metrics import payment_metrics, MetricsTimer
from .exceptions import (
    StripeConfigurationError,
    PaymentIntentError,
    RefundError,
    ConnectionTokenError,
    TerminalError,
    PaymentAmountError,
    CurrencyError,
    AuthenticationError
)

logger = logging.getLogger(__name__)


class StripePaymentService:
    """
    Service class for handling Stripe payment operations using direct HTTP API calls.
    
    This class encapsulates all Stripe API interactions and provides
    a clean interface for payment processing operations.
    """
    
    STRIPE_API_BASE_URL = "https://api.stripe.com/v1"
    
    def __init__(self):
        """Initialize the Stripe service with API configuration."""
        self._configure_stripe()
    
    def _configure_stripe(self):
        """Configure Stripe API with keys from Django settings."""
        if not hasattr(settings, 'STRIPE_SECRET_KEY') or not settings.STRIPE_SECRET_KEY:
            raise StripeConfigurationError("STRIPE_SECRET_KEY not configured")
        
        self.secret_key = settings.STRIPE_SECRET_KEY
        
        # Validate key format
        if not (self.secret_key.startswith('sk_test_') or self.secret_key.startswith('sk_live_')):
            raise StripeConfigurationError("STRIPE_SECRET_KEY must start with 'sk_test_' or 'sk_live_'")
        
        # Set up default headers for API requests
        self.headers = {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Stripe-Version': getattr(settings, 'STRIPE_API_VERSION', '2024-06-20')
        }
        
        logger.info("Stripe payment service configured successfully")
    
    def _make_stripe_request(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make a request to the Stripe API.
        
        Args:
            method: HTTP method ('GET', 'POST', 'PUT', 'DELETE')
            endpoint: API endpoint (without base URL)
            data: Request data
            
        Returns:
            Response data as dictionary
            
        Raises:
            Exception: If request fails
        """
        url = f"{self.STRIPE_API_BASE_URL}/{endpoint.lstrip('/')}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers, params=data, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=self.headers, data=data, timeout=30)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=self.headers, data=data, timeout=30)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=self.headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get('error', {}).get('message', f'HTTP {response.status_code}')
                # Use secure logging to avoid logging sensitive data in error responses
                secure_log_payment_event(
                    logger, logging.ERROR, 
                    f"Stripe API error: {response.status_code}",
                    {'error_type': error_data.get('error', {}).get('type', 'unknown')}
                )
                raise Exception(f"Stripe API error: {error_msg}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error communicating with Stripe: {str(e)}")
            raise Exception(f"Network error: {str(e)}")
    
    def create_payment_intent(
        self,
        amount: Decimal,
        currency: str = 'usd',
        payment_method_types: Optional[List[str]] = None,
        capture_method: str = 'automatic',
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a PaymentIntent with the Stripe API.
        
        Args:
            amount: Payment amount as Decimal (e.g., Decimal('10.50'))
            currency: Currency code (default: 'usd')
            payment_method_types: List of payment method types (default: ['card'])
            capture_method: 'automatic' or 'manual' capture
            metadata: Additional metadata to attach to the payment
            
        Returns:
            Dictionary containing PaymentIntent data
            
        Raises:
            PaymentIntentError: If payment intent creation fails
            PaymentAmountError: If amount is invalid
        """
        with MetricsTimer() as timer:
            try:
                # Record payment attempt
                payment_metrics.record_payment_attempt(float(amount), currency.upper())
                
                # Validate amount
                if amount <= 0:
                    raise PaymentAmountError(f"Amount must be positive, got: {amount}")
                
                # Convert amount to cents (Stripe expects integer cents)
                amount_cents = self._amount_to_cents(amount)
                
                # Set default payment method types
                if payment_method_types is None:
                    payment_method_types = ['card']
                
                # Prepare request data
                data = {
                    'amount': amount_cents,
                    'currency': currency.lower(),
                    'capture_method': capture_method
                }
                
                # Add payment method types
                for i, pmt in enumerate(payment_method_types):
                    data[f'payment_method_types[{i}]'] = pmt
                
                # Add metadata if provided
                if metadata:
                    for key, value in metadata.items():
                        data[f'metadata[{key}]'] = str(value)
                
                # Make API request
                intent_data = self._make_stripe_request('POST', 'payment_intents', data)
                
                logger.info(f"Created PaymentIntent: {intent_data.get('id')}")
                return intent_data
                    
            except Exception as e:
                if isinstance(e, PaymentAmountError):
                    raise
                logger.error(f"Error creating PaymentIntent: {str(e)}")
                raise PaymentIntentError(f"Failed to create payment intent: {str(e)}")
    
    def retrieve_payment_intent(self, payment_intent_id: str) -> Dict[str, Any]:
        """
        Retrieve a PaymentIntent from Stripe.
        
        Args:
            payment_intent_id: Stripe PaymentIntent ID
            
        Returns:
            Dictionary containing PaymentIntent data
            
        Raises:
            PaymentIntentError: If retrieval fails
        """
        try:
            intent_data = self._make_stripe_request('GET', f'payment_intents/{payment_intent_id}')
            logger.info(f"Retrieved PaymentIntent: {payment_intent_id}")
            return intent_data
            
        except Exception as e:
            logger.error(f"Error retrieving PaymentIntent {payment_intent_id}: {str(e)}")
            raise PaymentIntentError(f"Error retrieving payment: {str(e)}")
    
    def confirm_payment_intent(self, payment_intent_id: str) -> Dict[str, Any]:
        """
        Confirm a PaymentIntent to complete the payment.
        
        Args:
            payment_intent_id: Stripe PaymentIntent ID
            
        Returns:
            Dictionary containing confirmed PaymentIntent data
            
        Raises:
            PaymentIntentError: If confirmation fails
        """
        try:
            intent_data = self._make_stripe_request('POST', f'payment_intents/{payment_intent_id}/confirm')
            logger.info(f"PaymentIntent confirmed: {payment_intent_id}")
            return intent_data
            
        except Exception as e:
            logger.error(f"Error confirming PaymentIntent {payment_intent_id}: {str(e)}")
            raise PaymentIntentError(f"Payment confirmation failed: {str(e)}")
    
    def capture_payment_intent(self, payment_intent_id: str, amount_to_capture: Optional[Decimal] = None) -> Dict[str, Any]:
        """
        Capture a PaymentIntent that was created with manual capture.
        
        Args:
            payment_intent_id: Stripe PaymentIntent ID
            amount_to_capture: Specific amount to capture (optional, defaults to full amount)
            
        Returns:
            Dictionary containing captured PaymentIntent data
            
        Raises:
            PaymentIntentError: If capture fails
        """
        try:
            data = {}
            
            if amount_to_capture is not None:
                data['amount_to_capture'] = self._amount_to_cents(amount_to_capture)
            
            intent_data = self._make_stripe_request('POST', f'payment_intents/{payment_intent_id}/capture', data)
            logger.info(f"PaymentIntent captured: {payment_intent_id}")
            return intent_data
            
        except Exception as e:
            logger.error(f"Error capturing PaymentIntent {payment_intent_id}: {str(e)}")
            raise PaymentIntentError(f"Payment capture failed: {str(e)}")
    
    def create_refund(
        self,
        payment_intent_id: str,
        amount: Optional[Decimal] = None,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a refund for a PaymentIntent.
        
        Args:
            payment_intent_id: Stripe PaymentIntent ID to refund
            amount: Amount to refund (optional, defaults to full amount)
            reason: Reason for the refund
            metadata: Additional metadata
            
        Returns:
            Dictionary containing Refund data
            
        Raises:
            RefundError: If refund creation fails
        """
        with MetricsTimer() as timer:
            try:
                data = {
                    'payment_intent': payment_intent_id,
                }
                
                if amount is not None:
                    data['amount'] = self._amount_to_cents(amount)
                
                if reason:
                    data['reason'] = reason
                
                if metadata:
                    for key, value in metadata.items():
                        data[f'metadata[{key}]'] = str(value)
                
                refund_data = self._make_stripe_request('POST', 'refunds', data)
                refund_id = refund_data.get('id')
                refund_amount = float(refund_data.get('amount', 0)) / 100.0  # Convert from cents
                currency = refund_data.get('currency', 'USD').upper()
                
                # Record successful refund metrics
                payment_metrics.record_refund_success(
                    refund_id=refund_id,
                    amount=refund_amount,
                    currency=currency,
                    processing_time=timer.elapsed_ms
                )
                
                logger.info(f"Refund created: {refund_id} for PaymentIntent {payment_intent_id}")
                return refund_data
                
            except Exception as e:
                # Record failed refund metrics
                if amount:
                    payment_metrics.record_refund_failure(
                        refund_id=f"failed_{payment_intent_id}",
                        amount=float(amount),
                        currency='USD',  # Default, since we don't have the actual currency in error cases
                        error_code='refund_failed',
                        error_message=str(e),
                        processing_time=timer.elapsed_ms
                    )
                
                logger.error(f"Error creating refund for {payment_intent_id}: {str(e)}")
                raise RefundError(f"Refund processing failed: {str(e)}")
    
    def create_connection_token(self, location_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a ConnectionToken for Terminal reader access.
        
        Args:
            location_id: Optional Stripe Location ID to scope the token
            
        Returns:
            Dictionary containing ConnectionToken data
            
        Raises:
            ConnectionTokenError: If token creation fails
        """
        try:
            data = {}
            if location_id:
                data['location'] = location_id
            
            token_data = self._make_stripe_request('POST', 'terminal/connection_tokens', data)
            logger.info("ConnectionToken created successfully")
            return token_data
            
        except Exception as e:
            logger.error(f"Error creating ConnectionToken: {str(e)}")
            raise ConnectionTokenError(f"Connection token creation failed: {str(e)}")
    
    def create_terminal_location(
        self,
        display_name: str,
        address: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Create a Terminal Location in Stripe.
        
        Args:
            display_name: Human-readable location name
            address: Address dictionary with required fields
            
        Returns:
            Dictionary containing Terminal Location data
            
        Raises:
            TerminalError: If location creation fails
        """
        try:
            data = {
                'display_name': display_name
            }
            
            # Add address fields
            for key, value in address.items():
                data[f'address[{key}]'] = value
            
            location_data = self._make_stripe_request('POST', 'terminal/locations', data)
            logger.info(f"Terminal location created: {location_data.get('id')} - {display_name}")
            return location_data
            
        except Exception as e:
            logger.error(f"Error creating Terminal location: {str(e)}")
            raise TerminalError(f"Location creation failed: {str(e)}")
    
    # Utility methods for amount conversion
    def _amount_to_cents(self, amount: Decimal) -> int:
        """
        Convert Decimal amount to integer cents for Stripe API.
        
        Args:
            amount: Decimal amount (e.g., Decimal('10.50'))
            
        Returns:
            Amount in cents as integer (e.g., 1050)
        """
        return int(amount * 100)
    
    def _cents_to_amount(self, cents: int) -> Decimal:
        """
        Convert integer cents from Stripe API to Decimal amount.
        
        Args:
            cents: Amount in cents as integer (e.g., 1050)
            
        Returns:
            Decimal amount (e.g., Decimal('10.50'))
        """
        return Decimal(str(cents)) / 100
    
    # Webhook handling methods
    def verify_webhook_signature(self, payload: bytes, signature_header: str) -> bool:
        """
        Verify Stripe webhook signature to ensure authenticity.
        
        Args:
            payload: Raw request payload as bytes
            signature_header: Stripe-Signature header value
            
        Returns:
            True if signature is valid, False otherwise
        """
        # Check for webhook secret in either location
        webhook_secret = (getattr(settings, 'STRIPE_WEBHOOK_ENDPOINT_SECRET', None) or 
                         getattr(settings, 'STRIPE_WEBHOOK_SECRET', None))
        
        if not webhook_secret:
            logger.warning("STRIPE_WEBHOOK_SECRET not configured - webhook verification disabled")
            return True  # Allow webhooks if no secret configured (dev mode)
        
        try:
            # Parse the signature header
            signature_data = {}
            for item in signature_header.split(','):
                key, value = item.split('=', 1)
                signature_data[key] = value
            
            timestamp = signature_data.get('t')
            signature = signature_data.get('v1')
            
            if not timestamp or not signature:
                logger.error("Invalid signature header format")
                return False
            
            # Create expected signature
            signed_payload = f"{timestamp}.{payload.decode('utf-8')}"
            expected_signature = hmac.new(
                webhook_secret.encode('utf-8'),
                signed_payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # Verify signature
            if not hmac.compare_digest(expected_signature, signature):
                logger.error("Webhook signature verification failed")
                return False
            
            # Check timestamp (prevent replay attacks)
            current_time = int(timezone.now().timestamp())
            webhook_time = int(timestamp)
            
            if abs(current_time - webhook_time) > 300:  # 5 minutes tolerance
                logger.error("Webhook timestamp too old")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Webhook signature verification error: {str(e)}")
            return False
    
    def process_webhook_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a Stripe webhook event and update local records.
        
        Args:
            event_data: Stripe webhook event data
            
        Returns:
            Processing result dictionary
        """
        event_type = event_data.get('type')
        event_id = event_data.get('id')
        
        logger.info(f"Processing webhook event: {event_type} ({event_id})")
        
        with MetricsTimer() as timer:
            try:
                # Create or update PaymentWebhook record
                webhook_record, created = PaymentWebhook.objects.get_or_create(
                    stripe_event_id=event_id,
                    defaults={
                        'event_type': event_type,
                        'event_data': event_data,
                        'processed': False
                    }
                )
                
                if not created and webhook_record.processed:
                    logger.info(f"Webhook {event_id} already processed, skipping")
                    return {'status': 'already_processed', 'event_id': event_id}
                
                # Process based on event type
                result = self._handle_webhook_event_type(event_data, webhook_record)
                
                # Mark as processed
                webhook_record.processed = True
                webhook_record.processed_at = timezone.now()
                webhook_record.processing_result = result
                webhook_record.save()
                
                # Record successful webhook processing metrics
                payment_metrics.record_webhook_received(
                    event_type=event_type,
                    event_id=event_id,
                    processing_time=timer.elapsed_ms
                )
                
                logger.info(f"Successfully processed webhook {event_id}: {result}")
                return result
                
            except Exception as e:
                logger.error(f"Error processing webhook {event_id}: {str(e)}")
                # Update webhook record with error
                if 'webhook_record' in locals():
                    webhook_record.processing_result = {'error': str(e)}
                    webhook_record.save()
                
                # Record failed webhook processing (still record it)
                payment_metrics.record_webhook_received(
                    event_type=event_type,
                    event_id=event_id,
                    processing_time=timer.elapsed_ms
                )
                
                return {'status': 'error', 'message': str(e), 'event_id': event_id}
    
    def _handle_webhook_event_type(self, event_data: Dict[str, Any], webhook_record) -> Dict[str, Any]:
        """
        Handle specific webhook event types.
        
        Args:
            event_data: Stripe webhook event data
            webhook_record: Local webhook record
            
        Returns:
            Processing result
        """
        event_type = event_data.get('type')
        event_object = event_data.get('data', {}).get('object', {})
        
        if event_type.startswith('payment_intent.'):
            return self._handle_payment_intent_webhook(event_type, event_object, webhook_record)
        elif event_type.startswith('charge.'):
            return self._handle_charge_webhook(event_type, event_object, webhook_record)
        elif event_type.startswith('refund.'):
            return self._handle_refund_webhook(event_type, event_object, webhook_record)
        elif event_type.startswith('terminal.'):
            return self._handle_terminal_webhook(event_type, event_object, webhook_record)
        else:
            logger.info(f"Unhandled webhook event type: {event_type}")
            return {'status': 'unhandled', 'event_type': event_type}
    
    def _handle_payment_intent_webhook(self, event_type: str, payment_intent: Dict[str, Any], webhook_record) -> Dict[str, Any]:
        """Handle payment_intent.* webhook events."""
        payment_intent_id = payment_intent.get('id')
        new_status = payment_intent.get('status')
        amount = float(payment_intent.get('amount', 0)) / 100.0  # Convert from cents
        currency = payment_intent.get('currency', 'USD').upper()
        
        try:
            # Find local payment transaction
            payment_transaction = PaymentTransaction.objects.get(
                stripe_payment_intent_id=payment_intent_id
            )
            
            old_status = payment_transaction.status
            
            # Update payment transaction
            payment_transaction.status = new_status
            payment_transaction.stripe_status = new_status
            
            # Handle specific events and record metrics
            if event_type == 'payment_intent.succeeded':
                payment_transaction.processed_at = timezone.now()
                logger.info(f"Payment succeeded: {payment_intent_id}")
                
                # Record success metrics
                payment_metrics.record_payment_success(
                    payment_intent_id=payment_intent_id,
                    amount=amount,
                    currency=currency
                )
                
            elif event_type == 'payment_intent.payment_failed':
                failure_reason = payment_intent.get('last_payment_error', {}).get('message', 'Unknown error')
                error_code = payment_intent.get('last_payment_error', {}).get('code', 'unknown')
                payment_transaction.failure_reason = failure_reason
                payment_transaction.last_payment_error = json.dumps(payment_intent.get('last_payment_error', {}))
                logger.info(f"Payment failed: {payment_intent_id} - {failure_reason}")
                
                # Record failure metrics
                payment_metrics.record_payment_failure(
                    payment_intent_id=payment_intent_id,
                    amount=amount,
                    currency=currency,
                    error_code=error_code,
                    error_message=failure_reason
                )
                
            elif event_type == 'payment_intent.canceled':
                payment_transaction.status = 'canceled'
                logger.info(f"Payment canceled: {payment_intent_id}")
            
            payment_transaction.save()
            
            return {
                'status': 'processed',
                'event_type': event_type,
                'payment_intent_id': payment_intent_id,
                'old_status': old_status,
                'new_status': new_status,
                'local_transaction_id': str(payment_transaction.id)
            }
            
        except PaymentTransaction.DoesNotExist:
            logger.warning(f"PaymentTransaction not found for {payment_intent_id}")
            return {
                'status': 'no_local_record',
                'event_type': event_type,
                'payment_intent_id': payment_intent_id
            }
        except Exception as e:
            logger.error(f"Error handling payment_intent webhook: {str(e)}")
            raise
    
    def _handle_charge_webhook(self, event_type: str, charge: Dict[str, Any], webhook_record) -> Dict[str, Any]:
        """Handle charge.* webhook events."""
        payment_intent_id = charge.get('payment_intent')
        charge_id = charge.get('id')
        
        if not payment_intent_id:
            return {'status': 'no_payment_intent', 'charge_id': charge_id}
        
        try:
            payment_transaction = PaymentTransaction.objects.get(
                stripe_payment_intent_id=payment_intent_id
            )
            
            # Update with charge information
            if event_type == 'charge.succeeded':
                payment_transaction.status = 'succeeded'
                payment_transaction.processed_at = timezone.now()
                
            elif event_type == 'charge.failed':
                failure_reason = charge.get('failure_message', 'Charge failed')
                payment_transaction.failure_reason = failure_reason
                payment_transaction.status = 'failed'
            
            payment_transaction.save()
            
            return {
                'status': 'processed',
                'event_type': event_type,
                'charge_id': charge_id,
                'payment_intent_id': payment_intent_id
            }
            
        except PaymentTransaction.DoesNotExist:
            return {
                'status': 'no_local_record',
                'payment_intent_id': payment_intent_id,
                'charge_id': charge_id
            }
    
    def _handle_refund_webhook(self, event_type: str, refund: Dict[str, Any], webhook_record) -> Dict[str, Any]:
        """Handle refund.* webhook events."""
        refund_id = refund.get('id')
        payment_intent_id = refund.get('payment_intent')
        
        try:
            # Try to find existing refund first
            try:
                payment_refund = PaymentRefund.objects.get(stripe_refund_id=refund_id)
                created = False
            except PaymentRefund.DoesNotExist:
                # Find the payment transaction first
                payment_transaction = None
                if payment_intent_id:
                    try:
                        payment_transaction = PaymentTransaction.objects.get(
                            stripe_payment_intent_id=payment_intent_id
                        )
                    except PaymentTransaction.DoesNotExist:
                        logger.warning(f"PaymentTransaction not found for refund {refund_id}")
                        return {
                            'status': 'no_payment_transaction',
                            'refund_id': refund_id,
                            'payment_intent_id': payment_intent_id
                        }
                
                # Create new refund record with payment transaction
                payment_refund = PaymentRefund.objects.create(
                    stripe_refund_id=refund_id,
                    payment_transaction=payment_transaction,
                    amount=self._cents_to_amount(refund.get('amount', 0)),
                    currency=refund.get('currency', 'usd').upper(),
                    reason=refund.get('reason', 'requested_by_customer'),
                    status=refund.get('status', 'pending'),
                    metadata=refund.get('metadata', {}),
                    processed_by=None  # Webhook-created refunds don't have a processed_by user
                )
                created = True
            
            # Update refund status
            if event_type == 'refund.created':
                payment_refund.status = 'pending'
            elif event_type == 'refund.updated':
                payment_refund.status = refund.get('status', payment_refund.status)
            
            payment_refund.save()
            
            return {
                'status': 'processed',
                'event_type': event_type,
                'refund_id': refund_id,
                'payment_intent_id': payment_intent_id,
                'created': created
            }
            
        except Exception as e:
            logger.error(f"Error handling refund webhook: {str(e)}")
            raise
    
    def _handle_terminal_webhook(self, event_type: str, terminal_object: Dict[str, Any], webhook_record) -> Dict[str, Any]:
        """Handle terminal.* webhook events."""
        logger.info(f"Terminal webhook received: {event_type}")
        
        # For now, just log terminal events
        # In the future, this could handle terminal reader status updates
        return {
            'status': 'logged',
            'event_type': event_type,
            'terminal_object_id': terminal_object.get('id')
        }

    def link_transaction_to_payment(self, transaction_obj, payment_intent_data):
        """
        Link a transaction to a Stripe payment by creating a PaymentTransaction record.
        
        Args:
            transaction_obj: Django transaction model instance
            payment_intent_data: Stripe PaymentIntent data from API
            
        Returns:
            PaymentTransaction instance
        """
        from transaction.models import transaction
        
        payment_transaction = PaymentTransaction.objects.create(
            transaction=transaction_obj,
            payment_method=PaymentMethod.objects.filter(
                stripe_payment_method_type='card',
                is_active=True
            ).first(),
            amount=Decimal(payment_intent_data['amount']) / 100,
            currency=payment_intent_data['currency'],
            status=self._map_stripe_status(payment_intent_data['status']),
            stripe_payment_intent_id=payment_intent_data['id'],
            stripe_client_secret=payment_intent_data.get('client_secret'),
            stripe_status=payment_intent_data['status'],
            metadata=payment_intent_data.get('metadata', {}),
        )
        
        logger.info(f"Linked transaction {transaction_obj.transaction_id} to payment {payment_intent_data['id']}")
        return payment_transaction

    def update_transaction_payment_status(self, transaction_obj):
        """
        Update the transaction's payment status based on associated PaymentTransaction(s).
        
        Args:
            transaction_obj: Django transaction model instance
            
        Returns:
            Updated transaction object
        """
        if transaction_obj.has_stripe_payment:
            latest_payment = transaction_obj.payment_transactions.order_by('-created_at').first()
            if latest_payment and latest_payment.status == 'succeeded':
                # Transaction payment is complete
                logger.info(f"Transaction {transaction_obj.transaction_id} payment completed")
            elif latest_payment and latest_payment.status == 'failed':
                # Transaction payment failed
                logger.warning(f"Transaction {transaction_obj.transaction_id} payment failed")
                
        return transaction_obj

    def create_payment_for_transaction(self, transaction_obj):
        """
        Create a Stripe PaymentIntent for an existing transaction.
        
        Args:
            transaction_obj: Django transaction model instance
            
        Returns:
            Dictionary containing PaymentIntent data
        """
        intent_data = self.create_payment_intent(
            amount=transaction_obj.total_sale,
            currency='usd',
            metadata={
                'transaction_id': transaction_obj.transaction_id,
                'user_id': str(transaction_obj.user.id),
            }
        )
        
        # Link the payment to the transaction
        self.link_transaction_to_payment(transaction_obj, intent_data)
        
        return intent_data

    def _map_stripe_status(self, stripe_status):
        """
        Map Stripe payment status to our internal status.
        
        Args:
            stripe_status: Status from Stripe API
            
        Returns:
            Internal payment status
        """
        status_map = {
            'requires_payment_method': 'pending',
            'requires_confirmation': 'pending',
            'requires_action': 'pending',
            'processing': 'processing',
            'requires_capture': 'processing',
            'canceled': 'canceled',
            'succeeded': 'succeeded',
        }
        return status_map.get(stripe_status, stripe_status)


# Global service instance
stripe_service = StripePaymentService()
