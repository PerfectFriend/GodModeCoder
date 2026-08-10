# Ollama CPU-Only on AMD iGPU (Radeon 780M) — Validated Configuration

## Problem
Ollama defaults to Vulkan on AMD iGPU → OOM errors on Radeon 780M:
```
alloc_tensor_range: failed to allocate Vulkan0 buffer of size 1070244864
error loading model: unable to allocate Vulkan0 buffer
```

## Solution — CPU-Only Environment Variables (All Required)
```bash
# User-scope environment variables
setx OLLAMA_NUM_GPU 0
setx OLLAMA_GPU_LAYERS 0
setx OLLAMA_FLASH_ATTENTION 0
setx OLLAMA_KV_CACHE_TYPE f16
setx OLLAMA_NO_VULKAN 1
setx OLLAMA_CUDA 0
setx OLLAMA_ROCM 0
setx OLLAMA_METAL 0
setx OLLAMA_LOW_VRAM 1
setx OLLAMA_NUMA true
```

## Start Server (with env vars active in shell)
```bash
OLLAMA_NUM_GPU=0 OLLAMA_GPU_LAYERS=0 OLLAMA_FLASH_ATTENTION=0 \
OLLAMA_KV_CACHE_TYPE=f16 OLLAMA_NO_VULKAN=1 OLLAMA_CUDA=0 \
OLLAMA_ROCM=0 OLLAMA_METAL=0 OLLAMA_LOW_VRAM=1 OLLAMA_NUMA=true \
ollama serve
```

## Verify
```bash
curl -X POST http://localhost:11434/api/generate \
  -d '{"model": "qwen3:8b", "prompt": "test", "stream": false, "options": {"num_gpu": 0}}'
```

## Single-Model Strategy (Validated 2026-08-07)

| Model | Size | RAM | Speed | Decision |
|---|---|---|---|---|
| **qwen3:8b** | 5.2 GB | ~6 GB | 8-12 tok/s | ✅ KEEP — covers 95% tasks |
| qwen3:14b | 9.3 GB | ~10 GB | 4-6 tok/s | ❌ REMOVED — use cloud for deep analysis |
| gemma4:12b | 7.6 GB | ~8 GB | 5-7 tok/s | ❌ REMOVED — redundant |

**Disk savings:** ~17 GB freed (removed qwen3:14b + gemma4:12b)

## Cloud Fallback for Deep Analysis (5% of tasks)
- **Nemotron 3 Ultra 550b** (free NVIDIA API)
- **Claude Opus / GPT-4o** (when available)
- Use for: architectural audits, complex legacy refactoring, security reviews

## Integration with TurboCoder / GodModeCoder
- Skill: `ollama-cpu-worker` (created this session)
- Added to TurboCoder bootstrap sequence
- Cron jobs: `graph-pulse-export` (every 6h), `textbook-learning` (every 6h)
- Verification: `test_ollama_available()` in `hermes-verify-all.py`

## PowerShell Setup Script
See `scripts/setup-ollama-cpu.ps1` in GodModeCoder repo — sets all env vars, verifies Ollama API, pulls qwen3:8b.

## Notes
- Server MUST be running (`ollama serve`) before API calls
- All requests must include `"options": {"num_gpu": 0}` to enforce CPU
- Port 11434 — localhost only, never expose externally
- Timeout 300s for requests (generation takes 30-120s on CPU)