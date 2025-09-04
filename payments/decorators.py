"""
Security decorators for payment operations with PCI DSS compliance.
"""

from functools import wraps
from decimal import Decimal
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def payment_processor_required(view_func):
    """
    Decorator to ensure user has payment processing permissions.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        # Check if user has payment processing permission
        if not (request.user.has_perm('payments.add_paymenttransaction') or 
                request.user.is_staff):
            logger.warning(
                f"Payment processing access denied for user {request.user.username} "
                f"from IP {request.META.get('REMOTE_ADDR', 'unknown')}"
            )
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({
                    'error': True,
                    'message': 'You do not have permission to process payments.'
                }, status=403)
            raise PermissionDenied("You do not have permission to process payments.")
        
        logger.info(
            f"Payment processing access granted to user {request.user.username} "
            f"for {request.method} {request.path}"
        )
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


def refund_processor_required(view_func):
    """
    Decorator to ensure user has refund processing permissions.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        # Check if user has refund processing permission
        if not (request.user.has_perm('payments.add_paymentrefund') or 
                request.user.is_staff):
            logger.warning(
                f"Refund processing access denied for user {request.user.username} "
                f"from IP {request.META.get('REMOTE_ADDR', 'unknown')}"
            )
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({
                    'error': True,
                    'message': 'You do not have permission to process refunds.'
                }, status=403)
            raise PermissionDenied("You do not have permission to process refunds.")
        
        logger.info(
            f"Refund processing access granted to user {request.user.username} "
            f"for {request.method} {request.path}"
        )
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


def manager_approval_required(threshold_amount=None):
    """
    Decorator to require manager approval for high-value operations.
    
    Args:
        threshold_amount: Decimal amount requiring manager approval
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            # Get threshold from settings if not specified
            if threshold_amount is None:
                threshold = Decimal(str(getattr(settings, 'PAYMENT_REFUND_AUTHORIZATION_THRESHOLD', 100.00)))
            else:
                threshold = Decimal(str(threshold_amount))
            
            # Try to get amount from request data
            amount = None
            if request.method == 'POST':
                if hasattr(request, 'json') and request.json:
                    amount = request.json.get('amount')
                elif request.POST.get('amount'):
                    amount = request.POST.get('amount')
            
            # If amount exceeds threshold, require manager permissions
            if amount and Decimal(str(amount)) > threshold:
                if not (request.user.is_staff or request.user.is_superuser):
                    logger.warning(
                        f"Manager approval required for ${amount} operation by user {request.user.username} "
                        f"from IP {request.META.get('REMOTE_ADDR', 'unknown')}"
                    )
                    if request.headers.get('Content-Type') == 'application/json':
                        return JsonResponse({
                            'error': True,
                            'message': f'Manager approval required for amounts over ${threshold}.'
                        }, status=403)
                    raise PermissionDenied(f"Manager approval required for amounts over ${threshold}.")
                
                logger.info(
                    f"Manager approval granted for ${amount} operation by user {request.user.username}"
                )
            
            return view_func(request, *args, **kwargs)
        
        return _wrapped_view
    
    return decorator


def payment_dashboard_access_required(view_func):
    """
    Decorator to ensure user can access payment dashboard.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        # Check if user has permission to view payments
        if not (request.user.has_perm('payments.view_paymenttransaction') or 
                request.user.is_staff):
            logger.warning(
                f"Payment dashboard access denied for user {request.user.username} "
                f"from IP {request.META.get('REMOTE_ADDR', 'unknown')}"
            )
            raise PermissionDenied("You do not have permission to view payment information.")
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


def webhook_admin_required(view_func):
    """
    Decorator to ensure only administrators can access webhook management.
    """
    @wraps(view_func)
    @user_passes_test(lambda u: u.is_staff or u.is_superuser)
    def _wrapped_view(request, *args, **kwargs):
        logger.info(
            f"Webhook admin access granted to user {request.user.username} "
            f"for {request.method} {request.path}"
        )
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view
