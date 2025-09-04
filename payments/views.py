"""
Payment views and API endpoints for Stripe integration.

This module provides Django views and REST API endpoints for processing payments,
managing payment intents, handling refunds, and integrating with the POS system.
"""

import json
import logging
import csv
from decimal import Decimal
from typing import Dict, Any
from datetime import datetime, timedelta

from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.views import View
from django.db import transaction as db_transaction
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count, Avg
from django.template.loader import get_template

from .models import PaymentTransaction, PaymentRefund, PaymentMethod, PaymentWebhook
from .services import stripe_service
from .metrics import payment_metrics
from .decorators import (
    payment_processor_required,
    refund_processor_required, 
    manager_approval_required,
    payment_dashboard_access_required,
    webhook_admin_required
)
from .exceptions import (
    StripeConfigurationError,
    PaymentIntentError, 
    RefundError,
    ConnectionTokenError,
    PaymentAmountError
)
from transaction.models import transaction

logger = logging.getLogger(__name__)


class PaymentAPIView(View):
    """Base API view for payment endpoints with common functionality."""
    
    def dispatch(self, request, *args, **kwargs):
        """Add common headers and validation."""
        response = super().dispatch(request, *args, **kwargs)
        response['Content-Type'] = 'application/json'
        return response
    
    def json_response(self, data: Dict[str, Any], status: int = 200) -> JsonResponse:
        """Create a standardized JSON response."""
        return JsonResponse(data, status=status)
    
    def error_response(self, message: str, status: int = 400, error_code: str = None) -> JsonResponse:
        """Create a standardized error response."""
        error_data = {
            'error': True,
            'message': message
        }
        if error_code:
            error_data['error_code'] = error_code
        return JsonResponse(error_data, status=status)


@method_decorator([csrf_exempt, payment_processor_required], name='dispatch')
class CreatePaymentIntentView(PaymentAPIView):
    """API endpoint to create a Stripe PaymentIntent."""
    
    def post(self, request):
        """Create a new payment intent."""
        try:
            # Parse request data
            data = json.loads(request.body)
            amount = data.get('amount')
            currency = data.get('currency', 'usd')
            payment_method_types = data.get('payment_method_types', ['card'])
            capture_method = data.get('capture_method', 'automatic')
            metadata = data.get('metadata', {})
            
            # Validate required fields
            if not amount:
                return self.error_response("Amount is required", 400, "missing_amount")
            
            try:
                amount_decimal = Decimal(str(amount))
            except (ValueError, TypeError):
                return self.error_response("Invalid amount format", 400, "invalid_amount")
            
            # Add POS metadata
            metadata.update({
                'source': 'ireti_pos',
                'created_by': request.user.username if request.user.is_authenticated else 'anonymous',
                'pos_version': getattr(settings, 'POS_VERSION', '1.0')
            })
            
            # Create payment intent through service
            intent_data = stripe_service.create_payment_intent(
                amount=amount_decimal,
                currency=currency,
                payment_method_types=payment_method_types,
                capture_method=capture_method,
                metadata=metadata
            )
            
            # Create local PaymentTransaction record
            with db_transaction.atomic():
                payment_transaction = PaymentTransaction.objects.create(
                    stripe_payment_intent_id=intent_data['id'],
                    amount=amount_decimal,
                    currency=currency.upper(),
                    status=intent_data['status'],
                    metadata=metadata
                )
            
            logger.info(f"PaymentIntent created: {intent_data['id']} for amount {amount_decimal}")
            
            return self.json_response({
                'success': True,
                'payment_intent': {
                    'id': intent_data['id'],
                    'client_secret': intent_data['client_secret'],
                    'amount': intent_data['amount'],
                    'currency': intent_data['currency'],
                    'status': intent_data['status']
                },
                'local_transaction_id': payment_transaction.id
            })
            
        except PaymentAmountError as e:
            return self.error_response(str(e), 400, "invalid_amount")
        except PaymentIntentError as e:
            return self.error_response(f"Payment creation failed: {str(e)}", 500, "payment_creation_failed")
        except json.JSONDecodeError:
            return self.error_response("Invalid JSON format", 400, "invalid_json")
        except Exception as e:
            logger.error(f"Unexpected error creating payment intent: {str(e)}")
            return self.error_response("Internal server error", 500, "internal_error")


