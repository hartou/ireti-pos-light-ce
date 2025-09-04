# 🧪 Stripe Implementation Testing Guide

This guide covers all aspects of testing the Stripe payments integration in the Ireti POS Light system.

## 📋 Test Environment Setup

### 1. Configure Test Environment

```bash
# 1. Install test dependencies
pip install -r requirements.txt

# 2. Set up test environment variables
cp .env.example .env.test
```

Edit `.env.test` with test Stripe keys:
```env
STRIPE_PUBLISHABLE_KEY=pk_test_51234567890abcdef
STRIPE_SECRET_KEY=sk_test_51234567890abcdef
STRIPE_WEBHOOK_SECRET=whsec_1234567890abcdef
STRIPE_API_VERSION=2024-06-20
```

### 2. Database Setup for Testing

```bash
# Run migrations for payments app
python manage.py makemigrations payments
python manage.py migrate

# Create test superuser
python manage.py createsuperuser --username testadmin --email admin@test.com
```

## 🧪 Test Types and Execution

### 1. Unit Tests

Run specific test categories:

```bash
# Test payment models
python manage.py test payments.tests.test_models

# Test payment services
python manage.py test payments.tests.test_services

# Test all payment unit tests
python manage.py test payments.tests

# Run with coverage
coverage run --source='payments' manage.py test payments.tests
coverage report -m
coverage html  # Generate HTML coverage report
```

### 2. Integration Tests

```bash
# Test complete payment flows
python manage.py test payments.tests.test_integration

# Test with verbose output
python manage.py test payments.tests.test_integration -v 2

# Test specific integration scenario
python manage.py test payments.tests.test_integration.StripeIntegrationFlowTest.test_successful_payment_flow
```

### 3. Manual Testing Scenarios

#### A. Test Payment Intent Creation

Using Django shell:
```python
python manage.py shell

from payments.services import StripePaymentService
from decimal import Decimal

service = StripePaymentService()

# Test creating payment intent
result = service.create_payment_intent(
    amount=Decimal('10.00'),
    currency='usd',
    metadata={'test': 'true'}
)

print(f"Payment Intent ID: {result['id']}")
print(f"Client Secret: {result['client_secret']}")
```

#### B. Test with Stripe Test Cards

Use these test card numbers for manual testing:

```python
# Successful payments
VISA_SUCCESS = '4242424242424242'
MASTERCARD_SUCCESS = '5555555555554444'
AMEX_SUCCESS = '378282246310005'

# Declined payments
VISA_DECLINE_INSUFFICIENT_FUNDS = '4000000000009995'
VISA_DECLINE_STOLEN_CARD = '4000000000009979'
VISA_DECLINE_PROCESSING_ERROR = '4000000000000119'

# 3D Secure test cards
VISA_3DS_REQUIRED = '4000002760003184'
VISA_3DS_OPTIONAL = '4000002500003155'
```

#### C. Test Refund Processing

```python
# In Django shell
from payments.services import StripePaymentService
from decimal import Decimal

service = StripePaymentService()

# Create payment first
payment = service.create_payment_intent(
    amount=Decimal('20.00'),
    currency='usd'
)

# Then create refund
refund = service.create_refund(
    payment_intent_id=payment['id'],
    amount=Decimal('10.00'),  # Partial refund
    reason='requested_by_customer'
)

print(f"Refund ID: {refund['id']}")
```

### 4. Terminal Testing (POS Hardware)

#### A. Connection Token Testing

```python
# Test terminal connection
from payments.services import StripePaymentService

service = StripePaymentService()
token = service.create_connection_token()

print(f"Connection Token: {token['secret']}")
```

#### B. Hardware Reader Simulation

```bash
# Use Stripe CLI to simulate reader events
stripe listen --forward-to localhost:8000/payments/webhooks/

# In another terminal, trigger test events
stripe trigger payment_intent.succeeded
stripe trigger payment_intent.payment_failed
```

### 5. Webhook Testing

#### A. Local Webhook Testing

```bash
# 1. Install Stripe CLI
# Download from: https://stripe.com/docs/stripe-cli

# 2. Login to Stripe
stripe login

# 3. Forward webhooks to local server
stripe listen --forward-to localhost:8000/payments/webhooks/

# 4. Trigger test webhooks
stripe trigger payment_intent.succeeded
stripe trigger payment_intent.payment_failed
stripe trigger charge.dispute.created
```

#### B. Webhook Processing Validation

