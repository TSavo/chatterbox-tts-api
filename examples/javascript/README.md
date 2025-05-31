# Chatterbox TTS API - JavaScript Examples

This directory contains JavaScript examples for using the Chatterbox TTS API in both Node.js and browser environments.

## Prerequisites

1. **Make sure the API is running:**
   ```bash
   docker-compose up -d
   ```

2. **For Node.js examples, install dependencies:**
   ```bash
   npm install axios form-data
   ```

## Examples

### [basic_usage.js](basic_usage.js) - Node.js Examples
Comprehensive Node.js examples covering:
- Basic TTS generation
- Base64 encoded responses  
- Voice cloning with file uploads
- Batch processing
- Advanced parameter demonstrations

**Run with:**
```bash
node basic_usage.js
```

### [browser_demo.html](browser_demo.html) - Browser Demo
Interactive web page demonstrating:
- Real-time TTS generation
- Parameter adjustment with sliders
- Preset configurations
- Audio playback and download
- API health checking

**Open in browser:**
```bash
# Simply open the HTML file in your browser
open browser_demo.html  # macOS
start browser_demo.html # Windows
```

### [package.json](package.json) - Dependencies
Node.js package configuration with required dependencies.

## Quick Start Examples

### Node.js Quick Test
```javascript
const axios = require('axios');

async function quickTest() {
    try {
        const response = await axios.post('http://localhost:8000/tts', {
            text: "Hello from Node.js!",
            exaggeration: 0.7,
            return_base64: true
        });
        
        console.log('✅ Success:', response.data.duration_seconds + 's of audio generated');
    } catch (error) {
        console.log('❌ Error:', error.message);
    }
}

quickTest();
```

### Browser Quick Test
```javascript
// Fetch API example
fetch('http://localhost:8000/tts', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        text: "Hello from the browser!",
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

## CORS Configuration

The API includes CORS headers to allow browser requests. If you encounter CORS issues:

1. **Check API Configuration**: The API should have CORS enabled by default
2. **Local Testing**: Use `http://localhost:8000` (not `127.0.0.1`)
3. **HTTPS**: For production, ensure HTTPS is configured properly

## Error Handling

### Common Issues

1. **Connection Refused**: API not running
   ```bash
   docker-compose up -d
   ```

2. **CORS Errors**: Use correct origin in browser
3. **Timeout Errors**: Large texts or voice cloning may take longer
4. **File Upload Issues**: Ensure audio files are proper format

### Error Response Format
```javascript
{
    "success": false,
    "message": "Error description",
    "sample_rate": 22050,
    "duration_seconds": 0.0
}
```

## Performance Tips

1. **Batch Processing**: Use `/batch-tts` for multiple texts
2. **Base64 vs Binary**: Use binary for large files, base64 for web apps
3. **Parameter Tuning**: Lower values generally process faster
4. **Caching**: Cache generated audio when possible

## Integration Examples

### Express.js Server
```javascript
const express = require('express');
const axios = require('axios');

const app = express();
app.use(express.json());

app.post('/speak', async (req, res) => {
    try {
        const response = await axios.post('http://localhost:8000/tts', {
            text: req.body.text,
            exaggeration: req.body.exaggeration || 0.7,
            return_base64: false
        }, { responseType: 'arraybuffer' });
        
        res.set('Content-Type', 'audio/wav');
        res.send(response.data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.listen(3000);
```

### React Component
```javascript
import React, { useState } from 'react';

function TTSComponent() {
    const [text, setText] = useState('');
    const [audioUrl, setAudioUrl] = useState(null);
    
    const generateSpeech = async () => {
        try {
            const response = await fetch('http://localhost:8000/tts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: text,
                    exaggeration: 0.7,
                    return_base64: false
                })
            });
            
            const audioBlob = await response.blob();
            setAudioUrl(URL.createObjectURL(audioBlob));
        } catch (error) {
            console.error('TTS Error:', error);
        }
    };
    
    return (
        <div>
            <textarea 
                value={text} 
                onChange={(e) => setText(e.target.value)}
                placeholder="Enter text..."
            />
            <button onClick={generateSpeech}>Generate Speech</button>
            {audioUrl && <audio controls src={audioUrl} />}
        </div>
    );
}
```
