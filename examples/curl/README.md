# Chatterbox TTS API v3.0 - cURL Examples

These examples show how to use the enhanced Chatterbox TTS API with cURL commands for testing and automation.
Features new job tracking, queue system, and multiple output formats.

## Prerequisites

Make sure the API is running:
```bash
docker-compose up -d
```

## Basic Examples

### 1. Health Check
```bash
# Check if API is running
curl -X GET http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "device": "cuda",
#   "model_loaded": true,
#   "gpu_available": true,
#   "sample_rate": 22050
# }
```

### 2. Queue Status Check (NEW in v3.0)
```bash
# Check current queue status
curl -X GET http://localhost:8000/queue/status

# Expected response:
# {
#   "queue_size": 0,
#   "active_jobs": 0,
#   "total_jobs_processed": 42
# }
```

### 3. Basic TTS (Binary Audio Response)
```bash
# Generate speech and save to file (includes job tracking)
curl -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello! This is a test of the enhanced Chatterbox TTS API version 3.0 using cURL.",
    "exaggeration": 0.7,
    "cfg_weight": 0.6,
    "temperature": 1.0,
    "output_format": "wav"
  }' \
  --output "output_basic.wav" \
  --dump-header headers.txt

# Check the generated file and headers
ls -la output_basic.wav
cat headers.txt | grep "X-"
# Look for: X-Job-ID, X-Audio-Duration, X-Sample-Rate, X-Output-Format
```

### 4. Different Output Formats (NEW in v3.0)
```bash
# Generate MP3 format
curl -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This audio will be generated in MP3 format!",
    "exaggeration": 0.6,
    "cfg_weight": 0.5,
    "temperature": 1.0,
    "output_format": "mp3"
  }' \
  --output "output_test.mp3"

# Generate OGG format
curl -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This audio will be generated in OGG format!",
    "exaggeration": 0.6,
    "cfg_weight": 0.5,
    "temperature": 1.0,
    "output_format": "ogg"
  }' \
  --output "output_test.ogg"

# Compare file sizes
ls -lh output_test.*
```

### 5. TTS with Base64 Response and Job Tracking
```bash
# Generate speech with JSON response containing base64 audio and job ID
curl -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -d '{    "text": "This will return base64 encoded audio data with job tracking!",
    "exaggeration": 0.5,
    "cfg_weight": 0.5,
    "temperature": 1.0,
    "output_format": "mp3",
    "return_base64": true
  }' | jq '{job_id: .job_id, success: .success, duration: .duration_seconds}'

# Expected response:
# {
#   "job_id": "abc123-def456-ghi789",
#   "success": true,
#   "duration": 2.5
# }
```

### 6. Job Status Monitoring (NEW in v3.0)
```bash
# Get job status by ID (replace JOB_ID with actual job ID from previous request)
JOB_ID="abc123-def456-ghi789"

curl -X GET "http://localhost:8000/job/${JOB_ID}/status" | jq .

# Expected response:
# {
#   "job_id": "abc123-def456-ghi789",
#   "status": "completed",
#   "job_type": "tts",
#   "created_at": "2025-05-30T10:30:00Z",
#   "started_at": "2025-05-30T10:30:01Z",
#   "completed_at": "2025-05-30T10:30:03Z"
# }

# Get job result
curl -X GET "http://localhost:8000/job/${JOB_ID}/result" | jq '.success'
```
    "cfg_weight": 0.5,
    "temperature": 1.0,
    "return_base64": true
  }' | jq .

# Save just the base64 audio data
curl -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Base64 audio example",
    "return_base64": true
  }' | jq -r '.audio_base64' | base64 -d > output_base64.wav
```

## Advanced Examples

### 7. Voice Cloning (Enhanced with Job Tracking)
```bash
# Voice cloning with reference audio file and job tracking
curl -X POST http://localhost:8000/voice-clone \
  -F "text=This is voice cloning in action using cURL with job tracking!" \
  -F "exaggeration=0.6" \
  -F "cfg_weight=0.7" \
  -F "temperature=0.9" \
  -F "output_format=mp3" \
  -F "audio_file=@../test_audio.wav" \
  --output "output_cloned.mp3" \
  --dump-header voice_headers.txt

# Check job ID and voice cloning confirmation
cat voice_headers.txt | grep -E "X-Job-ID|X-Voice-Cloned"

# Voice cloning with base64 response and job ID
curl -X POST http://localhost:8000/voice-clone \
  -F "text=Cloned voice with JSON response and job tracking" \
  -F "return_base64=true" \
  -F "output_format=wav" \
  -F "audio_file=@../test_audio.wav" | jq '{job_id: .job_id, success: .success, voice_cloned: .voice_cloned}'
```

## Queue Management (NEW in v3.0)

### 8. Queue Monitoring Workflow
```bash
# Step 1: Check initial queue status
echo "Initial queue status:"
curl -s http://localhost:8000/queue/status | jq .

# Step 2: Submit multiple jobs quickly to see queue in action
echo "Submitting multiple jobs..."
for i in {1..3}; do
  curl -s -X POST http://localhost:8000/tts \
    -H "Content-Type: application/json" \
    -d "{\"text\": \"Job number $i in the queue\", \"return_base64\": true}" \
    | jq -r '.job_id' &
done
wait

# Step 3: Check queue status again
echo "Queue status after job submission:"
curl -s http://localhost:8000/queue/status | jq .
```

### 9. Job Lifecycle Monitoring
```bash
# Submit a job and get job ID
JOB_ID=$(curl -s -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Monitoring this job from submission to completion!",
    "exaggeration": 0.7,
    "return_base64": true
  }' | jq -r '.job_id')

