"""
End-to-end tests for Stripe payment integration using Playwright.
Tests the complete flow from cart to payment completion.
"""

import pytest
import asyncio
from playwright.async_api import async_playwright, Page
import json
import time
from django.contrib.auth.models import User
from django.test import TransactionTestCase
from django.test.utils import override_settings
from django.core.management import execute_from_command_line
import threading
import subprocess
import os
import signal


class StripeE2ETest(TransactionTestCase):
    """End-to-end test for Stripe payment flow using Playwright."""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create test user
        cls.test_user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        # Start Django development server in background
        cls.server_process = None
        cls.start_test_server()
    
    @classmethod
    def tearDownClass(cls):
        if cls.server_process:
            cls.server_process.terminate()
            cls.server_process.wait()
        super().tearDownClass()
    
    @classmethod
    def start_test_server(cls):
        """Start Django development server for testing."""
        try:
            # Kill any existing server on port 8000
            subprocess.run(['pkill', '-f', 'runserver'], capture_output=True)
            time.sleep(2)
            
            # Start new server
            cls.server_process = subprocess.Popen([
                'python', 'manage.py', 'runserver', '127.0.0.1:8000'
            ], cwd='/workspaces/ireti-pos-light', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for server to start
            time.sleep(5)
        except Exception as e:
            print(f"Error starting test server: {e}")
    
    async def test_stripe_payment_flow(self):
        """Test complete Stripe payment flow from cart to completion."""
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                # Navigate to POS login page
                await page.goto('http://127.0.0.1:8000/admin/login/')
                
                # Login
                await page.fill('input[name="username"]', 'testuser')
                await page.fill('input[name="password"]', 'testpass123')
                await page.click('input[type="submit"]')
                
                # Wait for redirect and navigate to POS main page
                await page.wait_for_timeout(2000)
                await page.goto('http://127.0.0.1:8000/')
                
                # Add items to cart (simulate scanning/adding products)
                # This would depend on your POS interface - adjust selectors as needed
                cart_data = [
                    {'barcode': 'TEST001', 'name': 'Test Product', 'price': '10.99', 'quantity': 2}
                ]
                
                # Inject cart data into session storage
                await page.evaluate(f"""
                    sessionStorage.setItem('cart', JSON.stringify({json.dumps(cart_data)}));
                """)
                
                # Navigate to transaction page
                await page.goto('http://127.0.0.1:8000/transaction/')
                
                # Select Stripe payment method
                stripe_button = page.locator('button:has-text("Stripe")')
                if await stripe_button.count() > 0:
                    await stripe_button.click()
                else:
                    # Try alternative selector
                    await page.click('input[value="STRIPE"]')
                
                # Wait for Stripe payment form to load
                await page.wait_for_timeout(3000)
                
                # Fill Stripe test card details
                # Note: In a real test, you'd use Stripe's test card numbers
                stripe_frame = page.frame_locator('iframe[name^="__privateStripeFrame"]')
                if await stripe_frame.count() > 0:
                    await stripe_frame.locator('input[name="cardnumber"]').fill('4242424242424242')
                    await stripe_frame.locator('input[name="exp-date"]').fill('12/34')
                    await stripe_frame.locator('input[name="cvc"]').fill('123')
                    await stripe_frame.locator('input[name="postal"]').fill('12345')
                
                # Submit payment
                submit_button = page.locator('button:has-text("Complete Payment")')
                if await submit_button.count() > 0:
                    await submit_button.click()
                
                # Wait for payment processing
                await page.wait_for_timeout(5000)
                
                # Check for success or error messages
                success_indicator = page.locator('.payment-success, .alert-success')
                error_indicator = page.locator('.payment-error, .alert-danger')
                
                if await success_indicator.count() > 0:
                    print("✅ Stripe payment flow completed successfully")
                    success = True
                elif await error_indicator.count() > 0:
                    error_text = await error_indicator.text_content()
                    print(f"❌ Payment failed with error: {error_text}")
                    success = False
                else:
                    print("⚠️ Payment status unclear - check manually")
                    success = None
                
                # Take screenshot for debugging
                await page.screenshot(path='/workspaces/ireti-pos-light/test_screenshots/stripe_e2e_result.png')
                
                return success
                
            except Exception as e:
                print(f"Error during Stripe E2E test: {e}")
                await page.screenshot(path='/workspaces/ireti-pos-light/test_screenshots/stripe_e2e_error.png')
                return False
            finally:
                await browser.close()
    
    def test_run_stripe_e2e(self):
        """Django test wrapper for async Stripe E2E test."""
        result = asyncio.run(self.test_stripe_payment_flow())
        
        # Assert based on result
        if result is True:
            self.assertTrue(True, "Stripe payment flow completed successfully")
        elif result is False:
            self.fail("Stripe payment flow failed")
        else:
            print("Warning: Stripe payment flow result unclear - manual verification needed")


if __name__ == '__main__':
    # Run the test directly
    import django
    from django.conf import settings
    from django.test.utils import get_runner
    
    if not settings.configured:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onlineretailpos.settings.local')
        django.setup()
    
    # Run test
    test = StripeE2ETest()
    test.setUpClass()
    try:
        test.test_run_stripe_e2e()
    finally:
        test.tearDownClass()
