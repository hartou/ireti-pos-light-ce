#!/usr/bin/env python3
"""
Legacy copy of test_stripe_direct
"""

...existing code...
#!/usr/bin/env python
"""
Legacy direct Stripe API Test
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import requests

project_root = Path(__file__).parent
load_dotenv(project_root / '.env')

stripe_secret = os.getenv('STRIPE_SECRET_KEY')
print("Legacy Stripe direct test placeholder - does not run by default")
