# Payment Troubleshooting Guide

## Overview

This comprehensive troubleshooting guide provides solutions for common payment issues, error codes, and system problems in the Ireti POS Light system. It's designed for technical staff, support personnel, and store managers to quickly diagnose and resolve payment-related issues.

## Quick Reference Error Codes

### Stripe Error Codes

| Error Code | Description | Quick Fix | Escalation Required |
|------------|-------------|-----------|-------------------|
| `card_declined` | Card issuer declined | Try different card | No |
| `expired_card` | Card has expired | Get new card info | No |
| `insufficient_funds` | Not enough funds | Try different payment | No |
| `incorrect_cvc` | Wrong security code | Re-enter CVC | No |
| `processing_error` | Generic processing error | Retry payment | If persistent |
| `rate_limit_error` | Too many API requests | Wait and retry | If frequent |
| `authentication_required` | 3D Secure needed | Guide customer through auth | No |
| `payment_intent_authentication_failure` | Auth failed | Try different card | No |

### System Error Codes

| Error Code | Description | Immediate Action | Resolution |
|------------|-------------|------------------|------------|
| `CONN_001` | Database connection lost | Check database status | Restart if needed |
| `CONN_002` | Stripe API unreachable | Check internet/firewall | Contact ISP |
| `AUTH_001` | Invalid API key | Check configuration | Update keys |
| `PROC_001` | Payment processing timeout | Retry operation | Check system load |
| `WEBHOOK_001` | Webhook verification failed | Check endpoint secret | Update webhook config |

## Common Payment Issues

### 1. Card Declined Errors

#### Symptoms
- Payment fails with "card_declined" error
- Customer reports card works elsewhere
- Multiple cards being declined

#### Diagnostic Steps
```bash
# Check recent transaction patterns
grep "card_declined" logs/payments.log | tail -20

# Verify Stripe connectivity
curl -H "Authorization: Bearer $STRIPE_SECRET_KEY" \
     https://api.stripe.com/v1/charges?limit=1

# Check system time synchronization
date && ntpstat
```

#### Common Causes & Solutions

**1. Insufficient Funds**
- **Symptoms**: `insufficient_funds` error code
- **Customer Action**: Use different payment method
- **Staff Action**: Suggest checking account balance
- **System Action**: Log transaction for audit

**2. Expired Card**
- **Symptoms**: `expired_card` error code
- **Customer Action**: Provide updated card information
- **Staff Action**: Help customer enter new expiry date
- **System Action**: Clear any cached card data

**3. Incorrect CVC**
- **Symptoms**: `incorrect_cvc` error code
- **Customer Action**: Re-enter security code
- **Staff Action**: Verify customer is reading correct code
- **System Action**: Allow up to 3 retry attempts

**4. Bank Security Block**
- **Symptoms**: Generic decline, card works elsewhere
- **Customer Action**: Contact card issuer
- **Staff Action**: Suggest calling bank to approve transaction
- **System Action**: Document for customer service follow-up

### 2. Network and Connectivity Issues

#### Symptoms
- Payments timeout or fail to process
- "Unable to connect" error messages
- Intermittent payment processing issues

#### Diagnostic Steps
```bash
# Test internet connectivity
ping -c 4 8.8.8.8

# Test Stripe API connectivity
curl -I https://api.stripe.com/

# Check DNS resolution
nslookup api.stripe.com

# Test webhook endpoint
curl -I https://yourdomain.com/payments/webhooks/stripe/
```

#### Solutions

**1. Internet Connection Issues**
```bash
# Restart network interface
sudo systemctl restart network

# Check firewall rules
sudo iptables -L | grep stripe
sudo ufw status

# Test with different DNS
echo "nameserver 8.8.8.8" >> /etc/resolv.conf
```

**2. Firewall Blocking Stripe**
```bash
# Allow Stripe API access
sudo ufw allow out 443/tcp
sudo ufw allow out 80/tcp

# Check if corporate firewall blocks Stripe
curl -v https://api.stripe.com/
```

