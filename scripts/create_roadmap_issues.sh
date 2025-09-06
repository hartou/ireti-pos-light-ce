#!/bin/bash

# Create GitHub issues from ROADMAP.md user stories
# Usage: ./scripts/create_roadmap_issues.sh [owner/repo]
# Example: ./scripts/create_roadmap_issues.sh hartou/ireti-pos-light-ce

set -e

REPO=${1:-"hartou/ireti-pos-light-ce"}
ROADMAP_FILE="docs/ROADMAP.md"

echo "🗺️ Creating GitHub issues from ROADMAP.md for repository: $REPO"

# Check if ROADMAP.md exists
if [[ ! -f "$ROADMAP_FILE" ]]; then
    echo "❌ Error: $ROADMAP_FILE not found!"
    exit 1
fi

# Check if gh CLI is installed and authenticated
if ! command -v gh &> /dev/null; then
    echo "❌ Error: GitHub CLI (gh) is not installed!"
    echo "📥 Install it from: https://cli.github.com/"
    exit 1
fi

if ! gh auth status &> /dev/null; then
    echo "❌ Error: GitHub CLI is not authenticated!"
    echo "🔐 Run: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI is ready"

# Function to create a roadmap issue
create_roadmap_issue() {
    local road_id="$1"
    local title="$2"
    local priority="$3"
    local description="$4"
    local acceptance_criteria="$5"
    local phase="$6"
    local target_date="$7"
    
    # Check if issue already exists
    if gh issue list --repo "$REPO" --search "$road_id in:title" --json number --jq length | grep -q "^0$"; then
        echo "📝 Creating issue: $road_id - $title"
        
        # Determine labels based on priority and content
        local labels="roadmap"
        case "$priority" in
            "Critical") labels="$labels,priority:critical" ;;
            "High") labels="$labels,priority:high" ;;
            "Medium") labels="$labels,priority:medium" ;;
            "Low") labels="$labels,priority:low" ;;
        esac
        
        # Add type labels based on content
        if [[ "$title" == *"test"* ]] || [[ "$title" == *"Test"* ]]; then
            labels="$labels,area:testing"
        elif [[ "$title" == *"deployment"* ]] || [[ "$title" == *"Docker"* ]] || [[ "$title" == *"container"* ]]; then
            labels="$labels,area:docker"
        elif [[ "$title" == *"documentation"* ]] || [[ "$title" == *"guide"* ]]; then
            labels="$labels,type:documentation"
        elif [[ "$title" == *"security"* ]] || [[ "$title" == *"Security"* ]]; then
            labels="$labels,area:security"
        elif [[ "$title" == *"API"* ]] || [[ "$title" == *"api"* ]]; then
            labels="$labels,area:api"
        elif [[ "$title" == *"mobile"* ]] || [[ "$title" == *"Mobile"* ]] || [[ "$title" == *"PWA"* ]]; then
            labels="$labels,area:pwa"
        else
            labels="$labels,type:feature"
        fi
        
        # Create issue body
        local body=$(cat << EOF
## 📋 Roadmap Item Details

**ID**: $road_id  
**Phase**: $phase  
**Priority**: $priority  
**Target**: $target_date  

## 📄 Description
$description

## ✅ Acceptance Criteria
$acceptance_criteria

## 🔗 Related Documentation
- [Development Roadmap](https://github.com/$REPO/blob/main/docs/ROADMAP.md)
- [System Instructions](https://github.com/$REPO/blob/main/docs/SYSTEM_INSTRUCTIONS.md)

## 📝 Implementation Notes
This issue is part of the structured development roadmap for Ireti POS Light CE. Please refer to the roadmap document for context and dependencies.

When implementing:
1. Follow the existing code patterns and architecture
2. Ensure all acceptance criteria are met
3. Update relevant documentation
4. Add appropriate tests
5. Update the roadmap status when completed

---
*This issue was automatically created from the [ROADMAP.md](https://github.com/$REPO/blob/main/docs/ROADMAP.md) document.*
EOF
)

        # Create the issue
        local issue_url=$(gh issue create \
            --repo "$REPO" \
            --title "$road_id: $title" \
            --body "$body" \
            --label "$labels")
        
        if [[ $? -eq 0 ]]; then
            echo "✅ Created: $issue_url"
        else
            echo "❌ Failed to create issue: $road_id"
        fi
    else
        echo "⏭️ Issue already exists: $road_id"
    fi
}

echo "🔍 Parsing roadmap issues..."

# High Priority - Phase 2 Issues
create_roadmap_issue "ROAD-001" \
    "Create comprehensive deployment troubleshooting guide" \
    "High" \
    "Create a comprehensive guide covering common deployment issues, solutions, and debugging steps for production environments." \
    "- Guide covers Docker, PostgreSQL, and Nginx deployment issues\n- Common error scenarios with step-by-step solutions\n- Debugging checklist and tools recommendations\n- Integration with existing deployment documentation" \
    "Phase 2: Stability & Production Readiness" \
    "Q4 2025"

create_roadmap_issue "ROAD-002" \
    "Add migration guide for version upgrades" \
    "High" \
    "Create step-by-step upgrade instructions with rollback procedures for version migrations." \
    "- Version-specific upgrade instructions\n- Database migration procedures\n- Configuration changes documentation\n- Rollback procedures for failed upgrades\n- Backup and restore recommendations" \
    "Phase 2: Stability & Production Readiness" \
    "Q4 2025"

create_roadmap_issue "ROAD-005" \
    "Add comprehensive unit tests for core POS functionality" \
    "High" \
    "Implement comprehensive unit tests achieving 80%+ test coverage for cart, inventory, and transaction modules." \
    "- 80%+ test coverage for core modules (cart, inventory, transaction)\n- Test suite runs in CI/CD pipeline\n- Mock external dependencies (Stripe, database)\n- Performance benchmarks for critical paths\n- Clear test documentation and examples" \
    "Phase 2: Stability & Production Readiness" \
    "Q1 2026"

create_roadmap_issue "ROAD-006" \
    "Implement integration tests for end-to-end workflows" \
    "High" \
    "Create automated integration tests for complete purchase workflows and user journeys." \
    "- End-to-end purchase workflow tests\n- Multi-user scenario testing\n- Payment processing integration tests\n- Database transaction validation\n- Automated test data setup and teardown" \
    "Phase 2: Stability & Production Readiness" \
    "Q1 2026"

create_roadmap_issue "ROAD-009" \
    "Security audit and hardening assessment" \
    "High" \
    "Conduct comprehensive security review with remediation plan for production deployment." \
    "- OWASP security assessment completed\n- Vulnerability scan results addressed\n- Security hardening checklist implemented\n- PCI DSS compliance verification\n- Security documentation updated" \
    "Phase 2: Stability & Production Readiness" \
    "Q1 2026"

# Critical Priority - Immediate Issues
create_roadmap_issue "ROAD-010" \
    "Fix v0.0.2 image availability on GHCR" \
    "Critical" \
    "Resolve the issue where v0.0.2 container image is not accessible on GitHub Container Registry." \
    "- Image properly built and tagged on GHCR\n- Multi-platform support (AMD64/ARM64)\n- Image pull works without authentication issues\n- Documentation updated with correct image references\n- CI/CD pipeline validates image availability" \
    "Phase 2: Stability & Production Readiness" \
    "Immediate"

create_roadmap_issue "ROAD-011" \
    "Verify multi-platform Docker builds (AMD64/ARM64)" \
    "High" \
    "Ensure Docker builds work correctly on both AMD64 and ARM64 architectures." \
    "- Successful builds on both AMD64 and ARM64\n- Runtime verification on both architectures\n- CI/CD pipeline tests both platforms\n- Performance benchmarks for each architecture\n- Documentation includes architecture-specific notes" \
    "Phase 2: Stability & Production Readiness" \
    "Q4 2025"

create_roadmap_issue "ROAD-012" \
    "Test production deployment with PostgreSQL and Nginx" \
    "High" \
    "Validate that docker-compose.prod.yml works correctly in production environments." \
    "- Production deployment tested with PostgreSQL\n- Nginx configuration working correctly\n- SSL/HTTPS properly configured\n- Database persistence and backups working\n- Performance meets production requirements" \
    "Phase 2: Stability & Production Readiness" \
    "Q4 2025"

# Medium Priority Issues
create_roadmap_issue "ROAD-003" \
    "Optimize GitHub Actions workflow conditions" \
    "Medium" \
    "Improve CI/CD efficiency by skipping builds for documentation-only changes." \
    "- Conditional workflow execution based on file changes\n- Documentation changes skip heavy build processes\n- Faster feedback for documentation PRs\n- Clear workflow status indicators\n- Maintained code quality checks" \
    "Phase 2: Stability & Production Readiness" \
    "Q4 2025"

create_roadmap_issue "ROAD-004" \
    "Create development environment setup script" \
    "Medium" \
    "Provide one-command setup for new developers to get started quickly." \
    "- Single script sets up complete development environment\n- Cross-platform compatibility (Windows, macOS, Linux)\n- Validates setup and provides troubleshooting\n- Integration with existing Docker setup\n- Clear documentation and examples" \
    "Phase 2: Stability & Production Readiness" \
    "Q1 2026"

create_roadmap_issue "ROAD-007" \
    "Add PWA functionality automated tests" \
    "Medium" \
    "Implement automated tests for offline capabilities and service worker behavior." \
    "- Service worker registration and caching tests\n- Offline functionality verification\n- PWA installation testing\n- Network status handling tests\n- Browser compatibility validation" \
    "Phase 2: Stability & Production Readiness" \
    "Q1 2026"

create_roadmap_issue "ROAD-008" \
    "Performance testing suite for production readiness" \
    "Medium" \
    "Create load testing framework with performance benchmarks for production validation." \
    "- Load testing framework implementation\n- Performance benchmarks established\n- Automated performance regression testing\n- Scalability testing for concurrent users\n- Performance monitoring and alerting" \
    "Phase 2: Stability & Production Readiness" \
    "Q1 2026"

echo ""
echo "🎉 Roadmap issue creation complete!"
echo "📋 View all issues: https://github.com/$REPO/issues?q=is%3Aissue+label%3Aroadmap"
echo "🗺️ Full roadmap: https://github.com/$REPO/blob/main/docs/ROADMAP.md"