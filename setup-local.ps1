# Local Development Setup Script
# Run this to install all dependencies including CUDA-enabled PyTorch

# Activate your virtual environment first:
# .\venv\Scripts\Activate.ps1

Write-Host "Installing CUDA-enabled PyTorch..." -ForegroundColor Green
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121

Write-Host "Installing other dependencies..." -ForegroundColor Green  
pip install -r requirements.txt

Write-Host "Testing GPU availability..." -ForegroundColor Green
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda}'); print(f'Device count: {torch.cuda.device_count()}')"

Write-Host "Setup complete!" -ForegroundColor Green
