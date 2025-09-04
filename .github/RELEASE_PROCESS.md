# 🚀 Release Process Documentation

## Overview
This document outlines the standardized release process for Ireti POS Light to ensure consistency and proper versioning.

## 🤖 AI Assistant Instructions

**CRITICAL**: If you are an AI assistant helping with releases, you MUST:

1. **Always use the release helper first**: `./scripts/release.sh help`
2. **Never create releases manually** without checking if the helper script works
3. **Follow the exact process** documented in `.github/instructions/release-management.instruction.md`
4. **Validate all prerequisites** before starting any release process
5. **Create GitHub releases** properly, not just Git tags

### Quick AI Assistant Commands
```bash
# Check if release helper exists and works
./scripts/release.sh help

# Create release using helper (preferred method)
./scripts/release.sh create v[VERSION]

# Only use manual process if helper fails
# (Follow manual steps below)
```

---

## Release Types

### Major Release (x.0.0)
- Breaking changes or significant new features
- Complete feature additions (like Stripe integration)
- Architectural changes
- **Example**: v1.0.0 - Complete Stripe Payment Integration

### Minor Release (x.y.0)
- New features that are backward compatible
- Significant enhancements to existing features
- New APIs or endpoints
- **Example**: v1.1.0 - Multi-currency support

### Patch Release (x.y.z)
- Bug fixes
- Security updates
- Minor improvements
- **Example**: v1.0.1 - Fix payment form validation bug

## Release Workflow

### 1. Pre-Release Preparation
```bash
# Ensure all tests pass
npm test
python manage.py test

# Update version numbers
# - Update version.py
# - Update package.json
# - Update any other version references

# Create/update release notes
# - Create RELEASE_NOTES_vX.Y.Z.md
# - Include breaking changes, new features, bug fixes
# - Add deployment instructions if needed
```

### 2. Version Update Process
```bash
# Update version.py
__version__ = "X.Y.Z"
__version_info__ = (X, Y, Z)
BUILD_DATE = "YYYY-MM-DD"
RELEASE_TYPE = "Description of release"

# Update package.json
"version": "X.Y.Z"

# Update README.md if needed
# - Update badges
# - Update feature descriptions
# - Update installation instructions
```

### 3. Release Commit and Tag
```bash
# Commit version updates
git add .
git commit -m "🚀 Release vX.Y.Z - Brief description

- Update version to X.Y.Z in version.py and package.json
- Add RELEASE_NOTES_vX.Y.Z.md
- Update documentation for new release
- Clean up repository for production release"

# Create annotated tag
git tag -a vX.Y.Z -m "Release vX.Y.Z - Brief description

Detailed release notes:
- Feature 1
- Feature 2
- Bug fix 1
- etc."

# Push commit and tag
git push origin main
git push origin vX.Y.Z
```

### 4. GitHub Release Creation
```bash
# Create GitHub release using CLI
gh release create vX.Y.Z \
  --title "🚀 Project Name vX.Y.Z - Release Title" \
  --notes-file RELEASE_NOTES_vX.Y.Z.md \
  --latest  # Only for major/minor releases

# For patch releases, omit --latest
gh release create vX.Y.Z \
  --title "🐛 Project Name vX.Y.Z - Patch Release" \
  --notes-file RELEASE_NOTES_vX.Y.Z.md
```

### 5. Automated Actions
The following actions are triggered automatically:
- **Docker Image Build**: Triggered by tag push (`.github/workflows/docker-publish.yml`)
- **Security Scan**: Automated security scanning
- **Container Registry**: Image pushed to GitHub Container Registry

## File Templates

### Release Notes Template
```markdown
# 🎉 Project Name vX.Y.Z - Release Title
**Release Date**: YYYY-MM-DD  
**Release Type**: Major/Minor/Patch Release

## 🚀 What's New in vX.Y.Z

### 🆕 New Features
- Feature 1 description
- Feature 2 description

### 🛠️ Improvements  
- Improvement 1
- Improvement 2

### 🐛 Bug Fixes
- Bug fix 1
- Bug fix 2

### 🔒 Security Updates
- Security update 1
- Security update 2

## 📋 Migration Notes
- Migration step 1
- Migration step 2

## 🚨 Breaking Changes
- Breaking change 1
- Breaking change 2

## 📚 Documentation
- New documentation added
- Updated guides

## 🎯 Known Issues
- Known issue 1
- Known issue 2
```

### Deployment Checklist Template
```markdown
# 🚀 Project Name vX.Y.Z Deployment Checklist

## Pre-Deployment
- [ ] All tests passing
- [ ] Version numbers updated
- [ ] Release notes created
- [ ] Security scan passed
- [ ] Documentation updated

## Deployment
- [ ] Tag created and pushed
- [ ] GitHub release created
- [ ] Docker image built
- [ ] Container registry updated

## Post-Deployment
- [ ] Production deployment tested
- [ ] Health checks passing
- [ ] Monitoring alerts configured
- [ ] Team notified of release
```

## Branch Strategy

### Main Branch
- Always production-ready
- All releases are tagged from main
- Requires pull request for changes
- Protected branch with required reviews

### Feature Branches
- `feature/feature-name`
- Created from main
- Merged via pull request
- Deleted after merge

### Release Branches (Optional for major releases)
- `release/vX.Y.Z`
- Used for release preparation
- Final testing and bug fixes
- Merged to main and tagged

## Versioning Rules

### Version Increment Guidelines
```bash
# Major version (X.0.0)
- Breaking API changes
- Major feature additions
- Architectural changes
- Database schema breaking changes

# Minor version (X.Y.0)
- New features (backward compatible)
- API additions (non-breaking)
- Significant improvements
- New optional dependencies

# Patch version (X.Y.Z)
- Bug fixes
- Security patches
- Documentation updates
- Minor improvements
```

### Pre-release Versions
```bash
# Alpha releases
vX.Y.Z-alpha.N

# Beta releases  
vX.Y.Z-beta.N

# Release candidates
vX.Y.Z-rc.N
```

## Rollback Process

### Quick Rollback
```bash
# Revert to previous release tag
git checkout vX.Y.Z-previous
git tag -a vX.Y.Z-hotfix -m "Hotfix: Rollback to previous stable version"
git push origin vX.Y.Z-hotfix

# Create GitHub release
gh release create vX.Y.Z-hotfix \
  --title "🚨 Hotfix vX.Y.Z - Rollback Release" \
  --notes "Emergency rollback to previous stable version due to critical issue."
```

### Hotfix Process
```bash
# Create hotfix branch from last stable tag
git checkout -b hotfix/critical-fix vX.Y.Z-stable
# Make minimal fix
git commit -m "hotfix: Fix critical issue"
# Merge to main and tag
git checkout main
git merge hotfix/critical-fix
git tag vX.Y.Z+1
```

## Quality Gates

### Pre-Release Checklist
- [ ] All automated tests pass
- [ ] Manual testing completed
- [ ] Security scan passed
- [ ] Performance testing (if applicable)
- [ ] Documentation updated
- [ ] Breaking changes documented
- [ ] Migration path tested

### Release Approval
- [ ] Technical lead approval
- [ ] Product owner approval (for major releases)
- [ ] Security team approval (for security-related changes)

## Communication

### Release Announcement
- Update README.md with latest version
- Post in team communication channels
- Update project documentation
- Notify stakeholders of breaking changes

### Release Notes Distribution
- GitHub release page
- Project README
- Documentation site
- Team communication channels

---

**Note**: This process should be followed for all releases to ensure consistency and reliability. Deviations should be documented and approved by the technical lead.
