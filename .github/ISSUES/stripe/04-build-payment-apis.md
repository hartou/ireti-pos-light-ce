---
title: "Stripe Task 4: Build Payment Views and APIs"
labels: ["enhancement", "payments", "stripe", "api"]
milestone: "Stripe Integration v0.1"
assignees: ["github-actions[bot]"]
---

Create REST endpoints for payment flows.

Acceptance Criteria:
- [x] Endpoints implemented in `payments/views.py` and routed in `payments/urls.py`
- [x] `POST /api/payments/create-intent/` creates PaymentIntent
- [x] `POST /api/payments/confirm/` confirms payments
- [x] `POST /api/payments/refund/` processes refunds
- [x] `GET /api/payments/status/<id>/` returns payment status
- [x] Serializers in `payments/serializers.py` with validation
- [x] Permissions: only authorized roles can process/refund
- [x] Integration tests for endpoints

References: `STRIPE_INTEGRATION_PLAN.md` (Task 4)
