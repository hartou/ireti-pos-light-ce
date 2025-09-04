# GitHub Issues for POS System Integration Fixes

Based on the comprehensive Playwright MCP testing, here are the specific GitHub issues to create:

## Issue #1: Register Payment Buttons Not Connected to Stripe Processing

**Title:** 🚨 CRITICAL: Register payment buttons bypass Stripe and use mock processing

**Priority:** P0 - Critical

**Labels:** `bug`, `payment`, `stripe`, `integration`, `critical`

**Description:**
The register system payment buttons (Debit/Credit, Cash, etc.) are not connected to the Stripe payment processing system. When users click payment buttons from the register, they are redirected to a mock payment completion page instead of the Stripe checkout flow.

**Current Behavior:**
- Click "Debit/Credit" from register with items in cart
- Redirects to `/endTransaction/{transaction_id}/?type=card&value=DEBIT_CREDIT&total={amount}`
- Shows message: "This is a online register and is not connected to a Cash-Drawer or a Card-Machine"
- Transaction marked as complete without payment processing

**Expected Behavior:**
- Payment buttons should redirect to Stripe payment form with cart data
- Should process actual payment through Stripe
- Should only mark transaction complete after successful payment

**Screenshots:**
- `10_register_with_product_added_buttons_enabled.png` - Register with enabled buttons
- `11_transaction_completed_but_no_stripe_processing.png` - Mock payment completion

**Technical Details:**
- Register payment handlers need to integrate with `/payments/` endpoint
- Cart data needs to be passed to Stripe payment form
- Transaction state should depend on payment success

---

## Issue #2: Stripe Elements Not Loading in Payment Form

**Title:** 🐛 Stripe Card Elements not rendering in payment form

**Priority:** P1 - High

**Labels:** `bug`, `stripe`, `frontend`, `javascript`

**Description:**
The Stripe payment form at `/payments/` shows a placeholder for "Card Details" but the actual Stripe Elements for card input are not loading. The form appears incomplete and payment processing fails.

**Current Behavior:**
- Navigate to Payment System → Payment Form
- Card Details section shows empty alert placeholder
- Process Payment button resets form without processing
- No actual card input fields visible

**Expected Behavior:**
- Stripe Elements should load and display card input fields
- Should show proper card number, expiry, and CVC inputs
- Should validate card data before processing

**Screenshots:**
- `12_stripe_payment_form_disconnected_from_register.png` - Payment form with missing elements
- `13_stripe_form_reset_missing_card_elements.png` - Form reset after processing attempt

**Technical Details:**
- Check Stripe publishable key configuration
- Verify Stripe.js initialization
- Ensure Elements are properly mounted
- Add error handling for Stripe configuration issues

---

## Issue #3: Register Cart Data Not Passed to Payment System

**Title:** 💔 No integration between register cart and Stripe payment form

**Priority:** P1 - High

**Labels:** `integration`, `payment`, `cart`, `data-flow`

**Description:**
The register system and payment system operate in isolation. Cart contents, totals, and product details from the register are not passed to the payment form, requiring manual re-entry of amounts.

**Current Behavior:**
- Add products to register cart (total: $6.52)
- Navigate to Payment Form
- Must manually enter amount again
- No product details or transaction context

**Expected Behavior:**
- Payment form should receive cart data from register
- Amount should be pre-populated
- Product details should be included in payment description
- Single seamless flow from cart to payment

**Screenshots:**
- `10_register_with_product_added_buttons_enabled.png` - Register with cart
- `12_stripe_payment_form_disconnected_from_register.png` - Empty payment form

**Technical Details:**
- Implement session-based cart storage
- Create API endpoint to transfer cart data
- Pass transaction ID and cart contents to payment form
- Maintain transaction state across systems

---

## Issue #4: Payment Dashboard Shows No Transaction Activity

**Title:** 📊 Payment dashboard not tracking register transactions

**Priority:** P2 - Medium

**Labels:** `dashboard`, `tracking`, `integration`

**Description:**
The payment dashboard shows zero activity (0 payments) even after completing transactions through the register system. This indicates the two systems are not sharing transaction data.

**Current Behavior:**
- Complete transaction through register
- Check Payment Dashboard
- Shows: Today's Payments: 0, Successful: 0, Pending: 0
- No transaction records displayed

**Expected Behavior:**
- Dashboard should show all payment attempts and completions
- Should track both successful and failed payments
- Should correlate with register transaction records

**Screenshots:**
- `14_payment_dashboard_showing_zero_payments.png` - Dashboard showing no activity

**Technical Details:**
- Link register transactions with payment records
- Implement payment status tracking
- Create unified transaction reporting
- Add payment method correlation

---

## Issue #5: Missing End-to-End Payment Flow Integration

**Title:** 🔄 Need complete payment workflow from register to Stripe completion

**Priority:** P0 - Critical

**Labels:** `epic`, `integration`, `workflow`, `payment`

**Description:**
Create a complete, seamless payment workflow that connects the register system to Stripe payment processing with proper error handling and transaction correlation.

**Requirements:**
1. Register payment buttons redirect to Stripe with cart data
2. Stripe Elements load and function properly
3. Payment success/failure updates register transaction
4. Receipt generation includes payment confirmation
5. Payment dashboard tracks all transactions

**Acceptance Criteria:**
- [ ] User can add products to register cart
- [ ] Payment buttons launch Stripe checkout with correct amount
- [ ] Stripe processes payment with test cards
- [ ] Successful payment marks register transaction complete
- [ ] Failed payment allows retry without losing cart
- [ ] Payment dashboard shows transaction activity
- [ ] Receipt includes payment confirmation details

**Screenshots:**
All 14 screenshots from test report demonstrate various aspects of this workflow

**Technical Tasks:**
- Modify register payment handlers
- Fix Stripe Elements loading
- Implement cart-to-payment data transfer
- Add payment status correlation
- Create unified transaction tracking
- Add proper error handling

---

*These issues were identified through comprehensive Playwright MCP visual testing and should be prioritized based on their impact on the core payment functionality.*
