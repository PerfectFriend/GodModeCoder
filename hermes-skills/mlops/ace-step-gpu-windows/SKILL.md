---
name: ace-step-gpu-windows
description: "Setup ACE-Step GPU on AMD iGPU via ROCm 7.2 or DirectML."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [ace-step, music-generation, amd, rocm, directml, gpu, inference, radeon-780m, rdna3]
---

## ACE-Step GPU Inference on Windows (AMD iGPU)

Complete workflow for running ACE-Step 1.5 music generation on AMD Radeon integrated graphics (RDNA3, e.g., Radeon 780M) using Windows ROCm 7.2 or Microsoft DirectML fallback.

## Trigger

- User wants ACE-Step GPU acceleration on AMD iGPU (Radeon 780M / RDNA3)
- Current CPU inference too slow (3-5 min/track → target 10-15 sec/track)
- Need 16GB UMA VRAM utilization for batch generation and LoRA training

## Key Enhancements (2026-08-05)

### GPU Detection for 16GB UMA
- **PowerShell + AMD model matching** detects 780M/760M/680M/8040/8050 models
- Returns **16.0 GB** even though Windows reports only 4GB dedicated VRAM
- Falls back to generic AMD APU UMA detection (≥16GB system RAM)
- Works without `wmi` module (uses PowerShell `Get-CimInstance`)

### LM Memory Functions (added to `acestep/gpu_config.py`)
```python
def get_lm_model_size(model_path: str) -> str:
    """Extract LM model size from path: 'acestep-5Hz-lm-0.6B' → '0.6B'"""
    
def get_lm_gpu_memory_ratio(model_path: str, total_gpu_gb: float) -> Tuple[float, float]:
    """Returns (ratio, target_memory_gb) for adaptive LM allocation:
    - 0.6B → 3 GB target
    - 1.7B → 8 GB target 
    - 4B → 12 GB target
    """
```

### GPU Tier System
16GB UMA = **tier5** (12-16GB):
- `max_batch_size_with_lm`: 4
- `max_duration_with_lm`: 480s (8 min)
- `recommended_lm_model`: `acestep-5Hz-lm-1.7B`
- `offload_to_cpu_default`: true (VAE/TextEnc)
- `quantization_default`: true (INT8)

### DirectML Detection
```python
def is_directml_platform() -> bool:
    if sys.platform != "win32": return False
    try:
        import torch, torch_directml
        return torch_directml.is_available()
    except Exception: return False
```

## Hardware Context

| Component | Spec |
|-----------|------|
| **GPU** | Radeon 780M (RDNA3, integrated) |
| **VRAM** | 16 GB UMA (BIOS: UMA Frame Buffer = 16GB) |
| **OS** | Windows 11 |
| **Driver** | AMD Adrenalin 26.1.1+ |
| **Python** | 3.12.x required for ROCm |

---

## Path A: ROCm 7.2 (Native AMD, Recommended)

### Prerequisites
```powershell
# 1. Python 3.12 (REQUIRED - ROCm 7.2 only provides Python 3.12 wheels)
winget install Python.Python.3.12

# 2. AMD Adrenalin driver 26.1.1+
# Download from: https://www.amd.com/en/support
```

### Installation

```powershell
# 1. Create dedicated venv (don't mix with CPU venv!)
python3.12 -m venv C:\Users\tomas\ace-step\extracted\venv_rocm
call C:\Users\tomas\ace-step\extracted\venv_rocm\Scripts\activate.bat

# 2. ROCm PyTorch (821 MB)
pip install --no-cache-dir https://repo.radeon.com/rocm/windows/rocm-rel-7.2/torch-2.9.1+rocmsdk20260116-cp312-cp312-win_amd64.whl

# 3. ROCm SDK components
pip install --no-cache-dir ^
  https://repo.radeon.com/rocm/windows/rocm-rel-7.2/rocm_sdk_core-7.2.0.dev0-py3-none-win_amd64.whl ^
  https://repo.radeon.com/rocm/windows/rocm-rel-7.2/rocm_sdk_devel-7.2.0.dev0-py3-none-win_amd64.whl ^
  https://repo.radeon.com/rocm/windows/rocm-rel-7.2/rocm_sdk_libraries_custom-7.2.0.dev0-py3-none-win_amd64.whl

# 4. ACE-Step dependencies for ROCm
pip install -r requirements-rocm.txt

# 5. Install ACE-Step in editable mode
pip install -e .
```

### Environment Variables (.env.rocm)

Create `C:\Users\tomas\ace-step\extracted\.env.rocm`:

```bash
# Model config
ACESTEP_DEVICE=auto
ACESTEP_CONFIG_PATH=acestep-v15-turbo
ACESTEP_LM_MODEL_PATH=acestep-5Hz-lm-1.7B
ACESTEP_LM_BACKEND=pt              # vllm NOT available on ROCm Windows
ACESTEP_INIT_LLM=true
ACESTEP_DOWNLOAD_SOURCE=auto

# ROCm specifics for RDNA3 (Radeon 780M = gfx1102)
HSA_OVERRIDE_GFX_VERSION=11.0.1
MIOPEN_FIND_MODE=FAST
TORCH_COMPILE_BACKEND=eager
TOKENIZERS_PARALLELISM=false
PYTORCH_HIP_ALLOC_CONF=garbage_collection_threshold:0.6,max_split_size_mb:128
```

