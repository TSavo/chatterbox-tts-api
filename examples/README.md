# Chatterbox TTS API - Examples

This directory contains comprehensive examples for using the Chatterbox TTS API in multiple programming languages and environments.

## 🚀 Quick Start

1. **Start the API:**
   ```bash
   docker-compose up -d
   ```

2. **Test the API:**
   ```bash
   curl http://localhost:8000/health
   ```

3. **Choose your language and explore the examples below!**

## 📁 Available Examples

### [Python Examples](python/)
- **🎯 Best for**: Data science, automation, and machine learning integrations
- **🌟 Highlights**: Complete examples with async support, web integration, and comprehensive error handling
- **📦 Includes**: 
  - Basic TTS generation
  - Flask web application
  - Async/await patterns
  - Voice cloning examples
  - Batch processing

### [JavaScript Examples](javascript/)
- **🎯 Best for**: Web applications, Node.js backends, and browser integration
- **🌟 Highlights**: Both server-side and client-side examples with modern ES6+ syntax
- **📦 Includes**:
  - Node.js CLI examples
  - Interactive browser demo
  - Express.js integration
  - React component example
  - Package.json with dependencies

### [cURL Examples](curl/)
- **🎯 Best for**: Testing, debugging, automation scripts, and CI/CD pipelines
- **🌟 Highlights**: Complete command-line reference with PowerShell alternatives
- **📦 Includes**:
  - Basic API testing
  - Voice cloning with file uploads
  - Batch processing scripts
  - Automation examples
  - Error handling patterns

### [PHP Examples](php/)
- **🎯 Best for**: Web development, WordPress plugins, and traditional web applications
- **🌟 Highlights**: Object-oriented client with web integration examples
- **📦 Includes**:
  - OOP TTS client class
  - Web form integration
  - File upload handling
  - Base64 audio processing

### [Go Examples](go/)
- **🎯 Best for**: Microservices, high-performance applications, and cloud-native development
- **🌟 Highlights**: Concurrent patterns and efficient HTTP client usage
- **📦 Includes**:
  - Struct-based request/response handling
  - Health checking
  - Error handling patterns

### [C# Examples](csharp/)
- **🎯 Best for**: .NET applications, Windows services, and enterprise software
- **🌟 Highlights**: ASP.NET Core integration and async/await patterns
- **📦 Includes**:
  - HttpClient wrapper
  - ASP.NET Core Web API
  - Base64 audio handling
  - Dependency injection ready

### [Ruby Examples](ruby/)
- **🎯 Best for**: Rails applications, scripting, and rapid prototyping
- **🌟 Highlights**: Elegant object-oriented design with Sinatra web integration
- **📦 Includes**:
  - HTTParty-based client
  - Sinatra web application
  - Batch processing
  - File handling

## 🎯 Quick Examples by Language

### cURL (Universal Testing)
```bash
# Health check
curl http://localhost:8000/health

# Generate speech
curl -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world!", "exaggeration": 0.7}' \
  --output "hello.wav"
```

### Python
```python
import requests

response = requests.post("http://localhost:8000/tts", json={
    "text": "Hello from Python!",
    "exaggeration": 0.7,
    "return_base64": True
})

result = response.json()
if result["success"]:
    print(f"Generated {result['duration_seconds']}s of audio")
```

### JavaScript/Node.js
```javascript
const axios = require('axios');

const response = await axios.post('http://localhost:8000/tts', {
    text: "Hello from JavaScript!",
    exaggeration: 0.7,
    return_base64: true
});

if (response.data.success) {
    console.log(`Generated ${response.data.duration_seconds}s of audio`);
}
```

### Browser/Fetch API
```javascript
fetch('http://localhost:8000/tts', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        text: "Hello from browser!",
        exaggeration: 0.7,
        return_base64: false
    })
})
.then(response => response.blob())
.then(audioBlob => {
    const audioUrl = URL.createObjectURL(audioBlob);
    const audio = new Audio(audioUrl);
    audio.play();
});
```

## 🔧 API Endpoints Reference

