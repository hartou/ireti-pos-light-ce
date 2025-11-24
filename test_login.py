#!/usr/bin/env python3
"""
Playwright test script to test login functionality on the deployed POS application.
"""

import asyncio
from playwright.async_api import async_playwright

async def test_login():
    async with async_playwright() as p:
        # Launch browser (headless=True for codespace environment)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Navigate to the application
            url = "https://ireti-pos-app.calmpebble-046010d8.eastus.azurecontainerapps.io"
            print(f"Navigating to: {url}")
            await page.goto(url)
            
            # Wait for page to load
            await page.wait_for_load_state('networkidle')
            
            # Check if we're redirected to login page
            current_url = page.url
            print(f"Current URL: {current_url}")
            
            # Take a screenshot of the current state
            await page.screenshot(path='login_page.png')
            print("Screenshot saved as login_page.png")
            
            # Look for login form elements
            username_field = await page.query_selector('input[name="username"]')
            password_field = await page.query_selector('input[name="password"]')
            login_button = await page.query_selector('input[type="submit"], button[type="submit"], button:has-text("Login")')
            
            if username_field and password_field and login_button:
                print("Login form found! Attempting to login...")
                
                # Fill in credentials
                await username_field.fill('admin')
                await password_field.fill('admin123')
                
                print("Credentials filled, clicking login button...")
                
                # Click login button and wait for navigation
                await login_button.click()
                
                # Wait for navigation or response
                await page.wait_for_load_state('networkidle', timeout=10000)
                
                # Check new URL
                new_url = page.url
                print(f"After login URL: {new_url}")
                
                # Take screenshot after login attempt
                await page.screenshot(path='after_login.png')
                print("Post-login screenshot saved as after_login.png")
                
                # Check for success indicators
                if '/user/login' not in new_url:
                    print("✅ LOGIN SUCCESSFUL! Redirected away from login page")
                    
                    # Look for dashboard or welcome elements
                    welcome_element = await page.query_selector('text="Welcome"')
                    dashboard_element = await page.query_selector('text="Dashboard"')
                    
                    if welcome_element or dashboard_element:
                        print("✅ Found welcome/dashboard elements")
                    
                    # Get page title
                    title = await page.title()
                    print(f"Page title: {title}")
                    
                else:
                    print("❌ LOGIN FAILED - Still on login page")
                    
                    # Check for error messages
                    error_elements = await page.query_selector_all('.alert, .error, .message')
                    for error in error_elements:
                        error_text = await error.text_content()
                        if error_text:
                            print(f"Error message: {error_text}")
                
            else:
                print("❌ Login form elements not found")
                print(f"Username field: {username_field is not None}")
                print(f"Password field: {password_field is not None}")
                print(f"Login button: {login_button is not None}")
                
                # Get page content for debugging
                content = await page.content()
                print("Page content (first 500 chars):")
                print(content[:500])
        
        except Exception as e:
            print(f"❌ Error during test: {str(e)}")
            await page.screenshot(path='error_screenshot.png')
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_login())