@method_decorator([csrf_exempt, payment_processor_required], name='dispatch') 
class RetrievePaymentIntentView(PaymentAPIView):
    """API endpoint to retrieve a Stripe PaymentIntent."""
    
    def get(self, request, payment_intent_id):
        """Retrieve payment intent details."""
        try:
            # Retrieve from Stripe
            intent_data = stripe_service.retrieve_payment_intent(payment_intent_id)
            
            # Get local transaction record if exists
            local_transaction = None
            try:
                payment_transaction = PaymentTransaction.objects.get(
                    stripe_payment_intent_id=payment_intent_id
                )
                local_transaction = {
                    'id': payment_transaction.id,
                    'local_status': payment_transaction.status,
                    'created_at': payment_transaction.created_at.isoformat(),
                    'updated_at': payment_transaction.updated_at.isoformat()
                }
            except PaymentTransaction.DoesNotExist:
                pass
            
            return self.json_response({
                'success': True,
                'payment_intent': {
                    'id': intent_data['id'],
                    'amount': intent_data['amount'],
                    'currency': intent_data['currency'],
                    'status': intent_data['status'],
                    'client_secret': intent_data.get('client_secret'),
                    'payment_method': intent_data.get('payment_method'),
                    'created': intent_data['created']
                },
                'local_transaction': local_transaction
            })
            
        except PaymentIntentError as e:
            return self.error_response(str(e), 404, "payment_not_found")
        except Exception as e:
            logger.error(f"Error retrieving payment intent {payment_intent_id}: {str(e)}")
            return self.error_response("Failed to retrieve payment", 500, "retrieval_error")


@method_decorator([csrf_exempt, payment_processor_required], name='dispatch')
class ConfirmPaymentIntentView(PaymentAPIView):
    """API endpoint to confirm a Stripe PaymentIntent."""
    
    def post(self, request, payment_intent_id):
        """Confirm a payment intent to complete the payment."""
        try:
            # Confirm payment through Stripe
            intent_data = stripe_service.confirm_payment_intent(payment_intent_id)
            
            # Update local transaction record
            try:
                with db_transaction.atomic():
                    payment_transaction = PaymentTransaction.objects.get(
                        stripe_payment_intent_id=payment_intent_id
                    )
                    payment_transaction.status = intent_data['status']
                    payment_transaction.save()
                    
                    # If payment succeeded, create a transaction record
                    if intent_data['status'] == 'succeeded':
                        # Link to existing transaction if transaction_id provided
                        request_data = json.loads(request.body) if request.body else {}
                        transaction_id = request_data.get('transaction_id')
                        
                        if transaction_id:
                            try:
                                pos_transaction = transaction.objects.get(id=transaction_id)
                                payment_transaction.transaction = pos_transaction
                                payment_transaction.save()
                            except transaction.DoesNotExist:
                                logger.warning(f"Transaction {transaction_id} not found for payment {payment_intent_id}")
                        
            except PaymentTransaction.DoesNotExist:
                logger.warning(f"Local PaymentTransaction not found for {payment_intent_id}")
            
            return self.json_response({
                'success': True,
                'payment_intent': {
                    'id': intent_data['id'],
                    'status': intent_data['status'],
                    'amount': intent_data['amount'],
                    'currency': intent_data['currency']
                }
            })
            
        except PaymentIntentError as e:
            return self.error_response(str(e), 400, "confirmation_failed")
        except json.JSONDecodeError:
            return self.error_response("Invalid JSON format", 400, "invalid_json")
        except Exception as e:
            logger.error(f"Error confirming payment intent {payment_intent_id}: {str(e)}")
            return self.error_response("Payment confirmation failed", 500, "confirmation_error")


