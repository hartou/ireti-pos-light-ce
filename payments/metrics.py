"""
Payment metrics and observability utilities for monitoring and analytics.

This module provides functionality to track payment performance metrics,
success/failure rates, and processing latency for operational monitoring.
"""

import logging
import time
from django.utils import timezone
from django.db import models
from django.db.models import Count, Avg, Sum
from django.conf import settings
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from collections import defaultdict
import json

logger = logging.getLogger('payments.metrics')


class PaymentMetrics:
    """
    Service for collecting and reporting payment metrics.
    """
    
    def __init__(self):
        self.logger = logger
    
    def record_payment_attempt(self, amount: float, currency: str = 'USD', metadata: dict = None):
        """Record a payment attempt for metrics tracking."""
        try:
            from .models import PaymentMetric
            PaymentMetric.objects.create(
                event_type='payment_attempt',
                amount=amount,
                currency=currency,
                metadata=metadata or {},
                timestamp=timezone.now()
            )
            self.logger.info(f"Recorded payment attempt: {amount} {currency}")
        except Exception as e:
            self.logger.error(f"Failed to record payment attempt metric: {e}")
    
    def record_payment_success(self, payment_intent_id: str, amount: float, 
                             currency: str = 'USD', processing_time: float = None):
        """Record a successful payment for metrics tracking."""
        try:
            from .models import PaymentMetric
            metadata = {'payment_intent_id': payment_intent_id}
            if processing_time:
                metadata['processing_time_ms'] = processing_time
            
            PaymentMetric.objects.create(
                event_type='payment_success',
                amount=amount,
                currency=currency,
                metadata=metadata,
                timestamp=timezone.now()
            )
            self.logger.info(f"Recorded payment success: {payment_intent_id} - {amount} {currency}")
        except Exception as e:
            self.logger.error(f"Failed to record payment success metric: {e}")
    
    def record_payment_failure(self, payment_intent_id: str, amount: float, 
                             currency: str = 'USD', error_code: str = None, 
                             error_message: str = None, processing_time: float = None):
        """Record a failed payment for metrics tracking."""
        try:
            from .models import PaymentMetric
            metadata = {
                'payment_intent_id': payment_intent_id,
                'error_code': error_code,
                'error_message': error_message[:500] if error_message else None  # Truncate long messages
            }
            if processing_time:
                metadata['processing_time_ms'] = processing_time
            
            PaymentMetric.objects.create(
                event_type='payment_failure',
                amount=amount,
                currency=currency,
                metadata=metadata,
                timestamp=timezone.now()
            )
            self.logger.info(f"Recorded payment failure: {payment_intent_id} - {error_code}")
        except Exception as e:
            self.logger.error(f"Failed to record payment failure metric: {e}")
    
    def record_refund_success(self, refund_id: str, amount: float, 
                            currency: str = 'USD', processing_time: float = None):
        """Record a successful refund for metrics tracking."""
        try:
            from .models import PaymentMetric
            metadata = {'refund_id': refund_id}
            if processing_time:
                metadata['processing_time_ms'] = processing_time
            
            PaymentMetric.objects.create(
                event_type='refund_success',
                amount=amount,
                currency=currency,
                metadata=metadata,
                timestamp=timezone.now()
            )
            self.logger.info(f"Recorded refund success: {refund_id} - {amount} {currency}")
        except Exception as e:
            self.logger.error(f"Failed to record refund success metric: {e}")
    
    def record_refund_failure(self, refund_id: str, amount: float, 
                            currency: str = 'USD', error_code: str = None, 
                            error_message: str = None, processing_time: float = None):
        """Record a failed refund for metrics tracking."""
        try:
            from .models import PaymentMetric
            metadata = {
                'refund_id': refund_id,
                'error_code': error_code,
                'error_message': error_message[:500] if error_message else None
            }
            if processing_time:
                metadata['processing_time_ms'] = processing_time
            
            PaymentMetric.objects.create(
                event_type='refund_failure',
                amount=amount,
                currency=currency,
                metadata=metadata,
                timestamp=timezone.now()
            )
            self.logger.info(f"Recorded refund failure: {refund_id} - {error_code}")
        except Exception as e:
            self.logger.error(f"Failed to record refund failure metric: {e}")
    
    def record_webhook_received(self, event_type: str, event_id: str, processing_time: float = None):
        """Record webhook reception for metrics tracking."""
        try:
            from .models import PaymentMetric
            metadata = {
                'webhook_event_type': event_type,
                'webhook_event_id': event_id
            }
            if processing_time:
                metadata['processing_time_ms'] = processing_time
            
            PaymentMetric.objects.create(
                event_type='webhook_received',
                metadata=metadata,
                timestamp=timezone.now()
            )
            self.logger.info(f"Recorded webhook received: {event_type}")
        except Exception as e:
            self.logger.error(f"Failed to record webhook metric: {e}")
    
    def get_payment_success_rate(self, hours: int = 24) -> Dict[str, Any]:
        """Get payment success rate for the specified time period."""
        try:
            from .models import PaymentMetric
            
            since = timezone.now() - timedelta(hours=hours)
            
            # Get payment attempts and successes
            total_attempts = PaymentMetric.objects.filter(
                event_type='payment_attempt',
                timestamp__gte=since
            ).count()
            
            successful_payments = PaymentMetric.objects.filter(
                event_type='payment_success',
                timestamp__gte=since
            ).count()
            
            failed_payments = PaymentMetric.objects.filter(
                event_type='payment_failure',
                timestamp__gte=since
            ).count()
            
            # Calculate rates
            total_processed = successful_payments + failed_payments
            success_rate = (successful_payments / total_processed * 100) if total_processed > 0 else 0
            
            return {
                'time_period_hours': hours,
                'total_attempts': total_attempts,
                'successful_payments': successful_payments,
                'failed_payments': failed_payments,
                'success_rate_percentage': round(success_rate, 2),
                'processed_vs_attempts': {
                    'processed': total_processed,
                    'abandoned': total_attempts - total_processed
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to calculate payment success rate: {e}")
            return {'error': str(e)}
    
    def get_processing_latency_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get payment processing latency statistics."""
        try:
            from .models import PaymentMetric
            
            since = timezone.now() - timedelta(hours=hours)
            
            # Get successful payments with processing time
            success_metrics = PaymentMetric.objects.filter(
                event_type='payment_success',
                timestamp__gte=since,
                metadata__has_key='processing_time_ms'
            )
            
            # Get failure metrics with processing time
            failure_metrics = PaymentMetric.objects.filter(
                event_type='payment_failure',
                timestamp__gte=since,
                metadata__has_key='processing_time_ms'
            )
            
            # Extract processing times
            success_times = [
                float(metric.metadata.get('processing_time_ms', 0))
                for metric in success_metrics
            ]
            
            failure_times = [
                float(metric.metadata.get('processing_time_ms', 0))
                for metric in failure_metrics
            ]
            
            all_times = success_times + failure_times
            
            if not all_times:
                return {'message': 'No processing time data available'}
            
            # Calculate statistics
            avg_time = sum(all_times) / len(all_times)
            min_time = min(all_times)
            max_time = max(all_times)
            
            # Calculate percentiles
            sorted_times = sorted(all_times)
            length = len(sorted_times)
            p50 = sorted_times[length // 2] if length > 0 else 0
            p95 = sorted_times[int(length * 0.95)] if length > 0 else 0
            p99 = sorted_times[int(length * 0.99)] if length > 0 else 0
            
            return {
                'time_period_hours': hours,
                'total_measurements': len(all_times),
                'successful_payments': len(success_times),
                'failed_payments': len(failure_times),
                'latency_ms': {
                    'average': round(avg_time, 2),
                    'minimum': round(min_time, 2),
                    'maximum': round(max_time, 2),
                    'p50_median': round(p50, 2),
                    'p95': round(p95, 2),
                    'p99': round(p99, 2)
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to calculate processing latency: {e}")
            return {'error': str(e)}
    
    def get_webhook_processing_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get webhook processing statistics."""
        try:
            from .models import PaymentMetric
            
            since = timezone.now() - timedelta(hours=hours)
            
            webhook_metrics = PaymentMetric.objects.filter(
                event_type='webhook_received',
                timestamp__gte=since
            )
            
            # Group by webhook event type
            webhook_stats = defaultdict(int)
            processing_times = []
            
            for metric in webhook_metrics:
                event_type = metric.metadata.get('webhook_event_type', 'unknown')
                webhook_stats[event_type] += 1
                
                if 'processing_time_ms' in metric.metadata:
                    processing_times.append(float(metric.metadata['processing_time_ms']))
            
            # Calculate processing time stats
            latency_stats = {}
            if processing_times:
                avg_time = sum(processing_times) / len(processing_times)
                sorted_times = sorted(processing_times)
                length = len(sorted_times)
                
                latency_stats = {
                    'average_ms': round(avg_time, 2),
                    'minimum_ms': round(min(processing_times), 2),
                    'maximum_ms': round(max(processing_times), 2),
                    'p50_median_ms': round(sorted_times[length // 2], 2) if length > 0 else 0,
                    'p95_ms': round(sorted_times[int(length * 0.95)], 2) if length > 0 else 0
                }
            
            return {
                'time_period_hours': hours,
                'total_webhooks': sum(webhook_stats.values()),
                'webhook_types': dict(webhook_stats),
                'processing_latency': latency_stats
            }
        except Exception as e:
            self.logger.error(f"Failed to get webhook processing stats: {e}")
            return {'error': str(e)}
    
    def get_error_analysis(self, hours: int = 24) -> Dict[str, Any]:
        """Get error analysis for failed payments."""
        try:
            from .models import PaymentMetric
            
            since = timezone.now() - timedelta(hours=hours)
            
            failed_payments = PaymentMetric.objects.filter(
                event_type='payment_failure',
                timestamp__gte=since
            )
            
            # Group errors by code
            error_codes = defaultdict(int)
            error_messages = defaultdict(int)
            
            for metric in failed_payments:
                error_code = metric.metadata.get('error_code', 'unknown')
                error_message = metric.metadata.get('error_message', 'unknown')
                
                error_codes[error_code] += 1
                # Group similar error messages (first 100 chars)
                error_key = error_message[:100] if error_message else 'unknown'
                error_messages[error_key] += 1
            
            return {
                'time_period_hours': hours,
                'total_failures': failed_payments.count(),
                'error_codes': dict(error_codes),
                'common_error_messages': dict(sorted(
                    error_messages.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:10])  # Top 10 error messages
            }
        except Exception as e:
            self.logger.error(f"Failed to analyze errors: {e}")
            return {'error': str(e)}


class MetricsTimer:
    """Context manager for timing operations."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time() * 1000  # Convert to milliseconds
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time() * 1000  # Convert to milliseconds
    
    @property
    def elapsed_ms(self) -> float:
        """Get elapsed time in milliseconds."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0


# Global metrics instance
payment_metrics = PaymentMetrics()
