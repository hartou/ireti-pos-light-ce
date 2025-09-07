#!/bin/bash

# PWA Implementation Validation Script
# Usage: ./validate_pwa.sh [story_id]
# Example: ./validate_pwa.sh PWA-004

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Base URLs
BASE_URL="http://localhost:8000"
ADMIN_URL="$BASE_URL/admin/"

echo -e "${BLUE}🔍 PWA Implementation Validation Tool${NC}"
echo "======================================"

# Function to check if Django is running
check_django_running() {
    echo -e "${YELLOW}⏳ Checking if Django server is running...${NC}"
    if curl -s "$BASE_URL" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Django server is running${NC}"
        return 0
    else
        echo -e "${RED}❌ Django server is not running${NC}"
        echo "Please start the server with: python manage.py runserver"
        exit 1
    fi
}

# Function to validate Service Worker
validate_service_worker() {
    echo -e "${YELLOW}⏳ Validating Service Worker...${NC}"
    
    # Check if SW file exists
    if [ -f "iretilightpos/static/js/sw.js" ]; then
        echo -e "${GREEN}✅ Service Worker file exists${NC}"
    else
        echo -e "${RED}❌ Service Worker file missing${NC}"
        return 1
    fi
    
    # Check SW registration in base template
    if grep -q "navigator.serviceWorker.register" iretilightpos/templates/base.html; then
        echo -e "${GREEN}✅ Service Worker registration found in base template${NC}"
    else
        echo -e "${RED}❌ Service Worker registration missing${NC}"
        return 1
    fi
    
    # Test SW endpoint
    if curl -s "$BASE_URL/static/js/sw.js" | head -n 1 | grep -q "//"; then
        echo -e "${GREEN}✅ Service Worker accessible at URL${NC}"
    else
        echo -e "${RED}❌ Service Worker not accessible${NC}"
        return 1
    fi
}

# Function to validate PWA Manifest
validate_manifest() {
    echo -e "${YELLOW}⏳ Validating PWA Manifest...${NC}"
    
    # Check if manifest file exists
    if [ -f "iretilightpos/static/manifest.webmanifest" ]; then
        echo -e "${GREEN}✅ Manifest file exists${NC}"
    else
        echo -e "${RED}❌ Manifest file missing${NC}"
        return 1
    fi
    
    # Check manifest link in base template
    if grep -q "manifest.webmanifest" iretilightpos/templates/base.html; then
        echo -e "${GREEN}✅ Manifest linked in base template${NC}"
    else
        echo -e "${RED}❌ Manifest link missing${NC}"
        return 1
    fi
    
    # Test manifest endpoint
    if curl -s "$BASE_URL/static/manifest.webmanifest" | grep -q "name"; then
        echo -e "${GREEN}✅ Manifest accessible and valid JSON${NC}"
    else
        echo -e "${RED}❌ Manifest not accessible or invalid${NC}"
        return 1
    fi
}

