#!/usr/bin/env python3
"""
Basic API tests for Chatterbox TTS API
"""

import pytest
import requests
import time
from pathlib import Path

# Test configuration
API_BASE_URL = "http://localhost:8000"
TIMEOUT = 30

class TestAPI:
    """Basic API functionality tests"""
    
    def test_health_check(self):
        """Test basic health check endpoint"""
        response = requests.get(f"{API_BASE_URL}/", timeout=TIMEOUT)
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "device" in data
    
    def test_detailed_health_check(self):
        """Test detailed health check endpoint"""
        response = requests.get(f"{API_BASE_URL}/health", timeout=TIMEOUT)
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "unhealthy"]
    
    def test_queue_status(self):
        """Test queue status endpoint"""
        response = requests.get(f"{API_BASE_URL}/queue/status", timeout=TIMEOUT)
        assert response.status_code == 200
        
        data = response.json()
        assert "queue_size" in data
        assert "total_jobs_processed" in data
        assert isinstance(data["queue_size"], int)
        assert isinstance(data["total_jobs_processed"], int)

class TestTTS:
    """TTS functionality tests"""
    
    def test_basic_tts_wav(self):
        """Test basic TTS generation with WAV output"""
        request_data = {
            "text": "Hello, this is a test.",
            "exaggeration": 0.5,
            "cfg_weight": 0.5,
            "temperature": 1.0,
            "output_format": "wav",
            "return_base64": False
        }
        
        response = requests.post(
            f"{API_BASE_URL}/tts",
            json=request_data,
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        assert response.headers.get("Content-Type") == "audio/wav"
        assert len(response.content) > 1000  # Should have audio data
    
    def test_basic_tts_mp3(self):
        """Test basic TTS generation with MP3 output"""
        request_data = {
            "text": "Hello, this is an MP3 test.",
            "output_format": "mp3",
            "return_base64": False
        }
        
        response = requests.post(
            f"{API_BASE_URL}/tts",
            json=request_data,
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        assert response.headers.get("Content-Type") == "audio/mpeg"
        assert len(response.content) > 1000  # Should have audio data
    
    def test_base64_tts(self):
        """Test TTS with base64 output"""
        request_data = {
            "text": "Hello, this is a base64 test.",
            "return_base64": True
        }
        
        response = requests.post(
            f"{API_BASE_URL}/tts",
            json=request_data,
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "audio_base64" in data
        assert "duration_seconds" in data
        assert "sample_rate" in data
        assert len(data["audio_base64"]) > 1000  # Should have base64 data

class TestBatchTTS:
    """Batch TTS functionality tests"""
    
    def test_batch_processing(self):
        """Test batch TTS processing"""
        request_data = {
            "texts": [
                "First test sentence.",
                "Second test sentence.",
                "Third test sentence."
            ],
            "exaggeration": 0.5,
            "cfg_weight": 0.5,
            "temperature": 1.0
        }
        
        response = requests.post(
            f"{API_BASE_URL}/batch-tts",
            json=request_data,
            timeout=60  # Longer timeout for batch
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "results" in data
        assert len(data["results"]) == 3
        assert "total_duration" in data
        
        # Check each result
        for result in data["results"]:
            assert result["success"] is True
            assert "audio_base64" in result
            assert "duration_seconds" in result

class TestValidation:
    """Input validation tests"""
    
    def test_empty_text(self):
        """Test validation with empty text"""
        request_data = {
            "text": "",
            "return_base64": True
        }
        
        response = requests.post(
            f"{API_BASE_URL}/tts",
            json=request_data,
            timeout=TIMEOUT
        )
        
        # Should return validation error
        assert response.status_code == 422
    
    def test_invalid_parameters(self):
        """Test validation with invalid parameters"""
        request_data = {
            "text": "Test text",
            "exaggeration": 5.0,  # Out of range
            "cfg_weight": -1.0,   # Out of range
            "temperature": 0.0,   # Out of range
            "return_base64": True
        }
        
        response = requests.post(
            f"{API_BASE_URL}/tts",
            json=request_data,
            timeout=TIMEOUT
        )
        
        # Should return validation error
        assert response.status_code == 422
    
    def test_invalid_output_format(self):
        """Test validation with invalid output format"""
        request_data = {
            "text": "Test text",
            "output_format": "invalid",
            "return_base64": False
        }
        
        response = requests.post(
            f"{API_BASE_URL}/tts",
            json=request_data,
            timeout=TIMEOUT
        )
        
        # Should return validation error
        assert response.status_code == 422

if __name__ == "__main__":
    # Run basic smoke test
    print("Running basic smoke test...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ API is responding")
        else:
            print(f"❌ API returned status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API: {e}")
        print("Make sure to run: docker-compose up -d")
