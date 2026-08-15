# ACE-Step ROCm Windows - Quick Verification Commands

## Verify ROCm Installation
```cmd
venv_rocm\Scripts\python -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0)); print('HIP:', torch.version.hip)"
```

## Verify GPU Memory Detection
```cmd
venv_rocm\Scripts\python -c "
from acestep.gpu_config import get_gpu_memory_gb, get_gpu_tier, get_gpu_config
mem = get_gpu_memory_gb()
print(f'GPU Memory: {mem:.1f} GB')
tier = get_gpu_tier(mem)
print(f'GPU Tier: {tier}')
config = get_gpu_config(mem)
print(f'Config: tier={config.tier}')
print(f'  Max duration with LM: {config.max_duration_with_lm}s')
print(f'  Max batch with LM: {config.max_batch_size_with_lm}')
print(f'  Recommended LM: {config.recommended_lm_model}')
print(f'  Offload CPU: {config.offload_to_cpu_default}')
print(f'  Quantization: {config.quantization_default}')
"
```

## Verify Tokenizers Version
```cmd
venv_rocm\Scripts\python -c "import tokenizers; print('Tokenizers:', tokenizers.__version__)"
```

## Test Generation (10s jingle)
```cmd
venv_rocm\Scripts\python -c "
import os
os.environ['ACESTEP_DEVICE'] = 'auto'
os.environ['ACESTEP_LM_BACKEND'] = 'pt'
os.environ['ACESTEP_INIT_LLM'] = 'true'

from acestep.api_server import main
# Note: This starts the API server. For single generation, use CLI instead.
"

# Or use CLI:
venv_rocm\Scripts\python -m acestep.cli -c scripts/gen_jingle.toml
```

## Expected Outputs
```
GPU Memory: 16.0 GB
GPU Tier: tier5
Config: tier=tier5
  Max duration with LM: 480s
  Max batch with LM: 4
  Recommended LM: acestep-5Hz-lm-1.7B
  Offload CPU: True
  Quantization: True
```