### Launch

```bat
REM Use the ROCm launcher (sets all env vars automatically)
start_gradio_ui_rocm.bat

REM Or API server:
start_api_server_rocm.bat

REM Or direct python:
python -m acestep.acestep_v15_pipeline --port 7860
```

---

## Path B: DirectML (Microsoft Fallback, Easier)

**Use when ROCm fails or for quick testing.** Works with Python 3.11 (current CPU venv).

### Prerequisites
```powershell
# Python 3.11 embedded (already in ace-step/extracted/python_embeded)
# Install pip if missing
curl -s https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python_embeded\python.exe get-pip.py
```

### Installation

```powershell
# In python_embeded venv:
python_embeded\Scripts\pip.exe install torch-directml

# This installs: torch 2.4.1+cpu, torchvision 0.19.1, torch-directml 0.2.5
# Note: Incompatible with ace-step's CUDA torch 2.7.1+cu128 requirement
```

### ACE-Step Adaptation for DirectML

**ACE-Step doesn't natively support DirectML.** Need to patch `gpu_config.py` and `handler.py`:

#### 1. Patch `acestep/gpu_config.py` - Add DirectML detection

```python
# In get_gpu_memory_gb(), add after XPU check:
elif hasattr(torch, 'directml') and torch.directml.is_available():
    # DirectML on Windows - estimate from system RAM
    # DirectML uses system RAM as unified memory
    try:
        import psutil
        total_ram_gb = psutil.virtual_memory().total / (1024**3)
        # Conservative: assume 50% available for GPU workloads
        return total_ram_gb * 0.5
    except Exception:
        return 16.0  # Fallback for 780M 16GB UMA
```

#### 2. Patch `acestep/handler.py` - Add DirectML device support

```python
# In initialize_service(), add after XPU check:
elif device == "directml":
    try:
        import torch_directml
        self.device = torch_directml.device()
        self.dtype = torch.float32  # DirectML prefers fp32
        logger.info(f"[initialize_service] DirectML device: {self.device}")
    except ImportError:
        logger.warning("DirectML requested but torch_directml not installed. Falling back to CPU.")
        self.device = "cpu"
        self.dtype = torch.float32
```

#### 3. Update launch scripts

Create `start_gradio_ui_dml.bat`:
```bat
@echo off
set ACESTEP_DEVICE=directml
set ACESTEP_LM_BACKEND=pt
set ACESTEP_CONFIG_PATH=acestep-v15-turbo
set ACESTEP_LM_MODEL_PATH=acestep-5Hz-lm-1.7B
set ACESTEP_INIT_LLM=true

call python_embeded\Scripts\activate.bat
python -u acestep\acestep_v15_pipeline.py --port 7860 --device directml
pause
```

---

## Performance Comparison

| Metric | CPU (current) | ROCm 7.2 (target) | DirectML (est.) |
|--------|---------------|-------------------|-----------------|
| **Turbo 120s** | 180-300 sec | **8-15 sec** | ~30-60 sec |
| **Turbo 180s** | 270-450 sec | **12-20 sec** | ~45-90 sec |
| **LM inference** | 30-60 sec | **2-4 sec** | ~10-20 sec |
| **Batch size** | 1 | **4-8** | 2-4 |
| **Max duration** | 8 min | **10 min** | 8 min |
| **LoRA training** | ❌ | ✅ (16GB min) | ⚠️ Maybe |
| **Python version** | 3.11 | **3.12 required** | 3.11 OK |

---

## GPU Tier for 16GB UMA

ACE-Step classifies 16GB as **tier6a** (16-20GB):

```python
# From gpu_config.py GPU_TIER_CONFIGS["tier6a"]:
{
    "max_duration_with_lm": 480,      # 8 minutes
    "max_duration_without_lm": 600,   # 10 minutes
    "max_batch_size_with_lm": 4,
    "max_batch_size_without_lm": 8,
    "init_lm_default": true,
    "available_lm_models": ["acestep-5Hz-lm-0.6B", "acestep-5Hz-lm-1.7B"],
    "recommended_lm_model": "acestep-5Hz-lm-1.7B",
    "lm_backend_restriction": "all",
    "recommended_backend": "vllm",    # ROCm: use "pt" instead
    "offload_to_cpu_default": true,
    "offload_dit_to_cpu_default": false,
    "quantization_default": true,     # INT8 to fit in 16GB
    "compile_model_default": true,
    "lm_memory_gb": {"0.6B": 3, "1.7B": 8},
}
```

---

## Troubleshooting

### ROCm: "GPU NOT DETECTED"

