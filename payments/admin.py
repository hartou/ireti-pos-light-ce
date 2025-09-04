from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import PaymentMethod, PaymentTransaction, PaymentRefund, PaymentWebhook


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    """Admin interface for PaymentMethod model."""
    
    list_display = [
        'name', 
        'stripe_payment_method_type', 
        'is_active_display', 
        'sort_order',
        'created_at'
    ]
    list_filter = ['is_active', 'stripe_payment_method_type', 'created_at']
    search_fields = ['name']
    ordering = ['sort_order', 'name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'stripe_payment_method_type', 'is_active', 'sort_order')
        }),
        (_('System Information'), {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_active_display(self, obj):
        """Display active status with colored indicator."""
        if obj.is_active:
            return format_html('<span style="color: green;">✓ Active</span>')
        return format_html('<span style="color: red;">✗ Inactive</span>')
    is_active_display.short_description = _('Status')


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    """Admin interface for PaymentTransaction model."""
    
    list_display = [
        'stripe_payment_intent_id',
        'transaction_link',
        'amount_display',
        'status_display',
        'processed_by',
        'created_at'
    ]
    list_filter = [
        'status',
        'currency',
        'payment_method__name',
        'created_at',
        'processed_at'
    ]
    search_fields = [
        'stripe_payment_intent_id',
        'transaction__id',
        'processed_by__username'
    ]
    readonly_fields = [
        'id',
        'stripe_payment_intent_id',
        'stripe_client_secret',
        'stripe_status',
        'last_payment_error',
        'idempotency_key',
        'created_at',
        'updated_at',
        'processed_at'
    ]
    ordering = ['-created_at']
    
    fieldsets = (
        (_('Payment Information'), {
            'fields': (
                'transaction',
                'payment_method',
                'amount',
                'currency',
                'processed_by'
            )
        }),
        (_('Stripe Integration'), {
            'fields': (
                'stripe_payment_intent_id',
                'stripe_client_secret',
                'stripe_status',
                'last_payment_error'
            ),
            'classes': ('collapse',)
        }),
        (_('Status & Tracking'), {
            'fields': (
                'status',
                'failure_reason',
                'processed_at'
            )
        }),
        (_('Audit Trail'), {
            'fields': (
                'id',
                'idempotency_key',
                'metadata',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def transaction_link(self, obj):
        """Create a link to the related POS transaction."""
        if obj.transaction:
            url = reverse('admin:transaction_transaction_change', args=[obj.transaction.id])
            return format_html('<a href="{}">{}</a>', url, obj.transaction.id)
        return '-'
    transaction_link.short_description = _('POS Transaction')
    
    def amount_display(self, obj):
        """Format amount with currency."""
        return f"{obj.amount} {obj.currency}"
    amount_display.short_description = _('Amount')
    
    def status_display(self, obj):
        """Display status with color coding."""
        colors = {
            'succeeded': 'green',
            'failed': 'red',
            'pending': 'orange',
            'processing': 'blue',
            'canceled': 'gray',
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = _('Status')
    
    def has_add_permission(self, request):
        """Prevent manual creation of payment transactions."""
        return False


@admin.register(PaymentRefund)
class PaymentRefundAdmin(admin.ModelAdmin):
    """Admin interface for PaymentRefund model."""
    
    list_display = [
        'stripe_refund_id',
        'payment_transaction_link',
        'amount_display',
        'reason',
        'status_display',
        'processed_by',
        'authorized_by',
        'created_at'
    ]
    list_filter = [
        'status',
        'reason',
        'created_at',
        'processed_at'
    ]
    search_fields = [
        'stripe_refund_id',
        'payment_transaction__stripe_payment_intent_id',
        'processed_by__username',
        'authorized_by__username'
    ]
    readonly_fields = [
        'id',
        'stripe_refund_id',
        'idempotency_key',
        'created_at',
        'updated_at',
        'processed_at'
    ]
    ordering = ['-created_at']
    
    fieldsets = (
        (_('Refund Information'), {
            'fields': ('payment_transaction', 'amount', 'reason', 'description')
        }),
        (_('Authorization'), {
            'fields': ('processed_by', 'authorized_by')
        }),
        (_('Stripe Integration'), {
            'fields': ('stripe_refund_id',),
            'classes': ('collapse',)
        }),
        (_('Status & Tracking'), {
            'fields': ('status', 'failure_reason', 'processed_at')
        }),
        (_('Audit Trail'), {
            'fields': ('id', 'idempotency_key', 'metadata', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def payment_transaction_link(self, obj):
        """Create a link to the related payment transaction."""
        if obj.payment_transaction:
            url = reverse('admin:payments_paymenttransaction_change', args=[obj.payment_transaction.id])
            return format_html('<a href="{}">{}</a>', url, obj.payment_transaction.stripe_payment_intent_id)
        return '-'
    payment_transaction_link.short_description = _('Payment Transaction')
    
    def amount_display(self, obj):
        """Format amount with currency."""
        return f"{obj.amount} {obj.currency}"
    amount_display.short_description = _('Amount')
    
    def status_display(self, obj):
        """Display status with color coding."""
        colors = {
            'succeeded': 'green',
            'failed': 'red',
            'pending': 'orange',
            'canceled': 'gray'
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = _('Status')
    
    def has_add_permission(self, request):
        """Prevent manual creation of refunds through admin."""
        return False


@admin.register(PaymentWebhook)
class PaymentWebhookAdmin(admin.ModelAdmin):
    """Admin interface for PaymentWebhook model."""
    
    list_display = [
        'stripe_event_id',
        'event_type',
        'processed_display',
        'created_at',
        'processed_at'
    ]
    list_filter = [
        'processed',
        'event_type',
        'created_at'
    ]
    search_fields = [
        'stripe_event_id',
        'event_type'
    ]
    readonly_fields = [
        'id',
        'stripe_event_id',
        'event_type',
        'created_at',
        'processed_at'
    ]
    ordering = ['-created_at']
    
    fieldsets = (
        (_('Webhook Information'), {
            'fields': (
                'stripe_event_id',
                'event_type'
            )
        }),
        (_('Processing Status'), {
            'fields': (
                'processed',
                'processing_error',
                'processed_at'
            )
        }),
        (_('Metadata'), {
            'fields': (
                'id',
                'created_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def processed_display(self, obj):
        """Display processed status with colored indicator."""
        if obj.processed:
            return format_html('<span style="color: green;">✓ Processed</span>')
        elif obj.processing_error:
            return format_html('<span style="color: red;">✗ Error</span>')
        return format_html('<span style="color: orange;">⏳ Pending</span>')
    processed_display.short_description = _('Status')


# Inline admin for displaying related payments in transaction admin
class PaymentTransactionInline(admin.TabularInline):
    """Inline display for payments in transaction admin."""
    model = PaymentTransaction
    extra = 0
    readonly_fields = [
        'id',
        'payment_method',
        'amount',
        'currency',
        'status',
        'stripe_payment_intent_id',
        'created_at'
    ]
    fields = [
        'payment_method',
        'amount',
        'currency', 
        'status',
        'stripe_payment_intent_id',
        'created_at'
    ]
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


# Inline admin for displaying refunds in payment transaction admin  
class PaymentRefundInline(admin.TabularInline):
    """Inline display for refunds in payment transaction admin."""
    model = PaymentRefund
    extra = 0
    readonly_fields = [
        'id',
        'amount',
        'reason',
        'status',
        'processed_by',
        'created_at'
    ]
    fields = [
        'amount',
        'reason',
        'status',
        'processed_by',
        'created_at'
    ]
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


# Add the inline to PaymentTransactionAdmin
PaymentTransactionAdmin.inlines = [PaymentRefundInline]
