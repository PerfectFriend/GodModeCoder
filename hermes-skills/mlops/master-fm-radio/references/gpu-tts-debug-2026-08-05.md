# GPU-TTS Debug Session — 2026-08-05

## Problem Summary
Qwen3-TTS 1.7B-Base on AMD Radeon 780M via torch-directml 0.2.5 segfaults (exit 139) during any inference operation.

## Environment
- **Hardware**: Beelink SER9, Ryzen 7 255, Radeon 780M, 24 GB RAM (UMA=16 GB)
- **OS**: Windows 11, MSYS2/bash
- **Venv**: `C:\Users\tomas\tts-dml-env`
- **Python**: 3.11 (in venv)
- **Packages**:
  - torch 2.4.1+cpu
  - torch-directml 0.2.5 (from MS Azure DevOps index)
  - transformers 4.57.3
  - qwen_tts (copied from Voicebox PyInstaller unpack)
  - soundfile, numpy, safetensors

## Model
- **Type**: Qwen3-TTS 1.7B Base (`tts_model_type: base`)
- **Path**: `~/.cache/huggingface/hub/models--Qwen--Qwen3-TTS-12Hz-1.7B-Base/snapshots/fd4b254389122332181a7c3db7f27e918eec64e3`
- **Size**: 3.8 GB safetensors, 480 tensors
- **Config**: 1.93B params

## Reproduction Steps

```bash
# 1. Basic DML test - WORKS
env -u PYTHONPATH -u VIRTUAL_ENV /c/Users/tomas/tts-dml-env/Scripts/python.exe -c "
import torch, torch_directml
dml = torch_directml.device()
x = torch.tensor([1.0, 2.0, 3.0]).to(dml)
print('DML works:', x)
"

# 2. Load model on CPU - WORKS (~20s)
env -u PYTHONPATH -u VIRTUAL_ENV /c/Users/tomas/tts-dml-env/Scripts/python.exe -c "
import torch, torch_directml, glob, os
from qwen_tts.inference.qwen3_tts_model import Qwen3TTSModel
MODEL_DIR = glob.glob(os.path.expanduser('~/.cache/huggingface/hub/models--Qwen--Qwen3-TTS-12Hz-1.7B-Base/snapshots/*'))[0]
tts = Qwen3TTSModel.from_pretrained(MODEL_DIR, low_cpu_mem_usage=True)
print('Loaded on CPU')
"

# 3. Move to DML - SEGFAULT (exit 139)
env -u PYTHONPATH -u VIRTUAL_ENV /c/Users/tomas/tts-dml-env/Scripts/python.exe -c "
import torch, torch_directml, glob, os
from qwen_tts.inference.qwen3_tts_model import Qwen3TTSModel
MODEL_DIR = glob.glob(os.path.expanduser('~/.cache/huggingface/hub/models--Qwen--Qwen3-TTS-12Hz-1.7B-Base/snapshots/*'))[0]
dml = torch_directml.device()
tts = Qwen3TTSModel.from_pretrained(MODEL_DIR, low_cpu_mem_usage=True)
tts.model = tts.model.to(dml)  # <-- SEGFAULT HERE
tts.device = dml
print('Moved to DML')
"

# 4. Full gpu_tts_test.py - SEGFAULT
env -u PYTHONPATH -u VIRTUAL_ENV /c/Users/tomas/tts-dml-env/Scripts/python.exe scripts/gpu_tts_test.py "REF.wav" "Test"
```

## Observations

| Test | Result | Notes |
|---|---|---|
| `torch_directml.device()` creation | ✅ Works | Returns `privateuseone:0` |
| Tensor `.to(dml)` | ✅ Works | Basic matmul works |
| `from_pretrained()` CPU | ✅ Works | ~20s, loads 480 tensors |
| `.to(dml)` on model | ❌ Segfault | Exit 139, no Python traceback |
| CPU inference (no .to(dml)) | ❌ Segfault | In `create_voice_clone_prompt` |
| Empty model forward (CPU) | ❌ AttributeError | Config incomplete |
| `load_state_dict` | ❌ OSError/segfault | "Paging file too small" (false, 32GB) |

## Attempted Fixes
- Cleared `PYTHONPATH` and `VIRTUAL_ENV` → no effect
- `low_cpu_mem_usage=True` → helps CPU load but not DML move
- `torch.inference_mode()` → `@torch.no_grad()` patches applied in qwen_tts files
- Custom `torch.cat` wrapper for empty tensors → already in gpu_tts_test.py
- `repetition_penalty=1.0` → already set to avoid RepetitionPenaltyLogitsProcessor bug
- Paging file increased to 32 GB → no effect

## Root Cause Hypothesis
Architectural incompatibility between Qwen3-TTS 1.7B model structure (Mimi codec, custom attention) and torch-directml 0.2.5. The model loads on CPU but contains ops/kernels that DML cannot handle during weight transfer or inference.

## Impact on Master-FM
- **Day mode cron** (`*/15 7-19 * * *` → `day_breaking_news.py`): **BROKEN** — no breaking news generated
- **Night batch** (`0 20 * * *` → `night_batch.py`): **PARTIALLY BROKEN** — voice content fails
- **DJ streaming** (`dj.py`): Works but only plays cached content

## Next Steps
1. Try different torch-directml version (newer/older)
2. Try transformers downgrade (4.57.3 → 4.50.x)
3. Test Qwen3-TTS CustomVoice model variant instead of Base
4. Consider ROCm in WSL2 (but iGPU = DML only on Windows)
5. Fallback: Voicebox server on CPU (slow, ~5-6x realtime)
6. Fallback: GGUF quantized model via llama.cpp (if exists for Qwen3-TTS)

## Files Modified in This Session
- `scripts/day_breaking_news.py` — day mode cron script (already existed, verified structure)
- `scripts/gpu_tts_cli.py` — CLI wrapper (already existed)
- `scripts/gpu_tts_test.py` — Low-level test (already existed with DML fixes)

## Skill Updated
- `master-fm-radio` skill patched with current BROKEN status table and detailed diagnosis