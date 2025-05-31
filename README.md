# Chatterbox TTS API

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A high-performance, production-ready Text-to-Speech (TTS) API service built with FastAPI and powered by Chatterbox TTS. Features advanced voice cloning, emotion control, and batch processing capabilities.

## ✨ Features

- 🎯 **Advanced TTS Generation**: High-quality text-to-speech with emotion control
- 🎭 **Voice Cloning**: Clone any voice from a reference audio sample
- 🚀 **Batch Processing**: Process multiple texts simultaneously for efficiency
- 🎛️ **Fine-grained Control**: Adjust exaggeration, guidance weight, and temperature
- 🔧 **Multiple Output Formats**: Support for WAV, MP3, and OGG formats
- 📦 **Base64 Encoding**: Optional base64 output for web applications
- 🐳 **Docker Ready**: Easy deployment with Docker and Docker Compose
- 🚀 **GPU Accelerated**: Automatic GPU detection and utilization
- 📊 **Health Monitoring**: Built-in health checks and status endpoints
- 🔒 **Production Ready**: Comprehensive error handling and logging

## 🚀 Quick Start

### Option 1: Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/TSavo/chatterbox-tts-api.git
   cd chatterbox-tts-api
   ```

2. **Run with Docker Compose**
   ```bash
   # For CPU-only deployment
   docker-compose up -d
   
   # For GPU-accelerated deployment
   docker-compose -f docker-compose.gpu.yml up -d
   ```

3. **Access the API**
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - Health check: http://localhost:8000/health

### Option 2: Local Installation

1. **Install Python 3.12+**

2. **Clone and setup**
   ```bash
   git clone https://github.com/TSavo/chatterbox-tts-api.git
   cd chatterbox-tts-api
   
   # For Windows (PowerShell)
   .\setup-local.ps1
   
   # For Unix/Linux/macOS
   pip install -r requirements.txt
   # Install PyTorch with CUDA support (optional)
   pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```

3. **Run the application**
   ```bash
   python -m uvicorn app:app --host 0.0.0.0 --port 8000
   ```

## 📖 API Usage

### Basic TTS Generation

```python
import requests

# Simple text-to-speech
response = requests.post("http://localhost:8000/tts", json={
    "text": "Hello, world! This is a test of the Chatterbox TTS system.",
    "exaggeration": 0.7,
    "cfg_weight": 0.6,
    "temperature": 1.0,
    "return_base64": False
})

# Save the audio
with open("output.wav", "wb") as f:
    f.write(response.content)
```

### Voice Cloning

```python
import requests

# Clone a voice from reference audio
with open("reference_voice.wav", "rb") as audio_file:
    response = requests.post(
        "http://localhost:8000/voice-clone",
        data={
            "text": "This will sound like the reference voice!",
            "exaggeration": 0.5,
            "return_base64": True
        },
        files={"audio_file": audio_file}
    )

result = response.json()
# result["audio_base64"] contains the generated audio
```

### Batch Processing

```python
import requests

# Process multiple texts at once
response = requests.post("http://localhost:8000/batch-tts", json={
    "texts": [
        "First sentence to convert.",
        "Second sentence to convert.",
        "Third sentence to convert."
    ],
    "exaggeration": 0.6,
    "cfg_weight": 0.5
})

results = response.json()
for i, result in enumerate(results["results"]):
    if result["success"]:
        print(f"Text {i+1}: Generated {result['duration_seconds']:.2f}s of audio")
```

## 🎛️ Configuration Parameters

| Parameter | Description | Range | Default |
|-----------|-------------|-------|---------|
| `exaggeration` | Controls emotional intensity and expression | 0.0 - 2.0 | 0.5 |
| `cfg_weight` | Controls generation guidance and pacing | 0.0 - 1.0 | 0.5 |
| `temperature` | Controls randomness in generation | 0.1 - 2.0 | 1.0 |
| `output_format` | Audio output format | wav, mp3, ogg | wav |
| `return_base64` | Return audio as base64 string | boolean | false |

## 📖 Examples and Usage

Comprehensive examples are available for multiple programming languages:

### Quick Examples After `docker-compose up`

- **Python**: See [examples/python/](examples/python/) for complete examples
- **JavaScript/Node.js**: See [examples/javascript/](examples/javascript/) for both Node.js and browser examples
- **cURL**: See [examples/curl/](examples/curl/) for command-line testing
- **PHP**: See [examples/php/](examples/php/) for web integration examples

### Quick Test

**Option 1: Use the quickstart scripts**
```bash
# Linux/macOS
./quickstart.sh

