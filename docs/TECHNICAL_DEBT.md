# Technical Debt Backlog

## 🔐 Authentication & Security Improvements

### TD-001: Password Reset Workflow
**Priority**: Medium  
**Effort**: 2-3 days  
**Description**: Implement proper password reset functionality for admin users

**Current State**: 
- Admin password is hardcoded as `admin123` 
- No self-service password reset capability
- Users must manually reset via Django admin or shell

**Proposed Solution**:
1. **Password Reset Form**: Create `/user/password-reset/` endpoint
2. **Email Integration**: Configure email backend for reset links
3. **Reset Token System**: Secure token-based password reset
4. **UI Components**: 
   - "Forgot Password?" link on login page
   - Password reset request form
   - Password reset confirmation form
5. **Security Features**:
   - Token expiration (15-30 minutes)
   - Rate limiting on reset requests
   - Secure token generation

**Implementation Steps**:
```python
# URLs to add
urlpatterns = [
    path('user/password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('user/password-reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('user/reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('user/reset/done/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
```

**Templates Needed**:
- `registration/password_reset_form.html`
- `registration/password_reset_email.html`
- `registration/password_reset_done.html`
- `registration/password_reset_confirm.html`
- `registration/password_reset_complete.html`

**Configuration Required**:
- Email backend setup (SMTP/SendGrid/etc.)
- EMAIL_HOST, EMAIL_PORT, EMAIL_USE_TLS settings
- Email templates styling

**Testing Checklist**:
- [ ] Reset request sends email
- [ ] Token links work correctly
- [ ] Expired tokens are rejected
- [ ] Rate limiting prevents abuse
- [ ] Email templates render properly
- [ ] Mobile responsive forms

**Related Issues**: Security hardening, user experience improvement

---

## 🚀 Other Technical Debt Items

### TD-002: Production Configuration Management
**Priority**: High  
**Effort**: 1 day  
**Description**: Separate development and production settings properly

### TD-003: Error Logging & Monitoring
**Priority**: Medium  
**Effort**: 2 days  
**Description**: Implement proper error logging and system monitoring

### TD-004: Performance Optimization
**Priority**: Low  
**Effort**: 3-5 days  
**Description**: Database query optimization and caching implementation

### TD-005: Comprehensive Testing Suite
**Priority**: Medium  
**Effort**: 1 week  
**Description**: Unit tests, integration tests, and automated testing pipeline

### TD-006: API Documentation
**Priority**: Low  
**Effort**: 2-3 days  
**Description**: Document any exposed APIs with OpenAPI/Swagger

### TD-007: Advanced PWA Features
**Priority**: Low  
**Effort**: 1 week  
**Description**: Enhanced offline functionality, background sync, push notifications

---

## 📝 Notes
- Items marked as High priority should be addressed before next major release
- Medium priority items can be tackled based on user feedback
- Low priority items are nice-to-have improvements

**Last Updated**: August 11, 2025  
**Next Review**: After MVP feedback collection
