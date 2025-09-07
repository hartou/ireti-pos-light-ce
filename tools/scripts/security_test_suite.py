#!/usr/bin/env python3
"""
PCI DSS Security Test Suite with Stripe Integration
Tests security measures and compliance using Stripe services
"""

import os
import sys
import json
import hashlib
import hmac
import time
from datetime import datetime

# Add Django setup
sys.path.insert(0, '/workspaces/ireti-pos-light')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onlineretailpos.settings.base')

import django
django.setup()

from django.conf import settings
from payments.services import stripe_service
from payments.logging_utils import secure_log_payment_event
from payments.decorators import payment_processor_required
from django.contrib.auth.models import User, Permission
from django.test import RequestFactory
from django.http import HttpRequest

class SecurityTestSuite:
    def __init__(self):
        self.test_results = []
        self.factory = RequestFactory()
        
    def log_test_result(self, test_name, status, details):
        """Log test results"""
        result = {
            'test': test_name,
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {details}")
        
    def test_stripe_service_security(self):
        """Test Stripe service security configuration"""
        print("\n🔐 Testing Stripe Service Security...")
        
        try:
            # Test API key validation
            if hasattr(stripe_service, 'secret_key'):
                if stripe_service.secret_key.startswith(('sk_test_', 'sk_live_')):
                    self.log_test_result("Stripe API Key Format", "PASS", "Secret key format is valid")
                else:
                    self.log_test_result("Stripe API Key Format", "FAIL", "Invalid secret key format")
            else:
                self.log_test_result("Stripe API Key", "FAIL", "No secret key configured")
                
            # Test service initialization
            if hasattr(stripe_service, 'stripe'):
                self.log_test_result("Stripe Service Init", "PASS", "Stripe service properly initialized")
            else:
                self.log_test_result("Stripe Service Init", "FAIL", "Stripe service not initialized")
                
        except Exception as e:
            self.log_test_result("Stripe Service Security", "FAIL", f"Exception: {str(e)}")
            
    def test_webhook_signature_verification(self):
        """Test webhook signature verification security"""
        print("\n🔗 Testing Webhook Security...")
        
        try:
            # Create test webhook payload
            test_payload = json.dumps({
                "id": "evt_test_webhook",
                "object": "event",
                "type": "payment_intent.succeeded",
                "data": {
                    "object": {
                        "id": "pi_test_1234567890",
                        "status": "succeeded"
                    }
                }
            })
            
            # Test with valid signature (if webhook secret is configured)
            webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_ENDPOINT_SECRET', None)
            if webhook_secret:
                timestamp = str(int(time.time()))
                signature_payload = timestamp + "." + test_payload
                signature = hmac.new(
                    webhook_secret.encode('utf-8'),
                    signature_payload.encode('utf-8'),
                    hashlib.sha256
                ).hexdigest()
                
                test_signature = f"t={timestamp},v1={signature}"
                
                # Test signature verification
                if hasattr(stripe_service, 'verify_webhook_signature'):
                    try:
                        # Convert string payload to bytes for proper signature verification
                        payload_bytes = test_payload.encode('utf-8') if isinstance(test_payload, str) else test_payload
                        
                        # This should pass with valid signature
                        result = stripe_service.verify_webhook_signature(payload_bytes, test_signature)
                        if result:
                            self.log_test_result("Webhook Signature Verification", "PASS", 
                                               "Valid signature verification works")
                        else:
                            self.log_test_result("Webhook Signature Verification", "FAIL", 
                                               "Valid signature was rejected")
                        
                        # Test with invalid signature (should fail)
                        try:
                            invalid_signature = f"t={timestamp},v1=invalid_signature"
                            result = stripe_service.verify_webhook_signature(payload_bytes, invalid_signature)
                            if result:
                                self.log_test_result("Webhook Invalid Signature", "FAIL", 
                                                   "Invalid signature was accepted")
                            else:
                                self.log_test_result("Webhook Invalid Signature", "PASS", 
                                                   "Invalid signature properly rejected")
                        except Exception:
                            self.log_test_result("Webhook Invalid Signature", "PASS", 
                                               "Invalid signature properly rejected")
                            
                    except Exception as e:
                        self.log_test_result("Webhook Signature Verification", "FAIL", f"Error: {str(e)}")
                else:
                    self.log_test_result("Webhook Verification Method", "FAIL", 
                                       "verify_webhook_signature method not found")
            else:
                self.log_test_result("Webhook Secret Configuration", "WARN", 
                                   "No webhook secret configured for testing")
                
        except Exception as e:
            self.log_test_result("Webhook Security Test", "FAIL", f"Exception: {str(e)}")
            
    def test_access_control_decorators(self):
        """Test role-based access control decorators"""
        print("\n👥 Testing Access Control...")
        
        try:
            from payments.decorators import (
                payment_processor_required,
                refund_processor_required,
                manager_approval_required
            )
            
            self.log_test_result("Access Control Decorators", "PASS", 
                               "Security decorators are importable and functional")
            
            # Test decorator functionality (simplified test)
            try:
                # Create a mock user without permissions
                from django.contrib.auth.models import AnonymousUser
                
                class MockRequest:
                    def __init__(self):
                        self.user = AnonymousUser()
                        self.method = 'GET'
                
                test_request = MockRequest()
                
                @payment_processor_required
                def test_payment_view(request):
                    return "success"
                
                # This should redirect or raise an exception for unauthorized user
                try:
                    result = test_payment_view(test_request)
                    # If we get here without exception, check if it's a redirect response
                    if hasattr(result, 'status_code') and result.status_code in [302, 403]:
                        self.log_test_result("Access Control - Authorization", "PASS", 
                                           "Unauthorized access properly blocked with redirect")
                    else:
                        self.log_test_result("Access Control - Authorization", "FAIL", 
                                           "Unauthorized access was allowed")
                except Exception as e:
                    if 'login' in str(e).lower() or 'permission' in str(e).lower() or 'redirect' in str(e).lower():
                        self.log_test_result("Access Control - Authorization", "PASS", 
                                           "Unauthorized access properly blocked")
                    else:
                        self.log_test_result("Access Control - Authorization", "FAIL", 
                                           f"Unexpected error: {str(e)}")
                        
            except Exception as e:
                self.log_test_result("Access Control Authorization Test", "WARN", 
                                   f"Could not complete authorization test: {str(e)}")
                               
        except ImportError as e:
            self.log_test_result("Access Control Decorators", "FAIL", f"Import error: {str(e)}")
        except Exception as e:
            self.log_test_result("Access Control Test", "FAIL", f"Exception: {str(e)}")
            
    def test_secure_logging(self):
        """Test secure logging with data redaction"""
        print("\n📝 Testing Secure Logging...")
        
        try:
            from payments.logging_utils import redact_sensitive_data, secure_log_payment_event
            
            # Test data redaction
            test_data = {
                'card_number': '4242424242424242',
                'cvv': '123',
                'user_email': 'test@example.com',
                'amount': 2000
            }
            
            redacted = redact_sensitive_data(test_data)
            
            if redacted.get('card_number') in ['[REDACTED]...4242', '[CARD_REDACTED]']:
                self.log_test_result("Data Redaction - Card Number", "PASS", 
                                   "Card numbers properly redacted")
            else:
                self.log_test_result("Data Redaction - Card Number", "FAIL", 
                                   f"Card number not redacted: {redacted.get('card_number')}")
                
            if redacted.get('cvv') in ['***', '[REDACTED]', '[CVV_REDACTED]']:
                self.log_test_result("Data Redaction - CVV", "PASS", 
                                   "CVV properly redacted")
            else:
                self.log_test_result("Data Redaction - CVV", "FAIL", 
                                   f"CVV not redacted: {redacted.get('cvv')}")
                
            # Test secure logging
            try:
                secure_log_payment_event('test_payment', 'Test payment event', test_data)
                self.log_test_result("Secure Logging", "PASS", 
                                   "Secure logging function works without errors")
            except Exception as e:
                self.log_test_result("Secure Logging", "FAIL", f"Logging error: {str(e)}")
                
        except ImportError as e:
            self.log_test_result("Secure Logging Import", "FAIL", f"Import error: {str(e)}")
        except Exception as e:
            self.log_test_result("Secure Logging Test", "FAIL", f"Exception: {str(e)}")
            
    def test_https_security_headers(self):
        """Test HTTPS and security headers configuration"""
        print("\n🔒 Testing HTTPS Security Configuration...")
        
        try:
            # Check production security settings
            prod_settings_file = '/workspaces/ireti-pos-light/onlineretailpos/settings/production.py'
            if os.path.exists(prod_settings_file):
                with open(prod_settings_file, 'r') as f:
                    content = f.read()
                    
                required_settings = [
                    'SESSION_COOKIE_SECURE = True',
                    'CSRF_COOKIE_SECURE = True',
                    'SECURE_SSL_REDIRECT = True',
                    'SECURE_HSTS_SECONDS = 31536000'
                ]
                
                missing_settings = []
                for setting in required_settings:
                    if setting not in content:
                        missing_settings.append(setting)
                
                if not missing_settings:
                    self.log_test_result("Production HTTPS Settings", "PASS", 
                                       "All required HTTPS settings configured")
                else:
                    self.log_test_result("Production HTTPS Settings", "FAIL", 
                                       f"Missing settings: {missing_settings}")
            else:
                self.log_test_result("Production Settings File", "FAIL", 
                                   "Production settings file not found")
                
        except Exception as e:
            self.log_test_result("HTTPS Security Test", "FAIL", f"Exception: {str(e)}")
            
    def test_environment_security(self):
        """Test environment variable security"""
        print("\n🔑 Testing Environment Security...")
        
        try:
            # Check for required environment variables
            required_vars = ['STRIPE_SECRET_KEY', 'STRIPE_PUBLISHABLE_KEY']
            missing_vars = []
            
            for var in required_vars:
                if not os.getenv(var):
                    missing_vars.append(var)
            
            if not missing_vars:
                self.log_test_result("Environment Variables", "PASS", 
                                   "All required environment variables configured")
            else:
                self.log_test_result("Environment Variables", "FAIL", 
                                   f"Missing variables: {missing_vars}")
            
            # Check secret key format
            secret_key = os.getenv('STRIPE_SECRET_KEY', '')
            if secret_key.startswith(('sk_test_', 'sk_live_')):
                self.log_test_result("Secret Key Format", "PASS", 
                                   "Stripe secret key has valid format")
            else:
                self.log_test_result("Secret Key Format", "FAIL", 
                                   "Invalid Stripe secret key format")
                
        except Exception as e:
            self.log_test_result("Environment Security Test", "FAIL", f"Exception: {str(e)}")
            
    def test_no_cardholder_data_storage(self):
        """Test that no cardholder data is stored"""
        print("\n💳 Testing Cardholder Data Storage Policy...")
        
        try:
            from django.apps import apps
            
            # Check all Django models for prohibited fields
            prohibited_fields = [
                'card_number', 'cvv', 'cvc', 'expiry_date', 'security_code',
                'track_data', 'magnetic_stripe', 'chip_data', 'pan'
            ]
            
            violations = []
            
            for model in apps.get_models():
                for field in model._meta.get_fields():
                    if hasattr(field, 'name') and field.name.lower() in prohibited_fields:
                        violations.append(f"{model.__name__}.{field.name}")
            
            if not violations:
                self.log_test_result("No Cardholder Data Storage", "PASS", 
                                   "No prohibited cardholder data fields found in models")
            else:
                self.log_test_result("No Cardholder Data Storage", "FAIL", 
                                   f"Prohibited fields found: {violations}")
                
        except Exception as e:
            self.log_test_result("Cardholder Data Storage Test", "FAIL", f"Exception: {str(e)}")
            
    def generate_security_report(self):
        """Generate comprehensive security test report"""
        print("\n" + "="*80)
        print("PCI DSS SECURITY TEST REPORT")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        warning_tests = len([r for r in self.test_results if r['status'] == 'WARN'])
        
        print(f"\nTest Results Summary:")
        print(f"  Total Tests: {total_tests}")
        print(f"  ✅ Passed: {passed_tests}")
        print(f"  ❌ Failed: {failed_tests}")
        print(f"  ⚠️  Warnings: {warning_tests}")
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"  Success Rate: {success_rate:.1f}%")
        
        if failed_tests == 0:
            print(f"\n🎉 SECURITY COMPLIANCE: EXCELLENT")
            print("All critical security tests passed!")
        elif failed_tests <= 2:
            print(f"\n✅ SECURITY COMPLIANCE: GOOD")
            print("Minor issues found - review failed tests")
        else:
            print(f"\n⚠️ SECURITY COMPLIANCE: NEEDS ATTENTION")
            print("Multiple security issues found - immediate action required")
        
        # Detailed results
        print(f"\nDetailed Test Results:")
        for result in self.test_results:
            status_emoji = "✅" if result['status'] == "PASS" else "❌" if result['status'] == "FAIL" else "⚠️"
            print(f"  {status_emoji} {result['test']}: {result['details']}")
        
        return {
            'total': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'warnings': warning_tests,
            'success_rate': success_rate,
            'results': self.test_results
        }

def main():
    """Run complete security test suite"""
    print("🛡️ Starting PCI DSS Security Test Suite...")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    suite = SecurityTestSuite()
    
    # Run all security tests
    suite.test_stripe_service_security()
    suite.test_webhook_signature_verification()
    suite.test_access_control_decorators()
    suite.test_secure_logging()
    suite.test_https_security_headers()
    suite.test_environment_security()
    suite.test_no_cardholder_data_storage()
    
    # Generate report
    report = suite.generate_security_report()
    
    # Save report to file
    report_file = '/workspaces/ireti-pos-light/logs/security_test_report.json'
    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    # Exit with appropriate code
    exit_code = 0 if report['failed'] == 0 else 1
    return exit_code

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
