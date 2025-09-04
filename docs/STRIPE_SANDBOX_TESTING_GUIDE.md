# Ireti POS - Stripe Sandbox Testing Guide

**Version**: 1.0  
**Date**: September 2, 2025  
**Project**: Ireti POS Light - Stripe Payment Integration  
**Branch**: feature/stripe-payments-integration  

---

## 📋 Overview

This document provides a complete guide for testing the Ireti POS system with Stripe's sandbox environment. The integration has been fully implemented and validated, allowing you to safely test payment processing without real money transactions.

## ✅ Pre-Testing Setup Verification

### System Requirements Met
- ✅ Django 4.1.13 with Stripe payment integration
- ✅ Stripe Python SDK v11.1.0 (updated from v7.8.0)
- ✅ Test API keys configured and validated
- ✅ Database migrations completed
- ✅ Superuser account created
- ✅ Development server ready

### Environment Configuration
```bash
# Stripe Test Configuration
STRIPE_PUBLISHABLE_KEY=pk_test_51QvwFMPCHcLCM4BidnNhQWFpRC2NPI7GmLhHLBOOaGpWcRbMBGcXkyoUboLwPeWuPCB26O9rKbvQrvKXv2FT3sse00wwIEnnY3
STRIPE_SECRET_KEY=sk_test_YOUR_TEST_SECRET_KEY_HERE
STRIPE_CURRENCY=USD
STRIPE_MINIMUM_CHARGE=50
```

### Access Credentials
- **System URL**: http://127.0.0.1:8000/
- **Admin Username**: admin
- **Admin Email**: admin@example.com
- **Admin Password**: admin123

**Alternative Login:**
- **Username**: testuser
- **Email**: test@example.com
- **Password**: test123

---

## 🧪 Stripe Test Cards Reference

### ✅ Successful Payment Cards

| Card Number | Brand | Type | Expected Result |
|------------|-------|------|-----------------|
| `4242424242424242` | Visa | Standard | ✅ Payment succeeds |
| `5555555555554444` | Mastercard | Standard | ✅ Payment succeeds |
| `378282246310005` | American Express | Standard | ✅ Payment succeeds |
| `6011111111111117` | Discover | Standard | ✅ Payment succeeds |

### ❌ Declined Payment Cards

| Card Number | Brand | Decline Reason | Expected Result |
|------------|-------|----------------|-----------------|
| `4000000000000002` | Visa | Generic decline | ❌ Card declined |
| `4000000000009995` | Visa | Insufficient funds | ❌ Insufficient funds |
| `4000000000000069` | Visa | Expired card | ❌ Expired card |
| `4000000000000127` | Visa | Incorrect CVC | ❌ CVC check fails |
| `4000000000000119` | Visa | Processing error | ❌ Processing error |

### 🔧 Special Scenario Cards

| Card Number | Brand | Scenario | Expected Result |
|------------|-------|----------|-----------------|
| `4000000000000341` | Visa | Requires authentication | 🔐 3D Secure challenge |
| `4000002500003155` | Visa | International card | 🌍 International processing |
| `4000000000006975` | Visa | Disputed charge | ⚠️ Dispute potential |

### 📝 Test Card Usage Notes
- **Expiration Date**: Use any future date (e.g., 12/34, 06/28)
- **CVC Code**: Use any 3-digit code (e.g., 123, 456)
- **ZIP/Postal Code**: Use any valid code (e.g., 12345, 90210)
- **Cardholder Name**: Use any name

---

## 🚀 Step-by-Step Testing Procedure

### Phase 1: System Access & Login

1. **Start Development Server** (if not running)
   ```bash
   cd /workspaces/ireti-pos-light
   export STRIPE_SECRET_KEY='sk_test_YOUR_TEST_SECRET_KEY_HERE'
   export STRIPE_PUBLISHABLE_KEY='pk_test_51QvwFMPCHcLCM4BidnNhQWFpRC2NPI7GmLhHLBOOaGpWcRbMBGcXkyoUboLwPeWuPCB26O9rKbvQrvKXv2FT3sse00wwIEnnY3'
   python manage.py runserver 0.0.0.0:8000
   ```

2. **Access the Application**
   - Navigate to: http://127.0.0.1:8000/
   - Expected: Redirect to login page

3. **Login as Administrator**
   - Username: `admin`
   - Password: `Admin123!`
   - Expected: Successful login to dashboard

### Phase 2: Basic Payment Flow Testing

4. **Navigate to POS Interface**
   - Access the point-of-sale transaction interface
   - Expected: POS system loads with inventory items

5. **Create Test Transaction**
   - Add items to cart/transaction
   - Select "Stripe" as payment method
   - Expected: Stripe payment form renders

6. **Test Successful Payment**
   - Use card: `4242424242424242`
   - Expiry: `12/34`
   - CVC: `123`
   - ZIP: `12345`
   - Expected: Payment processes successfully

### Phase 3: Error Handling Testing

7. **Test Declined Card**
   - Use card: `4000000000000002`
   - Expected: Clear error message displayed

