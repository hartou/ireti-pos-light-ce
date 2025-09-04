# 🚀 Ireti POS Light v1.0.0 Deployment Checklist

## 📋 Pre-Deployment Checklist

### **Environment Setup**
- [ ] **Stripe Account**: Create and configure Stripe account
- [ ] **API Keys**: Obtain Stripe publishable and secret keys
- [ ] **Webhook Endpoint**: Configure webhook URL in Stripe dashboard
- [ ] **SSL Certificate**: Ensure HTTPS is configured for production
- [ ] **Domain Setup**: Configure proper domain/subdomain for the application

### **Container Configuration**
- [ ] **Database Volume**: Ensure SQLite database directory is mounted (`/app/db.sqlite3`)
- [ ] **Logs Volume**: Mount logs directory for persistent logging (`/app/logs/`)
- [ ] **Static Files**: Verify static files are properly served
- [ ] **Port Configuration**: Map container port 8000 to desired host port
- [ ] **Environment Variables**: Set all required environment variables

### **Required Environment Variables**
```bash
# Stripe Configuration (Required)
STRIPE_PUBLISHABLE_KEY=pk_live_...     # Live: pk_live_... | Test: pk_test_...
STRIPE_SECRET_KEY=sk_live_...          # Live: sk_live_... | Test: sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...        # From Stripe webhook configuration

# Application Configuration
DEBUG=False                            # Always False for production
STRIPE_LIVE_MODE=True                  # False for test mode, True for production
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Security (Optional but Recommended)
SECRET_KEY=your-long-random-secret-key
SECURE_SSL_REDIRECT=True              # If using HTTPS
```

## 🐳 Container Deployment Commands

### **Quick Start (Development/Testing)**
```bash
# Test Mode Deployment
docker run -d \
  --name ireti-pos-v1 \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -e STRIPE_PUBLISHABLE_KEY=pk_test_... \
  -e STRIPE_SECRET_KEY=sk_test_... \
  -e STRIPE_WEBHOOK_SECRET=whsec_... \
  -e STRIPE_LIVE_MODE=False \
  -e DEBUG=False \
  hartou/ireti-pos-light:v1.0.0
```

### **Production Deployment**
```bash
# Production Mode Deployment
docker run -d \
  --name ireti-pos-production \
  -p 80:8000 \
  -v /var/lib/ireti-pos/data:/app/data \
  -v /var/log/ireti-pos:/app/logs \
  -e STRIPE_PUBLISHABLE_KEY=pk_live_... \
  -e STRIPE_SECRET_KEY=sk_live_... \
  -e STRIPE_WEBHOOK_SECRET=whsec_... \
  -e STRIPE_LIVE_MODE=True \
  -e DEBUG=False \
  -e ALLOWED_HOSTS=pos.yourdomain.com \
  -e SECRET_KEY=your-production-secret-key \
  --restart unless-stopped \
  hartou/ireti-pos-light:v1.0.0
```

### **Docker Compose (Recommended)**
```yaml
version: '3.8'
services:
  ireti-pos:
    image: hartou/ireti-pos-light:v1.0.0
    container_name: ireti-pos-v1
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - STRIPE_PUBLISHABLE_KEY=pk_live_...
      - STRIPE_SECRET_KEY=sk_live_...
      - STRIPE_WEBHOOK_SECRET=whsec_...
      - STRIPE_LIVE_MODE=true
      - DEBUG=false
      - ALLOWED_HOSTS=pos.yourdomain.com
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## 🔧 Post-Deployment Verification

### **Application Health Checks**
- [ ] **Container Status**: Verify container is running (`docker ps`)
- [ ] **Application Access**: Test web interface accessibility
- [ ] **Database Migration**: Confirm all migrations applied successfully
- [ ] **Static Files**: Verify CSS/JS loading correctly
- [ ] **Admin Access**: Test admin login functionality

### **Stripe Integration Tests**
- [ ] **Payment Form**: Verify payment form loads with Stripe Elements
- [ ] **Test Transaction**: Process a test payment (use test card numbers)
- [ ] **Webhook Delivery**: Verify webhooks are being received
- [ ] **Transaction Recording**: Confirm payments are recorded in database
- [ ] **Error Handling**: Test payment failure scenarios

### **Security Verification**
- [ ] **HTTPS Enabled**: All traffic is encrypted
- [ ] **CSRF Protection**: Forms include CSRF tokens
- [ ] **Admin Access**: Only authorized users can access admin
- [ ] **Sensitive Data**: No sensitive information in logs
- [ ] **Error Pages**: Production error pages are displayed

### **Performance & Monitoring**
- [ ] **Response Time**: Application responds quickly
- [ ] **Memory Usage**: Container memory usage is reasonable
- [ ] **Disk Space**: Adequate disk space for SQLite database
- [ ] **Log Rotation**: Logs are properly rotated
- [ ] **Backup Strategy**: Database backup process is configured

## 🛠️ Stripe Dashboard Configuration

### **Webhook Setup**
1. Go to Stripe Dashboard > Developers > Webhooks
2. Add endpoint: `https://yourdomain.com/payments/webhook/`
3. Select events:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `charge.dispute.created`
4. Copy webhook secret to `STRIPE_WEBHOOK_SECRET` environment variable

### **Test Mode vs Live Mode**
- **Test Mode**: Use `pk_test_...` and `sk_test_...` keys, set `STRIPE_LIVE_MODE=False`
- **Live Mode**: Use `pk_live_...` and `sk_live_...` keys, set `STRIPE_LIVE_MODE=True`

## 📊 Container Specifications

### **System Requirements**
- **CPU**: 1 vCPU minimum, 2 vCPU recommended
- **RAM**: 512MB minimum, 1GB recommended
- **Storage**: 5GB minimum, 20GB recommended
- **Network**: HTTPS required for production

### **Container Features**
- **SQLite Database**: No external database required
- **Built-in Web Server**: Django development server for simplicity
- **Static Files**: Served via Django (consider nginx for high traffic)
- **Health Check**: Built-in health check endpoint
- **Logging**: Structured logging to files and stdout

## 🔍 Troubleshooting

### **Common Issues**
- **Container Won't Start**: Check environment variables and port conflicts
- **Payment Form Not Loading**: Verify Stripe keys and network connectivity
- **Webhook Failures**: Check webhook URL and secret configuration
- **Database Errors**: Ensure volume mounts are correct

### **Log Locations**
- **Application Logs**: `/app/logs/`
- **Payment Logs**: `/app/logs/payments.log`
- **Container Logs**: `docker logs container_name`

### **Support Resources**
- **Release Notes**: `RELEASE_NOTES_v1.0.0.md`
- **Payment Guide**: `docs/PAYMENT_OPERATIONS_RUNBOOK.md`
- **Troubleshooting**: `docs/PAYMENT_TROUBLESHOOTING_GUIDE.md`

---

**Note**: This deployment checklist is specifically designed for the SQLite container deployment of Ireti POS Light v1.0.0. For high-traffic production environments, consider using PostgreSQL and a reverse proxy like nginx.
