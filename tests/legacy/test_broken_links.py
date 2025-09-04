#!/usr/bin/env python3
"""
Legacy copy of test_broken_links
"""

...existing code...
#!/usr/bin/env python3
"""
Test suite for broken links (moved to tests/legacy for repo cleanup).
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onlineretailpos.settings.devlopement')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

def test_broken_links():
    """Test all broken links from the user stories."""
    
    test_cases = [
        ('/dashboard_sales/', 'BL-001', 'Sales Dashboard'),
        ('/dashboard_department/', 'BL-002', 'Department Dashboard'),
        ('/dashboard_products/', 'BL-003', 'Products Dashboard'),
        ('/transaction/', 'BL-004', 'Transactions list'),
        ('/register/product_lookup/', 'BL-005', 'Product lookup'),
        ('/inventory/', 'BL-006', 'Add Inventory'),
        ('/staff_portal/', 'BL-007', 'Admin portal'),
        ('/retail_display/', 'BL-009', 'Customer Display')
    ]
    
    client = Client()
    
    print("=== TESTING UNAUTHENTICATED ACCESS ===")
    print("Expected: All should return 302 (redirect to login)\n")
    
    all_unauthenticated_pass = True
    for url, story_id, description in test_cases:
        try:
            response = client.get(url, follow=False)
            status = response.status_code
            
            if status == 302:
                location = response.get('Location', '')
                if '/user/login/' in location:
                    print(f"✅ {story_id}: {url} → 302 (redirects to login)")
                else:
                    print(f"❌ {story_id}: {url} → 302 but wrong redirect: {location}")
                    all_unauthenticated_pass = False
            else:
                print(f"❌ {story_id}: {url} → {status} (expected 302)")
                all_unauthenticated_pass = False
                
        except Exception as e:
            print(f"❌ {story_id}: {url} → ERROR: {e}")
            all_unauthenticated_pass = False
    
    print(f"\n=== TESTING AUTHENTICATED ACCESS ===")
    print("Expected: All should return 200 (or 302 for admin portal)\n")
    
    User = get_user_model()
    try:
        admin_user = User.objects.get(username='admin')
        client.force_login(admin_user)
        print("✅ Logged in as admin user\n")
    except User.DoesNotExist:
        print("❌ Admin user not found - cannot test authenticated access")
        return False
    
    all_authenticated_pass = True
    for url, story_id, description in test_cases:
        try:
            response = client.get(url, follow=False)
            status = response.status_code
            
            if story_id == 'BL-007' and status in [302, 200]:
                print(f"✅ {story_id}: {url} → {status} (admin portal)")
            elif status == 200:
                print(f"✅ {story_id}: {url} → 200 ({description})")
            else:
                print(f"❌ {story_id}: {url} → {status} (expected 200)")
                all_authenticated_pass = False
                
        except Exception as e:
            print(f"❌ {story_id}: {url} → ERROR: {e}")
            all_authenticated_pass = False
    
    print(f"\n=== SUMMARY ===")
    if all_unauthenticated_pass and all_authenticated_pass:
        print("✅ All broken links are working correctly!")
        return True
    else:
        print("❌ Some links need fixing before marking as completed")
        return False

if __name__ == '__main__':
    test_broken_links()