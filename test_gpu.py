# Test script to verify GPU support in Docker
import torch
import sys

print("=== Docker GPU Test ===")
print(f"Python version: {sys.version}")
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"CUDA version: {torch.version.cuda}")
    print(f"cuDNN version: {torch.backends.cudnn.version()}")
    print(f"Device count: {torch.cuda.device_count()}")
    print(f"Current device: {torch.cuda.current_device()}")
    print(f"Device name: {torch.cuda.get_device_name(0)}")
    
    # Test tensor creation on GPU
    try:
        x = torch.randn(3, 3).cuda()
        print(f"GPU tensor test successful: {x.device}")
    except Exception as e:
        print(f"GPU tensor test failed: {e}")
else:
    print("❌ CUDA not available - check Docker GPU setup")
    
print("=== End Test ===")
