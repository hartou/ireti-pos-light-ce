"""
Secure logging utilities for PCI DSS compliance
"""

import logging
import re
import json
from datetime import datetime

# Patterns for sensitive data that should be redacted
SENSITIVE_PATTERNS = [
    # Credit card numbers (various formats)
    (r'\b4[0-9]{12}(?:[0-9]{3})?\b', '[CARD_REDACTED]'),  # Visa
    (r'\b5[1-5][0-9]{14}\b', '[CARD_REDACTED]'),         # Mastercard
    (r'\b3[47][0-9]{13}\b', '[CARD_REDACTED]'),          # American Express
    (r'\b3[0-9]{13}\b', '[CARD_REDACTED]'),              # Diners Club
    (r'\b6(?:011|5[0-9]{2})[0-9]{12}\b', '[CARD_REDACTED]'), # Discover
    # CVV/CVC codes
    (r'\b[0-9]{3,4}\b(?=.*(?:cvv|cvc|security|code))', '[CVV_REDACTED]'),
    # Social Security Numbers
    (r'\b\d{3}-?\d{2}-?\d{4}\b', '[SSN_REDACTED]'),
    # Email addresses (partial redaction)
    (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_REDACTED]'),
    # Phone numbers  
    (r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE_REDACTED]'),
    # Generic sensitive field patterns
    (r'(?i)(card_number|cardnumber|card-number)\s*[:\=]\s*["\']?[0-9\s-]{13,19}["\']?', r'\1=[CARD_REDACTED]'),
    (r'(?i)(expiry|exp_month|exp_year|expiration)\s*[:\=]\s*["\']?[0-9/]{2,7}["\']?', r'\1=[EXPIRY_REDACTED]'),
    (r'(?i)(password|pwd|secret)\s*[:\=]\s*["\']?[^"\'\s]+["\']?', r'\1=[PASSWORD_REDACTED]'),
]


def redact_sensitive_data(data):
    """
    Redact sensitive information from data before logging.
    
    Args:
        data: Dictionary or string containing potentially sensitive data
        
    Returns:
        dict/str: Data with sensitive information redacted
    """
    if isinstance(data, dict):
        redacted = {}
        for key, value in data.items():
            key_lower = key.lower()
            
            # Card number redaction
            if 'card' in key_lower and 'number' in key_lower:
                if isinstance(value, str) and len(value) >= 13:
                    redacted[key] = f"{value[:6]}...{value[-4:]}"
                else:
                    redacted[key] = '[CARD_REDACTED]'
            # CVV/CVC redaction  
            elif key_lower in ['cvv', 'cvc', 'security_code', 'cvc2']:
                redacted[key] = '***'
            # Expiry date redaction
            elif 'expiry' in key_lower or 'exp_' in key_lower:
                redacted[key] = '[EXPIRY_REDACTED]'
            # Email partial redaction
            elif 'email' in key_lower and isinstance(value, str) and '@' in value:
                parts = value.split('@')
                if len(parts) == 2:
                    username = parts[0]
                    domain = parts[1]
                    redacted_username = username[:2] + '***' if len(username) > 2 else '***'
                    redacted[key] = f"{redacted_username}@{domain}"
                else:
                    redacted[key] = '[EMAIL_REDACTED]'
            # Password redaction
            elif 'password' in key_lower or 'secret' in key_lower:
                redacted[key] = '[SECRET_REDACTED]'
            # Keep other fields as-is
            else:
                if isinstance(value, dict):
                    redacted[key] = redact_sensitive_data(value)
                elif isinstance(value, list):
                    redacted[key] = [redact_sensitive_data(item) if isinstance(item, dict) else item for item in value]
                else:
                    redacted[key] = value
                    
        return redacted
    
    elif isinstance(data, str):
        # Apply pattern-based redaction for strings
        redacted = data
        for pattern, replacement in SENSITIVE_PATTERNS:
            redacted = re.sub(pattern, replacement, redacted)
        return redacted
    
    else:
        return dataging
import re
from typing import Any, Dict

