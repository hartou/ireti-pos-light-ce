# Tech Debt: Stripe Integration Improvements

## Overview
Following the completion of Task 7 (Stripe Payment Integration), there are several areas that need improvement to make the integration production-ready and fully compliant with the original acceptance criteria.

## Tasks to Complete

### 1. Database Atomicity Fixes
**Priority: High**

**Issue**: Transaction creation and Stripe PaymentIntent operations are not wrapped in atomic database transactions, creating risk of inconsistent state if one operation fails.

**Locations to Fix**:
- `transaction/views.py` `start_stripe_payment()` - wrap transaction creation + PaymentIntent creation/linking
- `payments/services.py` `link_transaction_to_payment()` - ensure atomic operation
- Any other payment workflow endpoints that modify both transaction and payment records

**Implementation**:
```python
from django.db import transaction as db_transaction

@db_transaction.atomic
def start_stripe_payment(request):
    # Existing logic with atomic guarantee
```

### 2. Manager Authorization Flow for High-Value Refunds
**Priority: Medium**

**Issue**: Settings define `PAYMENT_REFUND_AUTHORIZATION_THRESHOLD = 100.00` and models have `PaymentRefund.authorized_by` field, but the authorization workflow is not implemented.

**Requirements**:
- Check refund amount against threshold in `ProcessRefundAPIView` and `CreateRefundView`
- Require manager authentication/approval for high-value refunds
- Record `authorized_by` field when manager approves
- Update UI to prompt for manager credentials when needed

**Files to Modify**:
- `payments/views.py` - Add authorization checks
- `onlineretailpos/templates/payments/` - Add manager approval UI
- Add manager permission checks

### 3. Comprehensive Test Suite
**Priority: Medium**

**Issue**: Missing automated tests for critical payment flows, edge cases, and failure scenarios.

**Tests Needed**:

#### Unit Tests (`tests/unit/test_payments.py`):
- `StripePaymentService` methods (create_payment_intent, confirm_payment_intent, create_refund)
- PaymentTransaction model methods and properties
- PaymentRefund model validation and authorization logic
- Webhook signature verification
- Error handling for failed Stripe API calls

#### Integration Tests (`tests/integration/test_payment_flows.py`):
- Complete payment lifecycle: cart → PaymentIntent → confirmation → transaction creation
- Webhook processing and status updates
- Refund flows with and without manager authorization
- Atomic transaction rollback scenarios
- Receipt generation with payment details

#### API Tests (`tests/integration/test_payment_apis.py`):
- All payment API endpoints (`CreatePaymentIntentView`, `ConfirmPaymentIntentView`, etc.)
- Error responses and status codes
- Authentication requirements
- Input validation

#### E2E Tests (`tests/e2e/test_stripe_checkout.py`):
- Browser-based payment flow using Playwright
- Stripe Elements integration
- Payment success and failure scenarios
- Receipt display and printing

### 4. Code Quality Improvements
**Priority: Low**

**Minor Issues**:
- Add proper error handling and logging in all payment methods
- Improve webhook processing resilience
- Add retry logic for failed Stripe API calls
- Standardize response formats across all API endpoints

## Acceptance Criteria

For each task:
- [ ] Implementation follows existing code patterns and style
- [ ] All new code has appropriate error handling and logging
- [ ] Changes are covered by comprehensive tests
- [ ] Documentation is updated (docstrings, README, etc.)
- [ ] No breaking changes to existing functionality
- [ ] Performance impact is minimal

## Timeline

- **Atomicity Fixes**: 1-2 days
- **Manager Authorization**: 2-3 days  
- **Test Suite**: 3-4 days
- **Code Quality**: 1-2 days

**Total Estimated Effort**: 7-11 days

## Definition of Done

- All existing Stripe payment functionality continues to work
- New atomic operations prevent data inconsistency
- Manager authorization properly gates high-value refunds
- Test coverage exceeds 90% for payment-related code
- All tests pass in CI/CD pipeline
- Code review approved by team lead
- Documentation updated and accurate

## Notes

These improvements address the gaps identified in the Task 7 completion review and will make the Stripe integration production-ready. The work can be done in small, reviewable pull requests to minimize risk and facilitate code review.
