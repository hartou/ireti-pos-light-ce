# 🧪 Complete Stripe Integration Testing Guide

## 📊 Current Testing Status

Based on our test results, here's the current status of the Stripe implementation:

### ✅ **What's Working:**
- **Task 2 Complete**: Payment models are fully implemented
  - `PaymentMethod` model ✅
  - `PaymentTransaction` model ✅  
  - `PaymentRefund` model ✅
  - `PaymentWebhook` model ✅
- **Django Integration**: Payment app is configured in settings ✅
- **Stripe Configuration**: Settings structure is ready ✅

### ⚠️ **What Needs Setup:**
- **API Keys**: Real Stripe test keys need to be configured
- **Database**: Migrations need to be applied
- **Dependencies**: Some compatibility issues to resolve

## 🚀 **Step-by-Step Testing Setup**

### **1. Get Stripe Test API Keys**

1. **Sign up/Login to Stripe:**
   - Go to [https://dashboard.stripe.com](https://dashboard.stripe.com)
   - Create account or login

2. **Get Test Keys:**
   - Navigate to **Developers > API Keys**
   - Toggle to **Test mode** (important!)
   - Copy your keys:
     - **Publishable key**: `pk_test_xxxxx`
     - **Secret key**: `sk_test_xxxxx`

3. **Update .env file:**
   ```env
   STRIPE_PUBLISHABLE_KEY=pk_test_your_actual_key_here
   STRIPE_SECRET_KEY=sk_test_your_actual_key_here
   STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
   ```

### **2. Fix Dependencies (if needed)**

If you encounter numpy/plotly compatibility issues:

```bash
# Option 1: Update packages
pip install --upgrade numpy plotly

# Option 2: Downgrade numpy if needed
pip install "numpy<2.0.0"

# Option 3: Skip plotly views temporarily by commenting out in views.py
```

### **3. Database Setup**

```bash
# Create and apply migrations
python manage.py makemigrations payments
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser
```

### **4. Run Basic Tests**

```bash
# Run the simple test script
python test_stripe_simple.py

# Expected successful output:
# ✅ Stripe configuration found
# ✅ PaymentMethod already exists  
# ✅ Connected to Stripe account: acct_xxxxx
# ✅ Payment intent created: pi_xxxxx
# ✅ Connection token created successfully
# ✅ Confirmed test mode (livemode=False)
```

### **5. Run Django Test Suite**

```bash
# Run payment app tests
python manage.py test payments.tests

# Run with verbose output
python manage.py test payments.tests -v 2

# Run specific test class
python manage.py test payments.tests.test_models.PaymentMethodModelTest
```

## 🔍 **Manual Testing Scenarios**

### **A. Django Admin Interface**

1. **Access Admin:**
   ```bash
   python manage.py runserver
   # Go to http://localhost:8000/admin/
   ```

2. **Test Payment Models:**
   - Create PaymentMethod entries
   - View PaymentTransaction records
   - Check PaymentWebhook logs

### **B. Django Shell Testing**

```python
python manage.py shell

# Test PaymentMethod
from payments.models import PaymentMethod
pm = PaymentMethod.objects.create(
    name='Test Visa',
    stripe_payment_method_type='card'
)
print(pm)

# Test direct Stripe API
import stripe
from django.conf import settings
stripe.api_key = settings.STRIPE_SECRET_KEY

# Create test payment intent
intent = stripe.PaymentIntent.create(
    amount=1000,  # $10.00
    currency='usd',
    payment_method_types=['card'],
)
print(f"Created: {intent.id}")
```

### **C. API Endpoint Testing (when implemented)**

```bash
# Test payment intent creation endpoint
curl -X POST http://localhost:8000/api/payments/create-intent/ \\
     -H "Content-Type: application/json" \\
     -d '{"amount": "10.00", "currency": "usd"}'

# Test connection token endpoint  
curl -X POST http://localhost:8000/api/payments/connection-token/
```

## 📋 **Test Scenarios with Stripe Test Cards**

Use these test card numbers for comprehensive testing:

### **Successful Payments:**
```
Visa: 4242424242424242
Mastercard: 5555555555554444
American Express: 378282246310005
```

### **Declined Payments:**
```
Insufficient funds: 4000000000009995
Stolen card: 4000000000009979
Processing error: 4000000000000119
```

### **3D Secure:**
```
Authentication required: 4000002760003184
Optional authentication: 4000002500003155
```

## 🛠 **Advanced Testing**

### **1. Webhook Testing**

```bash
# Install Stripe CLI
# https://stripe.com/docs/stripe-cli

# Login to your Stripe account
stripe login

# Forward webhooks to local development
stripe listen --forward-to localhost:8000/payments/webhooks/

# Trigger test events
stripe trigger payment_intent.succeeded
stripe trigger payment_intent.payment_failed
```

### **2. Terminal Testing (POS Hardware)**

```python
# Test terminal connection
from payments.services import StripePaymentService
service = StripePaymentService()

# Create connection token
token = service.create_connection_token()
print(f"Token: {token['secret']}")

# Use in POS terminal app with Stripe Terminal SDK
```

### **3. Load Testing**

```python
# Simple concurrent payment test
import concurrent.futures
import stripe
from django.conf import settings

def create_test_payment():
    stripe.api_key = settings.STRIPE_SECRET_KEY
    return stripe.PaymentIntent.create(
        amount=100,
        currency='usd',
        payment_method_types=['card']
    )

# Test 10 concurrent payments
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(create_test_payment) for _ in range(10)]
    results = [f.result() for f in futures]
    
print(f"Created {len(results)} payment intents")
```

## 📈 **Testing Checklist**

### **Pre-Production Testing**
- [ ] All unit tests passing
- [ ] Integration tests passing  
- [ ] Manual payment flow testing
- [ ] Refund processing testing
- [ ] Webhook event handling
- [ ] Error scenario testing
- [ ] Terminal connection testing
- [ ] Security validation

### **Performance Testing**
- [ ] Payment intent creation speed
- [ ] Concurrent payment handling
- [ ] Database query optimization
- [ ] Memory usage monitoring

### **Security Testing**
- [ ] API key protection
- [ ] Webhook signature verification
- [ ] Input validation
- [ ] SQL injection protection
- [ ] XSS protection

## 🐛 **Common Issues & Solutions**

### **1. "No API key provided"**
- **Cause**: Stripe API key not loaded from environment
- **Solution**: Check .env file and Django settings configuration

### **2. "Invalid webhook signature"**
- **Cause**: Webhook endpoint secret mismatch
- **Solution**: Update STRIPE_WEBHOOK_SECRET in .env

### **3. "Payment method types not supported"**
- **Cause**: Using unsupported payment method for region
- **Solution**: Check supported payment methods in Stripe dashboard

### **4. Database migration errors**
- **Cause**: Model changes not reflected in database
- **Solution**: Run `python manage.py makemigrations` and `python manage.py migrate`

## 📊 **Test Results Documentation**

### **Expected Test Output:**
```
🧪 Simple Stripe Integration Tests
========================================
✅ Stripe configuration found
✅ PaymentMethod already exists
✅ Connected to Stripe account: acct_1234567890
✅ Payment intent created: pi_1234567890
✅ Connection token created successfully
✅ Confirmed test mode (livemode=False)
========================================
📊 Test Results: 6 passed, 0 failed
🎉 All tests passed! Stripe integration is working.
```

## 🎯 **Next Steps After Testing**

1. **Implement Task 3**: Create Stripe service layer with proper error handling
2. **Implement Task 4**: Build payment views and API endpoints  
3. **Implement Task 5**: Set up webhook handlers
4. **Implement Task 6**: Create frontend payment UI
5. **Integration testing**: Connect with existing transaction system
6. **Production setup**: Configure live Stripe keys and production environment

This comprehensive testing approach ensures your Stripe integration is robust, secure, and ready for production use! 🚀
