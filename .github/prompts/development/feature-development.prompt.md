```prompt
---
mode: generate
context: development
description: "Comprehensive guidance for implementing new features in the Django POS system"
tools: ["semantic_search", "read_file", "create_file", "replace_string_in_file", "run_notebook_cell", "runTests"]
instructions: ["django-guidelines", "pos-business-rules", "security-requirements"]
---

# Feature Development Prompt

You are implementing a new feature for the Ireti POS Light system, a Django 4.1.13-based Point of Sale application with PWA capabilities.

## Context Analysis
1. **Understand the Feature Requirements**
   - Review the feature specification thoroughly
   - Identify business logic requirements specific to POS operations
   - Consider multi-language support (i18n) implications
   - Evaluate PWA offline functionality needs

2. **Analyze Existing Codebase**
   - Search for similar existing functionality using semantic_search
   - Review related models in cart/, inventory/, transaction/ apps
   - Examine existing views and templates for patterns
   - Check current database schema and migrations

## Implementation Approach

### 1. Database Design
- Design models following Django best practices
- Consider POS-specific requirements (transactions, inventory tracking, user roles)
- Plan for data integrity and concurrent access
- Include proper indexes for performance

### 2. Backend Implementation
- Create models with appropriate relationships
- Implement views using Django class-based views when appropriate
- Add proper error handling and validation
- Include logging for audit trails (important for POS systems)

### 3. Frontend Integration
- Use existing templates/base.html structure
- Maintain PWA compatibility
- Implement responsive design for various screen sizes
- Consider customer display screen requirements

### 4. Security Considerations
- Implement proper authentication and authorization
- Validate all inputs (especially financial data)
- Follow OWASP guidelines for web security
- Consider PCI compliance for payment-related features

## Testing Strategy
1. **Unit Tests** - Create comprehensive unit tests for models and business logic
2. **Integration Tests** - Test API endpoints and database interactions
3. **E2E Tests** - Test complete user workflows
4. **PWA Tests** - Verify offline functionality and service worker behavior

## Code Quality Checklist
- [ ] Follow Django coding conventions
- [ ] Include proper docstrings and comments
- [ ] Implement error handling and logging
- [ ] Add internationalization strings where needed
- [ ] Validate against existing code style
- [ ] Ensure PostgreSQL compatibility
- [ ] Test PWA offline behavior

## POS-Specific Considerations
- Transaction atomicity for financial operations
- Inventory tracking and real-time updates
- User role-based access (cashier, manager, admin)
- Receipt generation and printing
- Tax calculations and reporting
- Multi-store support considerations

## Deployment Notes
- Ensure Docker compatibility
- Consider database migration impacts
- Plan for zero-downtime deployment
- Document any new environment variables
- Update docker-compose configurations if needed

Remember to maintain consistency with existing code patterns and architectural decisions while implementing the new feature.
```
