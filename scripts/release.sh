#!/bin/bash

# 🚀 Ireti POS Light Release Helper Script
# This script helps create consistent releases following our standardized process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_step() {
    echo -e "${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

# Function to validate version format
validate_version() {
    local version=$1
    if [[ ! $version =~ ^v[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9\.\-]+)?$ ]]; then
        print_error "Invalid version format: $version"
        echo "Expected format: vX.Y.Z or vX.Y.Z-suffix (e.g., v1.0.0, v1.2.0-beta.1)"
        exit 1
    fi
}

# Function to check if version already exists
check_version_exists() {
    local version=$1
    if git tag -l | grep -q "^$version$"; then
        print_error "Version $version already exists!"
        exit 1
    fi
}

# Function to update version files
update_version_files() {
    local version=$1
    local clean_version=${version#v}  # Remove 'v' prefix
    local date=$(date +%Y-%m-%d)
    
    print_step "Updating version files..."
    
    # Update version.py
    if [[ -f "version.py" ]]; then
        cat > version.py << EOF
__version__ = "$clean_version"
__version_info__ = ($(echo $clean_version | tr '.' ' ' | cut -d'-' -f1))

# Ireti POS Light Version Information
APP_NAME = "Ireti POS Light"
APP_VERSION = __version__
BUILD_DATE = "$date"
RELEASE_TYPE = "$(get_release_type $version)"
EOF
        print_success "Updated version.py"
    fi
    
    # Update package.json
    if [[ -f "package.json" ]] && command -v jq > /dev/null; then
        jq ".version = \"$clean_version\"" package.json > package.json.tmp && mv package.json.tmp package.json
        print_success "Updated package.json"
    elif [[ -f "package.json" ]]; then
        sed -i "s/\"version\": \".*\"/\"version\": \"$clean_version\"/" package.json
        print_success "Updated package.json (without jq)"
    fi
}

# Function to determine release type
get_release_type() {
    local version=$1
    if [[ $version =~ (alpha|beta|rc) ]]; then
        echo "Pre-release"
    elif [[ $version =~ v[0-9]+\.0\.0$ ]]; then
        echo "Major Release"
    elif [[ $version =~ v[0-9]+\.[0-9]+\.0$ ]]; then
        echo "Minor Release"
    else
        echo "Patch Release"
    fi
}

# Function to create release notes template
create_release_notes() {
    local version=$1
    local release_file="RELEASE_NOTES_${version}.md"
    local date=$(date +"%B %d, %Y")
    local release_type=$(get_release_type $version)
    
    if [[ -f "$release_file" ]]; then
        print_warning "Release notes file $release_file already exists. Skipping creation."
        return
    fi
    
    print_step "Creating release notes template: $release_file"
    
    cat > "$release_file" << EOF
# 🎉 Ireti POS Light $version - $release_type
**Release Date**: $date  
**Release Type**: $release_type

## 🚀 What's New in $version

### 🆕 New Features
- [Add new features here]

### 🛠️ Improvements  
- [Add improvements here]

### 🐛 Bug Fixes
- [Add bug fixes here]

### 🔒 Security Updates
- [Add security updates here]

## 📋 Migration Notes
- [Add migration instructions here]

## 🚨 Breaking Changes
- [List any breaking changes here]

## 📚 Documentation
- [List documentation updates here]

## 🎯 Known Issues
- [List any known issues here]

## 🐳 Container Deployment
This release is optimized for SQLite container deployment with the following features:
- [List container-specific features]

## 📞 Support
- **Issues**: [Repository Issues](https://github.com/hartou/ireti-pos-light/issues)
- **Documentation**: [Project Documentation](https://github.com/hartou/ireti-pos-light/docs)

---
**Note**: Please review and update this template with actual release information before publishing.
EOF
    
    print_success "Created release notes template: $release_file"
    print_warning "Please edit $release_file with actual release information before continuing."
}

# Function to run pre-release checks
run_pre_release_checks() {
    print_step "Running pre-release checks..."
    
    # Check if we're on main branch
    local branch=$(git rev-parse --abbrev-ref HEAD)
    if [[ "$branch" != "main" ]]; then
        print_error "You must be on the main branch to create a release. Current branch: $branch"
        exit 1
    fi
    
    # Check if working directory is clean
    if [[ -n $(git status --porcelain) ]]; then
        print_error "Working directory is not clean. Please commit or stash changes."
        git status --short
        exit 1
    fi
    
    # Check if we're up to date with remote
    git fetch origin
    local local_commit=$(git rev-parse HEAD)
    local remote_commit=$(git rev-parse origin/main)
    if [[ "$local_commit" != "$remote_commit" ]]; then
        print_error "Local main branch is not up to date with origin/main"
        exit 1
    fi
    
    print_success "Pre-release checks passed"
}

# Function to run tests
run_tests() {
    print_step "Running tests..."
    
    # Run Django tests if manage.py exists
    if [[ -f "manage.py" ]]; then
        python manage.py test --verbosity=1
        print_success "Django tests passed"
    fi
    
    # Run npm tests if package.json exists
    if [[ -f "package.json" ]] && [[ -f "playwright.config.js" ]]; then
        npm test
        print_success "E2E tests passed"
    fi
}

# Main release function
create_release() {
    local version=$1
    local skip_tests=${2:-false}
    local auto_push=${3:-false}
    
    print_step "Starting release process for $version"
    
    # Validate inputs
    validate_version "$version"
    check_version_exists "$version"
    
    # Run pre-release checks
    run_pre_release_checks
    
    # Run tests unless skipped
    if [[ "$skip_tests" != "true" ]]; then
        run_tests
    else
        print_warning "Skipping tests as requested"
    fi
    
    # Update version files
    update_version_files "$version"
    
    # Create release notes template
    create_release_notes "$version"
    
    # Stage changes
    git add version.py package.json "RELEASE_NOTES_${version}.md" 2>/dev/null || true
    
    # Show what will be committed
    print_step "Changes to be committed:"
    git diff --cached --name-only
    
    if [[ "$auto_push" != "true" ]]; then
        echo
        print_warning "Ready to commit and tag release $version"
        read -p "Continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_error "Release cancelled by user"
            exit 1
        fi
    fi
    
    # Commit changes
    git commit -m "🚀 Release $version - $(get_release_type $version)

- Update version to ${version#v} in version.py and package.json
- Add RELEASE_NOTES_${version}.md template
- Prepare for $(get_release_type $version) release"
    
    print_success "Committed version update"
    
    # Create annotated tag
    git tag -a "$version" -m "Release $version - $(get_release_type $version)

$(get_release_type $version) for Ireti POS Light.
See RELEASE_NOTES_${version}.md for detailed information."
    
    print_success "Created tag $version"
    
    # Push if auto-push is enabled
    if [[ "$auto_push" == "true" ]]; then
        git push origin main
        git push origin "$version"
        print_success "Pushed commit and tag to origin"
        
        # Create GitHub release if gh CLI is available
        if command -v gh > /dev/null; then
            print_step "Creating GitHub release..."
            gh release create "$version" \
                --title "🚀 Ireti POS Light $version - $(get_release_type $version)" \
                --notes-file "RELEASE_NOTES_${version}.md" \
                --latest
            print_success "Created GitHub release"
        fi
    else
        echo
        print_success "Release preparation complete!"
        echo "Next steps:"
        echo "1. Edit RELEASE_NOTES_${version}.md with actual release information"
        echo "2. Push changes: git push origin main && git push origin $version"
        echo "3. Create GitHub release: gh release create $version --title '🚀 Ireti POS Light $version' --notes-file RELEASE_NOTES_${version}.md --latest"
    fi
}

# Help function
show_help() {
    cat << EOF
🚀 Ireti POS Light Release Helper

Usage: $0 <command> [options]

Commands:
    create <version>    Create a new release
    help               Show this help message

Options:
    --skip-tests       Skip running tests before release
    --auto-push        Automatically push changes and create GitHub release
    --dry-run          Show what would be done without making changes

Examples:
    $0 create v1.0.1                    # Create patch release
    $0 create v1.1.0                    # Create minor release  
    $0 create v2.0.0                    # Create major release
    $0 create v1.0.0-beta.1             # Create pre-release
    $0 create v1.0.1 --skip-tests       # Skip tests
    $0 create v1.0.1 --auto-push        # Auto-push and create GitHub release

Version Format:
    vX.Y.Z              Standard release (v1.0.0, v1.2.3)
    vX.Y.Z-suffix       Pre-release (v1.0.0-alpha.1, v2.0.0-beta.2)

EOF
}

# Main script logic
case "${1:-}" in
    "create")
        if [[ -z "${2:-}" ]]; then
            print_error "Version is required"
            show_help
            exit 1
        fi
        
        version="$2"
        skip_tests=false
        auto_push=false
        
        # Parse additional arguments
        shift 2
        while [[ $# -gt 0 ]]; do
            case $1 in
                --skip-tests)
                    skip_tests=true
                    shift
                    ;;
                --auto-push)
                    auto_push=true
                    shift
                    ;;
                --dry-run)
                    print_warning "Dry run mode - no changes will be made"
                    # TODO: Implement dry run mode
                    exit 0
                    ;;
                *)
                    print_error "Unknown option: $1"
                    show_help
                    exit 1
                    ;;
            esac
        done
        
        create_release "$version" "$skip_tests" "$auto_push"
        ;;
    "help"|"--help"|"-h"|"")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
