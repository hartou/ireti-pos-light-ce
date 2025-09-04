```prompt
---
mode: ask
context: review
description: "Comprehensive code quality review focusing on maintainability, readability, and best practices"
tools: ["read_file", "grep_search", "semantic_search", "get_errors", "list_code_usages"]
instructions: ["code-style", "django-guidelines", "performance-standards"]
---

# Code Quality Review Prompt

You are conducting a comprehensive code quality review for the Ireti POS Light system to ensure maintainability, readability, and adherence to best practices.

## Code Quality Framework

### 1. Quality Dimensions
- **Readability**: Code is clear and easy to understand
- **Maintainability**: Code is easy to modify and extend
- **Reliability**: Code handles errors gracefully and behaves predictably
- **Performance**: Code meets performance requirements and is efficiently written
- **Testability**: Code is designed to be easily testable

### 2. Review Scope Assessment
- **Change Impact**: Analyze the scope and impact of code changes
- **Complexity**: Evaluate cyclomatic complexity and cognitive load
- **Dependencies**: Review new dependencies and their implications
- **Architecture Alignment**: Ensure changes align with system architecture

## Django Code Quality Standards

### Model Quality
```python
# Good: Clear, well-documented model
class Product(models.Model):
    """Product model for inventory management."""
    
    name = models.CharField(max_length=200, help_text="Product display name")
    barcode = models.CharField(
        max_length=50, 
        unique=True, 
        db_index=True,
        help_text="Unique product barcode"
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['barcode']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.barcode})"
    
    def get_absolute_url(self):
        return reverse('product-detail', args=[str(self.id)])