@method_decorator([csrf_exempt, refund_processor_required, manager_approval_required()], name='dispatch')
class CreateRefundView(PaymentAPIView):
    """API endpoint to create a refund."""
    
    def post(self, request):
        """Create a refund for a payment intent."""
        try:
            data = json.loads(request.body)
            payment_intent_id = data.get('payment_intent_id')
            amount = data.get('amount')  # Optional - full refund if not provided
            reason = data.get('reason', 'requested_by_customer')
            metadata = data.get('metadata', {})
            
            if not payment_intent_id:
                return self.error_response("Payment intent ID is required", 400, "missing_payment_intent")
            
            # Convert amount to Decimal if provided
            amount_decimal = None
            if amount:
                try:
                    amount_decimal = Decimal(str(amount))
                except (ValueError, TypeError):
                    return self.error_response("Invalid refund amount format", 400, "invalid_amount")
            
            # Add POS metadata
            metadata.update({
                'source': 'ireti_pos',
                'refunded_by': request.user.username if request.user.is_authenticated else 'anonymous'
            })
            
            # Create refund through Stripe
            refund_data = stripe_service.create_refund(
                payment_intent_id=payment_intent_id,
                amount=amount_decimal,
                reason=reason,
                metadata=metadata
            )
            
            # Create local PaymentRefund record
            with db_transaction.atomic():
                # Find the original payment transaction
                try:
                    original_payment = PaymentTransaction.objects.get(
                        stripe_payment_intent_id=payment_intent_id
                    )
                except PaymentTransaction.DoesNotExist:
                    original_payment = None
                    logger.warning(f"Original PaymentTransaction not found for refund {payment_intent_id}")
                
                payment_refund = PaymentRefund.objects.create(
                    payment_transaction=original_payment,
                    stripe_refund_id=refund_data['id'],
                    amount=Decimal(str(refund_data['amount'])) / 100,  # Convert from cents
                    currency=refund_data['currency'].upper(),
                    reason=refund_data['reason'],
                    status=refund_data['status'],
                    processed_by=request.user if request.user.is_authenticated else None,
                    metadata=metadata
                )
            
            logger.info(f"Refund created: {refund_data['id']} for {payment_intent_id}")
            
            return self.json_response({
                'success': True,
                'refund': {
                    'id': refund_data['id'],
                    'amount': refund_data['amount'],
                    'currency': refund_data['currency'],
                    'status': refund_data['status'],
                    'reason': refund_data['reason']
                },
                'local_refund_id': payment_refund.id
            })
            
        except RefundError as e:
            return self.error_response(str(e), 400, "refund_failed")
        except json.JSONDecodeError:
            return self.error_response("Invalid JSON format", 400, "invalid_json")
        except Exception as e:
            logger.error(f"Error creating refund: {str(e)}")
            return self.error_response("Refund creation failed", 500, "refund_error")


@method_decorator(csrf_exempt, name='dispatch')
class CreateConnectionTokenView(PaymentAPIView):
    """API endpoint to create a Terminal connection token."""
    
    def post(self, request):
        """Create a connection token for Terminal SDK."""
        try:
            data = json.loads(request.body) if request.body else {}
            location_id = data.get('location_id')
            
            # Create connection token
            token_data = stripe_service.create_connection_token(location_id)
            
            return self.json_response({
                'success': True,
                'connection_token': token_data['secret']
            })
            
        except ConnectionTokenError as e:
            return self.error_response(str(e), 500, "connection_token_failed")
        except json.JSONDecodeError:
            return self.error_response("Invalid JSON format", 400, "invalid_json")
        except Exception as e:
            logger.error(f"Error creating connection token: {str(e)}")
            return self.error_response("Connection token creation failed", 500, "token_error")


@payment_dashboard_access_required
def payment_dashboard(request):
    """Dashboard view for payment management."""
    recent_payments = PaymentTransaction.objects.order_by('-created_at')[:10]
    recent_refunds = PaymentRefund.objects.order_by('-created_at')[:5]
    
    context = {
        'recent_payments': recent_payments,
        'recent_refunds': recent_refunds,
        'stripe_publishable_key': getattr(settings, 'STRIPE_PUBLISHABLE_KEY', ''),
    }
    
    return render(request, 'payments/dashboard.html', context)


