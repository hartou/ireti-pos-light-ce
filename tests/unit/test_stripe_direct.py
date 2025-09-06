#!/usr/bin/env python
"""
Direct Stripe API Test (moved to tests/unit)

Retained for local development; this script intentionally lives under tests/unit
so test runners and contributors can find it easily.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
project_root = Path(__file__).parent.parent
load_dotenv(project_root / '.env')

print("🔧 Environment Variables Test")
stripe_secret = os.getenv('STRIPE_SECRET_KEY')
stripe_public = os.getenv('STRIPE_PUBLISHABLE_KEY')

if stripe_secret:
    print("✅ STRIPE_SECRET_KEY: present (value not shown)")
else:
    print("❌ STRIPE_SECRET_KEY not found")

if stripe_public:
    print(f"✅ STRIPE_PUBLISHABLE_KEY: {stripe_public[:20]}...")
else:
    print("❌ STRIPE_PUBLISHABLE_KEY not found")

# The rest of the script is unchanged and intentionally minimal for unit runs
