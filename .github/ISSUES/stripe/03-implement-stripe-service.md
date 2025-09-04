---
title: "Stripe Task 3: Implement Stripe Service Layer"
labels: ["enhancement", "payments", "stripe", "backend"]
milestone: "Stripe Integration v0.1"
assignees: ["github-actions[bot]"]
---

Implement `StripePaymentService` for interacting with Stripe APIs.

Acceptance Criteria:
- [x] `payments/services.py` created with class `StripePaymentService`
- [x] Methods: `create_payment_intent`, `confirm_payment_intent`, `create_refund`, `retrieve_payment_intent`
- [x] Proper error handling and idempotency keys
- [x] Logging without sensitive data
- [x] Unit tests with mocked Stripe SDK
- [x] Exceptions defined in `payments/exceptions.py`

References: `STRIPE_INTEGRATION_PLAN.md` (Task 3)
