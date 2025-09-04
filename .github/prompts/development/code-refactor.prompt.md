```prompt
---
mode: generate
context: development
description: "Structured approach to refactoring and improving existing code in the POS system"
tools: ["semantic_search", "read_file", "replace_string_in_file", "grep_search", "runTests", "get_errors"]
instructions: ["django-guidelines", "code-style", "performance-standards"]
---

# Code Refactor Prompt

You are refactoring existing code in the Ireti POS Light system to improve maintainability, performance, or architecture while preserving functionality.

## Pre-Refactoring Analysis

### 1. Current State Assessment
- **Code Quality**: Identify code smells, duplication, or anti-patterns
- **Performance Issues**: Locate bottlenecks, inefficient queries, or resource waste
- **Technical Debt**: Document shortcuts or suboptimal implementations
- **Test Coverage**: Evaluate existing test coverage for the code to be refactored

### 2. Impact Analysis
- **Dependencies**: Map all components that depend on the code being refactored
- **User Impact**: Assess potential impact on POS operations during refactoring
- **Business Logic**: Ensure core POS functionality remains unchanged
- **Data Migration**: Identify any database schema changes needed

## Refactoring Categories

### Code Structure Improvements
- **Extract Methods**: Break down large functions into smaller, focused methods
- **Extract Classes**: Separate concerns into appropriate classes
- **Remove Duplication**: Consolidate repeated code into reusable components
- **Improve Naming**: Use clear, descriptive names for variables, methods, and classes

### Performance Optimizations
- **Database Queries**: Optimize ORM queries, reduce N+1 problems, add select_related/prefetch_related
- **Caching**: Implement appropriate caching strategies for frequently accessed data
- **Memory Usage**: Optimize data structures and reduce memory footprint
- **Response Times**: Improve API response times and page load speeds

### Architecture Improvements
- **Separation of Concerns**: Ensure models, views, and templates have clear responsibilities
- **Design Patterns**: Apply appropriate design patterns (Factory, Observer, etc.)
- **Service Layer**: Extract business logic into service classes
- **API Design**: Improve REST API structure and consistency

## Django-Specific Refactoring

### Models
- Optimize field types and indexes
- Improve model relationships and foreign keys
- Add proper validation and constraints
- Implement model managers for common queries

### Views
- Convert function-based views to class-based views where appropriate
- Implement proper error handling and logging
- Add request validation and sanitization
- Optimize template context data

### Templates
- Remove logic from templates, move to views or template tags
- Improve template inheritance and block structure
- Optimize static file loading and caching
- Ensure responsive design and PWA compatibility

## POS-Specific Refactoring Considerations

### Transaction Management
- Ensure atomic transactions for financial operations
- Implement proper rollback mechanisms
- Add transaction logging and audit trails
- Optimize concurrent transaction handling

### Inventory Management
- Improve real-time inventory tracking
- Optimize stock level calculations
- Implement efficient product lookup
- Add low-stock alerting mechanisms

### User Interface
- Streamline cashier workflows
- Improve customer display functionality
- Optimize receipt generation and printing
- Enhance offline PWA capabilities

## Refactoring Process

### 1. Preparation
- Create comprehensive tests for existing functionality
- Document current behavior and edge cases
- Set up staging environment for testing
- Create backup and rollback plan

### 2. Implementation Strategy
- **Incremental Changes**: Make small, testable changes
- **Backward Compatibility**: Maintain API compatibility where possible
- **Feature Flags**: Use feature toggles for major changes
- **Monitoring**: Add metrics and logging for refactored components

### 3. Testing Approach
- Run existing test suite after each change
- Add new tests for refactored components
- Perform integration testing with related systems
- Test PWA functionality and offline behavior

## Quality Assurance Checklist

### Code Quality
- [ ] Code follows Django and project conventions
- [ ] No code duplication or obvious inefficiencies
- [ ] Proper error handling and logging
- [ ] Clear and descriptive naming
- [ ] Appropriate comments and docstrings

### Performance
- [ ] Database queries are optimized
- [ ] No performance regressions introduced
- [ ] Memory usage is reasonable
- [ ] Response times meet performance standards

### Functionality
- [ ] All existing functionality preserved
- [ ] Business logic remains correct
- [ ] User workflows are unaffected
- [ ] Integration points still work correctly

### Maintainability
- [ ] Code is easier to understand and modify
- [ ] Components are properly separated
- [ ] Dependencies are minimized
- [ ] Documentation is updated

## Deployment Strategy

### Staged Rollout
1. **Development**: Complete testing in development environment
2. **Staging**: Full integration testing with production-like data
3. **Canary**: Deploy to limited production users first
4. **Full Deployment**: Roll out to all users with monitoring

### Monitoring Plan
- Set up alerts for performance metrics
- Monitor error rates and user feedback
- Track key business metrics (transaction success rates, etc.)
- Plan rollback procedures if issues arise

## Documentation Updates
- Update code comments and docstrings
- Refresh API documentation if interfaces changed
- Update deployment and configuration guides
- Document performance improvements achieved

Remember: The goal of refactoring is to improve code quality without changing external behavior. Always prioritize maintaining POS system reliability and performance.
```
