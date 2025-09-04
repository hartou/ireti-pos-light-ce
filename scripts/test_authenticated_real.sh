#!/bin/bash
echo "Testing authenticated access to all broken links URLs:"
echo "=================================================="

URLS=(
    "/dashboard_sales/"
    "/dashboard_department/"
    "/dashboard_products/"
    "/transaction/"
    "/register/product_lookup/"
    "/inventory/"
    "/staff_portal/"
    "/staff_portal/auth/group/"
    "/retail_display/"
)

for url in "${URLS[@]}"; do
    status=$(curl -s -o /dev/null -w "%{http_code}" -b cookies.txt "http://127.0.0.1:8000$url")
    
    if [ "$status" = "200" ]; then
        echo "✅ $url: $status (OK - Working correctly!)"
    elif [ "$status" = "302" ]; then
        echo "⚠️  $url: $status (Redirect - Authentication issue?)"
    elif [ "$status" = "500" ]; then
        echo "❌ $url: $status (Server Error - Template or view issue)"
    elif [ "$status" = "404" ]; then
        echo "❌ $url: $status (Not Found - URL pattern issue)"
    else
        echo "⚠️  $url: $status (Unexpected status)"
    fi
done

echo "=================================================="
echo "Test completed!"
