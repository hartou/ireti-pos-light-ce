```prompt
---
mode: chat
context: development
description: "Systematic approach to debugging and resolving issues in the Django POS system"
tools: ["semantic_search", "read_file", "get_errors", "run_in_terminal", "grep_search", "runTests", "get_terminal_output"]
instructions: ["django-guidelines", "pos-business-rules"]
---

# Bug Fix Prompt

You are debugging and fixing a bug in the Ireti POS Light system. Follow this systematic approach to identify, isolate, and resolve the issue.

## Initial Investigation

### 1. Problem Understanding
- **Reproduce the Issue**: Verify the exact steps to reproduce the bug
- **Impact Assessment**: Determine how critical this bug is to POS operations
- **User Context**: Understand which user roles are affected (cashier, manager, admin)
- **Environment**: Identify if this occurs in development, staging, or production

### 2. Error Analysis
- Use `get_errors` to check for compile/lint errors in related files
- Check Django logs for error messages and stack traces
- Review browser console for JavaScript/PWA-related errors
- Examine database logs for SQL errors or constraints violations

## Root Cause Investigation

### 1. Code Analysis
- Use `semantic_search` to find related code that might be causing the issue
- Use `grep_search` to locate error messages, exception handling, or related patterns
- Review recent changes in git history that might have introduced the bug
- Check model relationships and database constraints

### 2. Data Investigation
- Verify database state and data integrity
- Check for missing migrations or schema mismatches
- Review transaction logs for data corruption
- Validate foreign key relationships and constraints

### 3. Environment Factors
- Check Docker container health and resource usage
- Verify environment variables and configuration
- Review nginx/web server logs for request/response issues
- Check PWA service worker and caching behavior

## Bug Classification

### Critical Bugs (Fix Immediately)
- Payment processing failures
- Data corruption or loss
- Security vulnerabilities
- System crashes or unavailability

### High Priority Bugs
- Incorrect calculations (tax, totals, discounts)
- Inventory tracking errors
- User authentication issues
- Report generation failures

### Medium Priority Bugs
- UI/UX issues affecting workflow
- Performance degradation
- Internationalization problems
- PWA offline functionality issues

### Low Priority Bugs
- Minor display inconsistencies
- Non-critical feature malfunctions
- Documentation errors
- Development environment issues

## Fix Implementation

### 1. Solution Design
- Plan the minimal fix that addresses the root cause
- Consider backward compatibility and data migration needs
- Design rollback strategy if the fix fails
- Document the change rationale

### 2. Code Changes
- Make targeted changes with minimal scope
- Follow existing code patterns and conventions
- Add appropriate error handling and validation
- Include logging for future debugging

### 3. Testing Approach
- Create test cases that reproduce the original bug
- Verify the fix resolves the issue completely
- Test related functionality for regression
- Validate PWA behavior and offline functionality

## Validation Checklist

### Technical Validation
- [ ] Bug is completely resolved
- [ ] No regression in related functionality
- [ ] All existing tests pass
- [ ] New tests added for the bug scenario
- [ ] Code follows project conventions
- [ ] Proper error handling implemented

### Business Validation
- [ ] POS workflow functions correctly
- [ ] Financial calculations remain accurate
- [ ] User experience is not degraded
- [ ] Security is maintained
- [ ] Performance impact is acceptable

### Deployment Validation
- [ ] Database migrations work correctly
- [ ] Docker build succeeds
- [ ] Environment configurations updated
- [ ] Documentation updated
- [ ] Rollback plan tested

## POS-Specific Considerations
- **Transaction Integrity**: Ensure financial transactions remain atomic
- **Inventory Accuracy**: Verify stock levels are correctly maintained
- **User Sessions**: Check for session management issues
- **Receipt Generation**: Test printing and receipt formatting
- **Multi-User Access**: Verify concurrent user scenarios work properly

## Documentation
- Update comments and docstrings as needed
- Add issue resolution to CHANGELOG.md
- Document any configuration changes
- Update troubleshooting guides if applicable

## Post-Fix Monitoring
- Monitor error logs after deployment
- Track related metrics and performance
- Verify user feedback on the resolution
- Plan follow-up improvements if needed

Remember: Always test thoroughly in a staging environment before deploying bug fixes to production, especially for critical POS functionality.
```
