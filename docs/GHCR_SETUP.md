# Docker and GitHub Container Registry (GHCR) Setup

This document explains how to make your Docker images publicly available on GitHub Container Registry.

## 🐳 Current Status

- **Repository**: Public ✅
- **GHCR Package**: Needs to be made public ⚠️
- **Docker Image**: `ghcr.io/hartou/ireti-pos-light-ce:latest`

## 📦 Making GHCR Package Public

### Method 1: GitHub Web Interface (Recommended)

1. Go to [https://github.com/hartou/ireti-pos-light-ce/packages](https://github.com/hartou/ireti-pos-light-ce/packages)
2. Click on your package: `ireti-pos-light-ce`
3. Click on "Package settings" (gear icon)
4. Scroll down to "Danger Zone"
5. Click "Change visibility"
6. Select "Public"
7. Type the package name to confirm: `ireti-pos-light-ce`
8. Click "I understand the consequences, change package visibility"

### Method 2: GitHub CLI

```bash
gh api --method PATCH /user/packages/container/ireti-pos-light-ce --field visibility=public
```

### Method 3: REST API

```bash
curl -X PATCH \
  -H 'Accept: application/vnd.github.v3+json' \
  -H 'Authorization: token YOUR_PERSONAL_ACCESS_TOKEN' \
  https://api.github.com/user/packages/container/ireti-pos-light-ce \
  -d '{"visibility":"public"}'
```

## 🚀 Using the Public Docker Image

Once the package is public, anyone can use:

```bash
# Pull the latest image
docker pull ghcr.io/hartou/ireti-pos-light-ce:latest

# Run the container
docker run -p 8000:8000 -e DJANGO_SUPERUSER_USERNAME=admin -e DJANGO_SUPERUSER_PASSWORD=admin123 ghcr.io/hartou/ireti-pos-light-ce:latest

# Access the application
open http://localhost:8000
```

## 🔄 Automatic Builds

The repository includes a GitHub Actions workflow that automatically:

- Builds Docker images on every push to `main`
- Supports multi-architecture builds (AMD64 and ARM64)
- Tags images with version numbers and `latest`
- Pushes to GHCR with proper metadata

## 🔧 Local Development

For local development, you can still use docker-compose:

```bash
docker-compose up --build
```

## 📋 Benefits of Public GHCR Package

- ✅ No authentication required for pulling
- ✅ Faster downloads for users
- ✅ Better discoverability
- ✅ Automatic security scanning
- ✅ Integration with GitHub releases

## 🔒 Security Notes

- Public packages are scanned automatically for vulnerabilities
- Source code in this repository is already public
- No sensitive information should be in the Docker image
- Environment variables for secrets should be provided at runtime