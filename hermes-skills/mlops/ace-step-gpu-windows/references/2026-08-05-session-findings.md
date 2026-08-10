# Session Findings - 2026-08-05/2026-08-06

## Critical Findings

### 1. ONLY Working Generation Path: Gradio Web UI
**URL**: http://127.0.0.1:7860

**Why CLI Generation Fails:**
- `transformers 4.48.3`: Works for Gradio UI but **lacks `layer_type_validation`** needed for ACE-Step model config loading
- `transformers 4.50+`: Has `layer_type_validation` but **imports FSDP** (`torch.distributed.tensor`) which is **missing in ROCm Windows build** → `ModuleNotFoundError: torch._C._distributed_c10d`

**Solution**: Use Gradio Web UI for ALL generation tasks. CLI generation is NOT available on Windows ROCm.

### 2. Gradio UI Generation Workflow
1. Open http://127.0.0.1:7860
2. Click **"Initialize Service"** button (top section) — wait 60-90 seconds
3. Switch to **"Custom Mode"** (top dropdown: Simple → Custom)
4. Expand **"Advanced Parameters"** accordion:
   - **Inference Steps**: 8 (turbo default)
   - **CFG Scale**: 7.0
   - **Shift**: **3.0** (MANDATORY for turbo)
   - **Thinking**: ✅ ON (for lyrics)
   - **LM Backend**: `pt` (Windows ROCm)
   - **Quantization**: `int8_weight_only` (for 16GB)
2. Fill caption/lyrics, set duration, click **Generate**

### 3. Transformers Version Deadlock (No Solution)
| Version | Gradio UI | CLI Generation |
|---------|-----------|----------------|
| 4.48.3 | ✅ Works | ❌ No `layer_type_validation` |
| 4.50+ | ❌ FSDP import fails | ✅ Has `layer_type_validation` |

**Root Cause**: ROCm Windows PyTorch build doesn't include FSDP (`torch._C._distributed_c10d` missing).

### 4. Desktop GUI Crash Fix (2026-08-06)
**Problem**: GUI crashed on startup due to `import torch` at module level.

**Fix in `acectl_gui.py`:**
```python
# REMOVED: import torch (module level)

# ADDED: get_gpu_info() function with torch import inside
def get_gpu_info():
    """Get GPU info without blocking. Returns tuple or None."""
    try:
        import torch
        if torch.cuda.is_available():
            device = torch.cuda.get_device_name(0)
            allocated = torch.cuda.memory_allocated() / 1e9
            reserved = torch.cuda.memory_reserved() / 1e9
            max_alloc = torch.cuda.max_memory_allocated() / 1e9
            total = torch.cuda.get_device_properties(0).total_memory / 1e9
            return device, allocated, reserved, max_alloc, total
    except Exception:
        pass
    return None

# In __init__:
self.setup_ui()
self.root.after(100, self.start_monitoring)  # Deferred start
```

### 5. Environment Isolation (Critical)
**Hermes venv (Python 3.11) MUST be cleaned** to avoid conflicts with `venv_rocm` (Python 3.12):

Packages to REMOVE from Hermes venv:
```bash
numpy, torch*, transformers*, tokenizers*, diffusers*, huggingface*,
gradio*, fastapi*, pydantic*, scipy*, PIL*, bitsandbytes*, lycoris_lora*
```

### 6. Service Management Tools
- **CLI**: `acectl.py` + `acectl.bat` — start/stop/status/free-gpu/config
- **GUI**: `acectl_gui.py` + `acectl_gui.bat` — real-time monitoring
- **Desktop Shortcut**: `ACE-Step Control.lnk` on Desktop

### 7. GPU Tier for 16GB UMA (tier5)
- `max_batch_size_with_lm`: 4
- `max_duration_with_lm`: 480s (8 min)
- `recommended_lm_model`: `acestep-5Hz-lm-1.7B`
- `quantization_default`: true (INT8)

### 8. Disco Track Config (Ready)
File: `C:\Users\tomas\disco_config.toml`
- 30s Yellow Submarine disco track
- shift=3.0, steps=8, cfg=7.0, thinking=true

### 8. GPU Cleanup (Windows)
```python
# In acectl.py - calls EmptyWorkingSet on Windows
ctypes.windll.psapi.EmptyWorkingSet(ctypes.windll.kernel32.GetCurrentProcess())
```

---

## Files Created in This Session

| File | Purpose |
|------|---------|
| `C:\Users\tomas\ace-step\acectl.py` + `.bat` | CLI control tool |
| `C:\Users\tomas\ace-step\acectl_gui.py` + `.bat` | Desktop GUI |
| `C:\Users\tomas\Desktop\ACE-Step Control.lnk` | Desktop shortcut |
| `C:\Users\tomas\ace-step\disco_config.toml` | Disco track config |
| `C:\Users\tomas\.ace-step-control\config.json` | Persistent config |