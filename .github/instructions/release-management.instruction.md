---
applyTo: '**'
priority: HIGH
---

# 🚀 Release Management Instructions for AI Assistants

## MANDATORY: Always Use Release Helper for Any Release

### When Release Actions Are Requested
**ANY** of these user requests MUST trigger the release helper workflow:
- "create a release"
- "make a new version" 
- "release v[version]"
- "tag a release"
- "publish version"
- "prepare for release"
- "bump version"
- "update version to..."

### REQUIRED Steps for Every Release

#### 1. ALWAYS Check Release Helper First
```bash
# MANDATORY: Run this before any manual release actions
./scripts/release.sh help
```

#### 2. Use Release Helper (Preferred Method)
```bash
# For patch releases (bug fixes)
./scripts/release.sh create v[X.Y.Z]

# For minor releases (new features)  
./scripts/release.sh create v[X.Y.0]

# For major releases (breaking changes)
./scripts/release.sh create v[X.0.0]

# With auto-push (for trusted releases)
./scripts/release.sh create v[X.Y.Z] --auto-push
```

#### 3. Manual Release ONLY If Script Unavailable
If `./scripts/release.sh` doesn't exist or fails, follow manual process from `.github/RELEASE_PROCESS.md`:

1. **Validate Environment**
   ```bash
   # Check we're on main branch
   git branch --show-current
   # Check working directory is clean
   git status --porcelain
   # Check we're up to date
   git fetch && git status
   ```

2. **Update Version Files**
   - Update `version.py` with new version
   - Update `package.json` with new version
   - Update any other version references

3. **Create Release Notes**
   - Create `RELEASE_NOTES_v[VERSION].md`
   - Use template from `.github/RELEASE_PROCESS.md`
   - Include all changes, breaking changes, migration notes

4. **Run Quality Gates**
   ```bash
   # Run tests
   npm test
   python manage.py test
   
   # Security scan (if available)
   bandit -r . || true
   ```

5. **Commit, Tag, and Release**
   ```bash
   # Commit version updates
   git add version.py package.json RELEASE_NOTES_v[VERSION].md
   git commit -m "🚀 Release v[VERSION] - [DESCRIPTION]"
   
   # Create annotated tag
   git tag -a v[VERSION] -m "Release v[VERSION] - [DESCRIPTION]"
   
   # Push commit and tag
   git push origin main
   git push origin v[VERSION]
   
   # Create GitHub release
   gh release create v[VERSION] \
     --title "🚀 Ireti POS Light v[VERSION] - [TITLE]" \
     --notes-file RELEASE_NOTES_v[VERSION].md \
     --latest
   ```

### Version Number Guidelines

#### Version Increment Rules
- **Patch (v1.0.1)**: Bug fixes, security patches, documentation updates
- **Minor (v1.1.0)**: New features (backward compatible), API additions
- **Major (v2.0.0)**: Breaking changes, major features, architectural changes

#### Pre-release Formats
- Alpha: `v1.1.0-alpha.1`
- Beta: `v1.1.0-beta.1` 
- Release Candidate: `v1.1.0-rc.1`

### Required Validations

#### Pre-Release Checklist
- [ ] All tests pass (`npm test` and `python manage.py test`)
- [ ] Version format is valid (vX.Y.Z)
- [ ] Version doesn't already exist (`git tag -l`)
- [ ] Working directory is clean (`git status`)
- [ ] On main branch (`git branch --show-current`)
- [ ] Up to date with origin (`git fetch && git status`)

#### Post-Release Verification
- [ ] GitHub release created successfully
- [ ] Docker image build triggered (check Actions tab)
- [ ] Release notes are complete and accurate
- [ ] Version numbers updated in all files
- [ ] Container deployment tested (if applicable)

### Error Handling

#### If Release Helper Fails
1. **Check Error Message**: Read the output carefully
2. **Check Prerequisites**: Ensure git state is clean
3. **Manual Fallback**: Use manual process from `.github/RELEASE_PROCESS.md`
4. **Document Issue**: Note any script problems for future improvement

#### If GitHub Release Fails
```bash
# Retry with explicit notes file
gh release create v[VERSION] \
  --title "🚀 Ireti POS Light v[VERSION]" \
  --notes-file RELEASE_NOTES_v[VERSION].md \
  --latest

# If notes file missing, create basic release
gh release create v[VERSION] \
  --title "🚀 Ireti POS Light v[VERSION]" \
  --notes "Release v[VERSION] - See commit history for details" \
  --latest
```

### AI Assistant Specific Rules

#### NEVER Do These Actions Manually Without Release Helper
- ❌ Directly edit `version.py` without running release helper
- ❌ Create git tags manually without following process
- ❌ Create GitHub releases without proper release notes
- ❌ Skip testing before release
- ❌ Release from non-main branches

#### ALWAYS Do These Actions
- ✅ Run `./scripts/release.sh help` first
- ✅ Validate version format before proceeding
- ✅ Create comprehensive release notes
- ✅ Run all tests before releasing
- ✅ Verify GitHub release creation
- ✅ Check Docker image build status

#### Communication Requirements
When performing a release, ALWAYS inform the user:
1. **Process Being Used**: "Using release helper script" or "Using manual process"
2. **Version Being Created**: Clear statement of version and type
3. **Release Notes**: Status of release notes creation/updating
4. **Quality Gates**: Test results and validation status
5. **Final Status**: GitHub release URL and container build status

### File Locations Reference
- **Release Helper**: `./scripts/release.sh`
- **Process Documentation**: `.github/RELEASE_PROCESS.md`
- **Workflow**: `.github/workflows/release-management.yml`
- **Instructions**: `.github/instructions/release-management.instruction.md` (this file)

### Emergency Override
Only in absolute emergency situations where the release helper is broken and manual process is impossible, document the deviation and create an issue to fix the release system.

---

**CRITICAL**: This instruction has HIGH priority. Always follow this process for any release-related request to ensure consistency and prevent the issues we experienced with v1.0.0.
