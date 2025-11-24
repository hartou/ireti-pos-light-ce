#!/bin/bash

# Azure Container Apps Deployment using Bicep
# This script deploys the infrastructure using Infrastructure as Code

set -e

# Configuration
RESOURCE_GROUP="rg-ireti-pos"
LOCATION="eastus"
SUBSCRIPTION_ID="86c5f895-13b2-4329-8e76-87a91892a809"
DEPLOYMENT_NAME="ireti-pos-deployment-$(date +%Y%m%d-%H%M%S)"

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

echo_info "🚀 Starting Infrastructure as Code deployment for Ireti POS Light CE"

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo_error "Azure CLI is not installed. Please install it first."
    exit 1
fi

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

# Deploy using Bicep
echo_info "Deploying infrastructure using Bicep template..."
DEPLOYMENT_OUTPUT=$(az deployment group create \
    --resource-group "$RESOURCE_GROUP" \
    --template-file azure/main.bicep \
    --parameters azure/parameters.json \
    --name "$DEPLOYMENT_NAME" \
    --query 'properties.outputs' \
    --output json)

if [ $? -eq 0 ]; then
    echo_success "Infrastructure deployment completed successfully!"
    
    # Extract outputs
    APP_URL=$(echo "$DEPLOYMENT_OUTPUT" | jq -r '.applicationUrl.value')
    CONTAINER_APP_ID=$(echo "$DEPLOYMENT_OUTPUT" | jq -r '.containerAppId.value')
    
    echo ""
    echo_success "🎉 Deployment completed successfully!"
    echo_info "📋 Deployment Summary:"
    echo "  • Resource Group: $RESOURCE_GROUP"
    echo "  • Location: $LOCATION"
    echo "  • Deployment Name: $DEPLOYMENT_NAME"
    echo "  • Container App ID: $CONTAINER_APP_ID"
    echo ""
    echo_success "🌐 Application URL: $APP_URL"
    echo_info "🔐 Login credentials: admin / admin123"
    echo ""
    echo_warning "📝 Next steps:"
    echo "  1. Wait 2-3 minutes for the app to fully start"
    echo "  2. Visit the URL above to access your POS system"
    echo "  3. Update Stripe keys for production use"
    echo "  4. Monitor the application in Azure Portal"
    echo ""
    
    # Test the deployment
    echo_info "Testing the deployment..."
    sleep 30  # Wait a bit for the app to start
    
    if curl -s -f "$APP_URL" > /dev/null; then
        echo_success "Application is responding!"
    else
        echo_warning "Application might still be starting up. Check Azure Portal for status."
    fi
    
else
    echo_error "Deployment failed. Check the error messages above."
    exit 1
fi

echo_info "🏁 Deployment script completed!"