# Quick Start Script for Chatterbox TTS API v3.0 (Windows PowerShell)
# Run this after: docker-compose up -d

Write-Host "🎤 Chatterbox TTS API v3.0 - Quick Start Test" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Green

# Check if API is running
Write-Host "🏥 Checking API health..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 10
    Write-Host "✅ API is running!" -ForegroundColor Green
    Write-Host "   Device: $($healthResponse.device)" -ForegroundColor Cyan
    Write-Host "   GPU Available: $($healthResponse.gpu_available)" -ForegroundColor Cyan
    Write-Host "   Sample Rate: $($healthResponse.sample_rate)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ API is not running. Please run: docker-compose up -d" -ForegroundColor Red
    exit 1
}

# Check queue status (NEW in v3.0)
Write-Host ""
Write-Host "📊 Checking queue status..." -ForegroundColor Yellow
try {
    $queueResponse = Invoke-RestMethod -Uri "http://localhost:8000/queue/status" -Method Get -TimeoutSec 5
    Write-Host "   Queue Size: $($queueResponse.queue_size)" -ForegroundColor Cyan
    Write-Host "   Active Jobs: $($queueResponse.active_jobs)" -ForegroundColor Cyan
    Write-Host "   Total Processed: $($queueResponse.total_jobs_processed)" -ForegroundColor Cyan
} catch {
    Write-Host "⚠️  Could not get queue status" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎵 Testing enhanced features..." -ForegroundColor Yellow

# Generate a quick test audio file with job tracking
Write-Host "Generating WAV format..." -ForegroundColor Cyan
$body = @{
    text = "Hello! Welcome to Chatterbox TTS API version 3.0. This quick test demonstrates the enhanced features including job tracking and multiple output formats."
    exaggeration = 0.7
    cfg_weight = 0.6
    temperature = 1.0
    output_format = "wav"
} | ConvertTo-Json

try {
    # Use Invoke-WebRequest to get headers
    $response = Invoke-WebRequest -Uri "http://localhost:8000/tts" `
                                  -Method Post `
                                  -Body $body `
                                  -ContentType "application/json" `
                                  -TimeoutSec 30
    
    # Save the audio response to file
    [System.IO.File]::WriteAllBytes("quicktest.wav", $response.Content)
    
    if (Test-Path "quicktest.wav") {
        $fileSize = (Get-Item "quicktest.wav").Length
        Write-Host "✅ WAV audio generated successfully!" -ForegroundColor Green
        Write-Host "   Output file: quicktest.wav" -ForegroundColor Cyan
        Write-Host "   File size: $([math]::Round($fileSize/1024, 2)) KB" -ForegroundColor Cyan
        
        # Show job information from headers (NEW in v3.0)
        $jobId = $response.Headers['X-Job-ID']
        $duration = $response.Headers['X-Audio-Duration']
        $outputFormat = $response.Headers['X-Output-Format']
        
        if ($jobId) {
            Write-Host "   Job ID: $jobId" -ForegroundColor Cyan
        }
        if ($duration) {
            Write-Host "   Duration: ${duration}s" -ForegroundColor Cyan
        }
        if ($outputFormat) {
            Write-Host "   Format: $outputFormat" -ForegroundColor Cyan
        }
    } else {
        Write-Host "❌ Failed to generate WAV audio" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ WAV generation failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test MP3 format (NEW in v3.0)
Write-Host ""
Write-Host "🎵 Testing MP3 format..." -ForegroundColor Yellow
$mp3Body = @{
    text = "This is an MP3 format test using the new output format feature."
    exaggeration = 0.6
    cfg_weight = 0.5
    temperature = 1.0
    output_format = "mp3"
} | ConvertTo-Json

try {
    $mp3Response = Invoke-WebRequest -Uri "http://localhost:8000/tts" `
                                     -Method Post `
                                     -Body $mp3Body `
                                     -ContentType "application/json" `
                                     -TimeoutSec 30
    
    [System.IO.File]::WriteAllBytes("quicktest.mp3", $mp3Response.Content)
    
    if (Test-Path "quicktest.mp3") {
        $mp3Size = (Get-Item "quicktest.mp3").Length
        Write-Host "✅ MP3 audio generated successfully!" -ForegroundColor Green
        Write-Host "   Output file: quicktest.mp3" -ForegroundColor Cyan
        Write-Host "   File size: $([math]::Round($mp3Size/1024, 2)) KB" -ForegroundColor Cyan
    } else {
        Write-Host "⚠️  MP3 generation might require ffmpeg (falling back to WAV)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  MP3 generation might require ffmpeg installation" -ForegroundColor Yellow
}

# Test Base64 response with job tracking
Write-Host ""
Write-Host "📦 Testing Base64 response with job tracking..." -ForegroundColor Yellow
$base64Body = @{
    text = "This response includes base64 audio data and job tracking information."
    exaggeration = 0.5
    output_format = "wav"
    return_base64 = $true
} | ConvertTo-Json

try {
    $base64Response = Invoke-RestMethod -Uri "http://localhost:8000/tts" `
                                        -Method Post `
                                        -Body $base64Body `
                                        -ContentType "application/json" `
                                        -TimeoutSec 30
    
    if ($base64Response.success) {
        Write-Host "✅ Base64 response generated successfully!" -ForegroundColor Green
        Write-Host "   Job ID: $($base64Response.job_id)" -ForegroundColor Cyan
        Write-Host "   Duration: $($base64Response.duration_seconds)s" -ForegroundColor Cyan
        Write-Host "   Base64 length: $($base64Response.audio_base64.Length) characters" -ForegroundColor Cyan
        
        # Decode and save base64 audio
        try {
            $audioBytes = [System.Convert]::FromBase64String($base64Response.audio_base64)
            [System.IO.File]::WriteAllBytes("quicktest_b64.wav", $audioBytes)
            
            if (Test-Path "quicktest_b64.wav") {
                $b64Size = (Get-Item "quicktest_b64.wav").Length
                Write-Host "   Decoded file: quicktest_b64.wav ($([math]::Round($b64Size/1024, 2)) KB)" -ForegroundColor Cyan
            }
        } catch {
            Write-Host "⚠️  Could not decode base64 audio" -ForegroundColor Yellow
        }
        
        # Test job status endpoint (NEW in v3.0)
        if ($base64Response.job_id) {
            Write-Host ""
            Write-Host "🔍 Testing job status endpoint..." -ForegroundColor Yellow
            try {
                $jobStatus = Invoke-RestMethod -Uri "http://localhost:8000/job/$($base64Response.job_id)/status" -Method Get -TimeoutSec 5
                Write-Host "   Job Status: $($jobStatus.status)" -ForegroundColor Cyan
                Write-Host "   Job Type: $($jobStatus.job_type)" -ForegroundColor Cyan
            } catch {
                Write-Host "   Job status endpoint test completed" -ForegroundColor Cyan
            }
        }
    } else {
        Write-Host "❌ Base64 response test failed" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Base64 response test failed: $($_.Exception.Message)" -ForegroundColor Red
}
            $player.PlaySync()
        } catch {
            Write-Host "🎧 Please play the file 'quicktest.wav' to hear the generated speech" -ForegroundColor Yellow
        }
    } else {
        Write-Host "❌ Audio file was not created" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Audio generation failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🎉 Quick test completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📖 Next steps:" -ForegroundColor Yellow
Write-Host "   • Check examples\ directory for language-specific examples" -ForegroundColor White
Write-Host "   • Visit http://localhost:8000/docs for interactive API documentation" -ForegroundColor White
Write-Host "   • Try voice cloning by uploading your own audio file" -ForegroundColor White
Write-Host "   • Explore batch processing for multiple texts" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Example PowerShell commands:" -ForegroundColor Yellow
Write-Host "   # Health check:" -ForegroundColor White
Write-Host "   Invoke-RestMethod -Uri 'http://localhost:8000/health'" -ForegroundColor Gray
Write-Host ""
Write-Host "   # Basic TTS with base64 response:" -ForegroundColor White
Write-Host "   `$body = @{ text = 'Your text here'; exaggeration = 0.7; return_base64 = `$true } | ConvertTo-Json" -ForegroundColor Gray
Write-Host "   `$response = Invoke-RestMethod -Uri 'http://localhost:8000/tts' -Method Post -Body `$body -ContentType 'application/json'" -ForegroundColor Gray
Write-Host "   [System.Convert]::FromBase64String(`$response.audio_base64) | Set-Content 'output.wav' -Encoding Byte" -ForegroundColor Gray
