# ACE-Step Control Application Reference

## Overview
This session created a complete control application (CLI + Desktop GUI) for managing ACE-Step service lifecycle on Windows ROCm.

## Files Created
- `ace-step/acectl.py` - Full CLI tool (44 KB)
- `ace-step/acectl.bat` - Windows CLI wrapper
- `ace-step/acectl_gui.py` - Desktop GUI (24 KB, tkinter)
- `ace-step/acectl_gui.bat` - Windows GUI wrapper
- `.ace-step-control/config.json` - Persistent configuration
- `.ace-step-control/ace-step.pid` - Process tracking
- `.ace-step-control/ace-step.log` - Operation logs

## CLI Commands
```bash
acectl start              # Start API server
acectl start --gradio     # Start Gradio Web UI
acectl stop               # Stop service + free GPU
acectl restart            # Restart service
acectl status             # Show status (JSON)
acectl free-gpu           # Force GPU memory cleanup
acectl config --show      # View config
acectl config --port 8002 # Modify config
```

## Desktop GUI Features
- Start/Stop/Restart API or Gradio
- Real-time GPU memory monitoring (allocated/reserved/peak)
- Service status with PID, CPU%, memory
- Clickable URL to open Gradio/API docs
- Config editor dialog
- Live log viewer
- Force GPU memory cleanup button
- Auto-refresh every 2 seconds

## GPU Management
- Detects AMD Radeon 780M (16GB UMA via PowerShell + hostname)
- tier5 config: 480s max duration, batch=4 with LM
- Windows working set trimming (EmptyWorkingSet)
- PyTorch cache clearing (empty_cache, ipc_collect)
- Proper process tree termination (parent + children)

## Configuration Structure
```json
{
  "host": "127.0.0.1",
  "port": 8001,
  "gradio_port": 7860,
  "model": "acestep-v15-turbo",
  "device": "auto",
  "init_llm": true,
  "lm_model": "acestep-5Hz-lm-1.7B",
  "backend": "pt",
  "quantization": "int8_weight_only",
  "offload_to_cpu": true,
  "offload_dit_to_cpu": false,
  "use_flash_attention": false
}
```

## Verified Working
```bash
# Start Gradio
acectl start --gradio
# Gradio UI started on http://127.0.0.1:7860 (PID: 2236)

# Check status
acectl status
{"running": true, "pid": 2236, "gpu": {"device": "AMD Radeon 780M Graphics", "allocated_gb": 0.0}}

# Stop & free GPU
acectl stop
# Service stopped and GPU memory freed

# Force GPU cleanup
acectl free-gpu
# GPU memory freed. Allocated: 0.00GB
# Windows working set trimmed
```

## Key Implementation Details
- **Environment isolation**: Must run outside Hermes venv to avoid sys.path conflicts
- **Windows working set trimming**: Uses `ctypes.windll.psapi.EmptyWorkingSet` for GPU memory release
- **Process management**: Uses `psutil` for proper parent+children termination
- **GPU detection**: PowerShell `Get-CimInstance Win32_VideoController` + hostname check for 16GB UMA