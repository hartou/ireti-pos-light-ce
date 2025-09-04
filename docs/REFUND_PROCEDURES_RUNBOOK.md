# Refund Processing Procedures

## Overview

This document provides comprehensive procedures for processing refunds in the Ireti POS Light system. It covers authorization requirements, step-by-step processes, troubleshooting, and compliance considerations for refund management.

## Refund Authorization Matrix

### Authorization Levels

| Refund Amount | Authorization Required | Processing Time | Additional Requirements |
|---------------|----------------------|----------------|------------------------|
| $0.01 - $50.00 | Cashier | Immediate | Customer receipt |
| $50.01 - $200.00 | Shift Supervisor | Immediate | Customer receipt + ID |
| $200.01 - $500.00 | Store Manager | Same day | Customer receipt + ID + Manager approval |
| $500.01 - $2,000.00 | Regional Manager | 24-48 hours | Customer receipt + ID + Written justification |
| $2,000.01+ | Corporate Approval | 3-5 business days | Full documentation + Investigation |

### Special Circumstances

**Immediate Manager Override Required:**
- Refunds without original receipt
- Refunds after 30-day policy limit
- Damaged or defective merchandise
- Customer service escalations
- Suspected fraud or abuse

**Corporate Approval Required:**
- Refunds over $2,000
- Multiple refunds to same customer (>$1,000 total)
- Refunds older than 90 days
- Legal or regulatory requirements

## Standard Refund Procedures

### 1. Pre-Refund Verification

#### Customer Information Verification
1. **Required Documents**
   - Original receipt or transaction ID
   - Valid government-issued photo ID
   - Credit card used for original purchase (if available)

2. **Transaction Lookup**
   ```
   1. Access Payments Dashboard
   2. Search by transaction ID, date, or amount
   3. Verify transaction details match customer request
   4. Check refund eligibility and remaining refundable amount
   5. Review original payment method
   ```

3. **Eligibility Checks**
   - Transaction status is "succeeded"
   - Within refund time limit (default: 120 days from Stripe)
   - Sufficient refundable amount remaining
   - No previous disputes or chargebacks
   - Meets company refund policy requirements

#### Return Policy Verification
- **Standard Policy**: 30 days from purchase date
- **Extended Policy**: 60 days for defective items
- **No Refund Items**: Final sale, digital goods, custom orders
- **Partial Refund Items**: Used/opened items (per company policy)

### 2. Refund Processing Steps

#### Full Refund Process

**Step 1: Access Refund Interface**
1. Navigate to Payment Dashboard
2. Search for original transaction
3. Click on transaction ID
4. Select "Process Refund" button

**Step 2: Refund Details Entry**
```
Required Information:
- Refund Amount: $_______ (max: original transaction amount)
- Refund Reason: [dropdown selection]
  * requested_by_customer
  * duplicate
  * fraudulent
  * defective_product
  * wrong_item_shipped
  * order_cancelled
  * other (requires explanation)
- Internal Notes: [detailed explanation for records]
- Customer Notes: [information for customer receipt]
```

**Step 3: Authorization Process**
1. Enter authorization credentials (if required)
2. Get manager approval signature (if required)
3. Verify customer identity one more time
4. Confirm refund amount and reason

**Step 4: Process Refund**
1. Click "Process Refund" button
2. Wait for Stripe confirmation (typically 5-10 seconds)
3. Verify success status
4. Print customer refund receipt
5. Update internal records

#### Partial Refund Process

**When to Use Partial Refunds:**
- Customer keeps some items from original order
- Restocking fees apply
- Return items are damaged or used
- Promotional discounts need to be accounted for

**Calculation Steps:**
1. Calculate original item prices
2. Apply any applicable fees or deductions
3. Verify final refund amount
4. Document reason for partial refund
5. Process using same steps as full refund

### 3. Refund Methods and Timing

#### Refund Destinations

**Credit Card Refunds (Primary Method):**
- Refunds return to original payment method
- Processing time: 5-10 business days
- No cash refunds for card transactions
- Customer sees pending refund immediately in most cases

**Alternative Refund Methods (Manager Approval Required):**
- Store credit for lost receipts
- Gift card for returns without receipt
- Different credit card (same customer only)
- Cash refunds (limit: $50, receipt required)

#### Processing Timeline

