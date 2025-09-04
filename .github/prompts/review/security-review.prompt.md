```prompt
---
mode: ask
context: review
description: "Comprehensive security review checklist for Django POS system code changes"
tools: ["read_file", "grep_search", "semantic_search", "get_errors"]
instructions: ["security-requirements", "django-guidelines", "pos-business-rules"]
---

# Security Review Prompt

You are conducting a security review for code changes in the Ireti POS Light system, a Django-based Point of Sale application handling sensitive financial and customer data.

## Security Review Framework

### 1. Risk Assessment
- **Data Sensitivity**: Identify what sensitive data is being processed (payment info, customer data, financial records)
- **Attack Surface**: Analyze new or modified endpoints, forms, and data flows
- **Privilege Changes**: Review any changes to user permissions or access controls
- **Integration Points**: Assess security of external integrations and APIs

### 2. Threat Modeling
- **Authentication Bypass**: Could an attacker bypass login mechanisms?
- **Authorization Flaws**: Can users access data or functions they shouldn't?
- **Data Exposure**: Is sensitive information leaked through logs, errors, or responses?
- **Input Validation**: Are all inputs properly validated and sanitized?

## Critical Security Areas for POS Systems

### Payment Security
- **PCI DSS Compliance**: Ensure payment card data handling meets PCI DSS requirements
- **Data Encryption**: Verify sensitive data is encrypted at rest and in transit
- **Key Management**: Review cryptographic key storage and rotation
- **Payment Processing**: Validate secure payment gateway integration

### Authentication & Authorization
- **Password Security**: Strong password policies and secure storage (hashing)
- **Session Management**: Secure session handling and timeout mechanisms
- **Multi-Factor Authentication**: Implement MFA for privileged accounts
- **Role-Based Access**: Proper role separation (cashier, manager, admin)

### Data Protection
- **Personal Data**: Customer information protection and privacy compliance
- **Financial Data**: Transaction data integrity and confidentiality
- **Audit Logging**: Comprehensive logging of security-relevant events
- **Data Retention**: Secure data cleanup and retention policies

## Django Security Checklist

### Input Validation & Sanitization
```python
# Check for proper form validation
class PaymentForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    # Ensure all inputs are validated
```

### SQL Injection Prevention
```python
# BAD: Raw SQL with user input
cursor.execute("SELECT * FROM products WHERE name = '%s'" % product_name)

# GOOD: Parameterized queries
Product.objects.filter(name=product_name)
```

### Cross-Site Scripting (XSS) Prevention
- **Template Escaping**: Verify Django's auto-escaping is enabled
- **User Content**: All user-generated content is properly escaped
- **JavaScript**: Dynamic JavaScript generation is secure

### Cross-Site Request Forgery (CSRF) Protection
- **CSRF Tokens**: All forms include proper CSRF protection
- **API Endpoints**: REST API endpoints have appropriate CSRF handling
- **AJAX Requests**: AJAX calls include CSRF tokens

### Access Control
```python
# Check for proper permission decorators
@login_required
@permission_required('inventory.change_product')
def update_product(request, product_id):
    # Verify object-level permissions
    product = get_object_or_404(Product, id=product_id)
```

## POS-Specific Security Concerns

### Transaction Security
- **Atomic Operations**: Financial transactions are properly atomic
- **Double-Spending Prevention**: Inventory can't be oversold
- **Receipt Integrity**: Receipt data can't be tampered with
- **Refund Controls**: Proper authorization for refunds and voids

### Multi-User Environment
- **Concurrent Access**: Multiple cashiers can't interfere with each other
- **Session Isolation**: User sessions are properly isolated
- **Privilege Escalation**: Users can't elevate their permissions
- **Data Segregation**: Proper data separation between stores/locations

### Hardware Integration
- **Cash Drawer**: Secure cash drawer controls
- **Barcode Scanner**: Input validation for scanned data
- **Receipt Printer**: Secure printing queue management
- **Payment Terminal**: Secure communication with payment devices

## Security Code Review Checklist

### Authentication Review
- [ ] Password complexity requirements enforced
- [ ] Account lockout mechanisms in place
- [ ] Session timeout configured appropriately
- [ ] Secure password reset functionality
- [ ] Two-factor authentication where required

### Authorization Review
- [ ] Role-based access control properly implemented
- [ ] Object-level permissions checked
- [ ] Principle of least privilege followed
- [ ] Admin functions properly protected
- [ ] API endpoints have proper authorization

### Input Validation Review
- [ ] All user inputs validated server-side
- [ ] File uploads restricted and validated
- [ ] SQL injection prevention mechanisms
- [ ] Command injection prevention
- [ ] Path traversal prevention

### Data Protection Review
- [ ] Sensitive data encrypted at rest
- [ ] Secure communication (HTTPS/TLS)
- [ ] Proper key management
- [ ] Secure configuration management
- [ ] Logging doesn't expose sensitive data

### Error Handling Review
- [ ] Error messages don't leak sensitive information
- [ ] Proper exception handling
- [ ] Security logging for failed attempts
- [ ] Graceful degradation for security failures

## Common POS Security Vulnerabilities

### Business Logic Flaws
- **Negative Amounts**: Can users enter negative transaction amounts?
- **Discount Abuse**: Are discount calculations properly validated?
- **Inventory Manipulation**: Can inventory be artificially inflated?
- **Time Manipulation**: Are timestamps properly validated?

### Data Leakage
- **Log Files**: Do logs contain sensitive information?
- **Error Messages**: Do errors expose system internals?
- **API Responses**: Do responses include unnecessary sensitive data?
- **Debug Information**: Is debug mode disabled in production?

### Privilege Issues
- **Horizontal Privilege Escalation**: Can cashiers access other cashiers' data?
- **Vertical Privilege Escalation**: Can users gain admin privileges?
- **Bypass Mechanisms**: Can security controls be bypassed?

## Security Testing Recommendations

### Automated Security Testing
- **Static Analysis**: Use tools like bandit for Python security analysis
- **Dependency Scanning**: Check for vulnerable dependencies
- **SAST/DAST**: Static and dynamic application security testing
- **Secret Scanning**: Ensure no hardcoded secrets in code

### Manual Security Testing
- **Penetration Testing**: Regular professional security assessments
- **Code Review**: Peer review with security focus
- **Threat Modeling**: Regular threat model updates
- **Red Team Exercises**: Simulated attacks on the system

## Compliance Considerations

### PCI DSS Requirements
- **Secure Network**: Firewall configuration and network segmentation
- **Protect Cardholder Data**: Encryption and tokenization
- **Vulnerability Management**: Regular security updates and patches
- **Access Control**: Strict access controls and monitoring

### Privacy Regulations
- **GDPR/CCPA**: Customer data protection and privacy rights
- **Data Minimization**: Collect only necessary customer information
- **Consent Management**: Proper consent mechanisms for data collection
- **Right to Deletion**: Ability to delete customer data on request

## Security Incident Response
- **Detection**: Proper monitoring and alerting for security events
- **Response Plan**: Clear incident response procedures
- **Communication**: Stakeholder notification procedures
- **Recovery**: Business continuity and disaster recovery plans

Remember: Security is not a one-time check but an ongoing process. Regular security reviews, updates, and monitoring are essential for maintaining a secure POS system.
```
