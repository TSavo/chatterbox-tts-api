#!/usr/bin/env python3
"""
Pytest configuration for Chatterbox TTS API tests
"""

import pytest
import requests
import time
import subprocess
import os
from pathlib import Path

# Test configuration
API_BASE_URL = "http://localhost:8000"
DOCKER_COMPOSE_FILE = "docker-compose.yml"

@pytest.fixture(scope="session")
def api_server():
    """
    Start the API server for testing if not already running
    """
    # Check if API is already running
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("API is already running")
            yield API_BASE_URL
            return
    except requests.exceptions.RequestException:
        pass
    
    # Start the API using docker-compose
    print("Starting API server with docker-compose...")
    
    # Check if docker-compose file exists
    if not Path(DOCKER_COMPOSE_FILE).exists():
        pytest.skip(f"Docker compose file {DOCKER_COMPOSE_FILE} not found")
    
    # Start the service
    try:
        subprocess.run(
            ["docker-compose", "up", "-d"],
            check=True,
            capture_output=True,
            text=True
        )
        
        # Wait for the service to be ready
        max_wait = 60  # seconds
        wait_interval = 2
        
        for _ in range(max_wait // wait_interval):
            try:
                response = requests.get(f"{API_BASE_URL}/", timeout=5)
                if response.status_code == 200:
                    print("API server is ready")
                    break
            except requests.exceptions.RequestException:
                pass
            time.sleep(wait_interval)
        else:
            pytest.fail("API server failed to start within timeout")
        
        yield API_BASE_URL
        
    except subprocess.CalledProcessError as e:
        pytest.skip(f"Failed to start docker-compose: {e}")
    
    finally:
        # Cleanup: stop the service
        try:
            subprocess.run(
                ["docker-compose", "down"],
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError:
            pass  # Ignore cleanup errors

@pytest.fixture
def sample_audio_file():
    """
    Create a sample audio file for testing voice cloning
    """
    # For now, return None - in a real test, you'd generate or provide a sample file
    return None

def pytest_configure(config):
    """
    Configure pytest with custom markers
    """
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )

def pytest_collection_modifyitems(config, items):
    """
    Automatically mark tests based on their names
    """
    for item in items:
        # Mark slow tests
        if "batch" in item.name or "voice_clone" in item.name:
            item.add_marker(pytest.mark.slow)
        
        # Mark integration tests
        if any(keyword in item.name for keyword in ["api", "endpoint", "integration"]):
            item.add_marker(pytest.mark.integration)
        
        # Mark unit tests
        if any(keyword in item.name for keyword in ["unit", "validation", "parse"]):
            item.add_marker(pytest.mark.unit)
