#!/usr/bin/env python3
"""
Model Download Script for Chatterbox TTS API Docker Image

This script pre-downloads all required model files during Docker build
to create a self-contained image that doesn't need internet access at runtime.
"""

import os
import sys
import torch
from pathlib import Path

def download_models():
    """Download and cache all required models"""
    print("🔄 Pre-downloading Chatterbox TTS models...")
    print(f"📁 Cache directory: {os.environ.get('HF_HOME', 'default')}")
    
    try:
        # Import ChatterboxTTS to trigger model downloads
        from chatterbox import ChatterboxTTS
        
        print("📦 Initializing ChatterboxTTS model...")
        
        # Initialize the model - this will download all required files
        model = ChatterboxTTS()
        
        print("✅ ChatterboxTTS model downloaded successfully!")
        
        # Check if CUDA is available and log device info
        if torch.cuda.is_available():
            print(f"🚀 CUDA available: {torch.cuda.get_device_name(0)}")
            print(f"💾 CUDA memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB")
        else:
            print("💻 CUDA not available, will use CPU")
        
        # Get cache directory size
        cache_dir = Path(os.environ.get('HF_HOME', '~/.cache/huggingface')).expanduser()
        if cache_dir.exists():
            total_size = sum(f.stat().st_size for f in cache_dir.rglob('*') if f.is_file())
            print(f"📊 Model cache size: {total_size / 1024**3:.2f}GB")
        
        print("🎉 Model pre-download completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import ChatterboxTTS: {e}")
        print("⚠️  This might be expected if chatterbox-tts is not properly installed")
        return False
        
    except Exception as e:
        print(f"❌ Model download failed: {e}")
        print("⚠️  The image will still work, but models will be downloaded on first use")
        return False

def verify_models():
    """Verify that models were downloaded correctly"""
    print("🔍 Verifying downloaded models...")
    
    cache_dir = Path(os.environ.get('HF_HOME', '~/.cache/huggingface')).expanduser()
    
    if not cache_dir.exists():
        print("⚠️  Cache directory doesn't exist")
        return False
    
    # Check for common model files
    model_files = list(cache_dir.rglob('*.bin')) + list(cache_dir.rglob('*.safetensors'))
    config_files = list(cache_dir.rglob('config.json'))
    
    print(f"📁 Found {len(model_files)} model files")
    print(f"⚙️  Found {len(config_files)} config files")
    
    if model_files and config_files:
        print("✅ Model verification passed")
        return True
    else:
        print("⚠️  Model verification failed - some files may be missing")
        return False

def main():
    """Main function"""
    print("🐳 Chatterbox TTS Model Download Script")
    print("=" * 50)
    
    # Set up environment
    os.environ.setdefault('HF_HOME', '/app/hf_cache')
    
    # Download models
    download_success = download_models()
    
    # Verify models
    if download_success:
        verify_models()
    
    print("=" * 50)
    
    if download_success:
        print("🎯 Model pre-download completed - image is ready!")
    else:
        print("⚠️  Model pre-download had issues - models will download at runtime")
    
    # Don't fail the Docker build even if model download fails
    # This ensures the image can still be built and used
    sys.exit(0)

if __name__ == "__main__":
    main()
