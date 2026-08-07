#!/usr/bin/env python3
"""
Auto-detect GPU configuration for ACE-Step inference.
Returns appropriate config dict for current hardware.
"""

import sys
import os
from pathlib import Path

def get_inference_config():
    """
    Auto-detect GPU and return appropriate ACE-Step config.
    
    Priority order:
    1. ROCm (Windows/Linux) - best performance
    2. DirectML (Windows) - fallback
    3. CPU - always works
    """
    import torch
    
    # ROCm detection (Windows/Linux)
    if torch.cuda.is_available():
        hip_version = getattr(torch.version, 'hip', None)
        if hip_version:
            return {
                "device": "cuda",
                "backend": "pt",
                "config_path": "acestep-v15-turbo",
                "lm_backend": "pt",
                "offload_to_cpu": False,
                "batch_size": 4,
                "init_llm": True,
                "quantization": "int8_weight_only",
            }
    
    # DirectML detection (Windows)
    try:
        import torch_directml
        if torch_directml.is_available():
            return {
                "device": "directml",
                "backend": "pt",
                "config_path": "acestep-v15-turbo",
                "lm_backend": "pt",
                "offload_to_cpu": False,
                "batch_size": 2,
                "init_llm": True,
                "quantization": "none",
            }
    except ImportError:
        pass
    
    # CPU fallback
    return {
        "device": "cpu",
        "backend": "pt",
        "config_path": "acestep-v15-turbo",
        "lm_backend": "pt",
        "offload_to_cpu": True,
        "batch_size": 1,
        "init_llm": False,
        "quantization": "none",
    }

if __name__ == "__main__":
    config = get_inference_config()
    import json
    print(json.dumps(config, indent=2))