8. **Test Insufficient Funds**
   - Use card: `4000000000009995`
   - Expected: Specific "insufficient funds" error

9. **Test Invalid CVC**
   - Use card: `4000000000000127`
   - Expected: CVC validation error

### Phase 4: Advanced Scenarios

10. **Test Authentication Required**
    - Use card: `4000000000000341`
    - Expected: 3D Secure authentication flow

11. **Test Different Payment Amounts**
    - Test minimum charge ($0.50)
    - Test various amounts ($1, $10, $100)
    - Expected: All amounts process correctly

---

## 📊 Verification Checklist

### ✅ Payment Processing
- [ ] Payment intent created successfully
- [ ] Stripe Elements UI renders correctly
- [ ] Card input validation works
- [ ] Payment confirmation received
- [ ] Transaction recorded in database
- [ ] Receipt/confirmation displayed

### ✅ Error Handling
- [ ] Declined cards show appropriate errors
- [ ] Network errors handled gracefully
- [ ] Invalid input prevented/corrected
- [ ] User-friendly error messages displayed
- [ ] System remains stable after errors

### ✅ Security Compliance
- [ ] No card data stored locally
- [ ] HTTPS enforced for payment pages
- [ ] Sensitive data properly logged/redacted
- [ ] PCI DSS compliance maintained

### ✅ Integration Points
- [ ] Transaction system integration
- [ ] Inventory updates after payment
- [ ] User session management
- [ ] Admin interface functions

---

## 🔍 Monitoring & Debugging

### Stripe Dashboard Monitoring
- **URL**: https://dashboard.stripe.com/test/payments
- **Monitor**: Payment intents, charges, disputes
- **Verify**: Transaction metadata and amounts

### Application Logs
```bash
# View payment logs
tail -f /workspaces/ireti-pos-light/logs/payments.log

# View Django debug output
# Check terminal running development server
```

### Database Verification
```bash
# Access Django admin
http://127.0.0.1:8000/admin/

# Check models:
# - payments.Payment
# - transaction.Transaction
# - payments.PaymentIntent
```

---

## 🐛 Troubleshooting Guide

### Common Issues & Solutions

**Issue**: "STRIPE_SECRET_KEY environment variable is required"
**Solution**: Ensure environment variables are exported before running server
```bash
export STRIPE_SECRET_KEY='sk_test_...'
export STRIPE_PUBLISHABLE_KEY='pk_test_...'
```

**Issue**: Payment form not rendering
**Solution**: Check browser console for JavaScript errors, verify Stripe.js loaded

**Issue**: "Invalid API key provided"
**Solution**: Verify test keys are correctly formatted and not live keys

**Issue**: Webhook signature verification fails
**Solution**: Update STRIPE_WEBHOOK_ENDPOINT_SECRET in environment

---

## 📈 Testing Scenarios Matrix

| Scenario | Test Case | Expected Result | Status |
|----------|-----------|-----------------|--------|
| **Happy Path** | Successful Visa payment | ✅ Payment completes | [ ] |
| **Happy Path** | Successful Mastercard | ✅ Payment completes | [ ] |
| **Error Handling** | Declined card | ❌ Clear error message | [ ] |
| **Error Handling** | Insufficient funds | ❌ Specific error shown | [ ] |
| **Error Handling** | Expired card | ❌ Expiry error shown | [ ] |
| **Security** | 3D Secure flow | 🔐 Authentication required | [ ] |
| **Edge Cases** | Minimum amount | ✅ $0.50 processes | [ ] |
| **Edge Cases** | Large amount | ✅ $999.99 processes | [ ] |
| **Integration** | Database recording | ✅ Transaction saved | [ ] |
| **Integration** | Admin interface | ✅ Payment visible | [ ] |

---

## 🎯 Success Criteria

### ✅ Testing Complete When:
1. All successful test cards process payments
2. All decline scenarios show appropriate errors
3. Payment data correctly stored in database
4. Admin interface shows transaction details
5. No JavaScript errors in browser console
6. All security validations pass
7. Stripe dashboard shows test transactions

### 📋 Final Validation
- [ ] End-to-end payment flow functional
- [ ] Error handling comprehensive
- [ ] Security compliance maintained
- [ ] Performance acceptable
- [ ] User experience optimized
- [ ] Documentation updated
- [ ] Ready for production deployment

---

## 📞 Support & Resources

### Stripe Resources
- **Test Cards**: https://stripe.com/docs/testing
- **Dashboard**: https://dashboard.stripe.com/test
- **API Docs**: https://stripe.com/docs/api
- **Webhooks**: https://stripe.com/docs/webhooks

### Project Resources
- **Repository**: hartou/ireti-pos-light
- **Branch**: feature/stripe-payments-integration
- **Documentation**: /workspaces/ireti-pos-light/docs/

---

**Document Status**: ✅ Ready for Testing  
**Last Updated**: September 2, 2025  
**Next Review**: After testing completion

*This document serves as the official testing guide for Stripe sandbox integration in the Ireti POS Light system.*