@payment_dashboard_access_required
def payment_detail(request, transaction_id):
    """Detailed view of a specific payment transaction."""
    payment = get_object_or_404(PaymentTransaction, id=transaction_id)
    
    # Get related refunds
    refunds = PaymentRefund.objects.filter(payment_transaction=payment)
    
    context = {
        'payment': payment,
        'refunds': refunds,
    }
    
    return render(request, 'payments/detail.html', context)


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(PaymentAPIView):
    """
    Stripe webhook endpoint for handling payment events.
    
    This view receives and processes webhook events from Stripe to keep
    local payment records in sync with Stripe's system.
    """
    
    def post(self, request):
        """Handle incoming Stripe webhook events."""
        try:
            # Get the raw payload
            payload = request.body
            signature_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
            
            if not payload:
                return self.error_response("Empty payload", 400, "empty_payload")
            
            if not signature_header:
                logger.warning("Webhook received without signature header")
                # In development, we might allow this, but log it
                if not settings.DEBUG:
                    return self.error_response("Missing signature", 400, "missing_signature")
            
            # Verify webhook signature
            if signature_header and not stripe_service.verify_webhook_signature(payload, signature_header):
                logger.error("Webhook signature verification failed")
                return self.error_response("Invalid signature", 400, "invalid_signature")
            
            # Parse the event data
            try:
                event_data = json.loads(payload.decode('utf-8'))
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in webhook payload: {str(e)}")
                return self.error_response("Invalid JSON", 400, "invalid_json")
            
            # Validate required event fields
            event_type = event_data.get('type')
            event_id = event_data.get('id')
            
            if not event_type or not event_id:
                return self.error_response("Missing required event fields", 400, "invalid_event")
            
            logger.info(f"Received webhook: {event_type} ({event_id})")
            
            # Process the webhook event
            result = stripe_service.process_webhook_event(event_data)
            
            # Return appropriate response
            if result.get('status') == 'error':
                logger.error(f"Webhook processing failed: {result.get('message')}")
                return self.error_response(
                    f"Processing failed: {result.get('message')}", 
                    500, 
                    "processing_error"
                )
            else:
                logger.info(f"Webhook processed successfully: {result}")
                return self.json_response({
                    'success': True,
                    'message': 'Webhook processed successfully',
                    'event_id': event_id,
                    'event_type': event_type,
                    'result': result
                })
                
        except Exception as e:
            logger.error(f"Unexpected error processing webhook: {str(e)}")
            return self.error_response("Internal server error", 500, "internal_error")


@webhook_admin_required
def webhook_dashboard(request):
    """Dashboard for monitoring webhook events."""
    # Get recent webhook events
    recent_webhooks = PaymentWebhook.objects.order_by('-created_at')[:20]
    
    # Get statistics
    total_webhooks = PaymentWebhook.objects.count()
    processed_webhooks = PaymentWebhook.objects.filter(processed=True).count()
    failed_webhooks = PaymentWebhook.objects.filter(
        processed=True, 
        processing_error__isnull=False
    ).count()
    
    context = {
        'recent_webhooks': recent_webhooks,
        'total_webhooks': total_webhooks,
        'processed_webhooks': processed_webhooks,
        'failed_webhooks': failed_webhooks,
        'success_rate': round((processed_webhooks - failed_webhooks) / max(processed_webhooks, 1) * 100, 1)
    }
    
    return render(request, 'payments/webhook_dashboard.html', context)


# Payment UI Views
@payment_processor_required
def payment_form(request):
    """Render the payment processing form."""
    context = {
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'page_title': 'Payment Processing',
    }
    return render(request, 'payments/payment_form.html', context)


@login_required
def pos_terminal(request):
    """Render the POS terminal interface."""
    context = {
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'store_name': getattr(settings, 'STORE_NAME', 'POS Terminal'),
        'page_title': 'POS Terminal',
    }
    return render(request, 'payments/pos_terminal.html', context)


@payment_dashboard_access_required
def payment_status(request, payment_intent_id=None):
    """Render the payment status interface with real-time updates."""
    # Get payment intent ID from URL parameter or GET parameter
    if not payment_intent_id:
        payment_intent_id = request.GET.get('payment_intent')
    
    context = {
        'payment_intent_id': payment_intent_id,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'page_title': 'Payment Status',
    }
    return render(request, 'payments/payment_status.html', context)


