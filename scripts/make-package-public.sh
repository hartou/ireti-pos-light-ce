#!/bin/bash

# Make GHCR Package Public Script
# This script provides instructions to make your GitHub Container Registry package public

echo "🔧 Making GitHub Container Registry Package Public"
echo "=================================================="
echo ""

REPO_NAME="ireti-pos-light-ce"
OWNER="hartou" 
PACKAGE_NAME="ireti-pos-light-ce"

echo "📦 Repository: $OWNER/$REPO_NAME"
echo "🐳 Package: ghcr.io/$OWNER/$PACKAGE_NAME"
echo ""

echo "🔐 Steps to make your GHCR package public:"
echo ""
echo "METHOD 1: Using GitHub Web Interface"
echo "-----------------------------------"
echo "1. Go to: https://github.com/$OWNER/$REPO_NAME/packages"
echo "2. Click on your package: $PACKAGE_NAME"
echo "3. Click on 'Package settings' (gear icon)"
echo "4. Scroll down to 'Danger Zone'"
echo "5. Click 'Change visibility'"
echo "6. Select 'Public'"
echo "7. Type the package name to confirm: $PACKAGE_NAME"
echo "8. Click 'I understand the consequences, change package visibility'"
echo ""

echo "METHOD 2: Using GitHub CLI (if installed)"
echo "----------------------------------------"
echo "gh api --method PATCH /user/packages/container/$PACKAGE_NAME --field visibility=public"
echo ""

echo "METHOD 3: Using REST API with curl"
echo "--------------------------------"
echo "curl -X PATCH \\"
echo "  -H 'Accept: application/vnd.github.v3+json' \\"
echo "  -H 'Authorization: token YOUR_PERSONAL_ACCESS_TOKEN' \\"
echo "  https://api.github.com/user/packages/container/$PACKAGE_NAME \\"
echo "  -d '{\"visibility\":\"public\"}'"
echo ""

echo "📋 After making the package public:"
echo "- Anyone can pull: docker pull ghcr.io/$OWNER/$PACKAGE_NAME:latest"
echo "- The package will be visible on your GitHub profile"
echo "- No authentication needed for public pulls"
echo ""

echo "🚀 Testing the public package:"
echo "docker pull ghcr.io/$OWNER/$PACKAGE_NAME:latest"
echo "docker run -p 8000:8000 ghcr.io/$OWNER/$PACKAGE_NAME:latest"
echo ""

echo "✅ Once the workflow runs, your image will be available publicly!"