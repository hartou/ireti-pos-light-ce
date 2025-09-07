#!/usr/bin/env python3
"""
PWA-015: Lighthouse PWA Audit Validation Script
Validates PWA requirements without needing to run Lighthouse
"""

import os
import json
import re
from pathlib import Path

def check_manifest():
    """Check PWA manifest configuration"""
    print("📋 Checking PWA Manifest...")
    
    manifest_path = Path("onlineretailpos/static/manifest.webmanifest")
    if not manifest_path.exists():
        print("❌ Manifest file not found")
        return False
    
    try:
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        required_fields = ['name', 'short_name', 'start_url', 'display', 'icons']
        missing_fields = [field for field in required_fields if field not in manifest]
        
        if missing_fields:
            print(f"❌ Missing required manifest fields: {missing_fields}")
            return False
        
        # Check icons
        if not manifest.get('icons') or len(manifest['icons']) < 2:
            print("❌ Manifest needs at least 2 icon sizes (192x192 and 512x512)")
            return False
        
        # Check icon files exist
        for icon in manifest['icons']:
            # Remove leading slash and prepend onlineretailpos/static
            icon_path = icon['src'].lstrip('/')
            full_icon_path = Path(f"onlineretailpos/{icon_path}")
            if not full_icon_path.exists():
                print(f"❌ Icon file not found: {icon['src']} (looked for {full_icon_path})")
                return False
        
        print("✅ Manifest configuration valid")
        return True
        
    except json.JSONDecodeError:
        print("❌ Manifest is not valid JSON")
        return False

def check_service_worker():
    """Check service worker implementation"""
    print("\n🔧 Checking Service Worker...")
    
    sw_path = Path("onlineretailpos/static/js/sw.js")
    if not sw_path.exists():
        print("❌ Service worker file not found")
        return False
    
    with open(sw_path, 'r') as f:
        sw_content = f.read()
    
    # Check for required service worker features
    required_features = [
        ('install event', r'addEventListener\([\'"]install[\'"]'),
        ('activate event', r'addEventListener\([\'"]activate[\'"]'),
        ('fetch event', r'addEventListener\([\'"]fetch[\'"]'),
        ('cache API', r'caches\.(open|match)'),
        ('offline fallback', r'/offline')
    ]
    
    for feature_name, pattern in required_features:
        if not re.search(pattern, sw_content):
            print(f"❌ Service worker missing: {feature_name}")
            return False
    
    print("✅ Service worker implementation valid")
    return True

def check_base_template():
    """Check base template for PWA requirements"""
    print("\n📄 Checking Base Template...")
    
    template_path = Path("onlineretailpos/templates/base.html")
    if not template_path.exists():
        print("❌ Base template not found")
        return False
    
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    # Check for required PWA elements
    required_elements = [
        ('manifest link', r'<link[^>]*rel=[\'"]manifest[\'"]'),
        ('theme color', r'<meta[^>]*name=[\'"]theme-color[\'"]'),
        ('viewport meta', r'<meta[^>]*name=[\'"]viewport[\'"]'),
        ('service worker registration', r'navigator\.serviceWorker\.register'),
        ('iOS PWA support', r'apple-mobile-web-app'),
        ('network status indicator', r'network-indicator'),
        ('update button', r'pwa-update-btn')
    ]
    
    for element_name, pattern in required_elements:
        if not re.search(pattern, template_content, re.IGNORECASE):
            print(f"❌ Template missing: {element_name}")
            return False
    
    print("✅ Base template PWA elements valid")
    return True

def check_security_settings():
    """Check Django security settings for PWA"""
    print("\n🔒 Checking Security Settings...")
    
    settings_path = Path("onlineretailpos/settings/base.py")
    if not settings_path.exists():
        print("❌ Settings file not found")
        return False
    
    with open(settings_path, 'r') as f:
        settings_content = f.read()
    
    # Check for PWA security configurations
    required_settings = [
        ('CSP configuration', r'CSP_'),
        ('Secure headers', r'SECURE_'),
        ('Service worker headers', r'SERVICE_WORKER_ALLOWED')
    ]
    
    for setting_name, pattern in required_settings:
        if not re.search(pattern, settings_content):
            print(f"❌ Security settings missing: {setting_name}")
            return False
    
    print("✅ Security settings configured")
    return True

def check_offline_page():
    """Check for offline page"""
    print("\n📴 Checking Offline Support...")
    
    # Check if offline template exists (common locations)
    offline_templates = [
        "onlineretailpos/templates/offline.html",
        "onlineretailpos/templates/registration/offline.html"
    ]
    
    offline_exists = any(Path(template).exists() for template in offline_templates)
    
    if not offline_exists:
        print("⚠️  Offline template not found (optional but recommended)")
        return True  # Not required but recommended
    
    print("✅ Offline support configured")
    return True

def check_static_files():
    """Check static file configuration"""
    print("\n📁 Checking Static Files...")
    
    # Check critical static files exist
    critical_files = [
        "onlineretailpos/static/manifest.webmanifest",
        "onlineretailpos/static/js/sw.js",
        "onlineretailpos/static/img/icons/icon-192x192.png",
        "onlineretailpos/static/img/icons/icon-512x512.png"
    ]
    
    missing_files = [f for f in critical_files if not Path(f).exists()]
    
    if missing_files:
        print(f"❌ Missing critical static files: {missing_files}")
        return False
    
    print("✅ Critical static files present")
    return True

def main():
    """Run PWA audit validation"""
    print("🚀 PWA-015: Lighthouse PWA Audit Validation")
    print("=" * 50)
    
    checks = [
        check_static_files,
        check_manifest,
        check_service_worker,
        check_base_template,
        check_security_settings,
        check_offline_page
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"❌ Error during check: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 PWA Audit Summary")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    score = (passed / total) * 100
    
    print(f"✅ Passed: {passed}/{total} checks")
    print(f"📈 PWA Readiness Score: {score:.1f}%")
    
    if score >= 90:
        print("🎉 PWA is ready for production!")
        print("\n💡 Next Steps:")
        print("1. Deploy to HTTPS server")
        print("2. Run Lighthouse audit: npx lighthouse <url> --only-categories=pwa")
        print("3. Test PWA installation on target devices")
    else:
        print("⚠️  PWA needs more work before production")
        print("\n🔧 Focus on failing checks above")
    
    return score >= 90

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)