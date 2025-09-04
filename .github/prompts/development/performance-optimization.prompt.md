```prompt
---
mode: ask
context: development
description: "Comprehensive performance analysis and optimization for the Django POS system"
tools: ["semantic_search", "read_file", "run_in_terminal", "grep_search", "get_terminal_output", "runTests"]
instructions: ["django-guidelines", "performance-standards", "pos-business-rules"]
---

# Performance Optimization Prompt

You are analyzing and optimizing performance issues in the Ireti POS Light system. This prompt guides you through systematic performance improvement.

## Performance Analysis Framework

### 1. Problem Identification
- **Symptom Description**: Clearly define the performance issue (slow page loads, high CPU, memory leaks)
- **Impact Assessment**: Determine business impact (customer wait times, system downtime, user frustration)
- **Baseline Metrics**: Establish current performance baselines before optimization
- **Success Criteria**: Define specific, measurable performance targets

### 2. Performance Profiling
- **Request/Response Times**: Measure page load times and API response times
- **Database Performance**: Analyze query execution times and database load
- **Memory Usage**: Monitor memory consumption patterns and potential leaks
- **CPU Utilization**: Track CPU usage during peak operations

## Performance Categories

### Database Optimization

#### Query Performance
- **Slow Query Identification**: Use Django Debug Toolbar or database logs
- **N+1 Query Problems**: Identify and fix with select_related/prefetch_related
- **Index Optimization**: Add appropriate database indexes for frequently queried fields
- **Query Complexity**: Simplify complex queries or break into smaller operations

#### Database Design
- **Normalization**: Balance between normalization and query performance
- **Foreign Keys**: Optimize relationships and constraints
- **Data Types**: Use appropriate field types for performance
- **Partitioning**: Consider table partitioning for large datasets

### Application Performance

#### Django Optimization
- **View Performance**: Optimize view logic and reduce template processing time
- **Middleware**: Minimize middleware overhead and optimize custom middleware
- **Static Files**: Implement proper static file serving and compression
- **Session Management**: Optimize session storage and cleanup

#### Caching Strategy
- **Database Caching**: Implement query result caching
- **Template Caching**: Cache frequently rendered templates
- **API Response Caching**: Cache API responses for read-heavy operations
- **Redis/Memcached**: Implement distributed caching for scalability

### Frontend Performance

#### PWA Optimization
- **Service Worker**: Optimize caching strategies and asset management
- **Bundle Size**: Minimize JavaScript and CSS bundle sizes
- **Image Optimization**: Compress and optimize images for web delivery
- **Lazy Loading**: Implement lazy loading for non-critical resources

#### User Experience
- **Perceived Performance**: Improve loading animations and feedback
- **Critical Rendering Path**: Optimize CSS and JavaScript loading
- **Network Requests**: Minimize HTTP requests and optimize payload sizes
- **Offline Performance**: Ensure smooth offline functionality

## POS-Specific Performance Considerations

### Transaction Processing
- **Payment Speed**: Optimize payment processing workflows
- **Receipt Generation**: Improve receipt printing and display performance
- **Concurrent Transactions**: Handle multiple simultaneous transactions efficiently
- **Transaction History**: Optimize historical data queries and pagination

### Inventory Management
- **Stock Lookups**: Fast product search and barcode scanning
- **Real-time Updates**: Efficient inventory tracking and synchronization
- **Bulk Operations**: Optimize bulk inventory updates and imports
- **Reporting Performance**: Fast generation of sales and inventory reports

### Multi-User Performance
- **Concurrent Users**: Handle multiple cashiers and managers simultaneously
- **Session Management**: Optimize user session handling and cleanup
- **Role-Based Access**: Efficient permission checking and authorization
- **Database Locking**: Minimize database locks and contention

## Optimization Techniques

### Database Optimization
```python
# Example optimizations
# Use select_related for foreign keys
products = Product.objects.select_related('category', 'supplier')

# Use prefetch_related for reverse foreign keys
transactions = Transaction.objects.prefetch_related('items__product')

# Add database indexes
class Product(models.Model):
    barcode = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=200, db_index=True)
```

### Caching Implementation
```python
# Cache expensive calculations
@cache_memoize(timeout=300)  # 5-minute cache
def calculate_daily_sales():
    return Transaction.objects.filter(
        date__date=timezone.now().date()
    ).aggregate(total=Sum('total_amount'))
```

### Query Optimization
```python
# Before: N+1 queries
for transaction in Transaction.objects.all():
    print(transaction.customer.name)  # Database hit for each

# After: Optimized
for transaction in Transaction.objects.select_related('customer'):
    print(transaction.customer.name)  # Single query
```

## Performance Testing

### Load Testing
- **Concurrent Users**: Test with multiple simultaneous users
- **Peak Hours**: Simulate busy store periods
- **Transaction Volume**: Test with high transaction volumes
- **Data Growth**: Test performance with large datasets

### Benchmarking
- **Response Times**: Measure API and page response times
- **Throughput**: Test transactions per second capacity
- **Resource Usage**: Monitor CPU, memory, and disk usage
- **Database Performance**: Track query execution times

### Monitoring Setup
- **Application Metrics**: CPU, memory, response times
- **Database Metrics**: Query performance, connection pools
- **Business Metrics**: Transaction success rates, user satisfaction
- **Alert Thresholds**: Set up alerts for performance degradation

## Implementation Strategy

### Phase 1: Quick Wins
- Add missing database indexes
- Implement basic query optimization
- Enable gzip compression
- Optimize static file serving

### Phase 2: Systematic Optimization
- Implement caching layers
- Optimize complex queries
- Improve frontend loading
- Database connection pooling

### Phase 3: Advanced Optimization
- Consider database sharding
- Implement CDN for static assets
- Advanced caching strategies
- Microservices architecture

## Validation and Testing

### Performance Validation
- [ ] Performance targets met
- [ ] No functionality regressions
- [ ] User experience improved
- [ ] Resource usage optimized
- [ ] Scalability improved

### Business Impact Assessment
- [ ] Customer wait times reduced
- [ ] System reliability improved
- [ ] User satisfaction increased
- [ ] Operational costs optimized
- [ ] Scalability requirements met

## Monitoring and Maintenance

### Ongoing Monitoring
- Set up performance dashboards
- Implement automated performance testing
- Regular performance reviews
- Capacity planning updates

### Performance Budget
- Establish performance budgets for new features
- Monitor performance regressions in CI/CD
- Regular performance audits
- Team performance awareness training

Remember: Performance optimization is an ongoing process. Focus on measuring, optimizing, and monitoring in cycles to maintain optimal system performance.
```
