# GPU Config Enhancement for 16GB UMA Detection
# This file documents the changes made to ace-step/extracted/acestep/gpu_config.py
# to support AMD Radeon 780M 16GB UMA detection on Windows.

## Key Changes Made

### 1. DirectML Platform Detection
Added `is_directml_platform()` function to detect Windows with DirectML available.

### 2. Windows GPU Detection Priority
Moved Windows-specific detection to run BEFORE generic fallbacks:
1. WMI GPU detection (via `wmi` module)
2. WMIC GPU detection (fallback)
3. PowerShell Get-CimInstance (best for AMD iGPU)
4. Hostname-based detection (Beelink SER9)
5. AMD APU model matching (780M, 760M, 680M, etc.)
6. System RAM >= 16GB → assumes UMA

### 3. AMD APU Model Matching
Added detection for known AMD APU iGPU models with UMA support:
- 780M, 780 (Ryzen 7000/8000 series)
- 8040, 8050 (Ryzen 8000 series)
- 760M, 740M (Lower tier 7000 series)
- 680M, 660M (Ryzen 6000 series)

### 4. LM Memory Functions
Added `get_lm_model_size()` and `get_lm_gpu_memory_ratio()` for LM memory allocation:
- 0.6B model → 3GB target
- 1.7B model → 8GB target
- 4B model → 12GB target

### 5. 16GB UMA Detection Logic
The detection now correctly returns 16.0 GB for Radeon 780M:
1. PowerShell detects "AMD Radeon 780M Graphics" with 4GB AdapterRAM
2. Model matching finds "780M" in GPU name
3. Returns 16.0 GB (full UMA) instead of 4GB (dedicated VRAM)

## Verification
Run after changes:
```cmd
venv_rocm\Scripts\python -c "
from acestep.gpu_config import get_gpu_memory_gb, get_gpu_tier, get_gpu_config
mem = get_gpu_memory_gb()
print(f'GPU Memory: {mem:.1f} GB')
print(f'GPU Tier: {get_gpu_tier(mem)}')
config = get_gpu_config(mem)
print(f'Config: tier={config.tier}, batch={config.max_batch_size_with_lm}')
"
```

Expected output:
```
GPU Memory: 16.0 GB
GPU Tier: tier5
Config: tier=tier5, batch=4
```