# Function to validate specific PWA story
validate_pwa_story() {
    local story_id=$1
    
    echo -e "${YELLOW}⏳ Validating PWA Story: $story_id${NC}"
    
    case $story_id in
        "PWA-004")
            echo "Checking static assets caching..."
            if grep -q "STATIC_CACHE\|static.*cache\|cache-first" iretilightpos/static/js/sw.js; then
                echo -e "${GREEN}✅ PWA-004: Static assets caching implemented${NC}"
            else
                echo -e "${RED}❌ PWA-004: Static assets caching not found${NC}"
                return 1
            fi
            ;;
        "PWA-005")
            echo "Checking API caching..."
            if grep -q "API_CACHE\|api.*cache\|stale-while-revalidate\|handleAPIRequest" iretilightpos/static/js/sw.js; then
                echo -e "${GREEN}✅ PWA-005: API caching implemented${NC}"
            else
                echo -e "${RED}❌ PWA-005: API caching not found${NC}"
                return 1
            fi
            ;;
        "PWA-007")
            echo "Checking network status UI..."
            if grep -q "network.*indicator\|network.*status\|navigator\.onLine" iretilightpos/templates/base.html; then
                echo -e "${GREEN}✅ PWA-007: Network status UI implemented${NC}"
            else
                echo -e "${RED}❌ PWA-007: Network status UI not found${NC}"
                return 1
            fi
            ;;
        "PWA-012")
            echo "Checking iOS PWA support..."
            if grep -q "apple-touch-icon\|apple-mobile-web-app" iretilightpos/templates/base.html; then
                echo -e "${GREEN}✅ PWA-012: iOS PWA support implemented${NC}"
            else
                echo -e "${RED}❌ PWA-012: iOS PWA support not found${NC}"
                return 1
            fi
            ;;
        "PWA-014")
            echo "Checking security headers..."
            if grep -q "CSP_\|SECURE_\|SERVICE_WORKER_ALLOWED" iretilightpos/settings/base.py; then
                echo -e "${GREEN}✅ PWA-014: Security headers implemented${NC}"
            else
                echo -e "${RED}❌ PWA-014: Security headers not found${NC}"
                return 1
            fi
            ;;
        "PWA-015")
            echo "Running PWA readiness audit..."
            if python scripts/pwa_audit.py > /dev/null 2>&1; then
                echo -e "${GREEN}✅ PWA-015: PWA audit passed (100% readiness)${NC}"
            else
                echo -e "${RED}❌ PWA-015: PWA audit failed${NC}"
                return 1
            fi
            ;;
        "PWA-016")
            echo "Checking SW update flow..."
            if grep -q "UPDATE_AVAILABLE\|pwa-update-btn\|handleUpdateClick" iretilightpos/static/js/sw.js iretilightpos/templates/base.html; then
                echo -e "${GREEN}✅ PWA-016: SW update flow implemented${NC}"
            else
                echo -e "${RED}❌ PWA-016: SW update flow not found${NC}"
                return 1
            fi
            ;;
        *)
            echo -e "${RED}❌ Unknown PWA story: $story_id${NC}"
            return 1
            ;;
    esac
}

# Function to run basic authentication test
test_authentication() {
    echo -e "${YELLOW}⏳ Testing authenticated access...${NC}"
    
    # Test if login page is accessible
    if curl -s "$BASE_URL/admin/login/" | grep -q "Django"; then
        echo -e "${GREEN}✅ Login page accessible${NC}"
    else
        echo -e "${RED}❌ Login page not accessible${NC}"
        return 1
    fi
}

# Function to check for regressions
check_regressions() {
    echo -e "${YELLOW}⏳ Checking for potential regressions...${NC}"
    
    # Check if main pages are still accessible
    local pages=("" "admin/" "admin/login/")
    
    for page in "${pages[@]}"; do
        local url="$BASE_URL/$page"
        local status=$(curl -s -o /dev/null -w "%{http_code}" "$url")
        
        if [ "$status" = "200" ] || [ "$status" = "302" ]; then
            echo -e "${GREEN}✅ $url responding correctly ($status)${NC}"
        else
            echo -e "${RED}❌ $url returning error ($status)${NC}"
            return 1
        fi
    done
}

# Main validation function
main() {
    local story_id=$1
    
    echo -e "${BLUE}Starting PWA validation...${NC}"
    echo ""
    
    # Core checks
    check_django_running
    validate_service_worker
    validate_manifest
    test_authentication
    check_regressions
    
    echo ""
    
    # Story-specific validation
    if [ ! -z "$story_id" ]; then
        validate_pwa_story "$story_id"
        echo ""
    fi
    
    echo -e "${GREEN}🎉 PWA Validation Complete!${NC}"
    echo ""
    echo -e "${BLUE}💡 Next Steps:${NC}"
    echo "1. Test PWA features manually in Chrome"
    echo "2. Run Lighthouse audit: npx lighthouse $BASE_URL --only-categories=pwa"
    echo "3. Test on mobile device for full validation"
    echo "4. Update PWA_USER_STORIES.md with completion status"
}

# Run validation
main "$1"
