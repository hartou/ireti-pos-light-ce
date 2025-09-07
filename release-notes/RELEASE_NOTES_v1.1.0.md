# Ireti POS Light CE v1.1.0 Release Notes

**Release Date:** September 7, 2025  
**Release Type:** Minor Release - UI Fixes & Admin Enhancements

## 🎉 What's New in v1.1.0

This release focuses on fixing admin interface issues and enhancing the user experience with comprehensive admin tools.

## ✅ Fixed Issues

### Admin Interface Fixes
- **Fixed admin_transactions URL access** - Resolved TemplateDoesNotExist error for admin transactions page
- **Fixed admin_system URL access** - Resolved TemplateDoesNotExist error for admin system management page
- **Database field compatibility** - Fixed model field mismatches (timestamp→date_time, total→total_sale)
- **Docker configuration** - Fixed image paths and requirements file references in Docker setup

### Template Enhancements
- **Created comprehensive admin/transactions.html** - Full-featured transaction management interface
- **Created complete admin/system.html** - System administration and maintenance interface
- **Enhanced base template** - Added proper CSS block inheritance support

## 🚀 New Features

### Transaction Management Interface
- Complete transaction overview with filtering and search
- Real-time statistics dashboard (total transactions, revenue, averages)
- Advanced filtering by date range and payment type
- Responsive table with pagination and sorting
- Export and print functionality
- Transaction status indicators and action buttons

### System Administration Interface
- System health monitoring dashboard
- Database statistics and health indicators
- System information display (Django version, Python version, database engine)
- Maintenance tools (cache clearing, database backup, optimization)
- Log file management and viewing
- System status indicators with color-coded health status

### Enhanced Docker Support
- Fixed Docker build issues with requirements.txt path
- Improved container startup scripts
- Better environment variable handling
- Auto-creation of admin users in containers

## 🛠️ Technical Improvements

### Code Quality
- Fixed model field references throughout admin views
- Improved error handling in admin interface
- Better template inheritance structure
- Enhanced responsive design for mobile devices

### Docker & Deployment
- Updated Docker image build process
- Fixed static file collection in containers
- Improved production deployment configuration
- Better environment variable documentation

## 📦 Distribution Options

### Docker Distribution
- **Pre-built Container**: `ghcr.io/hartou/ireti-pos-light-ce:1.1.0-CE`
- **Docker Compose**: Quick start with development and production configurations
- **Manual Build**: Build from source with updated Dockerfile

### Standalone Distribution
- **Source Code**: Complete application with production-ready configuration
- **Requirements**: Updated dependencies for Python 3.8+
- **Installation Guide**: Step-by-step setup instructions

## 🔧 Installation & Upgrade

### New Installation
```bash
# Docker (Recommended)
docker run -p 8000:8000 -e STRIPE_SECRET_KEY=sk_test_... ghcr.io/hartou/ireti-pos-light-ce:1.1.0-CE

# Or with Docker Compose
git clone https://github.com/hartou/ireti-pos-light-ce
cd ireti-pos-light-ce
docker-compose up -d
```

### Upgrade from v1.0.0
```bash
git pull origin main
git checkout v1.1.0-CE
docker-compose build --no-cache
docker-compose up -d
```

## 🧪 Testing & Validation

- ✅ Playwright automated testing confirms admin URLs working
- ✅ Docker container builds successfully
- ✅ Admin interface fully functional with authentication
- ✅ Database migrations tested and working
- ✅ Static file collection working in production

## 📋 Requirements

- Python 3.8+
- Django 4.1.13
- SQLite (default) or PostgreSQL
- Stripe API keys for payment processing
- Docker (optional but recommended)

## 🔗 Links

- **Repository**: https://github.com/hartou/ireti-pos-light-ce
- **Docker Hub**: `ghcr.io/hartou/ireti-pos-light-ce:1.1.0-CE`
- **Documentation**: See `docs/` directory
- **Issues**: https://github.com/hartou/ireti-pos-light-ce/issues

## 🙏 Acknowledgments

This release addresses critical admin interface issues that prevented proper system management. The enhanced admin tools provide comprehensive system oversight and maintenance capabilities.

## 📝 Migration Notes

No database migrations required for this release. All changes are UI and template-based improvements.

---

**Download Links:**
- [Source Code (ZIP)](../../ireti-pos-light-ce-1.1.0-CE-standalone.zip)
- [Docker Files (ZIP)](../../ireti-pos-light-ce-1.1.0-CE-docker.zip)
- [GitHub Release](https://github.com/hartou/ireti-pos-light-ce/releases/tag/v1.1.0-CE)
