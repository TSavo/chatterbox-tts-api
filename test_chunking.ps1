# PowerShell script to test the new chunking functionality
# Run this after starting the API with docker-compose up

Write-Host "🎤 Testing Chatterbox TTS API Chunking" -ForegroundColor Cyan
Write-Host "=" * 50

# Check if API is running
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 10
    Write-Host "✅ API is healthy" -ForegroundColor Green
} catch {
    Write-Host "❌ API not available. Run: docker-compose up -d" -ForegroundColor Red
    exit 1
}

# Create output directory
New-Item -ItemType Directory -Force -Path "test_outputs" | Out-Null

# Test 1: Short text (no chunking)
Write-Host "`n🧪 Test 1: Short text" -ForegroundColor Yellow
$shortText = "This is a short test that should not require chunking."
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/tts" -Method POST -Body (@{
        text = $shortText
        return_base64 = $true
        exaggeration = 0.7
    } | ConvertTo-Json) -ContentType "application/json"
    
    Write-Host "✅ Short text: $($response.duration_seconds) seconds" -ForegroundColor Green
} catch {
    Write-Host "❌ Short text test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Long text (should chunk)
Write-Host "`n🧪 Test 2: Long text (chunking expected)" -ForegroundColor Yellow
$longText = @"
This is a comprehensive test of the Chatterbox TTS API's new intelligent chunking system.
This extensive piece of text has been specifically designed to exceed the forty-second duration limit.

The purpose of this test is to verify that the system can handle long-form content effectively.
When text exceeds the maximum duration threshold, the API automatically breaks it down into smaller, manageable chunks.
These chunks are created by analyzing the text for natural breaking points.

First, the system looks for paragraph breaks, which are indicated by double line breaks.
If paragraphs are still too long, it then examines single line breaks.

Next, it considers sentence boundaries marked by periods, exclamation points, and question marks.
The system also recognizes clause boundaries: commas, semicolons, and colons all provide opportunities for intelligent splitting.

Each chunk is processed individually by the TTS model, generating separate audio segments.
These segments are then seamlessly concatenated using FFmpeg to create a single, cohesive audio file.
The result should sound natural and continuous, as if it were generated as a single piece.

This chunking strategy solves a critical limitation of many TTS systems.
If you're hearing this complete message as a single audio file, then the chunking system is working perfectly!
"@

try {
    $start = Get-Date
    $response = Invoke-WebRequest -Uri "http://localhost:8000/tts" -Method POST -Body (@{
        text = $longText
        output_format = "mp3"
        exaggeration = 0.6
        return_base64 = $false
    } | ConvertTo-Json) -ContentType "application/json" -TimeoutSec 300
    
    $duration = [float]$response.Headers["X-Audio-Duration"]
    $generationTime = (Get-Date) - $start
    
    # Save audio file
    $outputPath = "test_outputs\long_text_chunking_test.mp3"
    [System.IO.File]::WriteAllBytes($outputPath, $response.Content)
    
    Write-Host "✅ Long text: $($duration) seconds duration" -ForegroundColor Green
    Write-Host "   Generation time: $($generationTime.TotalSeconds) seconds" -ForegroundColor Gray
    Write-Host "   Saved to: $outputPath" -ForegroundColor Gray
    
    if ($duration -gt 45) {
        Write-Host "🎉 Successfully generated audio longer than 40s limit!" -ForegroundColor Magenta
    }
    
} catch {
    Write-Host "❌ Long text test failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n📊 Chunking tests completed!" -ForegroundColor Cyan
Write-Host "Check the test_outputs folder for generated audio files." -ForegroundColor Gray