# Optimized Dockerfile using pre-built PyTorch image for faster builds
FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install only the additional packages we need (PyTorch already included)
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    python-multipart \
    chatterbox-tts

# Set up model cache directory
# Models will be downloaded on first run and cached for subsequent uses
ENV HF_HOME=/app/hf_cache
RUN mkdir -p /app/hf_cache

# Optional: Pre-download models during build (uncomment for self-contained image)
# COPY download_models.py .
# RUN python download_models.py

# Copy application code
COPY app.py .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