# Sensitive data patterns to redact from logs
SENSITIVE_PATTERNS = [
    # Credit card numbers (any format)
    (r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3[0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b', '[CARD_REDACTED]'),
    # Stripe secret keys
    (r'sk_[a-zA-Z0-9_]+', '[STRIPE_SECRET_REDACTED]'),
    # Stripe publishable keys  
    (r'pk_[a-zA-Z0-9_]+', '[STRIPE_PUBLIC_REDACTED]'),
    # Payment method IDs
    (r'pm_[a-zA-Z0-9_]+', '[PAYMENT_METHOD_REDACTED]'),
    # CVV codes
    (r'\bcvv\s*[:\=]\s*[0-9]{3,4}\b', 'cvv=[CVV_REDACTED]'),
    (r'\bcvc\s*[:\=]\s*[0-9]{3,4}\b', 'cvc=[CVC_REDACTED]'),
    # Social Security Numbers
    (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN_REDACTED]'),
    # Email addresses in payment context
    (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_REDACTED]'),
    # Phone numbers  
    (r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE_REDACTED]'),
    # Generic sensitive field patterns
    (r'(?i)(card_number|cardnumber|card-number)\s*[:\=]\s*["\']?[0-9\s-]{13,19}["\']?', r'\1=[CARD_REDACTED]'),
    (r'(?i)(expiry|exp_month|exp_year|expiration)\s*[:\=]\s*["\']?[0-9/]{2,7}["\']?', r'\1=[EXPIRY_REDACTED]'),
    (r'(?i)(password|pwd|secret)\s*[:\=]\s*["\']?[^"\'\s]+["\']?', r'\1=[PASSWORD_REDACTED]'),
]


class SecureFormatter(logging.Formatter):
    """
    Custom logging formatter that redacts sensitive information.
    """
    
    def format(self, record):
        # Apply standard formatting first
        formatted = super().format(record)
        
        # Redact sensitive patterns
        for pattern, replacement in SENSITIVE_PATTERNS:
            formatted = re.sub(pattern, replacement, formatted, flags=re.IGNORECASE)
        
        return formatted


def redact_sensitive_data(data: Any) -> Any:
    """
    Recursively redact sensitive data from dictionaries, lists, and strings.
    
    Args:
        data: The data to redact (dict, list, str, or other)
        
    Returns:
        The data with sensitive information redacted
    """
    if isinstance(data, dict):
        redacted = {}
        for key, value in data.items():
            # Redact sensitive keys
            if any(sensitive_key in key.lower() for sensitive_key in 
                   ['card', 'cvv', 'cvc', 'exp', 'ssn', 'password', 'secret', 'token']):
                if isinstance(value, str) and len(value) > 4:
                    redacted[key] = f"[REDACTED]...{value[-4:]}"
                else:
                    redacted[key] = "[REDACTED]"
            else:
                redacted[key] = redact_sensitive_data(value)
        return redacted
    
    elif isinstance(data, list):
        return [redact_sensitive_data(item) for item in data]
    
    elif isinstance(data, str):
        # Apply pattern-based redaction
        redacted = data
        for pattern, replacement in SENSITIVE_PATTERNS:
            redacted = re.sub(pattern, replacement, redacted, flags=re.IGNORECASE)
        return redacted
    
    else:
        return data


def secure_log_payment_event(event_type, message, data=None, level=logging.INFO):
    """
    Log payment events with automatic sensitive data redaction.
    
    Args:
        event_type: Type of payment event (e.g., 'payment_created', 'webhook_received')
        message: Log message
        data: Additional data to log (will be redacted)
        level: Logging level
    """
    logger = logging.getLogger('payments.security')
    
    # Prepare log data
    log_data = {
        'event_type': event_type,
        'message': message,
        'timestamp': datetime.now().isoformat(),
    }
    
    # Add and redact additional data if provided
    if data:
        log_data['data'] = redact_sensitive_data(data)
    
    # Log with appropriate level
    logger.log(level, json.dumps(log_data, default=str))


def create_audit_trail(user_id: str, action: str, resource_type: str, 
                      resource_id: str, details: Dict[str, Any] = None,
                      ip_address: str = None):
    """
    Create a secure audit trail entry for compliance.
    
    Args:
        user_id: ID of the user performing the action
        action: Action performed (e.g., 'payment_processed', 'refund_created')
        resource_type: Type of resource (e.g., 'payment', 'refund')
        resource_id: ID of the resource affected
        details: Additional details (will be redacted)
        ip_address: User's IP address
    """
    logger = logging.getLogger('payments.audit')
    
    audit_data = {
        'user_id': user_id,
        'action': action,
        'resource_type': resource_type,
        'resource_id': resource_id,
        'timestamp': logging.Formatter().formatTime(logging.LogRecord(
            name='', level=0, pathname='', lineno=0, 
            msg='', args=(), exc_info=None
        )),
        'ip_address': ip_address
    }
    
    if details:
        audit_data['details'] = redact_sensitive_data(details)
    
    secure_log_payment_event(
        logger, logging.INFO,
        f"AUDIT: {action} performed on {resource_type} {resource_id}",
        audit_data
    )
