# Chatterbox TTS API - Python Examples

This directory contains Python examples for using the Chatterbox TTS API.

## Prerequisites

1. Make sure the API is running:
   ```bash
   docker-compose up -d
   ```

2. Install required Python packages:
   ```bash
   pip install requests
   ```

## Examples

### [basic_usage.py](basic_usage.py)
Comprehensive examples covering all API features:
- Basic TTS generation
- Base64 encoded responses
- Voice cloning with reference audio
- Batch processing multiple texts
- Advanced parameter demonstrations

### [web_integration.py](web_integration.py)
Examples for web application integration:
- Flask web app with TTS endpoint
- Real-time audio generation
- File upload handling for voice cloning

### [async_examples.py](async_examples.py)
Asynchronous examples using `aiohttp`:
- Async/await patterns
- Concurrent requests
- Error handling with async code

## Running the Examples

```bash
# Run all basic examples
python basic_usage.py

# Run web integration example
python web_integration.py

# Run async examples
python async_examples.py
```

## Quick Start

```python
import requests

# Basic TTS request
response = requests.post("http://localhost:8000/tts", json={
    "text": "Hello, world!",
    "exaggeration": 0.7,
    "return_base64": True
})

result = response.json()
if result["success"]:
    print(f"Generated {result['duration_seconds']:.2f}s of audio")
```

## Common Use Cases

### Web Applications
- Generate audio for dynamic content
- Voice announcements
- Accessibility features

### Content Creation
- Voiceovers for videos
- Podcast production
- Audio book generation

### Interactive Systems
- Voice assistants
- Educational applications
- Gaming dialogue
