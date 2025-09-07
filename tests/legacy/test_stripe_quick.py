#!/usr/bin/env python
"""
Legacy copy of test_stripe_quick
"""

...existing code...
#!/usr/bin/env python
"""
Legacy quick stripe test (simplified).
"""
import os
import sys
import django
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iretilightpos.settings.devlopement')
os.environ['DJANGO_TESTING'] = '1'

try:
    django.setup()
except Exception:
    pass

print('Legacy quick stripe test placeholder')