@login_required
def receipt_view(request, transaction_id=None):
    """Display digital receipt for a completed transaction."""
    # Get transaction ID from URL or GET parameter
    if not transaction_id:
        transaction_id = request.GET.get('transaction')
    
    # Default receipt data for demonstration
    # In production, this would fetch from database
    default_items = [
        {
            'name': 'Coffee - Large',
            'amount': 4.50,
            'quantity': 1,
            'unit_price': 4.50
        },
        {
            'name': 'Blueberry Muffin',
            'amount': 3.25,
            'quantity': 1,
            'unit_price': 3.25
        }
    ]
    
    context = {
        'transaction_id': transaction_id,
        'receipt_number': f"RCP-{transaction_id[-6:] if transaction_id else '000001'}",
        'transaction_date': timezone.now(),
        'cashier_name': request.user.username,
        'customer_name': request.GET.get('customer', 'Guest'),
        'customer_email': request.GET.get('email', ''),
        'items': default_items,
        'subtotal': sum(item['amount'] for item in default_items),
        'tax_rate': 8.5,
        'tax_amount': sum(item['amount'] for item in default_items) * 0.085,
        'tip_amount': 0.00,
        'total_amount': sum(item['amount'] for item in default_items) * 1.085,
        'payment_method': 'Credit Card',
        'payment_id': transaction_id,
        'payment_status': 'success',
        'card_last_four': '4242',
        'authorization_code': 'AUTH123456',
        'store_name': getattr(settings, 'STORE_NAME', 'Ireti POS'),
        'store_address': getattr(settings, 'STORE_ADDRESS', '123 Main Street<br>City, State 12345<br>(555) 123-4567'),
        'return_policy': 'Returns accepted within 30 days with receipt.',
        'page_title': 'Receipt',
        'auto_print': request.GET.get('print', False),
    }
    
    # If this is a real transaction, fetch from database
    if transaction_id:
        try:
            # Try to get local transaction record
            from .models import Transaction
            transaction = Transaction.objects.filter(
                stripe_payment_intent_id=transaction_id
            ).first()
            
            if transaction:
                context.update({
                    'total_amount': float(transaction.amount),
                    'subtotal': float(transaction.amount) / 1.085,  # Assuming 8.5% tax
                    'tax_amount': float(transaction.amount) - (float(transaction.amount) / 1.085),
                    'payment_status': transaction.status,
                    'customer_name': transaction.customer_name or 'Guest',
                    'customer_email': transaction.customer_email or '',
                })
        except ImportError:
            pass  # Models not available
    
    return render(request, 'payments/receipt.html', context)


@method_decorator(csrf_exempt, name='dispatch')
class RecentTransactionsView(PaymentAPIView):
    """API view for fetching recent payment transactions."""
    
    def get(self, request):
        """Get recent payment transactions."""
        try:
            # Get recent transactions (last 10)
            transactions = PaymentTransaction.objects.select_related(
                'transaction'
            ).order_by('-created_at')[:10]
            
            transactions_data = []
            for tx in transactions:
                transactions_data.append({
                    'id': tx.stripe_payment_intent_id,
                    'amount': int(tx.amount * 100),  # Convert to cents
                    'currency': tx.currency,
                    'status': tx.status,
                    'description': tx.description or '',
                    'customer_name': tx.customer_name or 'Anonymous',
                    'created_at': tx.created_at.isoformat(),
                    'metadata': tx.metadata or {}
                })
            
            return self.json_response({
                'success': True,
                'transactions': transactions_data,
                'count': len(transactions_data)
            })
            
        except Exception as e:
            logger.error(f"Error fetching recent transactions: {str(e)}")
            return self.error_response(
                message="Failed to load recent transactions",
                status=500
            )


