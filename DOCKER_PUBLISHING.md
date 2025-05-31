# 🐳 Docker Publishing Guide

## 🚀 Quick Start - Manual Publishing

### **Step 1: Login to Docker Hub**

```bash
# Login to Docker Hub
docker login

# Enter your Docker Hub username and password/token
```

### **Step 2: Build and Publish**

**Option A: Use the automated script (Recommended)**

```bash
# Windows PowerShell
.\publish-docker.ps1

# Linux/macOS
chmod +x publish-docker.sh
./publish-docker.sh
```

**Option B: Manual commands**

```bash
# Build the image
docker build -t tsavo/chatterbox-tts-api:latest .

# Test the image locally
docker run -d --name test-chatterbox -p 8001:8000 tsavo/chatterbox-tts-api:latest
curl http://localhost:8001/
docker stop test-chatterbox && docker rm test-chatterbox

# Push to Docker Hub
docker push tsavo/chatterbox-tts-api:latest
```

## 🏷️ Tagging Strategy

### **Version Tags**
- `latest` - Latest stable release
- `v1.0.0` - Specific version
- `v1.0` - Minor version
- `v1` - Major version

### **Example Tagging**
```bash
# Tag multiple versions
docker tag tsavo/chatterbox-tts-api:latest tsavo/chatterbox-tts-api:v1.0.0
docker tag tsavo/chatterbox-tts-api:latest tsavo/chatterbox-tts-api:v1.0
docker tag tsavo/chatterbox-tts-api:latest tsavo/chatterbox-tts-api:v1

# Push all tags
docker push tsavo/chatterbox-tts-api:latest
docker push tsavo/chatterbox-tts-api:v1.0.0
docker push tsavo/chatterbox-tts-api:v1.0
docker push tsavo/chatterbox-tts-api:v1
```

## 🤖 Automated Publishing with GitHub Actions

### **Setup GitHub Secrets**

1. **Go to your GitHub repository**
2. **Settings → Secrets and variables → Actions**
3. **Add these secrets**:
   - `DOCKER_HUB_USERNAME`: Your Docker Hub username
   - `DOCKER_HUB_TOKEN`: Your Docker Hub access token

### **Create Docker Hub Access Token**

1. **Go to [Docker Hub](https://hub.docker.com/)**
2. **Account Settings → Security**
3. **New Access Token**
   - Description: "GitHub Actions - Chatterbox TTS API"
   - Permissions: Read, Write, Delete
4. **Copy the token** and add it to GitHub secrets

### **Automated Publishing Triggers**

The GitHub Actions workflow will automatically publish when:

- ✅ **Push to main branch** → `latest` tag
- ✅ **Create git tag** (e.g., `v1.0.0`) → version tags
- ✅ **All tests pass** → Only publish if CI is green

### **Manual Trigger**

You can also manually trigger publishing:

```bash
# Create and push a tag
git tag v1.0.0
git push origin v1.0.0

# This will trigger automated Docker publishing
```

## 📦 Docker Hub Repository Setup

### **Repository Configuration**

1. **Repository Name**: `chatterbox-tts-api`
2. **Visibility**: Public
3. **Description**: 
   ```
   High-performance TTS API with voice cloning, emotion control, and synchronous MP3 generation. 
   Built with FastAPI and powered by Chatterbox TTS.
   ```

### **README for Docker Hub**

```markdown
# Chatterbox TTS API

High-performance Text-to-Speech API with voice cloning and emotion control.

## Quick Start

```bash
# Run the API
docker run -p 8000:8000 tsavo/chatterbox-tts-api

# Access the API
curl http://localhost:8000/health
```

## Features

- 🎯 Advanced TTS with emotion control
- 🎭 Voice cloning from reference audio
- 🚀 Batch processing capabilities
- 🎵 Multiple formats: MP3, WAV, OGG
- 📦 Synchronous and base64 responses

## Documentation

- **API Docs**: http://localhost:8000/docs
- **GitHub**: https://github.com/TSavo/chatterbox-tts-api
- **Examples**: See GitHub repository

## Environment Variables

- `NVIDIA_VISIBLE_DEVICES=all` - Enable GPU support
- `HF_HOME=/app/hf_cache` - Model cache location

## GPU Support

```bash
# Run with GPU support
docker run --gpus all -p 8000:8000 tsavo/chatterbox-tts-api
```
```

## 🧪 Testing Published Images

### **Test Script**

```bash
#!/bin/bash

IMAGE_NAME="tsavo/chatterbox-tts-api:latest"

echo "🧪 Testing Docker image: $IMAGE_NAME"

# Pull the image
docker pull $IMAGE_NAME

# Run the container
docker run -d --name chatterbox-test -p 8002:8000 $IMAGE_NAME

# Wait for startup
echo "⏳ Waiting for API to start..."
sleep 30

# Test health endpoint
if curl -f http://localhost:8002/; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
fi

# Test TTS endpoint
echo "🎵 Testing TTS generation..."
curl -X POST http://localhost:8002/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello Docker!", "return_base64": true}' \
  | jq '.success'

# Cleanup
docker stop chatterbox-test
docker rm chatterbox-test

echo "🎉 Test completed"
```

## 📊 Multi-Architecture Support

The GitHub Actions workflow builds for multiple architectures:

- ✅ **linux/amd64** - Intel/AMD 64-bit
- ✅ **linux/arm64** - ARM 64-bit (Apple Silicon, etc.)

### **Manual Multi-Arch Build**

```bash
# Create and use buildx builder
docker buildx create --name multiarch --use

# Build for multiple platforms
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag tsavo/chatterbox-tts-api:latest \
  --push .
```

## 🔍 Image Information

### **Expected Image Size**
- **Compressed**: ~2.5-3GB
- **Uncompressed**: ~6-8GB

### **Layers**
- Base PyTorch image
- System dependencies (ffmpeg, curl)
- Python packages
- Application code

### **Security**
- ✅ Non-root user
- ✅ Minimal attack surface
- ✅ Regular security scans

## 🚀 Usage Examples

### **Basic Usage**
```bash
docker run -p 8000:8000 tsavo/chatterbox-tts-api
```

### **With GPU Support**
```bash
docker run --gpus all -p 8000:8000 tsavo/chatterbox-tts-api
```

### **With Model Caching**
```bash
docker run -p 8000:8000 \
  -v ./hf_cache:/root/.cache/huggingface \
  tsavo/chatterbox-tts-api
```

### **Production Deployment**
```bash
docker run -d \
  --name chatterbox-tts \
  --restart unless-stopped \
  --gpus all \
  -p 8000:8000 \
  -v ./hf_cache:/root/.cache/huggingface \
  tsavo/chatterbox-tts-api
```

## 📈 Monitoring

### **Health Checks**
```bash
# Basic health
curl http://localhost:8000/

# Detailed health
curl http://localhost:8000/health

# Queue status
curl http://localhost:8000/queue/status
```

### **Logs**
```bash
# View logs
docker logs chatterbox-tts

# Follow logs
docker logs -f chatterbox-tts
```

## 🎯 Next Steps

1. **✅ Publish to Docker Hub**
2. **✅ Set up automated publishing**
3. **✅ Test multi-architecture builds**
4. **✅ Create GitHub repository**
5. **✅ Announce to community**

---

**Ready to publish your Docker image and make TTS accessible to everyone! 🐳🎵**