**3. SSL Certificate Issues**
```bash
# Check SSL certificate validity
openssl s_client -connect api.stripe.com:443 -servername api.stripe.com

# Update CA certificates
sudo apt-get update && sudo apt-get install ca-certificates
```

### 3. Authentication and 3D Secure Issues

#### Symptoms
- Payment requires additional authentication
- Customer stuck in authentication flow
- Authentication timing out

#### Diagnostic Steps
```bash
# Check for 3D Secure requirements in logs
grep "authentication_required" logs/payments.log

# Verify webhook processing for auth events
grep "payment_intent.requires_action" logs/webhooks.log
```

#### Solutions

**1. Guide Customer Through 3D Secure**
1. Explain that bank requires additional verification
2. Ensure customer has phone for SMS codes
3. Allow 5-10 minutes for authentication process
4. Be patient - international cards may take longer

**2. Authentication Timeout**
1. Restart payment process
2. Try different browser if using web interface
3. Clear browser cache and cookies
4. Use different payment method if persistent

**3. Authentication Failure**
1. Verify customer is entering correct information
2. Check if customer's phone number is current
3. Try alternative authentication method
4. Contact customer's bank if needed

### 4. System Performance Issues

#### Symptoms
- Slow payment processing (>10 seconds)
- Timeouts during payment
- High error rates

#### Diagnostic Steps
```bash
# Check system resources
top
df -h
free -m

# Monitor database performance
ps aux | grep postgres
iostat -x 1 5

# Check application logs for performance issues
grep -E "(slow|timeout|performance)" logs/payments.log
```

#### Solutions

**1. High CPU Usage**
```bash
# Identify resource-heavy processes
top -o %CPU

# Restart application if needed
docker restart pos-django-webapp-container

# Check for memory leaks
docker stats pos-django-webapp-container
```

**2. Database Performance**
```bash
# Check database connections
docker exec -it pos-postgres-container psql -U DBUSER -c "SELECT count(*) FROM pg_stat_activity;"

# Analyze slow queries
docker exec -it pos-postgres-container psql -U DBUSER -c "SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
```

**3. Disk Space Issues**
```bash
# Check disk usage
df -h

# Clean up old log files
find logs/ -name "*.log" -mtime +30 -delete

# Clean up old Docker images
docker system prune -a
```

### 5. Webhook Processing Issues

#### Symptoms
- Webhooks not being received
- Payment status not updating
- Webhook processing errors

#### Diagnostic Steps
```bash
# Check webhook endpoint accessibility
curl -X POST https://yourdomain.com/payments/webhooks/stripe/ \
     -H "Content-Type: application/json" \
     -d '{"test": "connectivity"}'

# Review webhook logs
tail -f logs/webhooks.log

# Check webhook configuration in Stripe Dashboard
# https://dashboard.stripe.com/webhooks
```

#### Solutions

**1. Webhook Endpoint Unreachable**
```bash
# Check if webhook URL is accessible externally
curl -I https://yourdomain.com/payments/webhooks/stripe/

# Verify SSL certificate for webhook endpoint
openssl s_client -connect yourdomain.com:443

# Check firewall rules for incoming webhooks
sudo ufw status
```

**2. Webhook Signature Verification Failing**
```python
# Verify webhook endpoint secret is correct
echo $STRIPE_WEBHOOK_ENDPOINT_SECRET

# Check webhook secret in Stripe Dashboard
# Ensure it matches the environment variable
```

**3. Webhook Processing Timeouts**
```bash
# Check webhook processing performance
grep "webhook processing time" logs/webhooks.log

# Increase webhook timeout if needed (in settings)
# STRIPE_WEBHOOK_TIMEOUT=30
```

### 6. Database Connection Issues

#### Symptoms
- "Database connection lost" errors
- Payment data not saving
- Intermittent database errors

#### Diagnostic Steps
```bash
# Check database container status
docker ps | grep postgres

# Test database connectivity
docker exec -it pos-postgres-container pg_isready

# Check database logs
docker logs pos-postgres-container | tail -50
```

#### Solutions