@payment_dashboard_access_required
def payment_history(request):
    """Display payment transaction history with filtering and pagination."""
    try:
        # Get filter parameters
        filters = {
            'date_from': request.GET.get('date_from'),
            'date_to': request.GET.get('date_to'),
            'status': request.GET.get('status'),
            'amount_min': request.GET.get('amount_min'),
            'amount_max': request.GET.get('amount_max'),
            'search': request.GET.get('search'),
        }
        
        # Handle export requests
        export_format = request.GET.get('export')
        if export_format in ['csv', 'excel', 'pdf']:
            return export_payment_history(request, export_format, filters)
        
        # Build queryset with filters
        transactions = PaymentTransaction.objects.all().order_by('-created_at')
        
        # Apply date filters
        if filters['date_from']:
            try:
                date_from = datetime.strptime(filters['date_from'], '%Y-%m-%d').date()
                transactions = transactions.filter(created_at__date__gte=date_from)
            except ValueError:
                pass
                
        if filters['date_to']:
            try:
                date_to = datetime.strptime(filters['date_to'], '%Y-%m-%d').date()
                transactions = transactions.filter(created_at__date__lte=date_to)
            except ValueError:
                pass
        
        # Apply status filter
        if filters['status']:
            transactions = transactions.filter(status=filters['status'])
        
        # Apply amount filters
        if filters['amount_min']:
            try:
                amount_min = Decimal(filters['amount_min'])
                transactions = transactions.filter(amount__gte=amount_min)
            except (ValueError, TypeError):
                pass
                
        if filters['amount_max']:
            try:
                amount_max = Decimal(filters['amount_max'])
                transactions = transactions.filter(amount__lte=amount_max)
            except (ValueError, TypeError):
                pass
        
        # Apply search filter
        if filters['search']:
            search_query = filters['search'].strip()
            transactions = transactions.filter(
                Q(customer_name__icontains=search_query) |
                Q(customer_email__icontains=search_query) |
                Q(stripe_payment_intent_id__icontains=search_query) |
                Q(receipt_number__icontains=search_query)
            )
        
        # Calculate statistics
        stats = calculate_payment_stats(transactions)
        
        # Pagination
        paginator = Paginator(transactions, 25)  # 25 transactions per page
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        context = {
            'transactions': page_obj,
            'page_obj': page_obj,
            'filters': filters,
            'stats': stats,
        }
        
        return render(request, 'payments/history.html', context)
        
    except Exception as e:
        logger.error(f"Error loading payment history: {str(e)}")
        return render(request, 'payments/history.html', {
            'transactions': [],
            'error': 'Failed to load payment history',
            'stats': {
                'total_transactions': 0,
                'total_amount': 0,
                'successful_payments': 0,
                'failed_payments': 0,
            }
        })


def calculate_payment_stats(transactions_queryset):
    """Calculate summary statistics for payment transactions."""
    stats = transactions_queryset.aggregate(
        total_transactions=Count('id'),
        total_amount=Sum('amount'),
        successful_payments=Count('id', filter=Q(status='succeeded')),
        failed_payments=Count('id', filter=Q(status__in=['failed', 'canceled'])),
    )
    
    # Ensure defaults for None values
    stats.update({
        'total_transactions': stats['total_transactions'] or 0,
        'total_amount': stats['total_amount'] or Decimal('0.00'),
        'successful_payments': stats['successful_payments'] or 0,
        'failed_payments': stats['failed_payments'] or 0,
    })
    
    return stats


@login_required
@login_required
def transaction_detail(request, transaction_id):
    """Display detailed view of a single transaction."""
    try:
        transaction = get_object_or_404(PaymentTransaction, id=transaction_id)
        
        # Get related refunds
        refunds = PaymentRefund.objects.filter(
            payment_transaction=transaction
        ).order_by('-created_at')
        
        context = {
            'transaction': transaction,
            'refunds': refunds,
            'can_refund': (
                transaction.status == 'succeeded' and 
                transaction.refundable_amount > 0
            )
        }
        
        return render(request, 'payments/transaction_detail.html', context)
        
    except Exception as e:
        logger.error(f"Error loading transaction {transaction_id}: {str(e)}")
        raise Http404("Transaction not found")


class TransactionDetailAPIView(PaymentAPIView):
    """API endpoint for transaction details."""
    
    @method_decorator(login_required)
    def get(self, request, transaction_id):
        """Get transaction details via API."""
        try:
            transaction = get_object_or_404(PaymentTransaction, id=transaction_id)
            
            return self.json_response({
                'success': True,
                'transaction': {
                    'id': transaction.id,
                    'amount': float(transaction.amount),
                    'refundable_amount': float(transaction.refundable_amount),
                    'status': transaction.status,
                    'customer_name': transaction.customer_name,
                    'customer_email': transaction.customer_email,
                    'created': transaction.created.isoformat(),
                    'payment_method': transaction.payment_method,
                    'card_last_four': transaction.card_last_four,
                }
            })
            
        except Exception as e:
            logger.error(f"Error fetching transaction details: {str(e)}")
            return self.json_response({
                'success': False,
                'error': str(e)
            }, status=400)