```powershell
# 1. Check HSA_OVERRIDE_GFX_VERSION for your GPU:
# RX 7900 XT/XTX, RX 9070 XT: 11.0.0
# RX 7800 XT, RX 7700 XT:      11.0.1  ← Radeon 780M
# RX 7600:                       11.0.2

# 2. Verify ROCm installation:
rocm-smi

# 3. Check PyTorch ROCm build:
python -c "import torch; print(f'ROCm: {torch.version.hip}')"

# 4. Windows: Use start_gradio_ui_rocm.bat which sets required env vars
```

### ROCm: MIOPEN Errors / Slow First Run

```powershell
# MIOPEN_FIND_MODE=FAST disables exhaustive kernel benchmarking
# Without this, first-run VAE decode hangs for minutes on each conv layer
set MIOPEN_FIND_MODE=FAST
```

### ROCm: OOM on 16GB

```python
# Enable quantization (INT8) and CPU offload
offload_to_cpu_default: true
quantization_default: true  # INT8 essential for 16GB
```

### DirectML: Slow / OOM

```python
# DirectML uses system RAM - limit batch size
batch_size = 2
# Use float32 (DirectML fp16 support limited)
dtype = torch.float32
```

---

## Key Learnings (2026-08-05 Session)

### Working Generation Path: Gradio UI
- **Gradio UI (http://127.0.0.1:7860) is the ONLY working generation path** on Windows ROCm 7.2
- CLI generation (`python cli.py -c config.toml`) fails due to **transformers version conflict**:
  - `transformers 4.48.3`: Works for Gradio UI but **lacks `layer_type_validation`** needed for model config loading
  - `transformers 4.50+`: Has `layer_type_validation` but **imports FSDP** (`torch.distributed.tensor`) which is **missing in ROCm Windows build** → `ModuleNotFoundError: torch._C._distributed_c10d`
- **Solution**: Use Gradio Web UI for all generation tasks

### Environment Isolation Critical
- **Hermes venv (Python 3.11) site-packages MUST be cleaned** to avoid conflicts with `venv_rocm` (Python 3.12)
- Key packages to remove from Hermes venv: `numpy`, `torch*`, `transformers*`, `tokenizers*`, `diffusers*`, `huggingface*`, `gradio*`, `fastapi*`, `pydantic*`, `scipy*`, `PIL*`, `bitsandbytes*`, `lycoris_lora*`
- Use `acectl free-gpu` to force GPU memory cleanup (calls `EmptyWorkingSet` on Windows)

### Transformers Version Deadlock
- **No single transformers version works for both Gradio and CLI** on ROCm Windows:
  - `4.48.3`: Works for Gradio UI (no FSDP import), but ACE-Step model config requires `layer_type_validation` (added in 4.50+)
  - `4.50+`: Has `layer_type_validation`, but imports FSDP → fails on ROCm Windows (no `torch._C._distributed_c10d`)
- **Current workaround**: Use Gradio UI with transformers 4.48.3; CLI generation not available

### Service Management Tools Created
- **CLI**: `acectl.py` + `acectl.bat` (start/stop/status/free-gpu/config for API & Gradio)
- **GUI**: `acectl_gui.py` + `acectl_gui.bat` (real-time GPU monitoring, config editor, log viewer)
- **Desktop Shortcut**: `ACE-Step Control.lnk` on Desktop launches GUI
- **Config**: `disco_config.toml` for Yellow Submarine disco track (30s, shift=3.0, steps=8, cfg=7.0)

### GPU Tier for 16GB UMA (Updated)
- 16GB UMA = **tier5** (12-16GB) per updated `gpu_config.py`:
  - `max_batch_size_with_lm`: 4
  - `max_duration_with_lm`: 480s (8 min)
  - `available_lm_models`: 0.6B, 1.7B
  - `recommended_lm_model`: 1.7B
  - `offload_to_cpu_default`: true
  - `quantization_default`: true (INT8)

---

## Integration with AI Radio

### Switching CPU ↔ GPU in gen_music.py

```python
def get_inference_config():
    import torch
    import os
    
    # ROCm detection
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
            }
    
    # DirectML detection
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
    }
```

### API Server for Remote Generation

```powershell
# On GPU machine (WSL2 or Windows ROCm):
python -m acestep.api_server --port 8001 --host 0.0.0.0

# On Windows AI Radio machine:
# gen_music.py uses requests.post to http://localhost:8001/release_task
```

---

## References

- [ACE-Step ROCm Windows Setup](https://github.com/ACE-Step/ACE-Step-1.5/blob/main/requirements-rocm.txt)
- [AMD ROCm 7.2 Windows](https://repo.radeon.com/rocm/windows/rocm-rel-7.2/)
- [DirectML PyTorch](https://github.com/microsoft/DirectML/tree/main/pytorch)
- [ACE-Step GPU Compatibility](https://github.com/ACE-Step/ACE-Step-1.5/blob/main/docs/en/GPU_COMPATIBILITY.md)

---

## Templates

- `templates/env.rocm` — `.env` file for ROCm 7.2
- `templates/start_gradio_ui_dml.bat` — DirectML launcher
- `scripts/get_inference_config.py` — Auto-detect GPU config