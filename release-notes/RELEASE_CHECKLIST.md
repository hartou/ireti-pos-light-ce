# ✅ Release Checklist - Ireti POS Light

## 🎯 Pre-Release Preparation

### Environment & Prerequisites
- [ ] **On main branch**: `git branch --show-current` shows `main`
- [ ] **Working directory clean**: `git status --porcelain` shows no changes
- [ ] **Up to date with origin**: `git fetch && git status` shows up to date
- [ ] **Release helper available**: `./scripts/release.sh help` works
- [ ] **GitHub CLI available**: `gh --version` works (for GitHub release creation)

### Version Planning
- [ ] **Version format valid**: Following vX.Y.Z format
- [ ] **Version type determined**: 
  - [ ] Patch (v1.0.1) - Bug fixes, security patches
  - [ ] Minor (v1.1.0) - New features, backward compatible  
  - [ ] Major (v2.0.0) - Breaking changes, major features
- [ ] **Version doesn't exist**: `git tag -l | grep vX.Y.Z` returns nothing

## 🧪 Quality Gates

### Testing
- [ ] **Django tests pass**: `python manage.py test`
- [ ] **E2E tests pass**: `npm test` (Playwright tests)
- [ ] **Manual testing completed**: Payment flow, admin functions tested
- [ ] **Cross-browser testing**: Chrome, Safari/WebKit verified

### Security & Code Quality
- [ ] **Security scan passed**: `bandit -r .` (if available)
- [ ] **Dependencies checked**: `safety check` (if available)
- [ ] **No sensitive data exposed**: Check for API keys, passwords in code
- [ ] **CSRF protection verified**: Forms include proper CSRF tokens

### Documentation
- [ ] **README updated**: Version references, new features documented
- [ ] **Breaking changes documented**: If any breaking changes exist
- [ ] **Migration notes prepared**: Database or config changes noted
- [ ] **API changes documented**: If endpoints changed

## 📝 Release Creation

### Using Release Helper (Preferred)
- [ ] **Run release helper**: `./scripts/release.sh create vX.Y.Z`
- [ ] **Review generated files**: Check version.py, package.json updates
- [ ] **Edit release notes**: Update `RELEASE_NOTES_vX.Y.Z.md` with actual content
- [ ] **Confirm and push**: Follow helper script prompts

### Manual Process (Fallback)
- [ ] **Update version.py**: Set `__version__ = "X.Y.Z"` and build date
- [ ] **Update package.json**: Set `"version": "X.Y.Z"`
- [ ] **Create release notes**: Create `RELEASE_NOTES_vX.Y.Z.md`
- [ ] **Stage changes**: `git add version.py package.json RELEASE_NOTES_vX.Y.Z.md`
- [ ] **Commit changes**: `git commit -m "🚀 Release vX.Y.Z - Description"`
- [ ] **Create tag**: `git tag -a vX.Y.Z -m "Release vX.Y.Z - Description"`
- [ ] **Push commit**: `git push origin main`
- [ ] **Push tag**: `git push origin vX.Y.Z`

## 🚀 GitHub Release

### Release Creation
- [ ] **Create GitHub release**: `gh release create vX.Y.Z --title "🚀 Ireti POS Light vX.Y.Z" --notes-file RELEASE_NOTES_vX.Y.Z.md --latest`
- [ ] **Verify release page**: Check https://github.com/hartou/ireti-pos-light/releases/tag/vX.Y.Z
- [ ] **Release notes complete**: All sections filled with actual content
- [ ] **Assets uploaded**: Any additional files attached if needed

### Container & Automation
- [ ] **Docker build triggered**: Check GitHub Actions for container build
- [ ] **Container image published**: Verify ghcr.io/hartou/ireti-pos-light:vX.Y.Z exists
- [ ] **Automated workflows completed**: All GitHub Actions finished successfully

## 🐳 Post-Release Verification

### Container Deployment (Optional)
- [ ] **Test container deployment**: Pull and test new container image
- [ ] **Health checks pass**: Container starts and responds to health endpoint
- [ ] **Environment variables work**: Stripe integration functions correctly
- [ ] **Database migrations applied**: If applicable, test migration process

### Communication & Documentation
- [ ] **README badges updated**: Version badges reflect new release
- [ ] **Documentation site updated**: If applicable
- [ ] **Team notification sent**: Inform relevant stakeholders
- [ ] **Release announcement prepared**: For public releases

### Production Deployment (If Applicable)
- [ ] **Staging deployment tested**: Deploy to staging environment first
- [ ] **Production deployment planned**: Schedule and plan production deployment
- [ ] **Rollback plan ready**: Prepare rollback procedures if needed
- [ ] **Monitoring alerts configured**: Set up alerts for new release

## 🚨 Emergency Procedures

### If Release Fails
- [ ] **Check error messages**: Read output carefully for specific issues
- [ ] **Verify prerequisites**: Ensure all pre-release items completed
- [ ] **Clean up partial changes**: Reset to clean state if needed
- [ ] **Document issues**: Note problems for future improvement

### Rollback Process
- [ ] **Identify issue**: Determine if rollback is necessary
- [ ] **Create hotfix tag**: `git tag vX.Y.Z-hotfix` from stable commit
- [ ] **Create emergency release**: Use hotfix process
- [ ] **Notify stakeholders**: Communicate rollback and reasons

## 📋 Release Types Specific Checklists

### Major Release (vX.0.0)
- [ ] **Breaking changes documented**: All breaking changes listed
- [ ] **Migration guide created**: Step-by-step upgrade instructions
- [ ] **Deprecated features removed**: Clean up old, deprecated code
- [ ] **Performance testing completed**: Verify performance impact
- [ ] **Extended testing period**: Allow more time for community testing

### Minor Release (vX.Y.0)
- [ ] **New features documented**: All features explained with examples
- [ ] **Backward compatibility verified**: Existing functionality preserved
- [ ] **Feature flags considered**: For gradual rollout if applicable
- [ ] **Integration tests updated**: Cover new feature interactions

### Patch Release (vX.Y.Z)
- [ ] **Bug fixes verified**: Confirm fixes resolve reported issues
- [ ] **Regression testing**: Ensure fixes don't break existing functionality
- [ ] **Security patches applied**: If security-related, verify completeness
- [ ] **Fast-track testing**: Focus on affected areas only

## 📞 Support Resources

### Documentation
- **Release Process**: `.github/RELEASE_PROCESS.md`
- **Release Helper**: `scripts/release.sh help`
- **AI Instructions**: `.github/instructions/release-management.instruction.md`

### Commands Reference
```bash
# Check release helper
./scripts/release.sh help

# Create release (automated)
./scripts/release.sh create vX.Y.Z

# Manual fallback commands
git tag -l                                    # List existing tags
git branch --show-current                     # Check current branch
git status --porcelain                        # Check working directory
gh release list                               # List GitHub releases
```

---

**💡 Tip**: Print this checklist and check off items as you complete them. For automated releases, most items are handled by `./scripts/release.sh`, but verification steps are still important!
