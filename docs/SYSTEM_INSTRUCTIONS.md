# System Instructions for Ireti POS Light

This document provides comprehensive system instructions for contributors, maintainers, and automated processes working on the Ireti POS Light project.

## 🎯 Project Overview

**Ireti POS Light** is a modern, Django-based Point-of-Sale system with Progressive Web App features, designed for small to medium retail businesses. The project emphasizes:

- **Code Quality**: Automated testing, linting, and security scanning
- **Modern Architecture**: PWA features, containerization, and cloud-native deployment
- **Developer Experience**: Automated workflows, comprehensive documentation, and clear contribution guidelines

## 🚀 Development Workflow

### GitHub Copilot Branch Management

This project uses an automated branch management system for all development work:

#### For GitHub Copilot and Contributors:
1. **Never commit directly to main** - Always use feature branches
2. **Use the branch workflow**: 
   - Method 1: GitHub Actions → "GitHub Copilot Branch Management"
   - Method 2: `./scripts/copilot-branch.sh create "feature-name" "description"`
   - Method 3: Manual branch with `copilot/` prefix

#### Branch Naming Convention:
```
copilot/<feature-name>-<timestamp>
```

#### Quality Gates:
All Pull Requests from `copilot/` branches automatically run:
- Django deployment checks
- Database migration validation
- Docker container build and test
- Security scanning (safety, bandit)
- Auto-merge after all checks pass

## 📋 Release Management

### Version Strategy
- **Semantic Versioning**: MAJOR.MINOR.PATCH
- **Release Branches**: `release/vX.Y.Z` for preparing releases
- **Tagged Releases**: Git tags trigger Docker image builds
- **Container Registry**: GitHub Container Registry (GHCR)

### Release Process:
1. Create release branch from main
2. Update `version.py` and `CHANGELOG.md`
3. Create Git tag: `git tag -a vX.Y.Z -m "Release message"`
4. Push tag to trigger Docker build
5. Create GitHub release with release notes
6. Merge release branch back to main

### Docker Images:
```bash
# Latest release
ghcr.io/hartou/ireti-pos-light:latest

# Specific versions
ghcr.io/hartou/ireti-pos-light:v0.0.2
ghcr.io/hartou/ireti-pos-light:0.0.2
```

## 🛠️ Development Environment

### Prerequisites:
- Python 3.8+
- Docker and Docker Compose
- Node.js (for PWA development)
- Git and GitHub CLI (recommended)

### Setup Commands:
```bash
# Clone repository
git clone https://github.com/hartou/ireti-pos-light.git
cd ireti-pos-light

# Development setup
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser

# Docker development
docker compose up --build

# Production testing
docker compose -f docker-compose.prod.yml up -d
```

## 🔄 Automated Workflows

### Issue Management:
- **Auto-creation**: Issues created from user story tables
- **Auto-closing**: Issues closed when stories marked complete
- **Labels**: Automatic labeling based on content type

### Code Quality:
- **Linting**: Python code style checks
- **Security**: Dependency and code security scanning
- **Testing**: Django tests and Docker container validation
- **Documentation**: Automatic documentation updates

### Deployment:
- **Container Builds**: Automatic on tag push
- **Multi-platform**: AMD64 and ARM64 support
- **Registry Publishing**: GitHub Container Registry
- **Health Checks**: Container health monitoring

## 📚 Documentation Standards

### Required Documentation:
- **CHANGELOG.md**: All notable changes
- **README.md**: Project overview and quick start
- **DEPLOYMENT.md**: Production deployment guide
- **API Documentation**: Inline code documentation

### Documentation Updates:
- Update CHANGELOG.md for every release
- Keep README.md current with new features
- Document breaking changes prominently
- Include migration guides for major updates

## 🧪 Testing Strategy

### Test Types:
1. **Unit Tests**: Django model and view tests
2. **Integration Tests**: End-to-end workflow testing
3. **Container Tests**: Docker build and startup validation
4. **Security Tests**: Vulnerability and configuration scanning

### Test Execution:
```bash
# Run Django tests
python manage.py test

# Docker container test
docker build -t test-image .
docker run --rm test-image python manage.py check

# Security scanning
safety check
bandit -r . -x ./venv
```

## 🔒 Security Guidelines

### Code Security:
- **Dependency Management**: Regular updates and vulnerability scanning
- **Secrets Management**: Environment variables, never hardcoded
- **Input Validation**: Proper Django form validation
- **SQL Injection Prevention**: Use Django ORM, avoid raw queries

### Container Security:
- **Base Images**: Use official, updated base images
- **Non-root Users**: Run containers with non-privileged users
- **Minimal Images**: Multi-stage builds for production
- **Security Scanning**: Automatic vulnerability detection

### Deployment Security:
- **HTTPS**: Always use SSL/TLS in production
- **Database Security**: Strong passwords, network isolation
- **Access Control**: Role-based permissions
- **Backup Strategy**: Regular, encrypted backups

## 🎨 Code Style Guidelines

### Python Code Style:
- **PEP 8**: Standard Python style guide
- **Django Conventions**: Follow Django best practices
- **Docstrings**: Document all classes and functions
- **Type Hints**: Use type annotations where appropriate

### Frontend Code Style:
- **Consistent Indentation**: 2 spaces for HTML/CSS/JS
- **Modern JavaScript**: ES6+ features where supported
- **CSS Organization**: Modular, reusable stylesheets
- **PWA Standards**: Follow PWA best practices

### File Organization:
```
ireti-pos-light/
├── docs/                   # Documentation
├── scripts/               # Automation scripts
├── .github/workflows/     # CI/CD workflows
├── onlineretailpos/       # Django project
│   ├── settings/          # Environment configs
│   ├── static/           # Static assets
│   └── templates/        # HTML templates
├── cart/                 # Django app
├── inventory/            # Django app
├── transaction/          # Django app
└── requirements.txt      # Python dependencies
```

## 🚨 Error Handling

### Development Errors:
- **Django Debug**: Detailed error pages in development
- **Logging**: Comprehensive logging for debugging
- **Error Reporting**: Structured error information

### Production Errors:
- **Graceful Degradation**: Fallback functionality
- **User-Friendly Messages**: Clear error communication
- **Error Tracking**: Monitoring and alerting
- **Recovery Procedures**: Automatic retry mechanisms

## 📞 Support and Communication

### Getting Help:
- **Documentation**: Check docs/ directory first
- **GitHub Issues**: Report bugs and request features
- **GitHub Discussions**: Ask questions and share ideas
- **Pull Requests**: Contribute improvements

### Communication Guidelines:
- **Clear Descriptions**: Detailed issue and PR descriptions
- **Reproducible Examples**: Include steps to reproduce issues
- **Respectful Interaction**: Professional and constructive communication
- **Timely Responses**: Acknowledge contributions promptly

## 🏁 Quick Reference

### Common Commands:
```bash
# Start development
./scripts/copilot-branch.sh create "feature-name" "description"

# Run tests
python manage.py test

# Docker development
docker compose up --build

# Create release
git tag -a v0.0.3 -m "Release v0.0.3"
git push origin v0.0.3

# Deploy production
docker compose -f docker-compose.prod.yml up -d
```

### Important Files:
- `CHANGELOG.md` - Project changelog
- `version.py` - Current version information
- `requirements.txt` - Python dependencies
- `docker-compose.yml` - Development environment
- `docker-compose.prod.yml` - Production environment
- `.env.example` - Environment configuration template

---

**📝 Note**: This document should be updated whenever significant changes are made to the development workflow or project structure.