```

### View Quality
```python
# Good: Clean, focused class-based view
class ProductListView(LoginRequiredMixin, ListView):
    """Display paginated list of products."""
    
    model = Product
    template_name = 'inventory/product_list.html'
    context_object_name = 'products'
    paginate_by = 25
    
    def get_queryset(self):
        """Filter products based on search query."""
        queryset = Product.objects.select_related('category')
        search = self.request.GET.get('search')
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(barcode__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context
```

### Template Quality
```html
<!-- Good: Clean, semantic template -->
{% extends "base.html" %}
{% load i18n %}

{% block title %}{% trans "Products" %}{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <div class="col-12">
            <h1>{% trans "Product Inventory" %}</h1>
            
            <!-- Search Form -->
            <form method="get" class="mb-3">
                <div class="input-group">
                    <input type="text" name="search" 
                           value="{{ search_query }}" 
                           placeholder="{% trans 'Search products...' %}"
                           class="form-control">
                    <button type="submit" class="btn btn-primary">
                        {% trans "Search" %}
                    </button>
                </div>
            </form>
            
            <!-- Product Table -->
            {% include "inventory/product_table.html" %}
        </div>
    </div>
</div>
{% endblock %}
```

## Code Quality Checklist

### Readability Review
- [ ] **Naming Conventions**: Variables, functions, and classes have descriptive names
- [ ] **Code Comments**: Complex logic is well-commented
- [ ] **Documentation**: Public APIs have proper docstrings
- [ ] **Code Structure**: Logical organization and appropriate indentation
- [ ] **Magic Numbers**: No hardcoded values, constants are named

### Maintainability Review
- [ ] **DRY Principle**: No unnecessary code duplication
- [ ] **Single Responsibility**: Functions and classes have single, clear purposes
- [ ] **Loose Coupling**: Components are not tightly coupled
- [ ] **High Cohesion**: Related functionality is grouped together
- [ ] **Configuration**: Hardcoded values moved to settings

### Error Handling Review
- [ ] **Exception Handling**: Appropriate try-catch blocks
- [ ] **Graceful Degradation**: System handles errors gracefully
- [ ] **Logging**: Appropriate logging for debugging and monitoring
- [ ] **Input Validation**: All inputs are validated
- [ ] **Error Messages**: User-friendly error messages

### Performance Review
- [ ] **Database Queries**: Optimized ORM usage
- [ ] **Algorithmic Complexity**: Efficient algorithms used
- [ ] **Resource Usage**: Memory and CPU usage optimized
- [ ] **Caching**: Appropriate caching strategies
- [ ] **Lazy Loading**: Resources loaded only when needed

## POS-Specific Quality Considerations

### Business Logic Quality
- **Transaction Integrity**: Business rules properly enforced
- **Data Consistency**: State changes maintain data integrity
- **Concurrent Access**: Thread-safe operations for multi-user scenarios
- **Audit Trail**: Proper logging for financial operations

### User Interface Quality
- **Workflow Efficiency**: Streamlined cashier operations
- **Error Prevention**: UI prevents common user errors
- **Accessibility**: Interface is accessible to all users
- **Responsive Design**: Works well on different screen sizes

### Integration Quality
- **API Design**: Clean, consistent API interfaces
- **Error Handling**: Robust handling of external service failures
- **Data Validation**: Proper validation of external data
- **Monitoring**: Adequate logging for integration points

## Common Code Quality Issues

### Anti-Patterns to Avoid
```python
# BAD: God class with too many responsibilities
class POS:
    def process_sale(self): pass
    def manage_inventory(self): pass
    def generate_reports(self): pass
    def handle_payments(self): pass
    def manage_users(self): pass

# GOOD: Separated concerns
class SaleProcessor: pass
class InventoryManager: pass
class ReportGenerator: pass
```

### Complexity Issues
- **Cyclomatic Complexity**: Functions should have reasonable complexity
- **Nested Conditionals**: Avoid deep nesting, use early returns
- **Long Functions**: Break down large functions into smaller ones
- **Large Classes**: Split large classes into focused components

### Testing Quality
- **Test Coverage**: Adequate test coverage for critical paths
- **Test Quality**: Tests are focused and test one thing at a time
- **Test Maintainability**: Tests are easy to understand and maintain
- **Mock Usage**: Appropriate use of mocks and test doubles

## Code Metrics and Thresholds

### Complexity Metrics
- **Cyclomatic Complexity**: < 10 for functions
- **Lines of Code**: Functions < 50 lines, classes < 500 lines
- **Parameter Count**: Functions < 5 parameters
- **Nested Depth**: < 4 levels of nesting

### Quality Metrics
- **Test Coverage**: > 80% code coverage
- **Documentation Coverage**: All public APIs documented
- **Code Duplication**: < 5% duplicated code
- **Technical Debt**: Manageable technical debt ratio

## Automated Quality Tools

### Static Analysis Tools
- **flake8**: Python style guide enforcement
- **pylint**: Comprehensive Python code analysis
- **black**: Automatic code formatting
- **isort**: Import statement organization
- **mypy**: Static type checking

### Django-Specific Tools
- **django-extensions**: Django development utilities
- **django-debug-toolbar**: Development debugging
- **django-silk**: Profiling and monitoring
- **safety**: Dependency vulnerability checking

## Review Process

### Pre-Review Preparation
1. **Automated Checks**: Ensure all automated quality checks pass
2. **Test Execution**: All tests pass and coverage is adequate
3. **Documentation**: Code changes are properly documented
4. **Self-Review**: Developer has reviewed their own changes

### Review Focus Areas
1. **Business Logic**: Verify correctness of POS-specific functionality
2. **Security**: Check for security vulnerabilities
3. **Performance**: Identify potential performance issues
4. **Maintainability**: Assess long-term code maintainability

### Review Outcome
- **Approve**: Code meets quality standards
- **Request Changes**: Specific improvements needed
- **Comment**: Suggestions for future improvements
- **Follow-up**: Schedule follow-up reviews if needed

## Continuous Quality Improvement

### Quality Monitoring
- Regular code quality assessments
- Tracking quality metrics over time
- Team code quality training
- Knowledge sharing sessions

### Process Improvement
- Regular review process evaluation
- Tool evaluation and adoption
- Coding standard updates
- Best practice documentation

Remember: Code quality review is not just about finding problems but also about sharing knowledge and improving the overall codebase quality.
```
