# Roadmap User Stories and Development Items

This document tracks development roadmap items in a structured table format for automated GitHub issue creation. Each row represents a development task that contributes to the overall project roadmap.

**Status Values**: `Pending` (default), `In Progress`, `Completed`, `Deferred`

---

| ID | Phase | Area | Priority | User Story | Acceptance Criteria (condensed) | Status |
|---|---|---|---|---|---|---|
| ROAD-001 | Phase 2 | Documentation | High | Create deployment troubleshooting guide | - Guide covers Docker, PostgreSQL, Nginx deployment issues<br>- Common error scenarios with solutions<br>- Debugging checklist and tools<br>- Integration with existing docs | Pending |
| ROAD-002 | Phase 2 | Documentation | High | Add migration guide for version upgrades | - Version-specific upgrade instructions<br>- Database migration procedures<br>- Rollback procedures for failed upgrades<br>- Backup and restore recommendations | Pending |
| ROAD-003 | Phase 2 | CI/CD | Medium | Optimize GitHub Actions workflow conditions | - Conditional execution based on file changes<br>- Skip builds for docs-only changes<br>- Faster feedback for documentation PRs<br>- Maintained code quality checks | Pending |
| ROAD-004 | Phase 2 | DevEx | Medium | Create development environment setup script | - Single script for complete dev setup<br>- Cross-platform compatibility<br>- Setup validation and troubleshooting<br>- Integration with Docker setup | Pending |
| ROAD-005 | Phase 2 | Testing | High | Add comprehensive unit tests for core POS | - 80%+ test coverage for core modules<br>- CI/CD pipeline integration<br>- Mock external dependencies<br>- Performance benchmarks for critical paths | Pending |
| ROAD-006 | Phase 2 | Testing | High | Implement integration tests for workflows | - End-to-end purchase workflow tests<br>- Multi-user scenario testing<br>- Payment processing integration tests<br>- Automated test data management | Pending |
| ROAD-007 | Phase 2 | Testing | Medium | Add PWA functionality automated tests | - Service worker and caching tests<br>- Offline functionality verification<br>- PWA installation testing<br>- Browser compatibility validation | Pending |
| ROAD-008 | Phase 2 | Testing | Medium | Performance testing suite for production | - Load testing framework<br>- Performance benchmarks<br>- Automated regression testing<br>- Scalability testing for concurrent users | Pending |
| ROAD-009 | Phase 2 | Security | High | Security audit and hardening assessment | - OWASP security assessment<br>- Vulnerability scan remediation<br>- Security hardening checklist<br>- PCI DSS compliance verification | Pending |
| ROAD-010 | Phase 2 | Deployment | Critical | Fix v0.0.2 image availability on GHCR | - Image properly built and tagged<br>- Multi-platform support (AMD64/ARM64)<br>- Image pull works without auth issues<br>- CI/CD validates image availability | Pending |
| ROAD-011 | Phase 2 | Deployment | High | Verify multi-platform Docker builds | - Successful builds on AMD64 and ARM64<br>- Runtime verification on both architectures<br>- CI/CD tests both platforms<br>- Performance benchmarks per architecture | Pending |
| ROAD-012 | Phase 2 | Deployment | High | Test production deployment with PostgreSQL | - Production deployment tested<br>- Nginx configuration working<br>- SSL/HTTPS properly configured<br>- Database persistence and backups working | Pending |
| ROAD-013 | Phase 3 | Reporting | High | Enhanced sales reporting system | - Detailed analytics with filtering/export<br>- Daily/weekly/monthly reports<br>- Graphs and visualization<br>- Performance optimization | Planned |
| ROAD-014 | Phase 3 | Inventory | High | Inventory reporting and alerts | - Low stock alerts and notifications<br>- Automatic reordering capabilities<br>- Supplier management integration<br>- Configurable stock thresholds | Planned |
| ROAD-015 | Phase 3 | Financial | Medium | Financial summaries and tax reporting | - End-of-day/month financial reports<br>- Tax reporting capabilities<br>- Integration with accounting software<br>- Export to common formats | Planned |
| ROAD-016 | Phase 3 | Analytics | Medium | Customer analytics dashboard | - Purchase pattern analysis<br>- Customer segmentation<br>- Trend visualization<br>- Actionable insights | Planned |
| ROAD-017 | Phase 3 | Multi-Store | High | Multi-store support | - Multiple store location support<br>- Centralized management interface<br>- Store-specific inventory/reporting<br>- User management per store | Planned |
| ROAD-018 | Phase 3 | CRM | Medium | Customer management system | - Customer account profiles<br>- Purchase history tracking<br>- Contact information management<br>- Customer preferences storage | Planned |
| ROAD-019 | Phase 3 | Marketing | Medium | Loyalty programs and promotions | - Points-based loyalty system<br>- Discount and promotion campaigns<br>- Configurable loyalty rules<br>- Automated point calculation | Planned |
| ROAD-020 | Phase 3 | HR | Low | Employee management and scheduling | - Staff scheduling system<br>- Role-based permissions<br>- Performance tracking<br>- Time tracking integration | Planned |

---

### Cross-cutting acceptance criteria (apply to all roadmap tasks)
- Follow existing code patterns and architecture
- Include appropriate documentation updates
- Add relevant tests for new functionality
- Maintain backward compatibility where possible
- Update CHANGELOG.md with notable changes

### Workflow checklist per task
1) Analyze requirements and design approach
2) Implement feature following project patterns
3) Add tests and update documentation
4) Verify functionality and performance
5) Update roadmap status when complete

### Quick-create GitHub issues
Use the helper script to create issues for all pending roadmap items:

```bash
bash scripts/create_roadmap_issues.sh hartou/ireti-pos-light-ce
```

Requirements: GitHub CLI (gh) authenticated with access to the repo.