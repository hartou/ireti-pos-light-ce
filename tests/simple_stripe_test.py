#!/usr/bin/env python
"""
Simple Stripe API Test
"""

import stripe
import os
from decimal import Decimal

# Initialize Stripe with your test secret key
stripe.api_key = 'sk_test_YOUR_TEST_SECRET_KEY_HERE'

print("🧪 Simple Stripe API Test")
print("=" * 30)

try:
    # Test basic API call
    print("Testing payment intent creation...")
    intent = stripe.PaymentIntent.create(
        amount=1000,  # $10.00 in cents
        currency='usd',
        automatic_payment_methods={'enabled': True},
        metadata={
            'test': 'true',
            'source': 'ireti_pos'
        }
    )
    
    print(f"✅ Success!")
    print(f"   Payment Intent ID: {intent.id}")
    print(f"   Amount: ${intent.amount / 100:.2f}")
    print(f"   Status: {intent.status}")
    print(f"   Client Secret: {intent.client_secret[:20]}...")
    
    # Cancel the test payment
    stripe.PaymentIntent.cancel(intent.id)
    print(f"   🚫 Test payment cancelled")
    
    print("\n✅ Stripe API is working correctly!")
    
except stripe.error.AuthenticationError as e:
    print(f"❌ Authentication Error: {e}")
except stripe.error.APIConnectionError as e:
    print(f"❌ API Connection Error: {e}")
except stripe.error.StripeError as e:
    print(f"❌ Stripe Error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
