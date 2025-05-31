#!/bin/bash

# Docker Publishing Script for Chatterbox TTS API
# Run this script to build and publish to Docker Hub

VERSION=${1:-latest}
DOCKER_HUB_USERNAME=${2:-tsavo}
SKIP_BUILD=${SKIP_BUILD:-false}
SKIP_PUSH=${SKIP_PUSH:-false}

IMAGE_NAME="$DOCKER_HUB_USERNAME/chatterbox-tts-api"
FULL_TAG="${IMAGE_NAME}:${VERSION}"

echo "🐳 Chatterbox TTS API - Docker Publishing"
echo "========================================="
echo "Image: $FULL_TAG"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "✅ Docker is running"

# Build the image
if [ "$SKIP_BUILD" != "true" ]; then
    echo "🔨 Building Docker image..."
    build_start=$(date +%s)
    
    if docker build -t "$FULL_TAG" .; then
        build_end=$(date +%s)
        build_duration=$((build_end - build_start))
        echo "✅ Build completed in ${build_duration}s"
        
        # Show image size
        size=$(docker images "$FULL_TAG" --format "{{.Size}}" | head -n 1)
        echo "📦 Image size: $size"
    else
        echo "❌ Build failed"
        exit 1
    fi
else
    echo "⏭️ Skipping build (SKIP_BUILD=true)"
fi

# Tag additional versions if building latest
if [ "$VERSION" = "latest" ] && [ "$SKIP_BUILD" != "true" ]; then
    echo ""
    echo "🏷️ Creating additional tags..."
    
    # Tag with v1.0.0
    docker tag "$FULL_TAG" "${IMAGE_NAME}:v1.0.0"
    echo "✅ Tagged as ${IMAGE_NAME}:v1.0.0"
    
    # Tag with v1.0
    docker tag "$FULL_TAG" "${IMAGE_NAME}:v1.0"
    echo "✅ Tagged as ${IMAGE_NAME}:v1.0"
    
    # Tag with v1
    docker tag "$FULL_TAG" "${IMAGE_NAME}:v1"
    echo "✅ Tagged as ${IMAGE_NAME}:v1"
fi

# Test the image
echo ""
echo "🧪 Testing the image..."

# Start container for testing
test_container="chatterbox-test-$$"
docker run -d --name "$test_container" -p 8001:8000 "$FULL_TAG"

sleep 10

# Test health endpoint
if curl -f http://localhost:8001/ > /dev/null 2>&1; then
    echo "✅ Image test passed - API is responding"
else
    echo "⚠️ Image test failed - API not responding (this may be normal if model is still loading)"
fi

# Clean up test container
docker stop "$test_container" > /dev/null 2>&1
docker rm "$test_container" > /dev/null 2>&1

# Push to Docker Hub
if [ "$SKIP_PUSH" != "true" ]; then
    echo ""
    echo "🚀 Publishing to Docker Hub..."
    echo "Please make sure you're logged in: docker login"
    echo ""
    
    read -p "Continue with push to Docker Hub? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        
        # Push main tag
        echo "📤 Pushing $FULL_TAG..."
        if docker push "$FULL_TAG"; then
            echo "✅ Successfully pushed $FULL_TAG"
        else
            echo "❌ Failed to push $FULL_TAG"
            exit 1
        fi
        
        # Push additional tags if latest
        if [ "$VERSION" = "latest" ]; then
            for tag in "v1.0.0" "v1.0" "v1"; do
                echo "📤 Pushing ${IMAGE_NAME}:${tag}..."
                if docker push "${IMAGE_NAME}:${tag}"; then
                    echo "✅ Successfully pushed ${IMAGE_NAME}:${tag}"
                else
                    echo "❌ Failed to push ${IMAGE_NAME}:${tag}"
                fi
            done
        fi
        
        echo ""
        echo "🎉 Docker image published successfully!"
        echo "📦 Docker Hub: https://hub.docker.com/r/$DOCKER_HUB_USERNAME/chatterbox-tts-api"
        echo ""
        echo "🚀 Users can now run:"
        echo "   docker run -p 8000:8000 $IMAGE_NAME"
        echo ""
        
    else
        echo "⏭️ Skipping push to Docker Hub"
    fi
else
    echo "⏭️ Skipping push (SKIP_PUSH=true)"
fi

echo ""
echo "📋 Summary:"
echo "   Image: $FULL_TAG"
echo "   Size: $(docker images "$FULL_TAG" --format '{{.Size}}' | head -n 1)"
echo "   Ready for: docker run -p 8000:8000 $IMAGE_NAME"
