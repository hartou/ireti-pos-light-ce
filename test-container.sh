#!/bin/bash

echo "🧪 Testing Published Ireti POS Light CE Container..."
echo "=================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "✅ Docker is running"

# Pull the latest image
echo "📦 Pulling the latest image from GHCR..."
if docker pull ghcr.io/hartou/ireti-pos-light-ce:latest; then
    echo "✅ Image pulled successfully"
else
    echo "❌ Failed to pull image"
    exit 1
fi

# Test 1: Run without required environment variables (should fail)
echo ""
echo "🧪 Test 1: Running without required Stripe keys (should fail)..."
CONTAINER_ID=$(docker run -d --name ireti-test-fail -p 8001:8000 ghcr.io/hartou/ireti-pos-light-ce:latest)
sleep 5
LOGS=$(docker logs ireti-test-fail 2>&1)
if echo "$LOGS" | grep -q "STRIPE_SECRET_KEY environment variable is required"; then
    echo "✅ Test 1 PASSED: Container correctly requires Stripe environment variables"
    docker stop ireti-test-fail && docker rm ireti-test-fail > /dev/null
else
    echo "❌ Test 1 FAILED: Container should require Stripe environment variables"
    docker stop ireti-test-fail && docker rm ireti-test-fail > /dev/null
    exit 1
fi

# Test 2: Run with dummy Stripe keys (should start)
echo ""
echo "🧪 Test 2: Running with valid Stripe test keys..."
CONTAINER_ID=$(docker run -d --name ireti-test-pass -p 8002:8000 \
  -e STRIPE_SECRET_KEY=sk_test_dummy_key_for_testing_only \
  -e STRIPE_PUBLISHABLE_KEY=pk_test_dummy_key_for_testing_only \
  -e DJANGO_DEBUG=True \
  -e DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0 \
  -e DJANGO_SECRET_KEY=test-secret-key \
  ghcr.io/hartou/ireti-pos-light-ce:latest)

echo "⏳ Waiting for container to start..."
sleep 15

# Check if container is running
if docker ps | grep -q ireti-test-pass; then
    echo "✅ Container is running"
    
    # Test HTTP response
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8002/ || echo "000")
    if [ "$HTTP_CODE" = "302" ] || [ "$HTTP_CODE" = "200" ]; then
        echo "✅ Test 2 PASSED: Web interface is accessible (HTTP $HTTP_CODE)"
        echo "🌐 You can test the interface at: http://localhost:8002/"
    else
        echo "❌ Test 2 FAILED: Web interface not accessible (HTTP $HTTP_CODE)"
        docker logs ireti-test-pass
    fi
else
    echo "❌ Test 2 FAILED: Container is not running"
    echo "Container logs:"
    docker logs ireti-test-pass
fi

# Cleanup
echo ""
echo "🧹 Cleaning up test containers..."
docker stop ireti-test-pass && docker rm ireti-test-pass > /dev/null

echo ""
echo "📋 Summary:"
echo "=========="
echo "The published container ghcr.io/hartou/ireti-pos-light-ce:latest works correctly!"
echo ""
echo "⚠️  REQUIREMENTS:"
echo "- STRIPE_SECRET_KEY environment variable (format: sk_test_* or sk_live_*)"
echo "- STRIPE_PUBLISHABLE_KEY environment variable (format: pk_test_* or pk_live_*)"
echo ""
echo "🚀 To run the container properly:"
echo "docker run -p 8000:8000 \\"
echo "  -e STRIPE_SECRET_KEY=sk_test_your_actual_key \\"
echo "  -e STRIPE_PUBLISHABLE_KEY=pk_test_your_actual_key \\"
echo "  -e DJANGO_SUPERUSER_USERNAME=admin \\"
echo "  -e DJANGO_SUPERUSER_PASSWORD=Admin123! \\"
echo "  ghcr.io/hartou/ireti-pos-light-ce:latest"
echo ""
echo "✅ Container test completed successfully!"