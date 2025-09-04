# Payment Operations Runbook

## Overview

This runbook provides step-by-step procedures for managing payment operations in the Ireti POS Light system. It covers standard payment processing, troubleshooting, and operational guidelines for day-to-day payment management.

## System Architecture

### Payment Flow Components
- **Frontend**: Django-powered POS interface with Stripe Elements integration
- **Backend**: Django service layer handling payment logic and Stripe API calls
- **Database**: PostgreSQL storing transaction records and payment metadata
- **Stripe Integration**: Payment processing, webhooks, and refund handling
- **Monitoring**: Metrics collection and observability dashboards

### Key Models
- `PaymentTransaction`: Core payment records with Stripe payment intent mapping
- `PaymentRefund`: Refund transaction records
- `PaymentWebhook`: Stripe webhook event processing logs
- `PaymentMetric`: Performance and observability metrics

## Standard Operating Procedures

### 1. Daily Payment Operations

#### Morning Startup Checklist
1. **System Health Check**
   ```bash
   # Check application status
   docker ps | grep pos-django-webapp-container
   
   # Verify database connectivity
   python manage.py dbshell -c "SELECT 1;"
   
   # Check Stripe connectivity
   curl -H "Authorization: Bearer $STRIPE_SECRET_KEY" https://api.stripe.com/v1/account
   ```

2. **Review Previous Day's Transactions**
   - Access payment dashboard: `/payments/dashboard/`
   - Check for any failed or incomplete transactions
   - Review webhook processing logs: `/payments/webhooks/`
   - Verify metrics are updating: `/payments/metrics/`

3. **Verify Integration Status**
   - Confirm webhook endpoints are accessible
   - Test a small test payment if possible
   - Check error logs for any overnight issues

#### Processing Customer Payments

**Standard Card Payment Process:**

1. **Cashier Workflow**
   ```
   1. Add items to transaction
   2. Calculate total amount
   3. Select "Card Payment" method
   4. Enter amount (if different from total)
   5. Click "Process Payment"
   6. Customer inserts/taps card
   7. Wait for authorization
   8. Print receipt upon success
   ```

2. **System Process Flow**
   ```
   Transaction Creation → Payment Intent → Customer Auth → Confirmation → Receipt
   ```

3. **Success Indicators**
   - Payment status shows "succeeded"
   - Transaction record updated in database
   - Customer receives receipt
   - Webhook confirmation received

4. **Failure Handling**
   - Display clear error message to customer
   - Log error details for investigation
   - Offer alternative payment method
   - Retry if appropriate (network issues)

### 2. Transaction Management

#### Viewing Transaction Details
1. Navigate to Payments Dashboard
2. Use search filters (date, amount, status, customer)
3. Click on transaction ID for full details
4. Review payment timeline and webhook events

#### Transaction Status Meanings
- **`requires_payment_method`**: Payment intent created, awaiting customer payment
- **`requires_confirmation`**: Payment method attached, needs confirmation
- **`requires_action`**: Customer authentication required (3D Secure)
- **`processing`**: Payment being processed by card networks
- **`succeeded`**: Payment completed successfully
- **`requires_capture`**: Manual capture required (if configured)
- **`canceled`**: Payment intent was canceled
- **`payment_failed`**: Payment failed due to declined card or other error

### 3. Error Response Procedures

#### Common Error Scenarios

**Card Declined (`card_declined`)**
1. Inform customer their card was declined
2. Suggest they check with their bank
3. Offer alternative payment method
4. Do not retry the same card immediately

**Insufficient Funds (`insufficient_funds`)**
1. Inform customer of insufficient funds
2. Suggest they use a different card
3. Offer to split payment across multiple methods
4. Document if customer requests to hold items

**Network Connection Issues**
1. Check internet connectivity
2. Verify Stripe API accessibility
3. Switch to offline mode if available
4. Process payments when connection restored

**Authentication Required (`authentication_required`)**
1. Guide customer through 3D Secure flow
2. Ensure customer has their phone for SMS codes
3. Allow sufficient time for authentication
4. Retry if authentication fails initially

#### Escalation Procedures

**When to Escalate:**
- Repeated payment failures across multiple customers
- System errors that prevent payment processing
- Webhook processing failures
- Customer disputes or chargebacks
- Suspected fraudulent activity

**Escalation Contacts:**
- Technical Issues: IT Support Team
- Payment Disputes: Store Manager
- Fraud Concerns: Security Team
- System Outages: On-call Engineer

### 4. Monitoring and Metrics

#### Key Performance Indicators (KPIs)

**Payment Success Rate**
- Target: >98% success rate
- Monitor via: `/payments/metrics/`
- Alert threshold: <95% over 1 hour period

**Processing Latency**
- Target: <3 seconds average processing time
- Monitor: P95 latency should be <5 seconds
- Alert threshold: P95 >10 seconds

**Webhook Processing**
- Target: 100% webhook processing rate
- Monitor: Unprocessed webhooks should be 0
- Alert threshold: >10 failed webhooks in 1 hour

#### Daily Monitoring Tasks

1. **Check Payment Success Rate** (Morning, Afternoon, Evening)
   ```bash
   # API call to get current metrics
   curl -H "Authorization: Bearer $API_TOKEN" \
        "https://yourpos.com/payments/api/metrics/?hours=1"
   ```

