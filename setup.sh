#!/bin/bash

# 🚀 Ireti POS Light CE - Quick Setup Script
# This script helps you get started quickly with the Community Edition

set -e

echo "🛒 Ireti POS Light Community Edition - Quick Setup"
echo "================================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker &> /dev/null || ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Setup environment file
if [ ! -f .env ]; then
    echo "📝 Creating environment configuration..."
    cp config/.env.example .env
    echo "✅ Created .env file from template"
    echo ""
    echo "🔧 IMPORTANT: Edit .env file with your Stripe API keys:"
    echo "   - STRIPE_SECRET_KEY=sk_test_..."
    echo "   - STRIPE_PUBLISHABLE_KEY=pk_test_..."
    echo "   - STRIPE_WEBHOOK_ENDPOINT_SECRET=whsec_..."
    echo ""
else
    echo "✅ Environment file (.env) already exists"
    echo ""
fi

# Ask user which setup they want
echo "🚀 Choose your setup:"
echo "1) Development setup (SQLite, quick start)"
echo "2) Production setup (PostgreSQL, Nginx)"
echo ""
read -p "Enter your choice (1 or 2): " choice

case $choice in
    1)
        echo ""
        echo "🔨 Starting development setup..."
        docker compose up -d
        echo ""
        echo "✅ Development setup complete!"
        echo ""
        echo "🌐 Access your POS system:"
        echo "   • Main Interface: http://localhost:8000"
        echo "   • Admin Panel: http://localhost:8000/admin/"
        echo ""
        echo "📋 Default admin credentials:"
        echo "   • Username: admin"
        echo "   • Password: Admin123!"
        echo ""
        ;;
    2)
        echo ""
        echo "🏭 Starting production setup..."
        docker compose -f docker/docker-compose.prod.yml up -d
        echo ""
        echo "✅ Production setup complete!"
        echo ""
        echo "🌐 Access your POS system:"
        echo "   • Main Interface: http://localhost"
        echo "   • Admin Panel: http://localhost/admin/"
        echo ""
        echo "⚠️  Remember to:"
        echo "   • Configure your domain in docker/nginx.conf"
        echo "   • Set up SSL certificates for production"
        echo "   • Update your environment variables in .env"
        echo ""
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again and choose 1 or 2."
        exit 1
        ;;
esac

echo "🎉 Setup complete! Your Ireti POS Light CE is running."
echo ""
echo "📚 For more information:"
echo "   • Documentation: docs/"
echo "   • Stripe Testing: docs/STRIPE_TESTING_GUIDE.md"
echo "   • Deployment: docs/DEPLOYMENT.md"
echo ""
echo "❓ Need help? Visit: https://github.com/hartou/ireti-pos-light-ce/issues"
