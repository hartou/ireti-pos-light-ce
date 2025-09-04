#!/usr/bin/env python
"""
Validate Stripe configuration setup without requiring Django installation.
This script checks the syntax and structure of our configuration changes.
"""

import os
import re

def check_requirements_txt():
    """Check if stripe is properly added to requirements.txt"""
    with open('requirements.txt', 'r') as f:
        content = f.read()
    
    if 'stripe==' in content:
        print("✅ Stripe dependency found in requirements.txt")
        # Extract version
        match = re.search(r'stripe==([^\n]+)', content)
        if match:
            print(f"   Version: {match.group(1)}")
        return True
    else:
        print("❌ Stripe dependency not found in requirements.txt")
        return False

def check_env_example():
    """Check if Stripe variables are in .env.example"""
    with open('.env.example', 'r') as f:
        content = f.read()
    
    stripe_vars = [
        'STRIPE_PUBLISHABLE_KEY',
        'STRIPE_SECRET_KEY', 
        'STRIPE_WEBHOOK_ENDPOINT_SECRET'
    ]
    
    found_vars = []
    for var in stripe_vars:
        if var in content:
            found_vars.append(var)
            print(f"✅ {var} found in .env.example")
        else:
            print(f"❌ {var} not found in .env.example")
    
    return len(found_vars) == len(stripe_vars)

def check_docker_compose():
    """Check if Stripe variables are in docker-compose.yml"""
    with open('docker-compose.yml', 'r') as f:
        content = f.read()
    
    stripe_vars = [
        'STRIPE_PUBLISHABLE_KEY',
        'STRIPE_SECRET_KEY',
        'STRIPE_WEBHOOK_ENDPOINT_SECRET'
    ]
    
    found_vars = []
    for var in stripe_vars:
        if f'{var}:' in content:
            found_vars.append(var)
            print(f"✅ {var} found in docker-compose.yml")
        else:
            print(f"❌ {var} not found in docker-compose.yml")
    
    return len(found_vars) == len(stripe_vars)

def check_settings_syntax():
    """Basic syntax check for settings/base.py additions"""
    try:
        with open('onlineretailpos/settings/base.py', 'r') as f:
            content = f.read()
        
        # Check for Stripe configuration section
        if 'STRIPE_PUBLISHABLE_KEY' in content and 'STRIPE_SECRET_KEY' in content:
            print("✅ Stripe configuration found in settings/base.py")
        else:
            print("❌ Stripe configuration not found in settings/base.py")
            return False
        
        # Basic Python syntax check
        compile(content, 'settings/base.py', 'exec')
        print("✅ Settings file syntax is valid")
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax error in settings/base.py: {e}")
        return False
    except Exception as e:
        print(f"❌ Error checking settings/base.py: {e}")
        return False

def main():
    print("🔧 Validating Stripe Task 1: Setup Configuration")
    print("=" * 50)
    
    checks = [
        check_requirements_txt(),
        check_env_example(), 
        check_docker_compose(),
        check_settings_syntax()
    ]
    
    passed = sum(checks)
    total = len(checks)
    
    print("\n" + "=" * 50)
    print(f"📊 Validation Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All validation checks passed! Ready for next task.")
        return 0
    else:
        print("⚠️  Some validation checks failed. Please review above.")
        return 1

if __name__ == "__main__":
    exit(main())