| Refund Method | Processing Time | Customer Notification |
|---------------|----------------|---------------------|
| Same Credit Card | 5-10 business days | Immediate receipt |
| Store Credit | Immediate | Immediate receipt |
| Gift Card | Immediate | Card issued on-site |
| Cash | Immediate | Receipt required |
| Different Card | 5-10 business days | Email notification |

### 4. System Operations

#### Using the POS Refund Interface

**Navigation Path:**
```
Main Dashboard → Payments → Search Transaction → Transaction Details → Process Refund
```

**Interface Elements:**
- Transaction Summary (read-only)
- Refund Amount field (editable)
- Reason dropdown (required)
- Notes fields (internal and customer)
- Authorization section (if required)
- Process/Cancel buttons

**Keyboard Shortcuts:**
- `Ctrl+F`: Find transaction
- `Ctrl+R`: Process refund (after authorization)
- `Esc`: Cancel current operation
- `F1`: Help/Documentation

#### API Processing (For Developers)

**Refund API Endpoint:**
```http
POST /payments/api/refunds/
Content-Type: application/json
Authorization: Bearer [user_token]

{
  "transaction_id": "uuid",
  "amount": "50.00",
  "reason": "requested_by_customer",
  "notes": "Customer returned item - unused condition"
}
```

**Response Format:**
```json
{
  "success": true,
  "refund_id": "re_xxxxxxxxxxxxxxxxxxxx",
  "amount": "50.00",
  "status": "succeeded",
  "estimated_arrival": "2024-02-15",
  "message": "Refund processed successfully"
}
```

### 5. Error Handling and Troubleshooting

#### Common Refund Errors

**"Refund amount exceeds refundable amount"**
- **Cause**: Requesting refund larger than available balance
- **Resolution**: Check previous refunds, verify remaining amount
- **Process**: Calculate correct amount and retry

**"Payment intent not found"**
- **Cause**: Invalid transaction ID or data corruption
- **Resolution**: Verify transaction ID, check database integrity
- **Process**: Contact technical support if persistent

**"Refund failed - insufficient funds"**
- **Cause**: Merchant account lacks sufficient balance
- **Resolution**: Contact finance team to add funds
- **Process**: Retry refund after account funding

**"Customer card expired or invalid"**
- **Cause**: Original payment card no longer valid
- **Resolution**: Issue store credit or process to different card
- **Process**: Get customer's current card information

#### Escalation Procedures

**Level 1: Cashier Issues**
- System errors or interface problems
- Customer complaints about refund processing
- Questions about refund policies
- **Escalate to**: Shift Supervisor

**Level 2: Supervisor Issues**
- Authorization problems
- System outages affecting refunds
- Customer disputes about refund amounts
- **Escalate to**: Store Manager

**Level 3: Manager Issues**
- Technical system failures
- Large refund processing problems
- Customer legal threats or complaints
- **Escalate to**: IT Support and Regional Manager

**Level 4: Corporate Issues**
- System-wide refund processing failures
- Legal or regulatory compliance issues
- Major customer disputes or media attention
- **Escalate to**: Corporate Customer Service and Legal

### 6. Compliance and Record Keeping

#### Documentation Requirements

**Required Records for All Refunds:**
- Original transaction details
- Refund amount and reason
- Authorization signatures (if required)
- Customer identification verification
- Refund processing timestamp
- System confirmation number

**Retention Periods:**
- Transaction records: 7 years
- Refund receipts: 3 years
- Customer identification: 1 year
- Authorization forms: 3 years
- System logs: 1 year

#### Audit Trail Maintenance

**System Logging:**
- All refund requests are automatically logged
- Timestamps for each processing step
- User identification for all actions
- System response codes and messages
- Customer information (anonymized)

**Manual Documentation:**
- Physical signature forms (if required)
- Customer complaint records
- Special circumstance justifications
- Manager approval documentation

### 7. Fraud Prevention

#### Red Flags for Refund Fraud

**Transaction Patterns:**
- Multiple refund requests in short timeframe
- Refunds to different cards than original payment
- High-value refunds without proper documentation
- Refunds for items reported as never received

**Customer Behavior:**
- Reluctance to provide identification
- Stories that change during interaction
- Urgency or pressure tactics
- Multiple attempts with different staff

**System Indicators:**
- IP address mismatches (for online components)
- Unusual transaction patterns
- Previously flagged customer accounts
- Chargebacks or disputes on file

