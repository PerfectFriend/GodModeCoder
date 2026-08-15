#!/usr/bin/env python3
"""
ACE-Step ROCm GPU Verification Script
Verifies ROCm 7.2 installation and GPU detection for AMD iGPU (Radeon 780M).
Run after completing ROCm setup to confirm GPU is accessible.
"""

import sys
import os

def verify_rocm():
    """Verify ROCm 7.2 installation and GPU detection."""
    print("=" * 60)
    print("ACE-Step ROCm 7.2 GPU Verification")
    print("=" * 60)
    
    # Check Python version
    print(f"\nPython: {sys.version}")
    
    # Check torch
    try:
        import torch
        print(f"\nPyTorch: {torch.__version__}")
        
        # Check CUDA/ROCm availability
        cuda_available = torch.cuda.is_available()
        print(f"CUDA/ROCm available: {cuda_available}")
        
        if cuda_available:
            device_name = torch.cuda.get_device_name(0)
            print(f"Device: 
            print(f"  Name: {device_name}")
            
            props = torch.cuda.get_device_properties(0)
            print(f"  VRAM: {props.total_memory / 1e9:.2f} GB")
            print(f"  Compute Capability: {props.major}.{props.minor}")
            
            # Check HIP version
            hip_version = getattr(torch.version, 'hip', None)
            print(f"  HIP version: {hip_version}")
            
            # Simple GPU compute test
            print("\nRunning GPU compute test...")
            x = torch.randn(100, 100, device='cuda')
            y = torch.matmul(x, x.t())
            print(f"  Matrix multiplication: OK (result shape: {y.shape})")
            
            # Test bfloat16
            x_bf16 = torch.randn(100, 100, device='cuda', dtype=torch.bfloat16)
            y_bf16 = torch.matmul(x_bf16, x_bf16.t())
            print(f"  bfloat16 matmul: OK")
            
            return True
        else:
            print("  ERROR: CUDA/ROCm not available!")
            print("  Check HSA_OVERRIDE_GFX_VERSION and AMD driver")
            return False
            
    except Exception as e:
        print(f"  ERROR: {e}")
        return False
    
    # Check transformers version compatibility
    try:
        import transformers
        print(f"\nTransformers: {transformers.__version__}")
        
        import tokenizers
        print(f"Tokenizers: {tokenizers.__version__}")
        
        # Check tokenizers version compatibility
        from packaging import version
        tok_version = version.parse(tokenizers.__version__)
        if version.parse("0.22.0") <= tok_version <= version.parse("0.23.0"):
            print("  Tokenizers version: OK (compatible with transformers)")
        else:
            print(f"  WARNING: Tokenizers {tokenizers.__version__} may be incompatible")
            print("  Expected: >=0.22.0, <=0.23.0")
            
    except Exception as e:
        print(f"  Transformers check failed: {e}")

    print("\n" + "=" * 60)
    return False


if __name__ == "__main__":
    # Set environment variables for ROCm
    os.environ.setdefault('HSA_OVERRIDE_GFX_VERSION', '11.0.2')
    os.environ.setdefault('MIOPEN_FIND_MODE', 'FAST')
    os.environ.setdefault('TORCH_COMPILE_BACKEND', 'eager')
    
    success = verify_rocm()
    
    if success:
        print("\n✅ GPU verification PASSED - Ready for ACE-Step inference")
        sys.exit(0)
    else:
        print("\n❌ GPU verification FAILED - Check configuration")
        sys.exit(1)