echo "Job ID: $JOB_ID"

# Monitor job status until completion
while true; do
  STATUS=$(curl -s "http://localhost:8000/job/${JOB_ID}/status" | jq -r '.status')
  echo "Job status: $STATUS"
  
  if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; then
    break
  fi
  
  sleep 1
done

# Get final result
echo "Job result:"
curl -s "http://localhost:8000/job/${JOB_ID}/result" | jq '{success: .success, duration: .duration_seconds}'
```

### 10. Batch Processing (Enhanced with Job Tracking)
```bash
# Process multiple texts at once with job tracking
BATCH_RESULT=$(curl -s -X POST http://localhost:8000/batch-tts \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "This is the first sentence in the enhanced batch processing.",
      "Here is the second sentence with job tracking.",
      "And finally, the third sentence in the queue system."
    ],
    "exaggeration": 0.6,
    "cfg_weight": 0.5,
    "temperature": 1.0,
    "output_format": "wav"
  }')

# Extract job ID and results
echo "Batch job ID:"
echo "$BATCH_RESULT" | jq -r '.job_id'

echo "Batch results summary:"
echo "$BATCH_RESULT" | jq '{success: .success, total_duration: .total_duration, count: (.results | length)}'

# Extract individual audio files from batch response
echo "Extracting audio files..."
echo "$BATCH_RESULT" | jq -r '.results[] | select(.success) | .audio_base64' | while read -r audio; do
  index=1
  echo "$audio" | base64 -d > "batch_output_${index}.wav"
  ((index++))
done
```
```bash
# Subtle emotion (low exaggeration)
curl -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is a calm and subtle voice.",
    "exaggeration": 0.2,
    "cfg_weight": 0.3,
    "temperature": 0.8
  }' --output "output_calm.wav"

# High emotion (high exaggeration)
curl -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is a very expressive and dramatic voice!",
    "exaggeration": 1.5,
    "cfg_weight": 0.8,
    "temperature": 1.2
  }' --output "output_dramatic.wav"
```

### 7. Different Guidance Levels
```bash
# Low guidance (more creative)
curl -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Creative and varied speech generation.",
    "cfg_weight": 0.2,
    "temperature": 1.5
  }' --output "output_creative.wav"

# High guidance (more controlled)
curl -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Controlled and consistent speech generation.",
    "cfg_weight": 0.9,
    "temperature": 0.7
  }' --output "output_controlled.wav"
```

## Testing and Debugging

### 8. Verbose Output
```bash
# Show detailed request/response information
curl -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Debug test", "return_base64": true}' \
  -v | jq .
```

### 9. Timing Requests
```bash
# Measure request time
time curl -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Timing test for performance measurement"}' \
  --output "timed_output.wav"
```

### 10. Error Handling
```bash
# Test with invalid parameters
curl -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "",
    "exaggeration": 5.0,
    "cfg_weight": 2.0
  }' | jq .

# Test with missing text
curl -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -d '{"exaggeration": 0.5}' | jq .
```

## Automation Scripts

### 11. Batch Script for Multiple Requests
```bash
#!/bin/bash
# batch_generate.sh

texts=(
  "First automated message"
  "Second automated message"  
  "Third automated message"
)

for i in "${!texts[@]}"; do
  echo "Generating audio $((i+1))/$(n{#texts[@]}): ${texts[$i]}"
  
  curl -X POST http://localhost:8000/tts \
    -H "Content-Type: application/json" \
    -d "{\"text\": \"${texts[$i]}\", \"exaggeration\": 0.7}" \
    --output "auto_output_$((i+1)).wav" \
    --silent
    
  if [ $? -eq 0 ]; then
    echo "✅ Generated auto_output_$((i+1)).wav"
  else
    echo "❌ Failed to generate audio $((i+1))"
  fi
done

echo "Batch generation complete!"
```

### 12. Monitor API Health
```bash
#!/bin/bash
# health_monitor.sh

while true; do
  response=$(curl -s http://localhost:8000/health)
  status=$(echo "$response" | jq -r '.status // "unknown"')
  
  if [ "$status" = "healthy" ]; then
    echo "$(date): ✅ API is healthy"
  else
    echo "$(date): ❌ API is not healthy: $response"
  fi
  
  sleep 30
done
```

## PowerShell Examples (Windows)

### 13. Basic PowerShell Request
```powershell
# Basic TTS request using PowerShell
$body = @{
    text = "Hello from PowerShell!"
    exaggeration = 0.7
    return_base64 = $true
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/tts" `
                             -Method Post `
                             -Body $body `
                             -ContentType "application/json"

if ($response.success) {
    Write-Host "✅ Generated $($response.duration_seconds)s of audio"
    # Decode base64 and save to file
    $audioBytes = [System.Convert]::FromBase64String($response.audio_base64)
    [System.IO.File]::WriteAllBytes("output_powershell.wav", $audioBytes)
} else {
    Write-Host "❌ Error: $($response.message)"
}
```

## Tips and Best Practices

1. **Use `jq` for JSON processing**: Install with `apt install jq` or `brew install jq`
2. **Save responses**: Always save audio to files for verification
3. **Error handling**: Check HTTP status codes and response content
4. **Rate limiting**: Add delays between requests for large batches
5. **File formats**: The API returns WAV format by default
6. **Headers**: Check response headers for metadata (duration, sample rate)

## Common Issues

1. **Connection refused**: Make sure `docker-compose up -d` is running
2. **File not found**: Check paths for reference audio files
3. **JSON errors**: Validate JSON with tools like `jq`
4. **Large responses**: Use `--output` to save binary data directly
5. **Timeouts**: Increase timeout for voice cloning: `--max-time 60`
