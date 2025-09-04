# Payments App

This Django app handles payment processing integration with Stripe for the Ireti POS Light system.

## Features

- Secure credit/debit card payment processing
- PCI DSS compliant implementation
- Refund and partial refund support
- Webhook handling for payment confirmations
- Multi-payment method support
- Offline payment queuing for PWA

## Security

This app implements strict security measures:
- No sensitive card data storage
- Encrypted data transmission
- Webhook signature verification
- Role-based access controls
- Comprehensive audit logging

## Models

- `PaymentMethod`: Available payment methods
- `PaymentTransaction`: Payment transaction records
- `PaymentRefund`: Refund transaction records

## API Endpoints

- `/api/payments/create-intent/` - Create Stripe payment intent
- `/api/payments/confirm/` - Confirm payment processing
- `/api/payments/refund/` - Process refunds
- `/api/payments/status/<id>/` - Check payment status

## Setup

1. Configure Stripe API keys in environment variables
2. Run migrations: `python manage.py migrate payments`
3. Configure webhook endpoints in Stripe dashboard
4. Set up appropriate user permissions

For detailed setup instructions, see the STRIPE_INTEGRATION_PLAN.md file.
