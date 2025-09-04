# 🏪 Ireti POS Light v1.0.0

**A Modern, Lightweight Point-of-Sale System with Complete Stripe Payment Integration**

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-brightgreen?style=flat-square" alt="version">
  <img src="https://img.shields.io/github/license/hartou/ireti-pos-light?style=flat-square&logo=opensourceinitiative&logoColor=white&color=0080ff" alt="license">
  <img src="https://img.shields.io/github/last-commit/hartou/ireti-pos-light?style=flat-square&logo=git&logoColor=white&color=0080ff" alt="last-commit">
  <img src="https://img.shields.io/github/languages/top/hartou/ireti-pos-light?style=flat-square&color=0080ff" alt="repo-top-language">
  <img src="https://img.shields.io/badge/payments-stripe-purple?style=flat-square&logo=stripe" alt="stripe-integration">
</p>

---

## 📋 What is Ireti POS Light?

**Ireti POS Light v1.0.0** is a production-ready, web-based Point-of-Sale (POS) system built with Django that enables businesses to manage retail operations with modern payment processing. This major release introduces complete Stripe payment integration, making it a comprehensive solution for businesses requiring secure, reliable payment processing.

### 🎯 **Core Purpose**
- **💳 Payment Processing**: Complete Stripe integration with real-time payment processing, refunds, and transaction management
- **🛒 Sales Management**: Process customer transactions with barcode scanning, product lookup, and digital receipt generation
- **📦 Inventory Control**: Track product stock levels, manage departments, and add new inventory items
- **Multi-Device Access**: Use on desktops, tablets, or mobile devices with responsive design
- **Offline Capability**: Continue operations even when internet connectivity is intermittent
- **Customer Display**: Dual-screen support for customer-facing product information and promotional content

### 🏢 **Who Is This For?**
- Small retail stores and cafes
- Pop-up shops and market vendors  
- Service businesses needing transaction tracking
- Organizations requiring a lightweight, self-hosted POS solution
- Developers looking for a modern Django POS system to customize

---

## ✨ Key Features

### 🛒 **POS Operations**
- **Product Management**: Add, edit, and organize products by departments
- **Transaction Processing**: Complete sales workflow with cart management
- **Receipt Generation**: Automatic receipt printing and digital receipts
- **Price Lookup**: Quick product search and pricing verification
- **Multi-Payment Support**: Cash and digital payment tracking

### 🌐 **Progressive Web App (PWA)**
- **Installable**: Can be installed on any device like a native app
- **Offline Mode**: Service worker enables offline functionality
- **Responsive Design**: Optimized for desktop, tablet, and mobile use
- **Network Status**: Real-time connection status indicators
- **Background Updates**: Automatic app updates when online

### 📊 **Management & Reporting**
- **Sales Dashboard**: Real-time sales analytics and reporting
- **Department Dashboard**: Performance tracking by product categories
- **Product Dashboard**: Inventory levels and product performance
- **Transaction History**: Complete audit trail of all sales
- **Multi-User Support**: Role-based access with staff and admin levels

### 🖥️ **Technical Features**
- **Multi-Language Support**: Internationalization (i18n) ready
- **Database Flexibility**: SQLite (development) or PostgreSQL (production)
- **Docker Ready**: Containerized deployment with Docker Compose
- **Customer Display**: Secondary screen support for customer-facing information
- **Hardware Integration**: Receipt printer support (ESCPOS compatible)

---

## 🚀 Quick Start

### Option 1: Using Pre-built Docker Image (Recommended)

```bash
# Pull the latest image from GitHub Container Registry
docker pull ghcr.io/hartou/ireti-pos-light:latest

# Run with automatic admin user creation
docker run -p 8000:8000 \
  -e DJANGO_SUPERUSER_USERNAME=admin \
  -e DJANGO_SUPERUSER_PASSWORD=Admin123! \
  -e DJANGO_SUPERUSER_EMAIL=admin@example.com \
  ghcr.io/hartou/ireti-pos-light:latest
```

**Access the application:**
- Main POS Interface: http://localhost:8000
- Admin Panel: http://localhost:8000/admin/
- Login with the credentials you provided above

### Option 2: Production Deployment with Docker Compose

```bash
# Clone the repository
git clone https://github.com/hartou/ireti-pos-light.git
cd ireti-pos-light

# Download production configuration
curl -O https://github.com/hartou/ireti-pos-light/releases/latest/download/docker-compose.prod.yml
curl -O https://github.com/hartou/ireti-pos-light/releases/latest/download/.env.example

# Configure your environment
cp .env.example .env
# Edit .env with your database credentials and settings

# Start with PostgreSQL and Nginx
docker compose -f docker-compose.prod.yml up -d
```

### Option 3: Development Setup

```bash
# Clone the repository
git clone https://github.com/hartou/ireti-pos-light.git
cd ireti-pos-light

# Install Python dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Create a superuser account
python manage.py createsuperuser

# Start the development server
python manage.py runserver 0.0.0.0:8000
```

---

## 📦 Deployment Options

### 🐳 **Docker Container Registry**

**Images are available from GitHub Container Registry:**

```bash
# Latest stable release
docker pull ghcr.io/hartou/ireti-pos-light:latest

# Specific version
docker pull ghcr.io/hartou/ireti-pos-light:v0.0.2

# All available tags
docker pull ghcr.io/hartou/ireti-pos-light:0.0.2
```

### 🗄️ **Database Options**

#### **Development (SQLite)**
- Default configuration for local development
- No additional setup required
- Data stored in local SQLite file

