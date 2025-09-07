"""
PWA-related and security middleware for Ireti POS Light
"""

import logging

logger = logging.getLogger(__name__)


class PWASecurityMiddleware:
    """
    Middleware to add PWA-specific and payment security headers
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add Service-Worker-Allowed header for service worker requests
        if request.path.endswith('/sw.js') or 'service-worker' in request.path:
            response['Service-Worker-Allowed'] = '/'
        
        # Enhanced security headers for payment-related paths
        if '/payments/' in request.path:
            # PCI DSS compliance headers
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-Frame-Options'] = 'DENY'  # Prevent clickjacking on payment pages
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            response['Permissions-Policy'] = 'payment=self, camera=(), microphone=(), geolocation=()'
            
            # Additional security for payment forms
            if any(path in request.path for path in ['/payment-form/', '/create-intent/', '/confirm/']):
                response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
                response['Pragma'] = 'no-cache'
                response['Expires'] = '0'
        else:
            # Standard PWA-friendly headers for non-payment pages
            response['X-Content-Type-Options'] = 'nosniff'
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response


class PaymentAuditMiddleware:
    """
    Middleware to audit payment-related requests for compliance
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log payment-related requests for audit trail (without sensitive data)
        if '/payments/' in request.path and request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            logger.info(
                f"Payment audit: {request.method} {request.path} "
                f"by user {getattr(request.user, 'username', 'anonymous')} "
                f"from IP {self.get_client_ip(request)}"
            )
        
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        """Get client IP address safely"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip