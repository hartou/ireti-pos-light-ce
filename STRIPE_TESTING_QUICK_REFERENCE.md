# Stripe Testing Quick Reference Card

## 🚀 Quick Start
```bash
# Login Credentials
URL: http://127.0.0.1:8000/
User: admin
Pass: admin123

# Alternative Login
User: testuser  
Pass: test123
```

## 💳 Essential Test Cards

### ✅ Success Cards
```
4242424242424242  (Visa - Success)
5555555555554444  (Mastercard - Success)
378282246310005   (Amex - Success)
```

### ❌ Decline Cards  
```
4000000000000002  (Generic decline)
4000000000009995  (Insufficient funds)
4000000000000069  (Expired card)
4000000000000127  (CVC failure)
```

### 📝 Card Details (use with any test card)
```
Expiry: 12/34 (any future date)
CVC: 123 (any 3 digits)
ZIP: 12345 (any postal code)
Name: Any name
```

## 🔍 Monitoring
- **Stripe Dashboard**: https://dashboard.stripe.com/test/payments
- **Django Admin**: http://127.0.0.1:8000/admin/
- **Logs**: Terminal output + /logs/payments.log

## ⚡ Testing Workflow
1. Login to system
2. Create transaction/cart
3. Select Stripe payment
4. Use test card numbers
5. Verify in Stripe dashboard
6. Check database records

---
*See STRIPE_SANDBOX_TESTING_GUIDE.md for complete documentation*