#### **Production (PostgreSQL)**
- Recommended for production deployments
- Use the provided `docker-compose.prod.yml`
- Includes database backups and persistent volumes

```yaml
# Example docker-compose.yml database configuration
services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: iretiposlightdb
      POSTGRES_USER: iretiposlightuser
      POSTGRES_PASSWORD: your_secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

#### **External Database**
Configure any PostgreSQL database by setting the `DATABASE_URL`:

```bash
# Environment variable format
DATABASE_URL=postgres://username:password@host:port/database_name

# Example with cloud database
DATABASE_URL=postgres://user:pass@db.example.com:5432/pos_database
```

### 🌐 **Production Deployment**

For production environments, the system includes:

- **Nginx Reverse Proxy**: Handles static files and SSL termination
- **PostgreSQL Database**: Reliable data persistence with backups
- **Docker Health Checks**: Automatic service monitoring and restart
- **SSL Support**: HTTPS configuration for secure transactions
- **Environment Configuration**: Secure secrets management

See our [Deployment Guide](https://github.com/hartou/ireti-pos-light/blob/main/DEPLOYMENT.md) for complete production setup instructions.

---

## 🔧 Configuration

### **Environment Variables**

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DJANGO_SECRET_KEY` | Django secret key for security | Generated | Yes |
| `DATABASE_URL` | Database connection string | SQLite | No |
| `DJANGO_DEBUG` | Enable debug mode | `False` | No |
| `DJANGO_ALLOWED_HOSTS` | Allowed hostnames | `localhost` | No |
| `DJANGO_SUPERUSER_USERNAME` | Admin username | - | Recommended |
| `DJANGO_SUPERUSER_PASSWORD` | Admin password | - | Recommended |
| `DJANGO_SUPERUSER_EMAIL` | Admin email | `admin@example.com` | No |

### **Hardware Integration**

- **Receipt Printers**: ESCPOS compatible thermal printers
- **Barcode Scanners**: USB HID-compliant barcode scanners
- **Customer Display**: Secondary monitor support for customer-facing screen
- **Touch Screens**: Optimized for touch interface on tablets and POS terminals

---

## 📱 Progressive Web App Features

### **Installation**
- Install directly from browser on any device
- Works like a native application
- Desktop shortcuts and app icons

### **Offline Functionality**
- Service worker caches essential resources
- Continue processing sales during network outages
- Automatic sync when connection is restored

### **Multi-Device Synchronization**
- Real-time inventory updates across devices
- Centralized transaction history
- Consistent user experience on all platforms

---

## 🛠️ Development & Customization

### **Technology Stack**
- **Backend**: Django 4.1.13 (Python web framework)
- **Frontend**: Bootstrap 4, jQuery, HTML5/CSS3
- **Database**: SQLite (dev) / PostgreSQL (production)  
- **Containerization**: Docker & Docker Compose
- **PWA**: Service Workers, Web App Manifest
- **Internationalization**: Django i18n framework

### **Project Structure**
```
ireti-pos-light/
├── cart/              # Shopping cart functionality
├── inventory/         # Product and inventory management
├── transaction/       # Sales transaction processing
├── onlineretailpos/   # Main Django project settings
│   ├── static/        # CSS, JavaScript, images
│   ├── templates/     # HTML templates
│   └── settings/      # Environment-specific settings
├── screenshots/       # Application screenshots
└── docker-compose.yml # Development Docker setup
```

### **Contributing**
1. Fork the repository: https://github.com/hartou/ireti-pos-light
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes and test thoroughly
4. Submit a pull request with clear description

### **Release Process**
This project follows a standardized release process with automated tooling:

```bash
# ✅ PREFERRED: Use release helper script (handles everything)
./scripts/release.sh create v1.0.1        # Patch release
./scripts/release.sh create v1.1.0        # Minor release  
./scripts/release.sh create v2.0.0        # Major release
./scripts/release.sh create v1.0.1 --auto-push  # Auto-push and create GitHub release

# ⚠️ Manual process (only if helper script fails)
1. Update version files (version.py, package.json)
2. Create release notes (RELEASE_NOTES_vX.Y.Z.md)
3. Commit and tag: git tag -a vX.Y.Z -m "Release vX.Y.Z"
4. Push: git push origin main && git push origin vX.Y.Z
5. Create GitHub release: gh release create vX.Y.Z --notes-file RELEASE_NOTES_vX.Y.Z.md
```

**🤖 AI Assistants**: ALWAYS use `./scripts/release.sh` - see `.github/instructions/release-management.instruction.md`

- **Release Documentation**: [.github/RELEASE_PROCESS.md](.github/RELEASE_PROCESS.md)
- **Automated Workflows**: [.github/workflows/release-management.yml](.github/workflows/release-management.yml)
- **Release Helper**: [scripts/release.sh](scripts/release.sh)

---

## 📞 Support & Documentation

- **GitHub Repository**: https://github.com/hartou/ireti-pos-light
- **Container Images**: https://github.com/hartou/ireti-pos-light/pkgs/container/ireti-pos-light
- **Latest Releases**: https://github.com/hartou/ireti-pos-light/releases
- **Issue Tracker**: https://github.com/hartou/ireti-pos-light/issues
- **Deployment Guide**: [DEPLOYMENT.md](https://github.com/hartou/ireti-pos-light/blob/main/DEPLOYMENT.md)

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🚀 Get Started Today!

Ready to streamline your retail operations? Choose your deployment method above and have your POS system running in minutes!

**Need help?** Check our [documentation](https://github.com/hartou/ireti-pos-light/wiki) or [open an issue](https://github.com/hartou/ireti-pos-light/issues) for support.