**1. Database Container Not Running**
```bash
# Start database container
docker start pos-postgres-container

# Check container health
docker inspect pos-postgres-container | grep Health
```

**2. Connection Pool Exhaustion**
```python
# Check Django database settings
# DATABASES['default']['OPTIONS']['MAX_CONNS'] = 20

# Monitor active connections
# SELECT count(*) FROM pg_stat_activity;
```

**3. Database Corruption**
```bash
# Check database integrity
docker exec -it pos-postgres-container \
  psql -U DBUSER -d OnlineRetailPOS -c "SELECT pg_database_size('OnlineRetailPOS');"

# Repair if needed (backup first!)
docker exec -it pos-postgres-container \
  pg_dump -U DBUSER OnlineRetailPOS > backup.sql
```

## Advanced Troubleshooting

### 1. API Rate Limiting

#### Symptoms
- `rate_limit_error` from Stripe
- Intermittent payment failures during busy periods
- "Too many requests" errors

#### Solutions
```python
# Implement exponential backoff
import time
import random

def retry_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError:
            if attempt == max_retries - 1:
                raise
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(wait_time)
```

### 2. Memory Leaks

#### Detection
```bash
# Monitor memory usage over time
while true; do
    docker stats --no-stream pos-django-webapp-container >> memory_usage.log
    sleep 300  # Check every 5 minutes
done

# Analyze memory patterns
grep "MEM USAGE" memory_usage.log | awk '{print $3}' | sort -hr
```

#### Solutions
```bash
# Restart application container
docker restart pos-django-webapp-container

# Implement memory monitoring alerts
# Add to crontab:
# */15 * * * * /path/to/memory_check.sh
```

### 3. Concurrency Issues

#### Symptoms
- Race conditions in payment processing
- Duplicate payment attempts
- Inconsistent payment states

#### Solutions
```python
# Use database transactions
from django.db import transaction

@transaction.atomic
def process_payment(payment_data):
    # Payment processing logic here
    pass

# Implement payment idempotency
def create_payment_intent(amount, idempotency_key=None):
    headers = {}
    if idempotency_key:
        headers['Idempotency-Key'] = idempotency_key
    # Stripe API call with headers
```

### 4. SSL/TLS Issues

#### Symptoms
- Certificate verification failures
- SSL handshake errors
- Secure connection warnings

#### Diagnostic Tools
```bash
# Test SSL configuration
openssl s_client -connect api.stripe.com:443 -servername api.stripe.com

# Check certificate chain
openssl verify -CAfile /etc/ssl/certs/ca-certificates.crt certificate.pem

# Test cipher suites
nmap --script ssl-enum-ciphers -p 443 api.stripe.com
```

## Monitoring and Alerting

### Key Metrics to Monitor

**Payment Success Rate**
```bash
# Alert if success rate drops below 95%
success_rate=$(calculate_success_rate_last_hour)
if [ $success_rate -lt 95 ]; then
    send_alert "Payment success rate is $success_rate%"
fi
```

**Processing Latency**
```bash
# Alert if P95 latency exceeds 10 seconds
p95_latency=$(get_p95_latency_last_hour)
if [ $p95_latency -gt 10000 ]; then  # milliseconds
    send_alert "Payment processing latency is high: ${p95_latency}ms"
fi
```

**Error Rate**
```bash
# Alert if error rate exceeds 2%
error_rate=$(calculate_error_rate_last_hour)
if [ $error_rate -gt 2 ]; then
    send_alert "Payment error rate is $error_rate%"
fi
```

### Automated Health Checks

**System Health Check Script**
```bash
#!/bin/bash
# health_check.sh

# Check application container
if ! docker ps | grep -q "pos-django-webapp-container"; then
    echo "ERROR: Application container not running"
    exit 1
fi

# Check database connectivity
if ! docker exec pos-postgres-container pg_isready > /dev/null; then
    echo "ERROR: Database not accessible"
    exit 1
fi

# Check Stripe connectivity
if ! curl -s -f https://api.stripe.com/ > /dev/null; then
    echo "ERROR: Cannot reach Stripe API"
    exit 1
fi

# Check webhook endpoint
if ! curl -s -f https://yourdomain.com/health/ > /dev/null; then
    echo "ERROR: Webhook endpoint unreachable"
    exit 1
fi

echo "All systems healthy"
```