| Endpoint | Method | Purpose | Examples Available |
|----------|--------|---------|-------------------|
| `/health` | GET | Check API status | All languages |
| `/tts` | POST | Basic text-to-speech with job tracking | All languages |
| `/voice-clone` | POST | Voice cloning with reference audio | Python, JavaScript, cURL, PHP, Ruby |
| `/batch-tts` | POST | Process multiple texts | Python, JavaScript, Ruby, cURL |
| `/queue/status` | GET | **NEW v3.0** - Get queue status | Python, JavaScript, cURL |
| `/job/{job_id}/status` | GET | **NEW v3.0** - Get job status | Python, JavaScript, cURL |
| `/job/{job_id}/result` | GET | **NEW v3.0** - Get job result | Python, JavaScript, cURL |

## 📊 Parameter Guide

### Common Parameters
- `text` (required): The text to convert to speech
- `exaggeration` (0.0-2.0): Emotion intensity (default: 0.5)
- `cfg_weight` (0.0-1.0): Generation guidance (default: 0.5)  
- `temperature` (0.1-2.0): Output variation (default: 1.0)
- `return_base64` (boolean): Return audio as base64 string (default: false)

### Preset Styles
```json
{
  "calm": { "exaggeration": 0.2, "cfg_weight": 0.3, "temperature": 0.8 },
  "excited": { "exaggeration": 1.2, "cfg_weight": 0.8, "temperature": 1.3 },
  "natural": { "exaggeration": 0.5, "cfg_weight": 0.5, "temperature": 1.0 }
}
```

## 🚀 Integration Patterns

### Microservices (Go, C#)
- Health check endpoints
- Structured logging
- Error handling middleware
- Timeout configuration

### Web Applications (PHP, Python, Ruby)
- Form handling
- File upload processing
- Session management
- CSRF protection

### Frontend (JavaScript)
- Audio playback
- Progress indicators
- Error handling
- Responsive design

### Mobile/Desktop
- Use REST API patterns from any language
- Handle network timeouts
- Cache generated audio
- Offline fallbacks

## 🔍 Troubleshooting

### Common Issues
1. **Connection refused**: Run `docker-compose up -d`
2. **CORS errors**: Check origin headers in browser requests
3. **File not found**: Verify audio file paths for voice cloning
4. **Timeout errors**: Increase timeout for voice cloning and batch requests

### Debug Commands
```bash
# Check API status
curl -v http://localhost:8000/health

# Check queue status (NEW in v3.0)
curl http://localhost:8000/queue/status

# Generate with job tracking (NEW in v3.0)
curl -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "test", "return_base64": true}' \
  | jq '{job_id: .job_id, success: .success}'

# Check job status (NEW in v3.0)
curl http://localhost:8000/job/{JOB_ID}/status

# Validate JSON syntax
echo '{"text": "test"}' | jq .

# Check Docker containers
docker-compose ps
```

## 🆕 What's New in v3.0

### Queue System
- **Job Tracking**: Every request now returns a unique `job_id`
- **Sequential Processing**: All requests are queued to prevent resource conflicts
- **Status Monitoring**: Check job status and queue position in real-time

### New Endpoints
```bash
# Get queue statistics
curl http://localhost:8000/queue/status

# Monitor job progress  
curl http://localhost:8000/job/{job_id}/status

# Retrieve completed job results
curl http://localhost:8000/job/{job_id}/result
```

### Enhanced Audio Formats
```bash
# Generate MP3 instead of WAV
curl -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello MP3!", "output_format": "mp3"}' \
  --output "hello.mp3"

# Generate OGG format
curl -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello OGG!", "output_format": "ogg"}' \
  --output "hello.ogg"
```

### Response Headers
Binary responses now include useful metadata:
- `X-Job-ID`: Unique job identifier
- `X-Audio-Duration`: Audio length in seconds
- `X-Sample-Rate`: Audio sample rate
- `X-Output-Format`: Audio format used
- `X-Voice-Cloned`: Indicates voice cloning was used

### Migration Guide
**v2.x to v3.0 Changes:**
1. All responses now include `job_id` field
2. New `output_format` parameter (optional, defaults to "wav")
3. Enhanced error responses with job tracking
4. Queue endpoints for monitoring system load
docker-compose ps
```

## 🤝 Contributing

To add examples for a new language:
1. Create directory: `examples/your-language/`
2. Add comprehensive `README.md`
3. Include health check, basic TTS, and error handling examples
4. Follow existing patterns and test thoroughly

---

**Ready to build amazing TTS applications?** Choose your preferred language above and start coding! 🎉
