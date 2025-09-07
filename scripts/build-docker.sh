#!/bin/bash
# Build and optionally push Docker container for CE release

set -e

IMAGE_NAME="ghcr.io/hartou/ireti-pos-light-ce"
VERSION="1.0.0-CE"
FULL_TAG="${IMAGE_NAME}:${VERSION}"

echo "🐳 Building Docker container for Ireti POS Light CE v${VERSION}"
echo "================================================================"

# Build from the release directory
cd /workspaces/ireti-pos-light-ce

echo "📦 Building Docker image: ${FULL_TAG}"
docker build -t "${FULL_TAG}" -f docker/dockerfile .

# Also tag as latest CE
docker tag "${FULL_TAG}" "${IMAGE_NAME}:latest-ce"

echo "✅ Docker build complete!"
echo ""
echo "🏷️  Tagged images:"
echo "   • ${FULL_TAG}"
echo "   • ${IMAGE_NAME}:latest-ce"
echo ""
echo "🚀 To test the container locally:"
echo "   docker run -p 8000:8000 -e STRIPE_SECRET_KEY=sk_test_your_key ${FULL_TAG}"
echo ""
echo "📤 To push to registry (requires authentication):"
echo "   docker push ${FULL_TAG}"
echo "   docker push ${IMAGE_NAME}:latest-ce"
echo ""

# Test the container briefly
echo "🧪 Testing container startup..."
CONTAINER_ID=$(docker run -d -p 8001:8000 \
  -e DJANGO_SECRET_KEY=test-key-for-build-test \
  -e DJANGO_DEBUG=True \
  "${FULL_TAG}")

sleep 5

if docker ps | grep -q "${CONTAINER_ID}"; then
    echo "✅ Container started successfully!"
    echo "🛑 Stopping test container..."
    docker stop "${CONTAINER_ID}" >/dev/null
    docker rm "${CONTAINER_ID}" >/dev/null
else
    echo "❌ Container failed to start properly"
    docker logs "${CONTAINER_ID}"
    docker rm "${CONTAINER_ID}" >/dev/null
    exit 1
fi

echo ""
echo "🎉 Docker container ready for Ireti POS Light CE v${VERSION}!"
