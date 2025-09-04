---
applyTo: '**'
---

# User Memory

## User Preferences
- Programming languages: Python, Django 5+, JavaScript
- Code style preferences: Clean, maintainable, and scalable code following Django best practices
- Development environment: VS Code with containerized development
- Communication style: Concise but thorough, professional

## Project Context
- Current project type: Django-based Point of Sale (POS) system
- Tech stack: Django 5+, PostgreSQL, Docker, Stripe payments, PWA capabilities
- Architecture patterns: Django MVT with service layer pattern for payment processing
- Key requirements: PCI DSS compliance, secure payment processing, production deployment ready

## Coding Patterns
- Service layer pattern for business logic
- Django best practices with proper model relationships
- Comprehensive error handling and logging
- Security-first approach with sensitive data redaction
- Docker containerization for all environments

## Context7 Research History
- Stripe integration patterns and best practices
- PCI DSS compliance requirements
- Django payment processing security measures
- Production deployment configurations

## Conversation History
- Currently working on Stripe payment testing in sandbox mode
- Stripe integration is implemented (Tasks 1-9 completed) 
- Django superuser created: admin / admin@example.com / admin123
- Alternative user: testuser / test@example.com / test123
- Stripe test keys configured and validated
- Development server running on http://127.0.0.1:8000/
- Credential issue resolved - updated passwords

## Current Testing Setup
- Stripe sandbox environment configured with test keys
- Stripe Python package updated to v11.1.0
- Environment variables set for STRIPE_SECRET_KEY and STRIPE_PUBLISHABLE_KEY
- Development server running with Stripe integration
- Ready for end-to-end payment testing with test cards
- Comprehensive testing documentation created: STRIPE_SANDBOX_TESTING_GUIDE.md
- Quick reference card available: STRIPE_TESTING_QUICK_REFERENCE.md

## Notes
- Project is on feature/stripe-payments-integration branch
- Using GHCR for container registry
- Production uses PostgreSQL with Nginx reverse proxy
- Security logging utilities already implemented for PCI compliance
- Stripe API connection validated successfully
