#!/usr/bin/env python3
"""
Flask Web Application with Chatterbox TTS Integration

This example shows how to integrate the Chatterbox TTS API
into a web application using Flask.
"""

from flask import Flask, request, jsonify, send_file, render_template_string
import requests
import base64
import tempfile
import os
from io import BytesIO

app = Flask(__name__)

# Configuration
TTS_API_URL = "http://localhost:8000"

# Simple HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Chatterbox TTS Web Demo</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        textarea { width: 100%; height: 100px; margin: 10px 0; }
        button { padding: 10px 20px; margin: 5px; background: #007bff; color: white; border: none; cursor: pointer; }
        button:hover { background: #0056b3; }
        .controls { margin: 20px 0; }
        .control-group { margin: 10px 0; }
        label { display: inline-block; width: 150px; }
        input[type="range"] { width: 200px; }
        .output { margin: 20px 0; padding: 20px; background: #f8f9fa; border-radius: 5px; }
        .error { color: #dc3545; }
        .success { color: #28a745; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎤 Chatterbox TTS Web Demo</h1>
        <p>Enter text below and generate speech using the Chatterbox TTS API.</p>
        
        <div class="controls">
            <div class="control-group">
                <label>Text to speak:</label><br>
                <textarea id="textInput" placeholder="Enter your text here...">Hello! This is a demonstration of the Chatterbox TTS API integrated into a web application.</textarea>
            </div>
            
            <div class="control-group">
                <label for="exaggeration">Exaggeration:</label>
                <input type="range" id="exaggeration" min="0" max="2" step="0.1" value="0.7">
                <span id="exaggerationValue">0.7</span>
            </div>
            
            <div class="control-group">
                <label for="cfgWeight">CFG Weight:</label>
                <input type="range" id="cfgWeight" min="0" max="1" step="0.1" value="0.6">
                <span id="cfgWeightValue">0.6</span>
            </div>
            
            <div class="control-group">
                <label for="temperature">Temperature:</label>
                <input type="range" id="temperature" min="0.1" max="2" step="0.1" value="1.0">
                <span id="temperatureValue">1.0</span>
            </div>
            
            <button onclick="generateSpeech()">🎵 Generate Speech</button>
            <button onclick="downloadAudio()" id="downloadBtn" style="display:none;">💾 Download Audio</button>
        </div>
        
        <div id="output" class="output" style="display:none;">
            <h3>Generated Audio:</h3>
            <audio id="audioPlayer" controls style="width: 100%;"></audio>
            <p id="audioInfo"></p>
        </div>
        
        <div id="status"></div>
    </div>

    <script>
        // Update slider values
        document.getElementById('exaggeration').oninput = function() {
            document.getElementById('exaggerationValue').innerHTML = this.value;
        }
        document.getElementById('cfgWeight').oninput = function() {
            document.getElementById('cfgWeightValue').innerHTML = this.value;
        }
        document.getElementById('temperature').oninput = function() {
            document.getElementById('temperatureValue').innerHTML = this.value;
        }

        let currentAudioBlob = null;

        async function generateSpeech() {
            const text = document.getElementById('textInput').value;
            const exaggeration = parseFloat(document.getElementById('exaggeration').value);
            const cfgWeight = parseFloat(document.getElementById('cfgWeight').value);
            const temperature = parseFloat(document.getElementById('temperature').value);
            
            if (!text.trim()) {
                showStatus('Please enter some text.', 'error');
                return;
            }
            
            showStatus('Generating speech...', 'info');
            
            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        text: text,
                        exaggeration: exaggeration,
                        cfg_weight: cfgWeight,
                        temperature: temperature
                    })
                });
                
                if (response.ok) {
                    const audioBlob = await response.blob();
                    currentAudioBlob = audioBlob;
                    
                    const audioUrl = URL.createObjectURL(audioBlob);
                    const audioPlayer = document.getElementById('audioPlayer');
                    audioPlayer.src = audioUrl;
                    
                    // Show audio info
                    const duration = response.headers.get('X-Audio-Duration');
                    const sampleRate = response.headers.get('X-Sample-Rate');
                    document.getElementById('audioInfo').innerHTML = 
                        `Duration: ${duration}s | Sample Rate: ${sampleRate}Hz | Size: ${(audioBlob.size / 1024).toFixed(1)}KB`;
                    
                    document.getElementById('output').style.display = 'block';
                    document.getElementById('downloadBtn').style.display = 'inline-block';
                    showStatus('Speech generated successfully!', 'success');
                } else {
                    const error = await response.text();
                    showStatus(`Error: ${error}`, 'error');
                }
            } catch (error) {
                showStatus(`Error: ${error.message}`, 'error');
            }
        }

        function downloadAudio() {
            if (currentAudioBlob) {
                const url = URL.createObjectURL(currentAudioBlob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'generated_speech.wav';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            }
        }

        function showStatus(message, type) {
            const statusDiv = document.getElementById('status');
            statusDiv.innerHTML = `<p class="${type}">${message}</p>`;
            if (type !== 'info') {
                setTimeout(() => {
                    statusDiv.innerHTML = '';
                }, 5000);
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/health')
def health():
    """Check if the TTS API is available"""
    try:
        response = requests.get(f"{TTS_API_URL}/health", timeout=5)
        return jsonify({
            "api_available": response.status_code == 200,
            "api_status": response.json() if response.status_code == 200 else None
        })
    except Exception as e:
        return jsonify({
            "api_available": False,
            "error": str(e)
        }), 503

@app.route('/generate', methods=['POST'])
def generate_speech():
    """Generate speech from text using the TTS API"""
    try:
        data = request.get_json()
        
        # Validate input
        if not data or 'text' not in data:
            return jsonify({"error": "Text is required"}), 400
        
        # Prepare TTS request
        tts_request = {
            "text": data['text'],
            "exaggeration": data.get('exaggeration', 0.7),
            "cfg_weight": data.get('cfg_weight', 0.6),
            "temperature": data.get('temperature', 1.0),
            "return_base64": False  # Return binary audio
        }
        
        # Call TTS API
        response = requests.post(
            f"{TTS_API_URL}/tts",
            json=tts_request,
            timeout=30
        )
        
        if response.status_code == 200:
            # Return the audio file with metadata headers
            return response.content, 200, {
                'Content-Type': 'audio/wav',
                'X-Audio-Duration': response.headers.get('X-Audio-Duration', 'unknown'),
                'X-Sample-Rate': response.headers.get('X-Sample-Rate', 'unknown'),
                'X-Exaggeration': str(tts_request['exaggeration']),
                'X-CFG-Weight': str(tts_request['cfg_weight'])
            }
        else:
            return jsonify({"error": f"TTS API error: {response.text}"}), response.status_code
            
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/voice-clone', methods=['POST'])
def voice_clone():
    """Generate speech with voice cloning"""
    try:
        # Check if audio file was uploaded
        if 'audio_file' not in request.files:
            return jsonify({"error": "Audio file is required"}), 400
        
        audio_file = request.files['audio_file']
        text = request.form.get('text')
        
        if not text:
            return jsonify({"error": "Text is required"}), 400
        
        # Prepare the request for TTS API
        clone_data = {
            "text": text,
            "exaggeration": float(request.form.get('exaggeration', 0.6)),
            "cfg_weight": float(request.form.get('cfg_weight', 0.7)),
            "temperature": float(request.form.get('temperature', 0.9)),
            "return_base64": False
        }
        
        # Forward to TTS API
        response = requests.post(
            f"{TTS_API_URL}/voice-clone",
            data=clone_data,
            files={"audio_file": audio_file},
            timeout=60
        )
        
        if response.status_code == 200:
            return response.content, 200, {
                'Content-Type': 'audio/wav',
                'X-Audio-Duration': response.headers.get('X-Audio-Duration', 'unknown'),
                'X-Voice-Cloned': 'true'
            }
        else:
            return jsonify({"error": f"Voice cloning failed: {response.text}"}), response.status_code
            
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == '__main__':
    print("🌐 Starting Chatterbox TTS Web Demo")
    print("   Make sure the TTS API is running: docker-compose up -d")
    print("   Web interface will be available at: http://localhost:5000")
    print("   API health check: http://localhost:5000/health")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