#### Fraud Prevention Procedures

1. **Always verify customer identity**
2. **Check customer history for patterns**
3. **Require manager approval for suspicious cases**
4. **Document all unusual circumstances**
5. **Report suspected fraud to security team**
6. **Preserve all evidence for investigation**

### 8. Customer Service Best Practices

#### Communication Guidelines

**Positive Language:**
- "I'd be happy to help you with that refund"
- "Let me look up your transaction right away"
- "I can process this refund for you today"
- "Your refund will appear on your statement in 5-10 business days"

**Avoid Negative Language:**
- "We can't do that"
- "That's against policy"
- "You should have..."
- "There's nothing I can do"

#### De-escalation Techniques

1. **Listen actively** to customer concerns
2. **Acknowledge their frustration**
3. **Explain the process clearly**
4. **Offer alternatives when possible**
5. **Set realistic expectations**
6. **Follow up on commitments**

#### Special Situations

**Customer Without Receipt:**
1. Attempt transaction lookup by card or date
2. Explain options (store credit, gift card)
3. Get manager approval for alternative refund
4. Document reason for exception

**Damaged or Defective Items:**
1. Examine item and document condition
2. Take photos if necessary
3. Process refund according to policy
4. Report quality issues to appropriate department
5. Follow up on customer satisfaction

**International Customers:**
1. Verify currency exchange rates
2. Explain international processing times
3. Provide additional documentation if needed
4. Consider alternative refund methods

### 9. Reporting and Analytics

#### Daily Refund Reporting

**Metrics to Track:**
- Total refund volume and amount
- Refund rate percentage
- Average refund processing time
- Common refund reasons
- Staff processing statistics

**Report Generation:**
1. Access Payments Dashboard
2. Navigate to Reports section
3. Select Refund Report
4. Choose date range and filters
5. Export to CSV or PDF

#### Weekly Management Reports

**Key Performance Indicators:**
- Refund rate trends
- Customer satisfaction scores
- Processing error rates
- Staff performance metrics
- Financial impact analysis

**Management Review Items:**
- Policy effectiveness
- Staff training needs
- System improvement opportunities
- Customer feedback trends

### 10. Training and Certification

#### Staff Training Requirements

**New Employee Training:**
- Refund policy overview (2 hours)
- System operation training (4 hours)
- Customer service skills (2 hours)
- Fraud prevention awareness (1 hour)
- Hands-on practice (4 hours)

**Ongoing Training:**
- Monthly policy updates
- Quarterly system training
- Annual fraud prevention refresher
- Customer service skills development

**Certification Requirements:**
- Pass written exam (80% minimum)
- Complete practical assessment
- Manager signoff on competency
- Annual recertification required

#### Training Resources

**Documentation:**
- This refund procedures manual
- Company refund policy
- System user guides
- Fraud prevention guidelines

**Online Training:**
- E-learning modules
- Video tutorials
- Interactive simulations
- Knowledge base articles

**Practical Training:**
- Shadow experienced staff
- Practice scenarios
- Role-playing exercises
- System sandbox environment

## Emergency Procedures

### System Outage During Refund

**Immediate Actions:**
1. Document refund request on paper
2. Explain situation to customer
3. Provide estimated resolution time
4. Offer to complete when system restored
5. Contact technical support

**Manual Processing (Manager Approval Required):**
1. Complete manual refund form
2. Get customer signature
3. Process in system when restored
4. Verify completion with customer
5. File manual documentation

### Disputed Refunds

**Customer Disputes:**
1. Listen to customer concerns
2. Review transaction history
3. Explain refund process and timing
4. Escalate to manager if unresolved
5. Document all interactions

**Bank Disputes/Chargebacks:**
1. Gather all transaction documentation
2. Prepare evidence package
3. Submit response within deadline
4. Monitor dispute resolution
5. Update customer as appropriate

## Contact Information

### Internal Support
- **IT Help Desk**: ext. 2200
- **Finance Department**: ext. 1500
- **Store Manager**: ext. 1001
- **Regional Manager**: 555-0199
- **Corporate Customer Service**: 800-555-0150

### External Support
- **Stripe Support**: https://support.stripe.com
- **Merchant Services**: 800-555-0175
- **Legal Department**: legal@company.com

---

*This document should be reviewed monthly and updated after any policy changes or system updates. All staff authorized to process refunds must be trained on these procedures.*
