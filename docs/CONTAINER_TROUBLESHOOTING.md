# 🐳 Container Troubleshooting Guide

## Container Not Starting Issues

### ❌ Error: "STRIPE_SECRET_KEY environment variable is required"

**Problem**: The container fails to start with this error message.

**Root Cause**: The Ireti POS Light CE application requires Stripe payment integration and validates that Stripe API keys are provided at startup.

**Solution**: Provide the required Stripe environment variables:

```bash
docker run -p 8000:8000 \
  -e STRIPE_SECRET_KEY=sk_test_your_actual_key \
  -e STRIPE_PUBLISHABLE_KEY=pk_test_your_actual_key \
  -e STRIPE_WEBHOOK_ENDPOINT_SECRET=whsec_your_webhook_secret \
  -e DJANGO_SUPERUSER_USERNAME=admin \
  -e DJANGO_SUPERUSER_PASSWORD=Admin123! \
  ghcr.io/hartou/ireti-pos-light-ce:latest
```

### 🔑 Getting Stripe Keys

1. **Test Keys (Development)**:
   - Go to <https://dashboard.stripe.com/test/apikeys>
   - Copy your "Publishable key" (starts with `pk_test_`)
   - Copy your "Secret key" (starts with `sk_test_`)

2. **Live Keys (Production)**:
   - Go to <https://dashboard.stripe.com/apikeys>
   - Copy your "Publishable key" (starts with `pk_live_`)
   - Copy your "Secret key" (starts with `sk_live_`)

### ⚠️ Key Format Requirements

The application validates Stripe key formats:

- **Secret Key**: Must start with `sk_test_` (test) or `sk_live_` (production)
- **Publishable Key**: Must start with `pk_test_` (test) or `pk_live_` (production)

**Invalid Examples**:
```bash
STRIPE_SECRET_KEY=sk_dummy  # ❌ Wrong format
STRIPE_PUBLISHABLE_KEY=pk_dummy  # ❌ Wrong format
```

**Valid Examples**:
```bash
STRIPE_SECRET_KEY=sk_test_51234567890abcdef...  # ✅ Correct test format
STRIPE_PUBLISHABLE_KEY=pk_test_51234567890abcdef...  # ✅ Correct test format
```

### 🧪 Testing Without Real Stripe Account

If you just want to test the container without a real Stripe account, you can use dummy keys with the correct format:

```bash
docker run -p 8000:8000 \
  -e STRIPE_SECRET_KEY=sk_test_dummy_key_for_testing_only \
  -e STRIPE_PUBLISHABLE_KEY=pk_test_dummy_key_for_testing_only \
  -e DJANGO_SUPERUSER_USERNAME=admin \
  -e DJANGO_SUPERUSER_PASSWORD=Admin123! \
  ghcr.io/hartou/ireti-pos-light-ce:latest
```

**Note**: Payment processing won't work with dummy keys, but the application will start and you can test other features.

### 🔧 Container Test Script

Use the included test script to validate the container:

```bash
# Run the comprehensive container test
./test-container.sh
```

This script will:
- Test that the container fails without Stripe keys (expected behavior)
- Test that the container starts with valid Stripe keys
- Verify the web interface is accessible

### 📋 All Required Environment Variables

| Variable | Required | Format | Description |
|----------|----------|---------|-------------|
| `STRIPE_SECRET_KEY` | ✅ Yes | `sk_test_*` or `sk_live_*` | Stripe API secret key |
| `STRIPE_PUBLISHABLE_KEY` | ✅ Yes | `pk_test_*` or `pk_live_*` | Stripe API publishable key |
| `STRIPE_WEBHOOK_ENDPOINT_SECRET` | ⚠️ Optional | `whsec_*` | Stripe webhook secret |
| `DJANGO_SUPERUSER_USERNAME` | ⚠️ Optional | Any string | Admin username |
| `DJANGO_SUPERUSER_PASSWORD` | ⚠️ Optional | Any string | Admin password |
| `DJANGO_SUPERUSER_EMAIL` | ⚠️ Optional | Email format | Admin email |

### 🚀 Quick Start Commands

**Development/Testing**:
```bash
# With test Stripe keys
docker run -p 8000:8000 \
  -e STRIPE_SECRET_KEY=sk_test_your_key \
  -e STRIPE_PUBLISHABLE_KEY=pk_test_your_key \
  -e DJANGO_SUPERUSER_USERNAME=admin \
  -e DJANGO_SUPERUSER_PASSWORD=Admin123! \
  ghcr.io/hartou/ireti-pos-light-ce:latest
```

**Production**:
```bash
# With live Stripe keys
docker run -p 8000:8000 \
  -e STRIPE_SECRET_KEY=sk_live_your_key \
  -e STRIPE_PUBLISHABLE_KEY=pk_live_your_key \
  -e STRIPE_WEBHOOK_ENDPOINT_SECRET=whsec_your_secret \
  -e DJANGO_SUPERUSER_USERNAME=admin \
  -e DJANGO_SUPERUSER_PASSWORD=YourSecurePassword \
  -e DJANGO_SUPERUSER_EMAIL=admin@yourcompany.com \
  ghcr.io/hartou/ireti-pos-light-ce:latest
```

### 📞 Still Having Issues?

1. Check the container logs: `docker logs <container_name>`
2. Verify your Stripe keys are valid and have the correct format
3. Ensure no extra spaces or quotes in environment variables
4. Check if port 8000 is already in use: `lsof -i :8000`
5. Try with different dummy test keys to isolate Stripe API issues

## Summary

**The container IS working correctly!** 

The "not working" issue is actually the container properly enforcing security by requiring valid Stripe API keys. This is the expected behavior for a POS system that handles payments.

Simply provide the required Stripe environment variables and the container will start successfully.