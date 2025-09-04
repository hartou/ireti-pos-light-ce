# 🤖 GitHub Copilot Branch Workflow

This repository is configured with an automated branch management system for GitHub Copilot development. This ensures all Copilot work happens in separate branches and gets properly merged back to main through Pull Requests.

## 🎯 Workflow Overview

### 1. **Branch Creation**
- All Copilot development happens in feature branches with the prefix `copilot/`
- Branches are automatically created with timestamps to avoid conflicts
- Each branch gets a tracking issue for progress monitoring

### 2. **Development Process**
- Make changes in the feature branch
- Commit and push changes regularly
- Automated testing runs on each push

### 3. **Merge Back to Main**
- Create a Pull Request when ready
- Automated checks run (Django tests, Docker build, security scans)
- Auto-merge happens after all checks pass
- Feature branch is automatically cleaned up

## 🚀 Quick Start

### Method 1: Using GitHub Actions (Recommended)

1. **Create a new Copilot branch:**
   - Go to the Actions tab in GitHub
   - Run "GitHub Copilot Branch Management" workflow
   - Provide feature name and description
   - Branch will be created automatically

2. **Start development:**
   ```bash
   git fetch origin
   git checkout copilot/your-feature-name-20250831-123456
   # Make your changes...
   git add .
   git commit -m "Your changes"
   git push origin copilot/your-feature-name-20250831-123456
   ```

3. **Create Pull Request:**
   ```bash
   gh pr create --title "🤖 Copilot: Your feature" --body "Description"
   ```

### Method 2: Using the Helper Script

```bash
# Create a new feature branch
./scripts/copilot-branch.sh create "fix-login-bug" "Fix authentication issue"

# List all Copilot branches
./scripts/copilot-branch.sh list

# Switch to an existing branch
./scripts/copilot-branch.sh switch fix-login-bug

# Create a Pull Request
./scripts/copilot-branch.sh pr

# Clean up merged branches
./scripts/copilot-branch.sh cleanup
```

## 🔄 Automated Processes

### Branch Protection
- Main branch is protected from direct pushes
- All changes must go through Pull Requests
- Copilot branches bypass protection rules for development

### Quality Gates
When a PR is created from a `copilot/` branch, these checks run automatically:

1. **Django Application Checks**
   - `python manage.py check --deploy`
   - Migration validation
   - Basic Django tests

2. **Docker Container Testing**
   - Build Docker image from branch
   - Test container startup
   - Verify Django application responds

3. **Security Scanning**
   - Dependency vulnerability checks with `safety`
   - Code security analysis with `bandit`

4. **Auto-merge**
   - If all checks pass, PR is automatically merged
   - Tracking issue is closed
   - Feature branch is deleted

## 📋 Branch Naming Convention

Branches follow this pattern:
```
copilot/<feature-name>-<timestamp>
```

Examples:
- `copilot/fix-login-bug-20250831-143022`
- `copilot/add-pwa-features-20250831-143125`
- `copilot/update-docker-config-20250831-143200`

## 🛠️ Manual Workflow (If Needed)

If you need to create branches manually:

```bash
# 1. Ensure main is up to date
git checkout main
git pull origin main

# 2. Create feature branch
git checkout -b copilot/your-feature-$(date +%Y%m%d-%H%M%S)

# 3. Make changes and commit
git add .
git commit -m "🤖 Your changes"
git push -u origin copilot/your-feature-$(date +%Y%m%d-%H%M%S)

# 4. Create PR
gh pr create --title "🤖 Copilot: Your feature" --body "Description" --label "copilot"
```

## 📊 Workflow Benefits

### ✅ **For Copilot Development**
- **Isolation**: Changes don't affect main until ready
- **Testing**: Automated validation before merge
- **Traceability**: Each feature has its own branch and issue
- **Rollback**: Easy to revert if something goes wrong

### ✅ **For Repository Management**
- **Clean History**: Squashed commits keep history readable
- **Automated Cleanup**: No orphaned branches
- **Quality Control**: All changes go through validation
- **Documentation**: Tracking issues document what was done

## 🔧 Configuration

### Environment Variables
The workflow uses these GitHub secrets/variables:
- `GITHUB_TOKEN`: Automatically provided by GitHub Actions
- No additional secrets required

### Permissions Required
The workflow needs these permissions:
- `contents: write` - To create branches and merge PRs
- `pull-requests: write` - To create and merge PRs
- `issues: write` - To create tracking issues

### Customization
You can customize the workflow by editing:
- `.github/workflows/copilot-branch-workflow.yml`
- `.github/workflows/copilot-auto-merge.yml`
- `scripts/copilot-branch.sh`

## 🚨 Troubleshooting

### Branch Creation Fails
- Check if you have push permissions to the repository
- Ensure main branch exists and is accessible

### Auto-merge Doesn't Work
- Check if PR is from a `copilot/` branch
- Verify all required checks are passing
- Look at the Actions tab for detailed logs

### Tests Fail
- Review the test output in GitHub Actions
- Fix issues in your feature branch
- Push changes to re-trigger tests

### Manual Override
If you need to merge manually:
```bash
# Force merge a Copilot PR
gh workflow run copilot-auto-merge.yml -f pr_number=123 -f force_merge=true
```

## 📞 Support

If you encounter issues with the Copilot workflow:

1. Check the GitHub Actions logs
2. Review this documentation
3. Create an issue with the `workflow` label
4. Contact the repository maintainers

---

**Happy Coding with GitHub Copilot! 🚀🤖**
