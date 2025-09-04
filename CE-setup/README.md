# 🛒 Ireti POS Light - Community Edition

![Version](https://img.shields.io/badge/version-1.0.0--CE-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Django](https://img.shields.io/badge/django-3.2-orange)
![Stripe](https://img.shields.io/badge/stripe-integrated-blueviolet)

**Ireti POS Light CE** is a modern, open-source Point of Sale system with complete Stripe payment integration. It's designed for small businesses that need a reliable, secure, and feature-rich POS solution without the enterprise price tag.

## ✨ Features

### 💳 **Complete Payment System**
- **Stripe Integration**: Ready-to-use payment processing 
- **Multiple Payment Methods**: Credit cards, mobile payments, etc.
- **Refund Processing**: Easy-to-use refund workflow
- **Transaction History**: Complete payment tracking

### 🛍️ **POS Capabilities**
- **Inventory Management**: Track stock and products
- **Transaction Recording**: Log all sales and returns
- **Customer Management**: Basic customer tracking
- **Responsive Interface**: Works on tablets and desktops

### 🔒 **Security & Compliance**
- **PCI Compliance**: Secure card handling via Stripe
- **CSRF Protection**: Protection against web vulnerabilities
- **Audit Logging**: Complete transaction audit trail
- **User Authentication**: Role-based access control

### 🔧 **Technical Highlights**
- **Django Backend**: Reliable Python-based framework
- **Responsive Frontend**: Bootstrap-based UI
- **SQLite Database**: Simple setup with no external DB required
- **Docker Ready**: One-command deployment with containers

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Pull and run the CE image
docker pull ghcr.io/hartou/ireti-pos-light-ce:latest
docker run -p 8000:8000 \
  -e STRIPE_SECRET_KEY=sk_test_your_key \
  -e STRIPE_PUBLISHABLE_KEY=pk_test_your_key \
  -e STRIPE_WEBHOOK_ENDPOINT_SECRET=whsec_your_secret \
  ghcr.io/hartou/ireti-pos-light-ce:latest
```

### Option 2: Local Installation

```bash
# Clone the repository
git clone https://github.com/hartou/ireti-pos-light-ce.git
cd ireti-pos-light-ce

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run the server
python manage.py runserver
```

### Configuration

1. Get your Stripe API keys from [Stripe Dashboard](https://dashboard.stripe.com/apikeys)
2. Create a `.env` file or set environment variables:

```
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_ENDPOINT_SECRET=whsec_...
```

## 📸 Screenshots

<table>
  <tr>
    <td><img src="screenshots/payment-screen.png" alt="Payment Screen" width="400"/></td>
    <td><img src="screenshots/admin-dashboard.png" alt="Admin Dashboard" width="400"/></td>
  </tr>
  <tr>
    <td><img src="screenshots/transaction-history.png" alt="Transaction History" width="400"/></td>
    <td><img src="screenshots/mobile-view.png" alt="Mobile View" width="400"/></td>
  </tr>
</table>

## 🤝 Contributing

We welcome contributions from the community! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines.

### How to Contribute
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 Documentation

- [User Guide](docs/USER_GUIDE.md)
- [Admin Guide](docs/ADMIN_GUIDE.md)
- [API Reference](docs/API_REFERENCE.md)
- [Developer Guide](docs/DEVELOPER_GUIDE.md)
- [Stripe Integration](docs/STRIPE_TESTING_GUIDE.md)

## 📊 Project Status

- **Current Version**: 1.0.0-CE
- **Stability**: Production-ready
- **Last Updated**: September 4, 2025
- **Release Cycle**: Monthly minor releases, quarterly major releases

## 📋 Roadmap

- [ ] Multi-currency support
- [ ] Additional payment processors
- [ ] Advanced inventory management
- [ ] Customer loyalty program
- [ ] Mobile app companion
- [ ] Plugin architecture for extensions

## 🔄 Version Differences

| Feature | Community Edition | Enterprise Edition |
|---------|-------------------|-------------------|
| **Core POS** | ✅ Full-featured | ✅ Enhanced |
| **Stripe Payments** | ✅ Complete | ✅ + Multi-processor |
| **Container Deploy** | ✅ Docker ready | ✅ + Kubernetes |
| **SQLite Database** | ✅ Default | ✅ + PostgreSQL/MySQL |
| **Basic Admin** | ✅ Included | ✅ + Advanced analytics |
| **Community Support** | ✅ GitHub issues | ❌ |
| **Enterprise Support** | ❌ | ✅ 24/7 SLA |
| **Custom Integrations** | ❌ | ✅ Professional services |

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Community & Support

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Community Q&A and discussions
- **Discord**: Join our [community server](https://discord.gg/ireti-pos) (coming soon)

## 🙏 Acknowledgements

- [Django](https://www.djangoproject.com/)
- [Stripe](https://stripe.com/)
- [Bootstrap](https://getbootstrap.com/)
- [Playwright](https://playwright.dev/)
- All our [contributors](CONTRIBUTORS.md)

---

Made with ❤️ by the Ireti POS Community
