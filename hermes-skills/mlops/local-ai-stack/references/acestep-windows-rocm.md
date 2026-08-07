# ACE-Step on Windows ROCm 7.2 (Radeon 780M, 16GB UMA)

> **Proven working 2026-08** on Beelink SER9 (Ryzen 7 255, Radeon 780M, 16GB UMA)

## Critical Dependency Versions (Locked)

```
transformers==4.48.3
tokenizers==0.21.4
torchao NOT INSTALLED (breaks on ROCm Windows - requires FSDP)
nano-vllm NOT INSTALLED (requires transformers>=4.51 which breaks Gradio)
Backend: "pt" (not vllm)
```

## Working Config.json for 16GB UMA

```json
{
  "model": "acestep-v15-turbo",
  "device": "auto",
  "init_llm": false,
  "lm_model": "acestep-5Hz-lm-1.7B",
  "backend": "pt",
  "quantization": "none",
  "offload_to_cpu": true,
  "offload_dit_to_cpu": false,
  "use_flash_attention": false
}
```

## Working Path (Gradio UI Only)

1. Start Gradio: `acectl start --gradio` → http://127.0.0.1:7860
2. Click **"Initialize Service"** button → wait 60-90 seconds
3. GPU memory shows ~8-12 GB allocated
4. Switch to **"Custom Mode"** (dropdown: Simple → Custom)
5. Expand **"Advanced Parameters"**
6. Set:
   - **Task Type**: text2music
   - **Inference Steps**: 8
   - **CFG Scale**: 7.0
   - **Shift**: **3.0** (MANDATORY for turbo!)
   - **Thinking**: ✅ ON
   - **LM Backend**: pt
   - **Quantization**: none
7. Fill caption + lyrics → **Generate**

## What Breaks & Why

| Component | Version | Why It Breaks |
|-----------|---------|---------------|
| transformers | ≥4.50 | Imports `torch.distributed.tensor` → needs FSDP (`torch._C._distributed_c10d` missing in ROCm Windows) |
| torchao | 0.15.0+ | Imports `torch.distributed._functional_collectives` → needs FSDP |
| nano-vllm | 0.2.0 | Requires transformers≥4.51 → upgrades transformers → breaks Gradio |
| vLLM backend | Any | Requires nano-vllm → chain of failures above |

## Working Environment

- **PyTorch**: 2.9.1+rocmsdk20260116 (ROCm 7.2 wheel)
- **HIP**: 7.2.26024-f6f897bd3d
- **GPU**: AMD Radeon 780M Graphics
- **VRAM reported**: 20.3 GB (16GB UMA + overhead)
- **Python**: 3.12 in `venv_rocm`

## Generation Parameters (MUST SET)

| Parameter | Value | Required |
|-----------|-------|----------|
| Task Type | text2music | ✅ |
| Inference Steps | 8 | ✅ |
| CFG Scale | 7.0 | ✅ |
| Shift | **3.0** | ✅ **MANDATORY** |
| Thinking | ON | ✅ |
| LM Backend | pt | ✅ |
| Quantization | none | ✅ |

## What Doesn't Work (Yet)

| Feature | Status |
|---------|--------|
| CLI generation (`python cli.py -c config.toml`) | ❌ FSDP import errors in diffusers |
| API server (`python -m acestep.api_server`) | ❌ Same FSDP errors |
| vLLM backend | ❌ Needs nano-vllm → transformers≥4.51 |
| Quantization (int8/int4) | ❌ Needs torchao → FSDP |

## Troubleshooting

**"Initialize Service" hangs / fails:**
- Check logs in `.ace-step-control/ace-step.log`
- Ensure `quantization: "none"` in config.json
- Ensure `backend: "pt"` in config.json
- Wait full 90 seconds after clicking Initialize

**Generate button stays disabled:**
- Must click "Initialize Service" FIRST
- Wait for GPU memory to show allocated (not 0.0 GB)
- Switch to Custom Mode
- Expand Advanced Parameters
- Fill all required fields (caption + lyrics for text2music)

**OOM on 16GB:**
- Set `init_llm: false` in config.json
- Click "Initialize Service" manually
- Set `quantization: "none"` (no torchao)
- Use `offload_to_cpu: true`

## Files Created This Session

- `acectl.py` / `acectl.bat` — CLI control (start/stop/status/free-gpu/config)
- `acectl_gui.py` / `acectl_gui.bat` — Desktop GUI with GPU monitoring
- `disco_config.toml` — Ready-to-use Yellow Submarine disco preset
- `.ace-step-control/config.json` — Working config for 16GB UMA