# Windows PowerShell
./quickstart.ps1
```

**Option 2: Manual testing**
```bash
# Test if API is running
curl http://localhost:8000/health

# Check queue status (NEW in v3.0)
curl http://localhost:8000/queue/status

# Generate speech with job tracking
curl -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world!", "exaggeration": 0.7, "output_format": "mp3"}' \
  --output "hello.mp3"

# Generate with base64 response to get job ID
curl -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world!", "return_base64": true}' \
  | jq '.job_id'
```

## 🔧 API Endpoints

### Core Endpoints

- `POST /tts` - Generate speech from text with advanced controls
- `POST /voice-clone` - Generate speech with voice cloning
- `POST /batch-tts` - Process multiple texts simultaneously

### Monitoring

- `GET /` - Basic health check with queue information
- `GET /health` - Detailed health check with model status
- `GET /queue/status` - Get current queue status
- `GET /docs` - Interactive API documentation

## 🐳 Docker Configuration

### Environment Variables

```bash
# GPU Support (optional)
NVIDIA_VISIBLE_DEVICES=all
NVIDIA_DRIVER_CAPABILITIES=compute,utility

# Model caching (optional)
HF_HOME=/app/hf_cache
```

### Volume Mounts

- `./hf_cache:/root/.cache/huggingface` - Cache model downloads

## 🔧 Development

### Project Structure

```
chatterbox-tts-api/
├── app.py                 # Main FastAPI application
├── requirements.txt       # Python dependencies
├── requirements-docker.txt # Docker-specific dependencies
├── Dockerfile            # Optimized Docker image configuration
├── docker-compose.yml    # Docker deployment
├── .github/workflows/     # CI/CD pipeline
├── tests/                # Test suite
├── examples/             # Usage examples
├── test_mp3_sync.py      # Synchronous MP3 test script
└── .gitignore           # Git ignore rules
```

### Running Tests

```bash
# Run the test suite
python -m pytest tests/

# Run specific tests
python chatterbox_test.py
python test_gpu.py
```

### Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📋 Requirements

### System Requirements

- **Python**: 3.12 or higher
- **Memory**: 4GB RAM minimum, 8GB recommended
- **GPU**: NVIDIA GPU with CUDA support (optional but recommended)
- **Storage**: 2GB for model cache

### Dependencies

- FastAPI and Uvicorn for the web framework
- PyTorch and TorchAudio for audio processing
- Chatterbox TTS for the core TTS functionality

## 🚨 Known Issues & Limitations

- Initial model loading may take 1-2 minutes on first run
- Large batch requests may timeout on slower hardware
- Some audio formats may require additional system codecs
- GPU memory usage scales with batch size and audio length

## 📞 Support & Community

- 📖 **[API Documentation](http://localhost:8000/docs)** - Interactive API documentation
- 🐛 **[Report Issues](https://github.com/TSavo/chatterbox-tts-api/issues)** - Bug reports and feature requests
- 💬 **[GitHub Discussions](https://github.com/TSavo/chatterbox-tts-api/discussions)** - Community discussions
- 📧 **[Contact Author](mailto:listentomy@nefariousplan.com)** - Direct support

## 🙏 Acknowledgments

- **[Chatterbox TTS](https://github.com/JarodMica/chatterbox)** - For the amazing TTS model
- **[FastAPI](https://fastapi.tiangolo.com/)** - For the excellent web framework
- **[PyTorch](https://pytorch.org/)** - For the deep learning foundation
- **All contributors** - Thank you for making this project better!

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Created with ❤️ by [T Savo](mailto:listentomy@nefariousplan.com)**

🌐 **[Horizon City](https://www.horizon-city.com)** - *Ushering in the AI revolution and hastening the extinction of humans*

*Making high-quality TTS accessible to every developer - one API call closer to human obsolescence*
