# Deployment Guide - Ireti POS Light v0.0.1

## 🚀 Quick Start

### Using Docker (Recommended)

1. **Pull the pre-built image:**
   ```bash
   docker pull ghcr.io/hartou/ireti-pos-light:v0.0.2
   ```

2. **Run with Docker Compose:**
   ```bash
   # Download production compose file
   curl -O https://raw.githubusercontent.com/hartou/ireti-pos-light/v0.0.2/docker-compose.prod.yml
   
   # Create environment file
   cp .env.example .env
   # Edit .env with your configuration
   
   # Start the application
   docker compose -f docker-compose.prod.yml up -d
   ```

3. **Access the application:**
   - Open http://localhost in your browser
   - Login with admin credentials from your .env file

## 🏗️ Production Deployment

### Prerequisites
- Docker and Docker Compose
- Domain name (optional, for HTTPS)
- SSL certificates (for HTTPS)

### Steps

1. **Clone or download the repository:**
   ```bash
   git clone https://github.com/hartou/ireti-pos-light.git
   cd ireti-pos-light
   git checkout v0.0.2
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   nano .env  # Edit with your settings
   ```

3. **Update production configuration:**
   - Edit `docker-compose.prod.yml` with your GitHub repository name
   - Configure `nginx.conf` with your domain (if using custom domain)

4. **Deploy:**
   ```bash
   docker compose -f docker-compose.prod.yml up -d
   ```

5. **Verify deployment:**
   ```bash
   docker compose -f docker-compose.prod.yml ps
   docker compose -f docker-compose.prod.yml logs webapp
   ```

## 🛠️ Development Setup

For development, use the regular docker-compose.yml:

```bash
git clone https://github.com/hartou/ireti-pos-light.git
cd ireti-pos-light
docker compose up --build
```

## 🔐 Security Considerations

- Change default passwords in `.env`
- Use strong `DJANGO_SECRET_KEY`
- Configure `DJANGO_ALLOWED_HOSTS` for your domain
- Enable HTTPS in production (configure nginx with SSL certificates)
- Regularly update the Docker image

## 📱 PWA Features

The application includes Progressive Web App features:
- Offline capability with service worker
- Installable on mobile devices
- Network status indicators
- Responsive design for all screen sizes

## 🆘 Troubleshooting

### Database Issues
```bash
# Reset database
docker compose -f docker-compose.prod.yml down -v
docker compose -f docker-compose.prod.yml up -d
```

### View Logs
```bash
# Application logs
docker compose -f docker-compose.prod.yml logs webapp

# Database logs
docker compose -f docker-compose.prod.yml logs db
```

### Access Django Shell
```bash
docker compose -f docker-compose.prod.yml exec webapp python manage.py shell
```

## 📊 Monitoring

Check application health:
```bash
curl http://localhost/health/
```

Monitor containers:
```bash
docker compose -f docker-compose.prod.yml top
```

## 🔄 Updates

To update to a newer version:
```bash
# Pull new image
docker compose -f docker-compose.prod.yml pull webapp

# Restart services
docker compose -f docker-compose.prod.yml up -d
```

## 💡 Support

For issues and support, please visit the GitHub repository and create an issue with detailed information about your setup and the problem encountered.
