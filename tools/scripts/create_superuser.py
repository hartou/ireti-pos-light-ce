import os
import sys
from pathlib import Path

# Ensure project root is on PYTHONPATH when running this script via path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.getenv('SETTINGS', 'onlineretailpos.settings.devlopement'))

try:
    import django
    django.setup()
    from django.contrib.auth import get_user_model
except Exception as e:
    print(f"Failed to initialize Django: {e}")
    sys.exit(1)

U = get_user_model()
u = os.environ.get('DJANGO_SUPERUSER_USERNAME')
e = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
p = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

print('Ensuring superuser (skips if vars not set) ...')
if u and p:
    if not U.objects.filter(username=u).exists():
        U.objects.create_superuser(u, e, p)
        print('Superuser created:', u)
    else:
        print('Superuser already exists:', u)
else:
    print('DJANGO_SUPERUSER_* not set; skipping superuser creation')
