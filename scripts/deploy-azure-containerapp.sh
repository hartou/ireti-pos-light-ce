#!/bin/bash

# Azure Container Apps Deployment Script for Ireti POS Light CE
# This script deploys the GHCR container to Azure Container Apps with Consumption SKU

set -e

# Configuration
RESOURCE_GROUP="rg-ireti-pos"
LOCATION="eastus"
CONTAINER_APP_ENV="ireti-pos-env"
CONTAINER_APP_NAME="ireti-pos-app"
CONTAINER_IMAGE="ghcr.io/hartou/ireti-pos-light-ce:latest"
SUBSCRIPTION_ID="86c5f895-13b2-4329-8e76-87a91892a809"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

echo_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

echo_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo_error() {
    echo -e "${RED}❌ $1${NC}"
}

echo_info "🚀 Starting Azure Container Apps deployment for Ireti POS Light CE"

# Set the subscription
echo_info "Setting Azure subscription..."
az account set --subscription "$SUBSCRIPTION_ID"
echo_success "Subscription set to: $SUBSCRIPTION_ID"

# Check if resource group exists, create if not
echo_info "Checking resource group..."
if ! az group show --name "$RESOURCE_GROUP" &> /dev/null; then
    echo_info "Creating resource group: $RESOURCE_GROUP"
    az group create --name "$RESOURCE_GROUP" --location "$LOCATION"
    echo_success "Resource group created"
else
    echo_success "Resource group already exists"
fi

# Register required providers
echo_info "Registering required Azure providers..."
az provider register --namespace Microsoft.OperationalInsights --wait
az provider register --namespace Microsoft.App --wait
echo_success "Providers registered"

# Install Container Apps extension
echo_info "Installing/updating Azure Container Apps CLI extension..."
az extension add --name containerapp --upgrade
echo_success "Container Apps extension ready"

# Create Container Apps Environment
echo_info "Creating Container Apps Environment..."
if ! az containerapp env show --name "$CONTAINER_APP_ENV" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
    az containerapp env create \
        --name "$CONTAINER_APP_ENV" \
        --resource-group "$RESOURCE_GROUP" \
        --location "$LOCATION"
    echo_success "Container Apps Environment created"
else
    echo_success "Container Apps Environment already exists"
fi

# Create the Container App with Consumption SKU
echo_info "Creating Container App with Consumption SKU..."

# Deploy the container app
echo_info "Deploying Container App..."
az containerapp create \
    --name "$CONTAINER_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --environment "$CONTAINER_APP_ENV" \
    --image "$CONTAINER_IMAGE" \
    --target-port 8000 \
    --ingress external \
    --cpu 0.25 \
    --memory 0.5Gi \
    --min-replicas 0 \
    --max-replicas 10 \
    --env-vars \
        DJANGO_SUPERUSER_USERNAME=admin \
        DJANGO_SUPERUSER_EMAIL=admin@example.com \
        DJANGO_SUPERUSER_PASSWORD=admin123 \
        STRIPE_SECRET_KEY=sk_test_YOUR_STRIPE_SECRET_KEY_HERE \
        STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_STRIPE_PUBLISHABLE_KEY_HERE \
        STRIPE_WEBHOOK_ENDPOINT_SECRET=whsec_test_12345 \
        DJANGO_SETTINGS_MODULE=iretilightpos.settings.devlopement

echo_success "Container App deployed successfully!"

# Get the application URL
echo_info "Getting application URL..."
APP_URL=$(az containerapp show --name "$CONTAINER_APP_NAME" --resource-group "$RESOURCE_GROUP" --query "properties.configuration.ingress.fqdn" -o tsv)

echo ""
echo_success "🎉 Deployment completed successfully!"
echo_info "📋 Deployment Summary:"
echo "  • Resource Group: $RESOURCE_GROUP"
echo "  • Location: $LOCATION"
echo "  • Container App: $CONTAINER_APP_NAME"
echo "  • Environment: $CONTAINER_APP_ENV"
echo "  • Image: $CONTAINER_IMAGE"
echo "  • SKU: Consumption (Serverless)"
echo "  • Scaling: 0-10 replicas"
echo "  • CPU: 0.25 cores"
echo "  • Memory: 0.5Gi"
echo ""
echo_success "🌐 Application URL: https://$APP_URL"
echo_info "🔐 Login credentials: admin / admin123"
echo ""
echo_warning "📝 Next steps:"
echo "  1. Wait 2-3 minutes for the app to fully start"
echo "  2. Visit the URL above to access your POS system"
echo "  3. Update Stripe keys in Azure portal for production"
echo "  4. Configure custom domain if needed"
echo ""

echo_info "🏁 Deployment script completed!"