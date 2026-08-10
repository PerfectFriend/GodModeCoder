# AMD Radeon 780M — Verified CPU-Only Ollama Setup

## Problem
Ollama defaults to Vulkan on AMD iGPU → OOM errors:
```
alloc_tensor_range: failed to allocate Vulkan0 buffer of size 1070244864
error loading model: unable to allocate Vulkan0 buffer
```

## Verified Working Configuration (Windows 11, Ryzen 7 255H, 16GB UMA)

### Environment Variables (ALL required)
```powershell
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

### Start Server
```powershell
$env:OLLAMA_NUM_GPU=0; $env:OLLAMA_GPU_LAYERS=0; $env:OLLAMA_FLASH_ATTENTION=0; `
$env:OLLAMA_KV_CACHE_TYPE="f16"; $env:OLLAMA_NO_VULKAN=1; `
$env:OLLAMA_CUDA=0; $env:OLLAMA_ROCM=0; $env:OLLAMA_METAL=0; `
$env:OLLAMA_LOW_VRAM=1; $env:OLLAMA_NUMA="true"; `
ollama serve
```

### Verified Models (keep only qwen3:8b)
| Model | Size | RAM | Speed | Use Case |
|---|---|---|---|---|
| **qwen3:8b** | 5.2 GB | ~6 GB | 8-12 tok/s | **KEEP** — code review, tests, refactor, docs, bug analysis |
| qwen3:14b | 9.3 GB | ~10 GB | 4-6 tok/s | DELETE — rare deep arch analysis |
| gemma4:12b | 7.6 GB | ~8 GB | 5-7 tok/s | DELETE — qwen3:8b covers this |

### API Test (confirmed working)
```bash
curl -X POST http://localhost:11434/api/generate \
  -d '{"model":"qwen3:8b","prompt":"code review test","stream":false,"options":{"num_gpu":0}}'
```

### Code Review Test Result (qwen3:8b)
**Input:** SQL injection vulnerable async function
**Output:** Found 4 issues — SQL injection, N+1 problem, no error handling, no type hints
**Quality:** Production-ready senior review level

### Performance (CPU-only, Ryzen 7 255H)
- qwen3:8b: 8-12 tokens/sec, ~6 GB RAM
- Generation time: 30-120 seconds depending on prompt complexity
- Use `timeout=300` in requests

### For Deep Analysis → Cloud
Use Nemotron 3 Ultra 550b (free via NVIDIA) for:
- Deep architectural audits
- Complex legacy refactoring
- Security audits
- System design decisions

## PowerShell Setup Script
See `scripts/setup-ollama-cpu.ps1` in GodModeCoder repo for automated setup.