"""
URL configuration for payments app.
"""

from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Payment Processing UI
    path('', views.payment_form, name='payment_form'),
    path('form/', views.payment_form, name='payment_form_alt'),
    path('terminal/', views.pos_terminal, name='pos_terminal'),
    path('status/', views.payment_status, name='payment_status'),
    path('status/<str:payment_intent_id>/', views.payment_status, name='payment_status_detail'),
    path('receipt/', views.receipt_view, name='receipt'),
    path('receipt/<str:transaction_id>/', views.receipt_view, name='receipt_detail'),
    
    # API endpoints for payment processing
    path('api/intent/', views.CreatePaymentIntentView.as_view(), name='create_payment_intent'),
    path('api/intent/<str:payment_intent_id>/', views.RetrievePaymentIntentView.as_view(), name='retrieve_payment_intent'),
    path('api/confirm/<str:payment_intent_id>/', views.ConfirmPaymentIntentView.as_view(), name='confirm_payment_intent'),
    path('api/refund/', views.CreateRefundView.as_view(), name='create_refund'),
    path('api/connection-token/', views.CreateConnectionTokenView.as_view(), name='create_connection_token'),
    path('api/recent/', views.RecentTransactionsView.as_view(), name='recent_transactions'),
    
    # Payment History and Transaction Management
    path('history/', views.payment_history, name='payment_history'),
    path('transaction/<str:transaction_id>/', views.transaction_detail, name='transaction_detail'),
    path('api/transaction/<str:transaction_id>/', views.TransactionDetailAPIView.as_view(), name='transaction_detail_api'),
    path('api/process-refund/', views.ProcessRefundAPIView.as_view(), name='process_refund'),
    
    # Webhook endpoint (CSRF exempt)
    path('webhook/', views.StripeWebhookView.as_view(), name='stripe_webhook'),
    
    # Dashboard and management views
    path('dashboard/', views.payment_dashboard, name='dashboard'),
    path('detail/<int:transaction_id>/', views.payment_detail, name='detail'),
    path('webhooks/', views.webhook_dashboard, name='webhook_dashboard'),
]
