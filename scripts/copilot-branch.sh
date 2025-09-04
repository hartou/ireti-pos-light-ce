#!/bin/bash

# GitHub Copilot Branch Helper Script
# This script helps GitHub Copilot create and work with feature branches

set -e

BRANCH_PREFIX="copilot/"
MAIN_BRANCH="main"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to create a new Copilot branch
create_branch() {
    local feature_name="$1"
    local description="$2"
    
    if [ -z "$feature_name" ]; then
        print_error "Feature name is required"
        echo "Usage: $0 create <feature-name> [description]"
        exit 1
    fi
    
    # Sanitize feature name
    feature_name=$(echo "$feature_name" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]/-/g' | sed 's/--*/-/g' | sed 's/^-\|-$//g')
    timestamp=$(date +%Y%m%d-%H%M%S)
    branch_name="${BRANCH_PREFIX}${feature_name}-${timestamp}"
    
    print_info "Creating Copilot feature branch: $branch_name"
    
    # Ensure we're on main and it's up to date
    print_info "Switching to main branch and updating..."
    git checkout "$MAIN_BRANCH"
    git pull origin "$MAIN_BRANCH"
    
    # Create and switch to new branch
    print_info "Creating new branch from main..."
    git checkout -b "$branch_name"
    
    # Push branch to remote
    print_info "Pushing branch to remote..."
    git push -u origin "$branch_name"
    
    print_status "Branch $branch_name created successfully!"
    
    # Create initial commit with branch info
    cat > .copilot-branch-info.md << EOF
# GitHub Copilot Development Branch

**Branch:** \`$branch_name\`
**Created:** $(date)
**Feature:** $feature_name
**Description:** ${description:-"No description provided"}

## Development Guidelines

1. Make all changes in this branch
2. Commit frequently with clear messages
3. Push changes regularly to backup your work
4. Create a Pull Request when ready to merge
5. The branch will be automatically cleaned up after merge

## Commands

\`\`\`bash
# Add and commit changes
git add .
git commit -m "Your descriptive commit message"

# Push changes
git push origin $branch_name

# Create PR (using gh CLI)
gh pr create --title "Your PR title" --body "Description of changes"
\`\`\`
EOF

    git add .copilot-branch-info.md
    git commit -m "🤖 Initialize Copilot branch: $feature_name"
    git push origin "$branch_name"
    
    print_status "Branch initialization complete!"
    print_info "You can now start developing in branch: $branch_name"
}

# Function to list Copilot branches
list_branches() {
    print_info "Current Copilot branches:"
    git branch -r | grep "origin/${BRANCH_PREFIX}" | sed "s/origin\///" | while read branch; do
        echo "  🌿 $branch"
    done
}

# Function to switch to a Copilot branch
switch_branch() {
    local branch_name="$1"
    
    if [ -z "$branch_name" ]; then
        print_error "Branch name is required"
        list_branches
        exit 1
    fi
    
    # Add prefix if not provided
    if [[ ! "$branch_name" == ${BRANCH_PREFIX}* ]]; then
        branch_name="${BRANCH_PREFIX}${branch_name}"
    fi
    
    print_info "Switching to branch: $branch_name"
    git checkout "$branch_name" || {
        print_warning "Branch not found locally, trying to fetch from remote..."
        git fetch origin "$branch_name:$branch_name"
        git checkout "$branch_name"
    }
    
    print_status "Now on branch: $branch_name"
}

# Function to create a Pull Request
create_pr() {
    local current_branch=$(git branch --show-current)
    
    if [[ ! "$current_branch" == ${BRANCH_PREFIX}* ]]; then
        print_error "Not on a Copilot branch. Current branch: $current_branch"
        exit 1
    fi
    
    print_info "Creating Pull Request for branch: $current_branch"
    
    # Push any uncommitted changes
    if ! git diff --quiet || ! git diff --cached --quiet; then
        print_warning "You have uncommitted changes. Please commit them first."
        exit 1
    fi
    
    # Push branch to ensure it's up to date
    git push origin "$current_branch"
    
    # Extract feature name for PR title
    feature_name=$(echo "$current_branch" | sed "s/${BRANCH_PREFIX}//" | sed 's/-[0-9]*$//')
    
    # Create PR using gh CLI
    if command -v gh &> /dev/null; then
        print_info "Creating PR using GitHub CLI..."
        gh pr create \
            --title "🤖 Copilot: $(echo $feature_name | sed 's/-/ /g')" \
            --body "Automated PR created by GitHub Copilot workflow.

**Branch:** \`$current_branch\`
**Feature:** $feature_name

## Changes
<!-- Describe your changes here -->

## Testing
- [ ] Manual testing completed
- [ ] Docker build tested
- [ ] No breaking changes

---
*This PR will be automatically merged after passing all checks.*" \
            --label "copilot,automated"
        
        print_status "Pull Request created successfully!"
    else
        print_warning "GitHub CLI not found. Please install 'gh' CLI or create PR manually at:"
        echo "https://github.com/$(git config --get remote.origin.url | sed 's/.*github\.com[:/]//' | sed 's/\.git$//')/compare/$current_branch"
    fi
}

# Function to clean up merged branches
cleanup() {
    print_info "Cleaning up merged Copilot branches..."
    
    # Switch to main
    git checkout "$MAIN_BRANCH"
    git pull origin "$MAIN_BRANCH"
    
    # Find merged branches
    git branch --merged | grep "$BRANCH_PREFIX" | while read branch; do
        if [ "$branch" != "$(git branch --show-current)" ]; then
            print_info "Deleting merged branch: $branch"
            git branch -d "$branch"
        fi
    done
    
    # Clean up remote tracking branches
    git remote prune origin
    
    print_status "Cleanup complete!"
}

# Main script logic
case "${1:-help}" in
    "create")
        create_branch "$2" "$3"
        ;;
    "list"|"ls")
        list_branches
        ;;
    "switch"|"checkout")
        switch_branch "$2"
        ;;
    "pr"|"pull-request")
        create_pr
        ;;
    "cleanup"|"clean")
        cleanup
        ;;
    "help"|*)
        echo "GitHub Copilot Branch Helper"
        echo ""
        echo "Usage: $0 <command> [options]"
        echo ""
        echo "Commands:"
        echo "  create <name> [description]  Create new Copilot feature branch"
        echo "  list                        List all Copilot branches"
        echo "  switch <name>               Switch to a Copilot branch"
        echo "  pr                          Create Pull Request for current branch"
        echo "  cleanup                     Clean up merged branches"
        echo "  help                        Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 create fix-login-bug 'Fix authentication issue'"
        echo "  $0 switch fix-login-bug"
        echo "  $0 pr"
        echo "  $0 cleanup"
        ;;
esac
