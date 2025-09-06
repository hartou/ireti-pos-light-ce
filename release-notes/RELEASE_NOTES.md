# Ireti POS Light - Release Notes

## Version 0.0.1 - MVP Release
**Release Date:** August 17, 2025

### 🎉 What's New
This is the initial MVP (Minimum Viable Product) release of Ireti POS Light - a modern web-based Point of Sale system built with Django.

### ✨ Features Included
- **Complete POS System**
  - Barcode scanning and product lookup
  - Shopping cart management
  - Transaction processing with multiple payment types (Cash, EBT, Credit/Debit)
  - Receipt generation and printing
  - Tax and deposit calculations

- **Inventory Management**
  - Product catalog with barcode support
  - Add/update inventory items
  - Department-based organization
  - Price lookup functionality

- **Dashboard & Reporting**
  - Sales dashboard with analytics
  - Department performance tracking
  - Product analytics dashboard
  - Transaction history and reporting
  - Interactive charts and visualizations

- **Progressive Web App (PWA)**
  - Service worker for offline functionality
  - App manifest for installation
  - Mobile-responsive design
  - Network status indicators
  - Install prompt for mobile devices

- **Multi-language Support**
  - Internationalization (i18n) ready
  - Language switching interface
  - Support for English, French, and Spanish

- **Authentication & Security**
  - User authentication system
  - Role-based access control
  - Admin panel integration
  - Secure session management

- **Docker Support**
  - Complete Docker Compose setup
  - PostgreSQL database integration
  - Development and production configurations
  - Volume mounting for live development

### 🔧 Technical Details
- **Backend:** Django 4.1.13
- **Database:** PostgreSQL
- **Frontend:** Bootstrap 4, jQuery
- **Charts:** Plotly.js
- **Container:** Docker with Docker Compose

### 🚀 Getting Started
1. Clone the repository
2. Copy `.env.sample` to `.env` and configure settings
3. Run with Docker Compose: `docker compose up`
4. Access the application at `http://localhost:8000`
5. Login with: `admin` / `Admin123!`

### 📋 Default Credentials
- **Username:** admin
- **Password:** Admin123!
- **Email:** admin@example.com

### 🌐 Key URLs
- **Main App:** `/user/login/`
- **Admin Panel:** `/admin/` (redirects to `/staff_portal/`)
- **Register:** `/register/`
- **Dashboards:** `/dashboard_sales/`, `/dashboard_department/`, `/dashboard_products/`
- **Customer Display:** `/retail_display/`

### 🛠 Known Issues & Limitations
- Password reset workflow needs implementation
- Production configuration hardening required
- Enhanced monitoring and logging needed
- Some PWA features still in development

### 📝 Configuration
The system can be configured via environment variables in the `.env` file:
- Store information (name, address, phone)
- Database settings
- Printer configuration
- Admin credentials

### 🔮 What's Next (v0.0.2)
- Complete PWA implementation
- Enhanced offline capabilities
- Password reset functionality
- Production deployment guides
- Advanced reporting features

---

**Full Documentation:** See README.md for detailed setup and usage instructions.
**Support:** Create issues on the project repository for bug reports and feature requests.
