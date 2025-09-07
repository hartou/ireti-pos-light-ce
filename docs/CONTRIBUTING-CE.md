# Contributing to Ireti POS Light Community Edition

Welcome! We're excited that you want to contribute to the Ireti POS Light Community Edition. This document provides guidelines and information about contributing to the project.

## 🎯 Project Vision

Ireti POS Light CE aims to be the **most developer-friendly, secure, and feature-complete open-source Point of Sale system**. We're building a community-driven platform that empowers small businesses with enterprise-grade POS capabilities.

## 🚀 Quick Start for Contributors

### Prerequisites
- Python 3.8+
- Node.js 16+ (for E2E testing)
- Docker (optional, for container testing)
- Git

### Setting Up Development Environment

```bash
# 1. Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/ireti-pos-light-ce.git
cd ireti-pos-light-ce

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
npm install  # For E2E tests

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your Stripe test keys

# 5. Run migrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Run development server
python manage.py runserver

# 8. Run tests
python manage.py test
npm test  # E2E tests
```

## 🤝 Ways to Contribute

### 🐛 Bug Reports
- **Search existing issues** before creating new ones
- **Use the bug report template** when filing issues
- **Include reproduction steps** and environment details
- **Add relevant labels** and assign to appropriate milestone

### ✨ Feature Requests
- **Check roadmap** first to avoid duplicate requests
- **Use the feature request template**
- **Provide clear use cases** and business justification
- **Consider backward compatibility** implications

### 💻 Code Contributions
- **Start with good first issues** labeled `good-first-issue`
- **Follow coding standards** (PEP 8 for Python, ESLint for JavaScript)
- **Write tests** for all new features and bug fixes
- **Update documentation** when adding features
- **Keep PRs focused** - one feature/fix per PR

### 📚 Documentation
- **Fix typos and improve clarity**
- **Add examples and tutorials**
- **Update API documentation**
- **Translate to other languages**

## 🔄 Development Workflow

### 1. **Issue-First Development**
- **Every contribution should address an issue**
- **Comment on issues** before starting work
- **Link PRs to issues** using GitHub keywords

### 2. **Branch Naming Convention**
```bash
feature/issue-number-short-description    # New features
bugfix/issue-number-short-description     # Bug fixes
docs/issue-number-short-description       # Documentation
refactor/issue-number-short-description   # Code refactoring
```

### 3. **Commit Message Format**
```
type(scope): short description

Longer description if needed

Fixes #issue-number
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Examples**:
```
feat(payments): add support for payment methods
fix(admin): resolve dashboard loading issue
docs(readme): update installation instructions
```

### 4. **Pull Request Process**

#### Before Submitting
- [ ] **Code follows style guidelines**
- [ ] **All tests pass** (`python manage.py test` and `npm test`)
- [ ] **New tests added** for features/fixes
- [ ] **Documentation updated** if needed
- [ ] **No merge conflicts** with main branch
- [ ] **Self-review completed**

#### PR Description Template
```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] E2E tests pass
- [ ] Manual testing completed

## Screenshots (if applicable)
Add screenshots for UI changes.

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Tests added/updated
- [ ] Documentation updated

Fixes #issue-number
```

## 🧪 Testing Guidelines

### **Unit Tests** (Required)
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test payments

# Run with coverage
coverage run manage.py test
coverage report
```

### **E2E Tests** (Required for UI changes)
```bash
# Run all E2E tests
npm test

# Run specific test
npx playwright test tests/payment-flow.spec.ts

# Run in headed mode (browser visible)
npx playwright test --headed
```

### **Manual Testing** (Recommended)
- Test payment flow with Stripe test cards
- Verify responsive design on mobile/tablet
- Check cross-browser compatibility
- Test admin functionality

## 📋 Code Style Guidelines

### **Python (Backend)**
- **Follow PEP 8** style guide
- **Use type hints** for function parameters and returns
- **Maximum line length**: 88 characters (Black formatter)
- **Use meaningful variable names**
- **Add docstrings** for classes and functions

```python
def process_payment(amount: Decimal, payment_method: str) -> PaymentResult:
    """
    Process a payment using the specified method.
    
    Args:
        amount: Payment amount in decimal format
        payment_method: Payment method identifier
        
    Returns:
        PaymentResult object with success status and details
    """
    # Implementation here
```

### **JavaScript (Frontend)**
- **Use modern ES6+ syntax**
- **Follow ESLint configuration**
- **Use camelCase** for variables and functions
- **Add JSDoc comments** for complex functions

```javascript
/**
 * Initialize Stripe payment form
 * @param {string} publishableKey - Stripe publishable key
 * @param {Object} options - Configuration options
 * @returns {Promise<StripeInstance>} Configured Stripe instance
 */
async function initializeStripeForm(publishableKey, options) {
    // Implementation here
}
```

### **CSS/SCSS**
- **Use Bootstrap classes** when possible
- **Follow BEM methodology** for custom classes
- **Mobile-first responsive design**
- **Use CSS custom properties** for theming

## 🛡️ Security Guidelines

### **Security-First Development**
- **Never commit secrets** (API keys, passwords)
- **Use environment variables** for configuration
- **Validate all user inputs**
- **Follow OWASP guidelines**
- **Regular dependency updates**

### **Stripe Integration Security**
- **Use Stripe test keys** in development
- **Never log sensitive payment data**
- **Validate webhooks** with signature verification
- **Use HTTPS** in production

## 🏷️ Issue Labels

### **Type Labels**
- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Improvements or additions to docs
- `good-first-issue` - Good for newcomers
- `help-wanted` - Extra attention is needed

### **Priority Labels**
- `priority: high` - Critical issues
- `priority: medium` - Important issues
- `priority: low` - Nice-to-have improvements

### **Component Labels**
- `payments` - Stripe/payment related
- `admin` - Admin interface
- `ui/ux` - User interface improvements
- `api` - Backend API changes
- `docker` - Container/deployment related

## 🎖️ Recognition

### **Contributor Recognition**
- **Contributors listed** in README.md
- **Special badges** for significant contributions
- **Annual contributor highlights**
- **Conference speaking opportunities**

### **Maintainer Pathway**
Active contributors may be invited to become maintainers with:
- **Commit access** to repository
- **Issue triage** responsibilities
- **PR review** authority
- **Release management** participation

## 📞 Getting Help

### **Community Channels**
- **GitHub Discussions**: General questions and community chat
- **GitHub Issues**: Bug reports and feature requests
- **Discord Server**: Real-time community support (coming soon)

### **Maintainer Contact**
- **@hartou**: Project maintainer and founder
- **Response time**: Usually within 24-48 hours

## 📜 Code of Conduct

This project adheres to our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code. Please report unacceptable behavior to the maintainers.

## 📄 License

By contributing to Ireti POS Light CE, you agree that your contributions will be licensed under the [MIT License](LICENSE).

## 🙏 Thank You

Thank you for contributing to Ireti POS Light Community Edition! Every contribution, no matter how small, makes a difference in building a better POS solution for small businesses worldwide.

---

**Happy Coding! 🚀**

For more detailed technical documentation, see our [Technical Documentation](docs/) and [API Reference](docs/api/).