def export_payment_history(request, format_type, filters):
    """Export payment history in various formats."""
    try:
        # Apply same filtering logic as main view
        transactions = PaymentTransaction.objects.all().order_by('-created_at')
        
        # Apply filters (same logic as payment_history view)
        if filters['date_from']:
            try:
                date_from = datetime.strptime(filters['date_from'], '%Y-%m-%d').date()
                transactions = transactions.filter(created_at__date__gte=date_from)
            except ValueError:
                pass
                
        if filters['date_to']:
            try:
                date_to = datetime.strptime(filters['date_to'], '%Y-%m-%d').date()
                transactions = transactions.filter(created_at__date__lte=date_to)
            except ValueError:
                pass
        
        if filters['status']:
            transactions = transactions.filter(status=filters['status'])
            
        if filters['search']:
            search_query = filters['search'].strip()
            transactions = transactions.filter(
                Q(customer_name__icontains=search_query) |
                Q(customer_email__icontains=search_query) |
                Q(stripe_payment_intent_id__icontains=search_query)
            )
        
        # Export as CSV
        if format_type == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="payment_history.csv"'
            
            writer = csv.writer(response)
            writer.writerow([
                'Date', 'Transaction ID', 'Customer Name', 'Customer Email',
                'Amount', 'Status', 'Payment Method', 'Card Last 4',
                'Receipt Number', 'Stripe Payment Intent ID'
            ])
            
            for transaction in transactions:
                writer.writerow([
                    transaction.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    transaction.id,
                    transaction.customer_name or '',
                    transaction.customer_email or '',
                    transaction.amount,
                    transaction.status,
                    transaction.payment_method or '',
                    transaction.card_last_four or '',
                    transaction.receipt_number or '',
                    transaction.stripe_payment_intent_id or '',
                ])
            
            return response
        
        # For Excel and PDF, we'll create simple CSV for now
        # Could be enhanced with openpyxl and reportlab libraries
        elif format_type in ['excel', 'pdf']:
            response = HttpResponse(content_type='text/csv')
            filename = f'payment_history.{format_type}'
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            writer = csv.writer(response)
            writer.writerow(['Payment History Export', f'Format: {format_type.upper()}'])
            writer.writerow([])
            writer.writerow([
                'Date', 'Transaction ID', 'Customer', 'Amount', 'Status'
            ])
            
            for transaction in transactions:
                writer.writerow([
                    transaction.created_at.strftime('%Y-%m-%d %H:%M'),
                    transaction.id,
                    transaction.customer_name or 'Walk-in',
                    f'${transaction.amount}',
                    transaction.status.title(),
                ])
            
            return response
            
    except Exception as e:
        logger.error(f"Error exporting payment history: {str(e)}")
        return HttpResponse("Export failed", status=500)


class ProcessRefundAPIView(PaymentAPIView):
    """API endpoint for processing refunds."""
    
    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def post(self, request):
        """Process a refund for a payment transaction."""
        try:
            data = json.loads(request.body)
            transaction_id = data.get('transaction_id')
            amount = Decimal(str(data.get('amount', 0)))
            reason = data.get('reason', 'requested_by_customer')
            notes = data.get('notes', '')
            
            # Get the original transaction
            transaction = get_object_or_404(PaymentTransaction, id=transaction_id)
            
            if transaction.status != 'succeeded':
                return self.json_response({
                    'success': False,
                    'error': 'Can only refund successful payments'
                }, status=400)
            
            if amount > transaction.refundable_amount:
                return self.json_response({
                    'success': False,
                    'error': 'Refund amount exceeds refundable amount'
                }, status=400)
            
            # Process refund through Stripe
            refund_result = stripe_service.create_refund(
                payment_intent_id=transaction.stripe_payment_intent_id,
                amount=amount,
                reason=reason
            )
            
            if not refund_result.get('success'):
                return self.json_response({
                    'success': False,
                    'error': refund_result.get('error', 'Refund failed')
                }, status=400)
            
            # Create refund record
            refund = PaymentRefund.objects.create(
                original_payment=transaction,
                amount=amount,
                stripe_refund_id=refund_result.get('refund_id'),
                reason=reason,
                notes=notes,
                status='succeeded',
                processed_by=request.user if hasattr(request, 'user') else None
            )
            
            # Update transaction refunded amount
            transaction.refunded_amount = (transaction.refunded_amount or Decimal('0')) + amount
            transaction.save()
            
            logger.info(f"Refund processed: ${amount} for transaction {transaction_id}")
            
            return self.json_response({
                'success': True,
                'refund_id': refund.id,
                'amount': float(amount),
                'message': 'Refund processed successfully'
            })
            
        except Exception as e:
            logger.error(f"Error processing refund: {str(e)}")
            return self.json_response({
                'success': False,
                'error': str(e)
            }, status=500)


