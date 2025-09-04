#!/usr/bin/env python
"""
Stripe Configuration Test Script for Ireti POS
This script validates that Stripe is properly configured for sandbox testing.
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.insert(0, '/workspaces/ireti-pos-light')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onlineretailpos.settings.devlopement')
django.setup()

import stripe
from django.conf import settings
from decimal import Decimal

def test_stripe_config():
    """Test Stripe configuration and basic functionality."""
    
    print("🧪 Testing Stripe Configuration for Ireti POS")
    print("=" * 50)
    
    # Check environment variables
    print("1. Checking environment variables...")
    stripe_keys = {
        'STRIPE_PUBLISHABLE_KEY': getattr(settings, 'STRIPE_PUBLISHABLE_KEY', None),
        'STRIPE_SECRET_KEY': getattr(settings, 'STRIPE_SECRET_KEY', None),
    }
    
    for key, value in stripe_keys.items():
        if value:
            print(f"   ✅ {key}: {value[:20]}...")
        else:
            print(f"   ❌ {key}: Not configured")
            return False
    
    # Validate key formats
    print("\n2. Validating key formats...")
    if not settings.STRIPE_SECRET_KEY.startswith('sk_test_'):
        print("   ❌ STRIPE_SECRET_KEY should start with 'sk_test_' for testing")
        return False
    else:
        print("   ✅ Secret key is a test key")
    
    if not settings.STRIPE_PUBLISHABLE_KEY.startswith('pk_test_'):
        print("   ❌ STRIPE_PUBLISHABLE_KEY should start with 'pk_test_' for testing")
        return False
    else:
        print("   ✅ Publishable key is a test key")
    
    # Set Stripe API key
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    # Test API connection
    print("\n3. Testing Stripe API connection...")
    try:
        account = stripe.Account.retrieve()
        print(f"   ✅ Successfully connected to Stripe API")
        print(f"   📧 Account email: {account.email}")
        print(f"   🏪 Business type: {account.business_type}")
        print(f"   🌍 Country: {account.country}")
    except stripe.error.AuthenticationError as e:
        print(f"   ❌ Authentication failed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ API connection failed: {e}")
        return False
    
    # Test creating a payment intent
    print("\n4. Testing payment intent creation...")
    try:
        intent = stripe.PaymentIntent.create(
            amount=1000,  # $10.00 in cents
            currency='usd',
            metadata={
                'test': 'true',
                'pos_system': 'ireti'
            }
        )
        print(f"   ✅ Payment intent created successfully")
        print(f"   💰 Amount: ${intent.amount / 100:.2f} {intent.currency.upper()}")
        print(f"   🆔 Payment Intent ID: {intent.id}")
        print(f"   📊 Status: {intent.status}")
        
        # Cancel the test payment intent
        stripe.PaymentIntent.cancel(intent.id)
        print(f"   🚫 Test payment intent cancelled")
        
    except Exception as e:
        print(f"   ❌ Payment intent creation failed: {e}")
        return False
    
    print("\n5. Testing common Stripe test cards...")
    test_cards = [
        {'number': '4242424242424242', 'brand': 'Visa', 'description': 'Successful payment'},
        {'number': '4000000000000002', 'brand': 'Visa', 'description': 'Declined card'},
        {'number': '4000000000009995', 'brand': 'Visa', 'description': 'Insufficient funds'},
        {'number': '4000000000000069', 'brand': 'Visa', 'description': 'Expired card'},
    ]
    
    for card in test_cards:
        print(f"   💳 {card['number']}: {card['brand']} - {card['description']}")
    
    print("\n✅ Stripe configuration test completed successfully!")
    print("\n🎯 Ready for testing with the following test cards:")
    print("   • 4242424242424242 (Visa - Success)")
    print("   • 5555555555554444 (Mastercard - Success)")  
    print("   • 4000000000000002 (Visa - Declined)")
    print("   • 4000000000009995 (Visa - Insufficient funds)")
    
    return True

if __name__ == '__main__':
    success = test_stripe_config()
    if success:
        print(f"\n🚀 Your Ireti POS system is ready for Stripe sandbox testing!")
    else:
        print(f"\n❌ Configuration issues found. Please fix the errors above.")
        sys.exit(1)
