# Chatterbox TTS API

[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/TSavo/chatterbox-tts-api?style=social)](https://github.com/TSavo/chatterbox-tts-api/stargazers)
[![Docker Pulls](https://img.shields.io/docker/pulls/tsavo/chatterbox-tts-api)](https://hub.docker.com/r/tsavo/chatterbox-tts-api)

> 🎤 **Production-ready TTS API with voice cloning in one Docker command**

High-quality text-to-speech with voice cloning, emotion control, and batch processing.

## 🚀 Quick Start

**Run it now:**
```bash
docker run -p 8000:8000 tsavo/chatterbox-tts-api
```

That's it! API is now running at http://localhost:8000

**Test it:**
```bash
curl -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world!"}' \
  --output hello.wav
```

## ✨ Features

- 🎭 **Voice Cloning** - Clone any voice from audio samples
- 🎛️ **Emotion Control** - Adjust intensity and expression
- 🔧 **Multiple Formats** - WAV, MP3, OGG output
- 🚀 **Batch Processing** - Handle multiple requests efficiently
- 📊 **Job Tracking** - Monitor processing status
- 🧩 **Smart Chunking** - Automatically handles long texts (40+ seconds)
- 🐳 **Docker Ready** - No setup required

## 📖 Usage Examples

**Basic TTS:**
```python
import requests

response = requests.post("http://localhost:8000/tts", json={
    "text": "Hello, this is a test!",
    "output_format": "mp3"
})

with open("output.mp3", "wb") as f:
    f.write(response.content)
```

**Voice Cloning:**
```python
with open("reference_voice.wav", "rb") as audio_file:
    response = requests.post(
        "http://localhost:8000/voice-clone",
        data={"text": "Clone this voice!"},
        files={"audio_file": audio_file}
    )
```

**Batch Processing:**
```python
response = requests.post("http://localhost:8000/batch-tts", json={
    "texts": ["First sentence", "Second sentence", "Third sentence"]
})
```

More examples: [examples/](examples/) | Interactive docs: http://localhost:8000/docs

## 🧩 Smart Text Chunking

The API automatically handles long texts that would exceed the 40-second TTS limit:

**How it works:**
1. **Estimates duration** from text length
2. **Intelligently splits** on natural boundaries:
   - Paragraph breaks (double line breaks)
   - Sentence endings (periods, !, ?)
   - Clause breaks (commas, semicolons, colons)
   - Word boundaries (last resort)
3. **Generates each chunk** separately
4. **Concatenates with ffmpeg** into seamless audio

**Example with long text:**
```python
long_text = """
Very long article or document content here...
Multiple paragraphs with natural breaks...
The system will automatically chunk this.
"""

# Will automatically chunk, generate, and concatenate
response = requests.post("http://localhost:8000/tts", json={
    "text": long_text,
    "output_format": "mp3"
})
# Returns single audio file with complete text
```

## 🎛️ Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `exaggeration` | Emotional intensity (0.0-2.0) | 0.5 |
| `cfg_weight` | Generation guidance (0.0-1.0) | 0.5 |
| `temperature` | Randomness (0.1-2.0) | 1.0 |
| `output_format` | Audio format (wav, mp3, ogg) | wav |

## 🔧 Advanced Setup

**With GPU support:**
```bash
docker run --gpus all -p 8000:8000 tsavo/chatterbox-tts-api
```

**Test the chunking feature:**
```bash
# Test with long text (will automatically chunk and concatenate)
python test_chunking.py
```

**Development/Custom builds:**
```bash
git clone https://github.com/TSavo/chatterbox-tts-api.git
cd chatterbox-tts-api
docker-compose up
```

**System Requirements:**
- Docker (includes ffmpeg for audio concatenation)
- 4GB+ RAM (8GB recommended)
- GPU optional but recommended

## 📞 Support

- 📖 **[Interactive API Docs](http://localhost:8000/docs)** - Try the API in your browser
- 🐛 **[Issues](https://github.com/TSavo/chatterbox-tts-api/issues)** - Bug reports and feature requests  
- 💬 **[Discussions](https://github.com/TSavo/chatterbox-tts-api/discussions)** - Community help

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

---

**[T Savo](mailto:listentomy@nefariousplan.com)** • **[Horizon City](https://www.horizon-city.com)**