class PaymentMetricsAPIView(PaymentAPIView):
    """API endpoint for payment performance metrics and observability."""
    
    @method_decorator(login_required)
    @method_decorator(payment_dashboard_access_required)
    def get(self, request):
        """Get payment metrics for monitoring and analytics."""
        try:
            # Get time period from query parameters (default to 24 hours)
            hours = int(request.GET.get('hours', 24))
            
            # Limit hours to prevent excessive queries
            hours = min(hours, 24 * 7)  # Max 1 week
            
            # Collect metrics
            success_rate_data = payment_metrics.get_payment_success_rate(hours)
            latency_data = payment_metrics.get_processing_latency_stats(hours)
            webhook_data = payment_metrics.get_webhook_processing_stats(hours)
            error_data = payment_metrics.get_error_analysis(hours)
            
            return self.json_response({
                'success': True,
                'time_period_hours': hours,
                'metrics': {
                    'payment_success_rate': success_rate_data,
                    'processing_latency': latency_data,
                    'webhook_processing': webhook_data,
                    'error_analysis': error_data
                },
                'timestamp': timezone.now().isoformat()
            })
            
        except ValueError as e:
            return self.json_response({
                'success': False,
                'error': f'Invalid time period: {str(e)}'
            }, status=400)
        except Exception as e:
            logger.error(f"Error retrieving payment metrics: {str(e)}")
            return self.json_response({
                'success': False,
                'error': 'Failed to retrieve metrics'
            }, status=500)


@login_required
@payment_dashboard_access_required
def payment_metrics_dashboard(request):
    """Render payment metrics dashboard."""
    try:
        # Get basic metrics for the last 24 hours for initial page load
        success_rate_data = payment_metrics.get_payment_success_rate(24)
        latency_data = payment_metrics.get_processing_latency_stats(24)
        webhook_data = payment_metrics.get_webhook_processing_stats(24)
        error_data = payment_metrics.get_error_analysis(24)
        
        context = {
            'success_rate': success_rate_data,
            'latency_stats': latency_data,
            'webhook_stats': webhook_data,
            'error_analysis': error_data,
            'current_time': timezone.now()
        }
        
        return render(request, 'payments/metrics_dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Error loading metrics dashboard: {str(e)}")
        return render(request, 'payments/metrics_dashboard.html', {
            'error': 'Failed to load metrics data'
        })


# API endpoint URLs mapping
urlpatterns = [
    # Payment Intent endpoints
    ('api/payments/create-intent/', CreatePaymentIntentView.as_view(), 'create_payment_intent'),
    ('api/payments/intent/<str:payment_intent_id>/', RetrievePaymentIntentView.as_view(), 'retrieve_payment_intent'),  
    ('api/payments/confirm/<str:payment_intent_id>/', ConfirmPaymentIntentView.as_view(), 'confirm_payment_intent'),
    
    # Refund endpoints
    ('api/payments/refund/', CreateRefundView.as_view(), 'create_refund'),
    ('api/refund/', ProcessRefundAPIView.as_view(), 'process_refund'),
    
    # Terminal endpoints
    ('api/payments/connection-token/', CreateConnectionTokenView.as_view(), 'create_connection_token'),
    
    # History and Details
    ('history/', payment_history, 'payment_history'),
    ('transaction/<str:transaction_id>/', transaction_detail, 'transaction_detail'),
    ('api/transaction/<str:transaction_id>/', TransactionDetailAPIView.as_view(), 'transaction_detail_api'),
    
    # UI Views
    ('form/', payment_form, 'payment-form'),
    
    # API endpoints for UI
    ('api/recent/', RecentTransactionsView.as_view(), 'recent-transactions'),
    
    # Metrics and Monitoring
    ('api/metrics/', PaymentMetricsAPIView.as_view(), 'payment-metrics-api'),
    ('metrics/', payment_metrics_dashboard, 'payment-metrics-dashboard'),
    
    # Dashboard views (will be added to main urls.py)
    ('payments/dashboard/', payment_dashboard, 'payment_dashboard'),
    ('payments/<int:transaction_id>/', payment_detail, 'payment_detail'),
]
