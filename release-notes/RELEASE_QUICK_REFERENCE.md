# 🚀 RELEASE QUICK REFERENCE

## For AI Assistants & Developers

### ⚡ Quick Commands
```bash
# Check release helper
./scripts/release.sh help

# Create patch release (bug fixes)
./scripts/release.sh create v1.0.1

# Create minor release (new features)  
./scripts/release.sh create v1.1.0

# Create major release (breaking changes)
./scripts/release.sh create v2.0.0

# Auto-push and create GitHub release
./scripts/release.sh create v1.0.1 --auto-push
```

### 🎯 Version Guidelines
- **Patch** (1.0.1): Bug fixes, security patches
- **Minor** (1.1.0): New features, backward compatible
- **Major** (2.0.0): Breaking changes, major features

### 📋 Manual Checklist (if script fails)
1. [ ] Check we're on main branch: `git branch --show-current`
2. [ ] Working directory clean: `git status --porcelain`
3. [ ] Up to date: `git fetch && git status`
4. [ ] Update `version.py` and `package.json`
5. [ ] Create `RELEASE_NOTES_vX.Y.Z.md`
6. [ ] Run tests: `npm test && python manage.py test`
7. [ ] Commit: `git commit -m "🚀 Release vX.Y.Z"`
8. [ ] Tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
9. [ ] Push: `git push origin main && git push origin vX.Y.Z`
10. [ ] GitHub release: `gh release create vX.Y.Z --notes-file RELEASE_NOTES_vX.Y.Z.md --latest`

### 📚 Documentation References
- **AI Instructions**: `.github/instructions/release-management.instruction.md`
- **Full Process**: `.github/RELEASE_PROCESS.md`
- **Release Helper**: `scripts/release.sh`
- **Workflow**: `.github/workflows/release-management.yml`

---
**🤖 AI Rule**: ALWAYS use `./scripts/release.sh` before manual process!
