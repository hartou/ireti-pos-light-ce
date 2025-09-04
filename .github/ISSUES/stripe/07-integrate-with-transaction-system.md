---
title: "Stripe Task 7: Integrate with Transaction System"
labels: ["enhancement", "payments", "stripe", "backend"]
milestone: "Stripe Integration v0.1"
assignees: ["github-actions[bot]"]
---

Wire payments into existing transactions and receipts.

Acceptance Criteria:
- [x] Link `PaymentTransaction` to `transaction.Transaction`
- [x] Update transaction workflow to create Stripe PaymentIntent and store IDs
- [x] Ensure atomicity: wrap payment and transaction updates in DB transactions
- [x] Update receipt views/templates to include payment details
- [x] Add manager authorization flow for high-value refunds
- [x] Tests covering transaction lifecycle with payments

References: `STRIPE_INTEGRATION_PLAN.md` (Task 7)
