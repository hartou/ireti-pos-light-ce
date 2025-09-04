#!/usr/bin/env python3
"""
Legacy copy of test_authenticated_links
"""

...existing code...
#!/usr/bin/env python
"""
Test authenticated access to important URLs (moved to tests/legacy for cleanup).
"""
import os
import django
from django.test import Client
from django.contrib.auth.models import User
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onlineretailpos.settings.devlopement')
django.setup()

def test_authenticated_access():
    """Test all broken links with an authenticated user."""
    
    client = Client()
    
    try:
        user = User.objects.get(username='testuser')
    except User.DoesNotExist:
        user = User.objects.create_superuser('testuser', 'test@example.com', 'testpass123')
    
    login_success = client.login(username='testuser', password='testpass123')
    if not login_success:
        print("❌ Failed to login test user")
        return
    
    print("✅ Successfully logged in test user")
    
    urls_to_test = [
        '/dashboard_sales/',
        '/dashboard_department/',
        '/dashboard_products/',
        '/transaction/',
        '/register/product_lookup/',
        '/inventory/',
        '/staff_portal/',
        '/staff_portal/auth/group/',
        '/retail_display/',
    ]
    
    for url in urls_to_test:
        try:
            response = client.get(url)
            status = response.status_code
            
            if status == 200:
                print(f"✅ {url}: {status} (OK)")
            elif status == 302:
                redirect_url = response.get('Location', 'Unknown')
                print(f"⚠️  {url}: {status} (Redirect to {redirect_url})")
            elif status == 404:
                print(f"❌ {url}: {status} (Not Found)")
            elif status == 500:
                print(f"❌ {url}: {status} (Server Error)")
            else:
                print(f"⚠️  {url}: {status}")
        except Exception as e:
            print(f"❌ {url}: Exception - {str(e)}")

if __name__ == '__main__':
    test_authenticated_access()
