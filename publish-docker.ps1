# Docker Publishing Script for Chatterbox TTS API
# Run this script to build and publish to Docker Hub

param(
    [string]$Version = "latest",
    [string]$DockerHubUsername = "tsavo",
    [switch]$SkipBuild = $false,
    [switch]$SkipPush = $false
)

$ImageName = "$DockerHubUsername/chatterbox-tts-api"
$FullTag = "${ImageName}:${Version}"

Write-Host "🐳 Chatterbox TTS API - Docker Publishing" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host "Image: $FullTag" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
try {
    docker info | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker first." -ForegroundColor Red
    exit 1
}

# Build the image
if (-not $SkipBuild) {
    Write-Host "🔨 Building Docker image..." -ForegroundColor Yellow
    $buildStart = Get-Date
    
    docker build -t $FullTag .
    
    if ($LASTEXITCODE -eq 0) {
        $buildEnd = Get-Date
        $buildDuration = [math]::Round(($buildEnd - $buildStart).TotalSeconds)
        Write-Host "✅ Build completed in ${buildDuration}s" -ForegroundColor Green
        
        # Show image size
        $size = docker images $FullTag --format "{{.Size}}" | Select-Object -First 1
        Write-Host "📦 Image size: $size" -ForegroundColor Cyan
    } else {
        Write-Host "❌ Build failed" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Skip: Skipping build (SkipBuild specified)" -ForegroundColor Yellow
}

# Tag additional versions if building latest
if ($Version -eq "latest" -and -not $SkipBuild) {
    Write-Host ""
    Write-Host "🏷️ Creating additional tags..." -ForegroundColor Yellow
    
    # Tag with v1.0.0
    docker tag $FullTag "${ImageName}:v1.0.0"
    Write-Host "✅ Tagged as ${ImageName}:v1.0.0" -ForegroundColor Green
    
    # Tag with v1.0
    docker tag $FullTag "${ImageName}:v1.0"
    Write-Host "✅ Tagged as ${ImageName}:v1.0" -ForegroundColor Green
    
    # Tag with v1
    docker tag $FullTag "${ImageName}:v1"
    Write-Host "✅ Tagged as ${ImageName}:v1" -ForegroundColor Green
}

# Test the image
Write-Host ""
Write-Host "🧪 Testing the image..." -ForegroundColor Yellow

# Start container for testing
$testContainer = "chatterbox-test-$(Get-Random)"
docker run -d --name $testContainer -p 8001:8000 $FullTag

Start-Sleep -Seconds 10

try {
    # Test health endpoint
    $response = Invoke-RestMethod -Uri "http://localhost:8001/" -TimeoutSec 30
    if ($response.message -like "*Chatterbox TTS API*") {
        Write-Host "✅ Image test passed - API is responding" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Image test warning - unexpected response" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ Image test failed - API not responding (this may be normal if model is still loading)" -ForegroundColor Yellow
} finally {
    # Clean up test container
    docker stop $testContainer | Out-Null
    docker rm $testContainer | Out-Null
}

# Push to Docker Hub
if (-not $SkipPush) {
    Write-Host ""
    Write-Host "🚀 Publishing to Docker Hub..." -ForegroundColor Yellow
    Write-Host "Please make sure you're logged in: docker login" -ForegroundColor Cyan
    Write-Host ""
    
    $confirm = Read-Host "Continue with push to Docker Hub? (y/n)"
    if ($confirm -eq "y" -or $confirm -eq "Y") {
        
        # Push main tag
        Write-Host "📤 Pushing $FullTag..." -ForegroundColor Yellow
        docker push $FullTag
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Successfully pushed $FullTag" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to push $FullTag" -ForegroundColor Red
            exit 1
        }
        
        # Push additional tags if latest
        if ($Version -eq "latest") {
            $additionalTags = @("v1.0.0", "v1.0", "v1")
            foreach ($tag in $additionalTags) {
                Write-Host "📤 Pushing ${ImageName}:${tag}..." -ForegroundColor Yellow
                docker push "${ImageName}:${tag}"
                
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "✅ Successfully pushed ${ImageName}:${tag}" -ForegroundColor Green
                } else {
                    Write-Host "❌ Failed to push ${ImageName}:${tag}" -ForegroundColor Red
                }
            }
        }
        
        Write-Host ""
        Write-Host "🎉 Docker image published successfully!" -ForegroundColor Green
        Write-Host "📦 Docker Hub: https://hub.docker.com/r/$DockerHubUsername/chatterbox-tts-api" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "🚀 Users can now run:" -ForegroundColor Yellow
        Write-Host "   docker run -p 8000:8000 $ImageName" -ForegroundColor Cyan
        Write-Host ""
        
    } else {
        Write-Host "Skip: Skipping push to Docker Hub" -ForegroundColor Yellow
    }
} else {
    Write-Host "Skip: Skipping push (SkipPush specified)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Summary:" -ForegroundColor Green
Write-Host "   Image: $FullTag" -ForegroundColor Cyan
Write-Host "   Size: $(docker images $FullTag --format '{{.Size}}' | Select-Object -First 1)" -ForegroundColor Cyan
Write-Host "   Ready for: docker run -p 8000:8000 $ImageName" -ForegroundColor Cyan
