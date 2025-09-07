#!/bin/bash
# Ireti POS Light CE - Release Preparation Script
# This script prepares the v1.0.0-CE release with multiple distribution options

set -e

VERSION="1.1.0-CE"
RELEASE_DIR="release/v${VERSION}"
DOCKER_IMAGE="ghcr.io/hartou/ireti-pos-light-ce"

echo "🚀 Preparing Ireti POS Light CE Release v${VERSION}"
echo "================================================="

# Create release directory structure
echo "📁 Creating release directory structure..."
mkdir -p "${RELEASE_DIR}"
mkdir -p "${RELEASE_DIR}/docker"
mkdir -p "${RELEASE_DIR}/standalone"
mkdir -p "${RELEASE_DIR}/docs"

# Prepare standalone distribution (source code without dev dependencies)
echo "📦 Preparing standalone distribution..."
rsync -av \
    --exclude='.git' \
    --exclude='.venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='node_modules' \
    --exclude='.pytest_cache' \
    --exclude='release' \
    --exclude='*.log' \
    --exclude='.env*' \
    . "${RELEASE_DIR}/standalone/ireti-pos-light-ce-${VERSION}/"

# Create a requirements.txt without development dependencies
echo "📝 Creating production requirements.txt..."
cat > "${RELEASE_DIR}/standalone/ireti-pos-light-ce-${VERSION}/requirements.txt" << 'EOF'
# Ireti POS Light CE v1.0.0 - Production Requirements
Django==4.1.13
python-dotenv==0.21.0
requests==2.31.0
stripe==5.4.0
gunicorn==21.2.0
whitenoise==6.5.0
psycopg2-binary==2.9.7
django-colorfield==0.7.2
django-import-export==2.8.0
pandas==1.4.3
plotly==5.10.0
python-dateutil==2.8.2
pytz==2022.1
django-jquery==3.1.0
django-mathfilters==1.0.0
EOF

# Create installation guide for standalone
echo "📚 Creating installation guide..."
cat > "${RELEASE_DIR}/standalone/INSTALLATION.md" << 'EOF'
# Ireti POS Light CE v1.0.0 - Standalone Installation

## Prerequisites
- Python 3.8 or higher
- pip package manager
- SQLite (included) or PostgreSQL (optional)

## Quick Installation

### 1. Extract and Navigate
```bash
unzip ireti-pos-light-ce-1.0.0-CE-standalone.zip
cd ireti-pos-light-ce-1.0.0-CE
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env with your Stripe keys and other settings
```

### 5. Initialize Database
```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 6. Start Development Server
```bash
python manage.py runserver
```

Visit http://localhost:8000 to access your POS system.

## Production Deployment
For production deployment, see docs/DEPLOYMENT.md
EOF

# Create Docker release files
echo "🐳 Preparing Docker distribution..."
cp docker/docker-compose.yml "${RELEASE_DIR}/docker/"
cp docker/docker-compose.prod.yml "${RELEASE_DIR}/docker/"
cp docker/dockerfile "${RELEASE_DIR}/docker/"

# Create Docker installation guide
cat > "${RELEASE_DIR}/docker/DOCKER_INSTALLATION.md" << 'EOF'
# Ireti POS Light CE v1.0.0 - Docker Installation

## Prerequisites
- Docker Engine 20.10+
- Docker Compose v2.0+

## Quick Start with Docker

### Option 1: Development Setup
```bash
# Clone or extract files
docker-compose up -d
```

### Option 2: Production Setup
```bash
# Set environment variables
export STRIPE_SECRET_KEY="sk_live_..."
export STRIPE_PUBLISHABLE_KEY="pk_live_..."
export DJANGO_SECRET_KEY="your-secret-key"

# Start production stack
docker-compose -f docker-compose.prod.yml up -d
```

### Option 3: Pre-built Image
```bash
docker run -d \
  -p 8000:8000 \
  -e STRIPE_SECRET_KEY="sk_test_..." \
  -e STRIPE_PUBLISHABLE_KEY="pk_test_..." \
  ghcr.io/hartou/ireti-pos-light-ce:1.0.0
```

## Configuration
Create a `.env` file with your Stripe configuration:
```
STRIPE_SECRET_KEY=sk_test_your_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here
STRIPE_WEBHOOK_ENDPOINT_SECRET=whsec_your_secret_here
DJANGO_SECRET_KEY=your-django-secret-key
```
EOF

# Copy documentation
echo "📖 Copying documentation..."
cp -r docs/ "${RELEASE_DIR}/docs/"
cp README.md "${RELEASE_DIR}/"
cp LICENSE "${RELEASE_DIR}/"
cp release-notes/RELEASE_NOTES_v1.0.0.md "${RELEASE_DIR}/RELEASE_NOTES.md"

# Create release summary
cat > "${RELEASE_DIR}/README.md" << 'EOF'
# 🛒 Ireti POS Light CE v1.0.0 - Community Edition Release

Welcome to the first official release of Ireti POS Light Community Edition!

## 🎉 What's Included

### 📦 Distribution Options
- **`standalone/`** - Complete source code for manual installation
- **`docker/`** - Docker containers for easy deployment
- **`docs/`** - Complete documentation and guides

### 🚀 Quick Start Options

#### Option 1: Docker (Recommended)
```bash
cd docker/
docker-compose up -d
```

#### Option 2: Standalone Installation
```bash
cd standalone/ireti-pos-light-ce-1.0.0-CE/
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

#### Option 3: Pre-built Container
```bash
docker run -p 8000:8000 ghcr.io/hartou/ireti-pos-light-ce:1.0.0
```

## 📚 Documentation
- `INSTALLATION.md` - Detailed installation instructions
- `docs/DEPLOYMENT.md` - Production deployment guide
- `docs/STRIPE_TESTING_GUIDE.md` - Payment testing setup
- `RELEASE_NOTES.md` - Complete changelog

## 🔗 Links
- **Repository**: https://github.com/hartou/ireti-pos-light-ce
- **Container**: ghcr.io/hartou/ireti-pos-light-ce:1.0.0
- **Issues**: https://github.com/hartou/ireti-pos-light-ce/issues
- **Documentation**: See `docs/` directory

## 💡 Need Help?
Check the documentation in the `docs/` folder or visit our GitHub repository for support.
EOF

# Create .env.example for standalone
cat > "${RELEASE_DIR}/standalone/ireti-pos-light-ce-${VERSION}/.env.example" << 'EOF'
# Ireti POS Light CE Configuration

# Django Settings
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=change-this-to-a-secure-random-key
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Database (optional - defaults to SQLite)
# DATABASE_URL=postgres://user:password@localhost:5432/iretiposlightdb

# Stripe Payment Configuration
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_WEBHOOK_ENDPOINT_SECRET=whsec_your_webhook_secret_here

# Optional Stripe Settings
STRIPE_CURRENCY=USD
STRIPE_MINIMUM_CHARGE=50
STRIPE_REFUND_DAYS_LIMIT=120

# Admin User (for Docker)
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=Admin123!
EOF

echo "✅ Release preparation complete!"
echo ""
echo "📁 Release files created in: ${RELEASE_DIR}/"
echo "🐳 Docker image will be: ${DOCKER_IMAGE}:${VERSION}"
echo ""
echo "Next steps:"
echo "1. Review files in ${RELEASE_DIR}/"
echo "2. Build and push Docker image"
echo "3. Create GitHub release"
echo "4. Create distribution archives"
