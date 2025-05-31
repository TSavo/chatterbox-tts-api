#!/bin/bash

# Quick Start Script for Chatterbox TTS API v3.0
# Run this after: docker-compose up -d

echo "🎤 Chatterbox TTS API v3.0 - Quick Start Test"
echo "=============================================="

# Check if API is running
echo "🏥 Checking API health..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ API is running!"
    curl -s http://localhost:8000/health | jq . 2>/dev/null || curl -s http://localhost:8000/health
else
    echo "❌ API is not running. Please run: docker-compose up -d"
    exit 1
fi

# Check queue status (NEW in v3.0)
echo ""
echo "📊 Checking queue status..."
curl -s http://localhost:8000/queue/status | jq . 2>/dev/null || curl -s http://localhost:8000/queue/status

echo ""
echo "🎵 Testing enhanced features..."

# Generate a quick test audio file with job tracking
echo "Generating WAV format..."
curl -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello! Welcome to Chatterbox TTS API version 3.0. This quick test demonstrates the enhanced features including job tracking and multiple output formats.",
    "exaggeration": 0.7,
    "cfg_weight": 0.6,
    "temperature": 1.0,
    "output_format": "wav"
  }' \
  --output "quicktest.wav" \
  --dump-header "headers.txt" \
  --silent

if [ -f "quicktest.wav" ] && [ -s "quicktest.wav" ]; then
    echo "✅ WAV audio generated successfully!"
    echo "   Output file: quicktest.wav"
    echo "   File size: $(du -h quicktest.wav | cut -f1)"
    
    # Show job information from headers
    if [ -f "headers.txt" ]; then
        JOB_ID=$(grep -i "x-job-id" headers.txt | cut -d' ' -f2 | tr -d '\r')
        DURATION=$(grep -i "x-audio-duration" headers.txt | cut -d' ' -f2 | tr -d '\r')
        echo "   Job ID: $JOB_ID"
        echo "   Duration: ${DURATION}s"
        rm -f headers.txt
    fi
else
    echo "❌ Failed to generate WAV audio"
    exit 1
fi

# Test MP3 format (NEW in v3.0)
echo ""
echo "🎵 Testing MP3 format..."
curl -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is an MP3 format test using the new output format feature.",
    "exaggeration": 0.6,
    "cfg_weight": 0.5,
    "temperature": 1.0,
    "output_format": "mp3"
  }' \
  --output "quicktest.mp3" \
  --silent

if [ -f "quicktest.mp3" ] && [ -s "quicktest.mp3" ]; then
    echo "✅ MP3 audio generated successfully!"
    echo "   Output file: quicktest.mp3"
    echo "   File size: $(du -h quicktest.mp3 | cut -f1)"
else
    echo "⚠️  MP3 generation might require ffmpeg (falling back to WAV)"
fi

# Test Base64 response with job tracking
echo ""
echo "📦 Testing Base64 response with job tracking..."
RESULT=$(curl -s -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This response includes base64 audio data and job tracking information.",
    "exaggeration": 0.5,
    "output_format": "wav",
    "return_base64": true
  }')

if echo "$RESULT" | jq -e '.success' > /dev/null 2>&1; then
    echo "✅ Base64 response generated successfully!"
    
    # Extract job information
    JOB_ID=$(echo "$RESULT" | jq -r '.job_id // "unknown"')
    DURATION=$(echo "$RESULT" | jq -r '.duration_seconds // "unknown"')
    B64_LENGTH=$(echo "$RESULT" | jq -r '.audio_base64' | wc -c)
    
    echo "   Job ID: $JOB_ID"
    echo "   Duration: ${DURATION}s"
    echo "   Base64 length: $B64_LENGTH characters"
    
    # Decode and save base64 audio
    echo "$RESULT" | jq -r '.audio_base64' | base64 -d > "quicktest_b64.wav" 2>/dev/null
    if [ -f "quicktest_b64.wav" ] && [ -s "quicktest_b64.wav" ]; then
        echo "   Decoded file: quicktest_b64.wav ($(du -h quicktest_b64.wav | cut -f1))"
    fi
    
    # Test job status endpoint (NEW in v3.0)
    if [ "$JOB_ID" != "unknown" ]; then
        echo ""
        echo "🔍 Testing job status endpoint..."
        curl -s "http://localhost:8000/job/${JOB_ID}/status" | jq . 2>/dev/null || echo "Job status endpoint test completed"
    fi
else
    echo "❌ Base64 response test failed"
fi
    if command -v afplay &> /dev/null; then
        echo "🔊 Playing audio... (macOS)"
        afplay quicktest.wav
    elif command -v aplay &> /dev/null; then
        echo "🔊 Playing audio... (Linux)"
        aplay quicktest.wav 2>/dev/null
    elif command -v powershell &> /dev/null; then
        echo "🔊 Playing audio... (Windows)"
        powershell -c "(New-Object Media.SoundPlayer 'quicktest.wav').PlaySync()"
    else
        echo "🎧 Play the file 'quicktest.wav' to hear the generated speech"
    fi
else
    echo "❌ Audio generation failed"
    exit 1
fi

echo ""
echo "🎉 Quick test completed successfully!"
echo ""
echo "📖 Next steps:"
echo "   • Check examples/ directory for language-specific examples"
echo "   • Visit http://localhost:8000/docs for interactive API documentation"
echo "   • Try voice cloning by uploading your own audio file"
echo "   • Explore batch processing for multiple texts"
echo ""
echo "🚀 Example commands:"
echo "   # Health check:"
echo "   curl http://localhost:8000/health"
echo ""
echo "   # Basic TTS:"
echo "   curl -X POST http://localhost:8000/tts \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"text\": \"Your text here\", \"exaggeration\": 0.7}' \\"
echo "     --output 'output.wav'"
echo ""
echo "   # With base64 response:"
echo "   curl -X POST http://localhost:8000/tts \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"text\": \"Your text\", \"return_base64\": true}'"