```python
# Check webhook processing in Django shell
from payments.models import PaymentWebhook

# View recent webhook events
webhooks = PaymentWebhook.objects.all()[:10]
for webhook in webhooks:
    print(f"{webhook.event_type}: {webhook.processed}")

# Check for processing errors
failed_webhooks = PaymentWebhook.objects.filter(processed=False)
for webhook in failed_webhooks:
    print(f"Failed: {webhook.event_type} - {webhook.processing_error}")
```

## 🔍 Testing Checklist

### Pre-Testing Checklist

- [ ] Test Stripe keys configured in `.env.test`
- [ ] Database migrations applied
- [ ] Test dependencies installed
- [ ] Django test database configured

### Unit Testing Checklist

- [ ] Payment models validation
- [ ] Payment service methods
- [ ] Error handling scenarios  
- [ ] Currency conversion logic
- [ ] Webhook event processing

### Integration Testing Checklist

- [ ] Complete payment flow (create → confirm → capture)
- [ ] Refund processing flow
- [ ] Terminal connection flow
- [ ] Webhook event handling
- [ ] Error scenarios end-to-end

### Manual Testing Checklist

#### Payment Processing
- [ ] Successful card payment
- [ ] Declined payment handling
- [ ] 3D Secure authentication
- [ ] Multiple payment methods
- [ ] International cards
- [ ] Different currencies

#### Terminal Integration
- [ ] Reader discovery
- [ ] Reader connection
- [ ] Card present payments
- [ ] Contactless payments
- [ ] Chip and PIN
- [ ] Receipt printing

#### Refund Processing
- [ ] Full refund
- [ ] Partial refund  
- [ ] Multiple partial refunds
- [ ] Refund authorization
- [ ] Refund receipt

#### Edge Cases
- [ ] Network interruption during payment
- [ ] Webhook delivery failures
- [ ] Duplicate payment prevention
- [ ] Invalid payment amounts
- [ ] Expired payment intents

## 🐛 Common Testing Issues

### 1. Authentication Errors
```
Error: Invalid API key provided
```
**Solution**: Verify `STRIPE_SECRET_KEY` in environment variables

### 2. Webhook Signature Verification
```
Error: Invalid webhook signature
```  
**Solution**: Check `STRIPE_WEBHOOK_SECRET` configuration

### 3. Payment Intent Not Found
```
Error: No such payment_intent: pi_test_xxx
```
**Solution**: Ensure using correct Stripe account/environment

### 4. Terminal Connection Issues
```
Error: No readers found
```
**Solution**: Use simulated readers for testing: `simulated: true`

### 5. Database Connection Errors
```
Error: PaymentTransaction matching query does not exist
```
**Solution**: Ensure test database is properly migrated

## 📊 Performance Testing

### Load Testing Payment Endpoints

```python
# Simple load test script
import concurrent.futures
import time
from payments.services import StripePaymentService

def test_payment_creation():
    service = StripePaymentService()
    return service.create_payment_intent(amount=Decimal('10.00'))

# Test with multiple concurrent requests
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(test_payment_creation) for _ in range(100)]
    results = [future.result() for future in futures]

print(f"Completed {len(results)} payment intent creations")
```

### Monitoring Test Metrics

```bash
# Monitor test database performance
python manage.py shell

from django.db import connection
print(f"Database queries: {len(connection.queries)}")

# Clear query log for fresh metrics
connection.queries.clear()
```

## 🚀 Continuous Integration Testing

### GitHub Actions Test Configuration

```yaml
# .github/workflows/stripe-tests.yml
name: Stripe Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    env:
      STRIPE_SECRET_KEY: ${{ secrets.STRIPE_TEST_SECRET_KEY }}
      STRIPE_PUBLISHABLE_KEY: ${{ secrets.STRIPE_TEST_PUBLISHABLE_KEY }}
      
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
        
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        
    - name: Run tests
      run: |
        python manage.py test payments.tests
        
    - name: Generate coverage report
      run: |
        coverage run --source='payments' manage.py test payments.tests
        coverage xml
        
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v1
```

## 📝 Test Documentation

### Recording Test Results

```bash
# Generate test report
python manage.py test payments.tests --verbosity=2 > test_results.txt

# Generate coverage report
coverage run --source='payments' manage.py test payments.tests
coverage report > coverage_report.txt
coverage html --directory=htmlcov/
```

### Test Case Documentation

Each test should include:
- **Purpose**: What is being tested
- **Setup**: Required test data
- **Steps**: Testing procedure  
- **Expected**: Expected outcome
- **Cleanup**: Post-test cleanup

This comprehensive testing approach ensures the Stripe integration is robust, secure, and ready for production use.
