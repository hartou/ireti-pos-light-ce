---
title: "Stripe Task 1: Setup Stripe Configuration"
labels: ["enhancement", "payments", "stripe", "priority:high"]
milestone: "Stripe Integration v0.1"
assignees: ["github-actions[bot]"]
---

Implement Stripe configuration across environments.

Acceptance Criteria:
- [x] Add `stripe` to `requirements.txt` and install
- [x] Configure `STRIPE_PUBLISHABLE_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_ENDPOINT_SECRET` in `onlineretailpos/settings/base.py`
- [x] Add keys to `.env.example` and `docker-compose.yml`
- [x] Ensure keys loaded via environment variables in all environments
- [x] Document setup steps in `STRIPE_INTEGRATION_PLAN.md`
- [x] Security review: no secrets committed, safe defaults

References: `STRIPE_INTEGRATION_PLAN.md` (Task 1)