2. **Review Error Logs**
   ```bash
   # Check payment logs
   tail -f logs/payments.log | grep ERROR
   
   # Check webhook logs
   tail -f logs/webhooks.log
   ```

3. **Verify Webhook Health**
   - Check `/payments/webhooks/` dashboard
   - Ensure no webhooks are stuck in "processing" state
   - Verify recent webhook timestamps are current

#### Weekly Monitoring Tasks

1. **Generate Payment Report**
   - Export transaction data for the week
   - Calculate total volume and average transaction size
   - Identify trends or anomalies

2. **Review Error Trends**
   - Analyze common error patterns
   - Identify opportunities for improvement
   - Update troubleshooting procedures if needed

3. **Performance Analysis**
   - Review latency trends
   - Check for any degradation in processing times
   - Optimize if necessary

### 5. Backup and Recovery

#### Data Protection
- All payment data is encrypted at rest and in transit
- Regular database backups occur automatically
- No sensitive card data is stored locally (PCI compliant)

#### System Recovery Procedures

**Database Recovery**
1. Identify backup closest to incident time
2. Restore from backup following DR procedures
3. Replay any missing transactions from Stripe
4. Verify data integrity

**Application Recovery**
1. Deploy from last known good Docker image
2. Verify environment variables are correct
3. Run database migrations if needed
4. Test payment processing before going live

**Stripe Configuration Recovery**
1. Verify API keys are correct and active
2. Reconfigure webhook endpoints if needed
3. Test webhook connectivity
4. Validate payment processing end-to-end

### 6. Maintenance Procedures

#### Regular Maintenance Tasks

**Daily**
- Monitor system health and payment metrics
- Review error logs for new issues
- Verify webhook processing is current

**Weekly**
- Generate and review payment reports
- Clean up old webhook logs (>30 days)
- Review and update error handling procedures

**Monthly**
- Rotate API keys if required by security policy
- Review payment processing performance trends
- Update system documentation
- Conduct payment processing training for staff

**Quarterly**
- Full system security review
- Update payment processing procedures
- Review and test disaster recovery procedures
- Conduct PCI compliance assessment

### 7. Security Procedures

#### PCI Compliance Monitoring
- Ensure no card data is logged or stored
- Verify all payment communications use HTTPS
- Monitor for any potential data exposure
- Regular security scans and assessments

#### Fraud Prevention
- Monitor for unusual transaction patterns
- Flag high-value transactions for review
- Implement velocity checking for repeat customers
- Report suspected fraud immediately

#### Access Control
- Limit payment processing permissions to authorized staff
- Regular review of user access rights
- Immediate access removal for terminated employees
- Multi-factor authentication for administrative access

### 8. Customer Service Procedures

#### Payment Questions
- Always verify customer identity before discussing payments
- Use transaction ID or receipt number for reference
- Provide clear explanation of payment status
- Offer alternative solutions for payment issues

#### Dispute Resolution
- Document all customer interactions
- Gather all relevant transaction information
- Coordinate with Stripe for chargeback responses
- Follow company dispute resolution procedures

#### Receipt and Record Keeping
- Ensure customers receive receipts for all transactions
- Maintain transaction records per legal requirements
- Provide transaction history when requested
- Handle refund requests promptly and professionally

## Emergency Procedures

### Payment System Outage
1. **Immediate Actions**
   - Switch to backup payment method (cash/check)
   - Document all transactions for later processing
   - Notify customers of temporary payment limitations
   - Contact technical support immediately

2. **Communication**
   - Inform all staff of the outage
   - Update customers with expected resolution time
   - Post notices if outage is extended
   - Notify management of business impact

3. **Recovery**
   - Test payment processing thoroughly before resuming
   - Process any queued transactions
   - Verify data integrity
   - Conduct post-incident review

### Security Incident
1. **Immediate Actions**
   - Isolate affected systems immediately
   - Document the incident timeline
   - Notify security team and management
   - Preserve evidence for investigation

2. **Assessment**
   - Determine scope of potential data exposure
   - Identify affected customer transactions
   - Assess business impact
   - Coordinate with legal and compliance teams

3. **Recovery**
   - Implement security patches or fixes
   - Reset compromised credentials
   - Monitor for ongoing threats
   - Conduct thorough security review

## Contact Information

### Internal Contacts
- **IT Support**: ext. 2200 / support@company.com
- **Store Manager**: ext. 1001
- **Security Team**: security@company.com
- **Legal/Compliance**: compliance@company.com

### External Contacts
- **Stripe Support**: https://support.stripe.com
- **Payment Processor Emergency**: 1-800-XXX-XXXX
- **Bank Merchant Services**: 1-800-XXX-XXXX

## Documentation and Training

### Required Reading
- Payment Card Industry Data Security Standards (PCI DSS)
- Company payment processing policies
- Stripe API documentation and best practices
- Emergency response procedures

### Training Schedule
- New employee payment processing training: Week 1
- Annual PCI compliance training: Required
- Quarterly procedure updates: As needed
- Emergency response drills: Bi-annually

---

*This runbook should be reviewed and updated quarterly or after any significant system changes. All staff with payment processing responsibilities should be familiar with these procedures.*