## Recovery Procedures

### 1. Payment System Recovery

**Complete System Failure**
1. **Assessment Phase**
   - Identify root cause
   - Estimate recovery time
   - Notify stakeholders

2. **Recovery Phase**
   ```bash
   # Stop all services
   docker-compose down
   
   # Restore from backup if needed
   restore_database_backup.sh
   
   # Start services
   docker-compose up -d
   
   # Verify functionality
   run_payment_test.sh
   ```

3. **Validation Phase**
   - Process test transactions
   - Verify webhook processing
   - Check data integrity
   - Resume normal operations

### 2. Data Corruption Recovery

**Symptom Detection**
```bash
# Check for data inconsistencies
python manage.py check_payment_integrity

# Verify webhook processing
python manage.py check_webhook_status
```

**Recovery Steps**
```bash
# Backup current state
pg_dump -U DBUSER OnlineRetailPOS > corrupted_backup.sql

# Restore from last known good backup
restore_database_backup.sh

# Replay missing transactions from Stripe
python manage.py sync_stripe_data --from="2024-01-01"
```

### 3. Security Incident Response

**Immediate Response**
1. **Isolate affected systems**
2. **Preserve evidence**
3. **Notify security team**
4. **Begin incident log**

**Investigation Steps**
```bash
# Check access logs for suspicious activity
grep -E "(failed|suspicious|unusual)" logs/payment_access.log

# Verify API key integrity
check_api_key_usage.sh

# Review recent configuration changes
git log --oneline --since="7 days ago" payments/
```

**Recovery Actions**
1. **Rotate API keys** if compromised
2. **Update webhook secrets**
3. **Implement additional monitoring**
4. **Conduct security review**

## Prevention Strategies

### 1. Proactive Monitoring

**Automated Alerts**
- Payment success rate drops below threshold
- Processing latency exceeds limits
- Error rate increases significantly
- System resource utilization high
- Webhook processing failures

**Regular Health Checks**
- Daily system health verification
- Weekly performance analysis
- Monthly security reviews
- Quarterly disaster recovery testing

### 2. Capacity Planning

**Load Testing**
```bash
# Simulate high transaction volume
python manage.py load_test_payments --transactions=1000 --concurrent=50

# Monitor system behavior under load
monitor_system_during_load_test.sh
```

**Resource Scaling**
- Monitor payment volume trends
- Plan for peak periods (holidays, sales)
- Implement auto-scaling if using cloud
- Maintain resource buffer for spikes

### 3. Documentation Maintenance

**Keep Updated**
- Error code references
- Troubleshooting procedures
- Contact information
- System configurations

**Regular Reviews**
- Monthly procedure validation
- Quarterly documentation updates
- Annual system architecture review
- Continuous improvement feedback

## Contact and Escalation

### Internal Contacts
- **Level 1 Support**: ext. 2200
- **System Administrator**: ext. 2201  
- **Database Administrator**: ext. 2202
- **Security Team**: security@company.com
- **DevOps Team**: devops@company.com

### External Contacts
- **Stripe Technical Support**: https://support.stripe.com
- **Internet Service Provider**: 1-800-XXX-XXXX
- **SSL Certificate Provider**: support@certprovider.com
- **Hosting Provider**: support@hosting.com

### Escalation Matrix

| Issue Severity | Response Time | Contact Level | Authority |
|----------------|---------------|---------------|-----------|
| Critical (System Down) | 15 minutes | On-call Engineer | Full access |
| High (Payment Failures) | 1 hour | Senior Support | Limited restart |
| Medium (Performance) | 4 hours | Support Team | Monitoring only |
| Low (Minor Issues) | Next business day | Regular Support | Documentation |

---

*This troubleshooting guide should be regularly updated based on new issues discovered and solutions developed. All technical staff should be familiar with these procedures and contact information should be kept current.*
