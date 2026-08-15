---
name: ace-step-rocm-windows
description: Use when setting up ACE-Step on Windows ROCm for AMD iGPU.
trigger: Setting up ACE-Step on Windows ROCm for AMD iGPU.
version: "1.0"
tags: [ace-step, rocm, windows, amd, igpu, inference, 780M]
---

# ACE-Step ROCm 7.2 on Windows (AMD iGPU)

## Overview
Complete workflow for running ACE-Step 1.5 inference on AMD Radeon 780M (RDNA3, gfx1102) with 16GB UMA using Windows ROCm 7.2. Python 3.12 mandatory.

## Prerequisites
- Windows 11, AMD driver 26.1.1+
- Python 3.12 installed (AMD only provides cp312 wheels for ROCm 7.2)
- 16GB+ system RAM (8GB reserved for UMA via BIOS)

## Step 1: Create Isolated ROCm Venv
```bash
cd C:\Users\tomas\ace-step\extracted
python3.12 -m venv venv_rocm
# CRITICAL: Must isolate from Hermes venv (sys.path conflict)
# Hermes injects its site-packages at index 2 in sys.path
```

## Step 2: Install ROCm SDK Components (~2.5GB, 15+ min)
```cmd
venv_rocm\Scripts\pip install --no-cache-dir ^
  https://repo.radeon.com/rocm/windows/rocm-rel-7.2/rocm_sdk_core-7.2.0.dev0-py3-none-win_amd64.whl ^
  https://repo.radeon.com/rocm/windows/rocm-rel-7.2/rocm_sdk_devel-7.2.0.dev0-py3-none-win_amd64.whl ^
  https://repo.radeon.com/rocm/windows/rocm-rel-7.2/rocm_sdk_libraries_custom-7.2.0.dev0-py3-none-win_amd64.whl ^
  https://repo.radeon.com/rocm/windows/rocm-rel-7.2/rocm-7.2.0.dev0.tar.gz
```

## Step 3: Replace CPU Torch with ROCm PyTorch
```cmd
venv_rocm\Scripts\pip uninstall -y torch torchvision torchaudio torch-directml
venv_rocm\Scripts\pip install --no-cache-dir ^
  https://repo.radeon.com/rocm/windows/rocm-rel-7.2/torch-2.9.1+rocmsdk20260116-cp312-cp312-win_amd64.whl ^
  https://repo.radeon.com/rocm/windows/rocm-rel-7.2/torchaudio-2.9.1+rocmsdk20260116-cp312-cp312-win_amd64.whl ^
  https://repo.radeon.com/rocm/windows/rocm-rel-7.2/torchvision-0.24.1+rocmsdk20260116-cp312-cp312-win_amd64.whl
```

## Step 4: Install ACE-Step Dependencies
```cmd
venv_rocm\Scripts\pip install -r requirements-rocm.txt
venv_rocm\Scripts\pip install -e . --no-deps
```

## Step 5: Configure .env for Radeon 780M (gfx1102)
```ini
# ACE-Step Environment Configuration (ROCm 7.2 Windows)
ACESTEP_CONFIG_PATH=acestep-v15-turbo
ACESTEP_LM_MODEL_PATH=acestep-5Hz-lm-1.7B
ACESTEP_DEVICE=auto
ACESTEP_LM_BACKEND=pt          # vllm not available on Windows ROCm
ACESTEP_INIT_LLM=auto

# RDNA3 gfx1102 override (RX 7600/780M = 11.0.2, RX 7800 XT = 11.0.1, RX 7900 = 11.0.0)
HSA_OVERRIDE_GFX_VERSION=11.0.2

TORCH_COMPILE_BACKEND=eager
MIOPEN_FIND_MODE=FAST
TOKENIZERS_PARALLELISM=false
```

## Step 6: Verify GPU Detection
```cmd
venv_rocm\Scripts\python -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0)); print(torch.version.hip)"
# Expected: True / AMD Radeon 780M Graphics / 7.2.x
```

## Step 7: Launch API Server
```cmd
start_api_server_rocm.bat
# API at http://127.0.0.1:8001
```

## GPU Detection Logic (16GB UMA)
The `acestep.gpu_config.get_gpu_memory_gb()` detects 16GB UMA via:
1. PowerShell `Get-CimInstance Win32_VideoController` → AdapterRAM (4GB dedicated)
2. AMD model matching: `780M`, `780`, `760M`, `740M`, `680M`, `660M` → assumes 16GB UMA
3. System RAM >= 16GB → confirms UMA configuration

## Critical Pitfalls
| Issue | Fix |
|-------|-----|
| WSL2 ROCm | **Does not work** for iGPU — dxgkrnl only exposes DirectML, not HIP/ROCm |
| DirectML | Segfault with ACE-Step (torch 2.4.1 vs 2.7.1+ required) |
| Hermes venv conflict | Clean `transformers`, `tokenizers`, `huggingface_hub` from `C:\Users\<user>\AppData\Local\hermes\hermes-agent\venv\Lib\site-packages` |
| tokenizers version | transformers 4.51-4.57 requires `tokenizers>=0.22.0,<=0.23.0` — pin 0.22.2 |
| CPU torch in venv_rocm | Must uninstall CPU torch before installing ROCm wheels |

## Performance Expectations (16GB UMA, RDNA3 780M)
| Task | CPU (current) | GPU ROCm (target) |
|------|---------------|-------------------|
| 10s jingle | ~180s | **~8-15s** |
| 180s track | ~300s+ | **~20-40s** |
| Batch 4 | OOM / too slow | **~60-120s** |

## References
- `references/rocm-plan.md` — Complete step-by-step plan with troubleshooting
- `references/control-application.md` — CLI + Desktop GUI control application (acectl/acectl_gui)
- `templates/.env.rocm` — Ready-to-use .env template
- `scripts/verify_rocm.py` — GPU verification script

## Files Created in This Session
- `ai-radio/docs/ROCM-PLAN.md` — Complete installation plan
- `ai-radio/docs/AI-RADIO-WORKFLOW.md` — Full workflow with presets
- `ai-radio/scripts/gen_music.py` — Preset-driven generation
- `ai-radio/scripts/gen_voice_content.py` — Emotional voice presets
- `ace-step/extracted/acestep/gpu_config.py` — Enhanced 16GB UMA detection
- `ace-step/acectl.py` — CLI control tool
- `ace-step/acectl.bat` — Windows CLI wrapper
- `ace-step/acectl_gui.py` — Desktop GUI (tkinter)
- `ace-step/acectl_gui.bat` — Windows GUI wrapper
- `.ace-step-control/` — Config, PID, logs directory