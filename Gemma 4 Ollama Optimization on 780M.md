Warning: Permanently added '100.124.152.97' (ED25519) to the list of known hosts.
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
---
tags: [textbook, ai-ml, gemma4, ollama, llama.cpp, vulkan, amd, radeon-780m, vram-optimization, moe]
source: textbook
status: learned
date: 2026-08-10
priority: 10
---

# Gemma 4 Ollama Optimization on 780M

## Summary
**Gemma 4 (26B MoE, 4B active)** runs surprisingly well on **Radeon 780M** via **llama.cpp + Vulkan** (~23-25 tok/s), but **Ollama is 5-6x slower** (~4.5 tok/s). Key optimizations: use **upstream ggml-org GGUF** (not Ollama blobs), **llama.cpp + Vulkan** (not Ollama), **`-np 1`** cuts SWA cache VRAM 3x, **Q4_K_M quantization** fits in shared VRAM.

## Performance Reality Check

| Runtime | Model | Quant | Tok/s (gen) | VRAM | Notes |
|---------|-------|-------|-------------|------|-------|
| **Ollama** | gemma4:26b | Q4_K_M | **~4.5** | ~16 GB | Slow, convenient |
| **llama.cpp + Vulkan** | gemma4-26B Q4_K_M | Q4_K_M | **~23-25** | ~16 GB | **5-6x faster** |
| **llama.cpp + Vulkan** | gemma4-26B Q4_K_M | Q4_K_M (reasoning off) | **~24** | ~16 GB | Final answer only |

**Hardware tested**: MINISFORUM UM890 Pro, Radeon 780M (RADV PHOENIX), 32GB system RAM, Ubuntu 24.04, llama.cpp `-DGGML_VULKAN=ON`

## Why Ollama Is Slow on 780M

1. **No Vulkan support** — Ollama uses CPU/Metal/ROCm, not Vulkan
2. **SWA cache bloat** — Sliding Window Attention cache not optimized
3. **No `-np 1` equivalent** — Can't disable parallel prompt processing
3. **Blob format mismatch** — Ollama GGUF blobs incompatible with upstream llama.cpp

## Optimal Setup: llama.cpp + Vulkan

### Build llama.cpp with Vulkan
```bash
# Ubuntu 24.04
sudo apt install vulkan-tools libvulkan-dev mesa-vulkan-drivers

git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
mkdir build && cd build
cmake -DGGML_VULKAN=ON -DCMAKE_BUILD_TYPE=Release ..
cmake --build . --config Release -j$(nproc)

# Verify Vulkan detection
./bin/llama-cli --help | grep -i vulkan
```

### Download Correct GGUF (NOT Ollama Blob)
```bash
# Use upstream ggml-org GGUF, NOT Ollama's installed blob
# Ollama blobs have different tensor layout (wrong tensor count)

wget https://huggingface.co/ggml-org/gemma-4-26B-A4B-it-GGUF/resolve/main/gemma-4-26B-A4B-it-Q4_K_M.gguf
# File: ~16 GB, Q4_K_M quantization
```

### Run with Optimal Flags
```bash
# Optimal flags for 780M
./bin/llama-cli \
  -m gemma-4-26B-A4B-it-Q4_K_M.gguf \
  -ngl 99 \              # Offload all layers to GPU
  -np 1 \                # CRITICAL: Single prompt processor, cuts SWA cache 3x
  -c 4096 \              # Context window
  -t 8 \                 # CPU threads (match cores)
  --temp 0.7 \
  --top-p 0.9 \
  --top-k 40 \
  --repeat-penalty 1.1 \
  -p "Your prompt here"

C:\Vault\Gemma 4 Ollama Optimization on 780M.md



# For reasoning models (Gemma 4 has reasoning):
./bin/llama-cli \
  -m gemma-4-26B-A4B-it-Q4_K_M.gguf \
  -ngl 99 -np 1 \
  --reasoning-budget 0 \  # Disable reasoning for speed
  -p "Your prompt"
```

## VRAM Optimization Flags Explained

| Flag | Purpose | VRAM Impact |
|------|---------|-------------|
| `-ngl 99` | Offload all layers to GPU | Required for speed |
| `-np 1` | **Single prompt processor** | **Cuts SWA cache 3x** (KEY) |
| `--reasoning-budget 0` | Disable reasoning traces | Saves KV cache |
| `-c 4096` | Limit context | Reduces KV cache |
| `-fa` | Flash Attention (if supported) | Reduces attention memory |
| `--mlock` | Lock memory, prevent swap | Prevents OOM kills |

## SWA Cache Optimization Deep Dive

### The Problem
Gemma 4 uses **Sliding Window Attention (SWA)** with window size 4096. Each layer caches K/V for last 4096 tokens. With 26B MoE (many layers), this explodes VRAM.

### The Fix: `-np 1`
```
Default (-np auto): Multiple prompt processors → each maintains SWA cache → 3x VRAM
-np 1: Single processor → shared SWA cache → 1x VRAM
```

**Measured**: `-np 1` reduces SWA cache from ~12 GB to ~4 GB on 780M.

## Quantization Comparison (26B MoE)

| Quant | Size | VRAM (780M) | Tok/s | Quality |
|-------|------|-------------|-------|---------|
| **Q4_K_M** | 16 GB | ~16 GB | **23-25** | ★★★★★ |
| Q5_K_M | 19 GB | ~19 GB | 20-22 | ★★★★★ |
| Q3_K_M | 13 GB | ~13 GB | 28-30 | ★★★★☆ |
| Q2_K | 11 GB | ~11 GB | 35-38 | ★★★☆☆ |

**Recommendation**: **Q4_K_M** — best balance for 780M (16 GB fits in shared VRAM).

## Complete Launch Script

```bash
#!/bin/bash
# run_gemma4_780m.sh

MODEL="gemma-4-26B-A4B-it-Q4_K_M.gguf"
PROMPT="$1"

if [ -z "$PROMPT" ]; then
    echo "Usage: $0 \"your prompt\""
    exit 1
fi

# Environment
export VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/radeon_icd.x86_64.json
export MESA_VK_DEVICE_SELECT=1002:15dd  # Force 780M if multiple GPUs

# Run
./llama.cpp/build/bin/llama-cli \
  -m "$MODEL" \
  -ngl 99 \
  -np 1 \
  -c 4096 \
  -t 8 \
  --temp 0.7 \
  --top-p 0.9 \
  --top-k 40 \
  --repeat-penalty 1.1 \
  --reasoning-budget 0 \
  -p "$PROMPT"
```

## Ollama vs llama.cpp Comparison

| Aspect | Ollama | llama.cpp + Vulkan |
|--------|--------|-------------------|
| **Ease of use** | `ollama run gemma4:26b` | Build + config |
| **Speed (tok/s)** | ~4.5 | **23-25** |
| **VRAM efficiency** | Poor | Excellent (`-np 1`) |
| **API/daemon** | Built-in | Custom (llama-server) |
| **Model management** | Auto | Manual |
| **Reasoning control** | Limited | `--reasoning-budget` |
| **780M suitability** | Marginal | **Excellent** |

## Running as API Server (Replace Ollama)

```bash
# Start llama-server with Vulkan
./llama.cpp/build/bin/llama-server \
  -m gemma-4-26B-A4B-it-Q4_K_M.gguf \
  -ngl 99 -np 1 \
  -c 4096 \
  --host 0.0.0.0 --port 8080 \
  --reasoning-budget 0

# Test
curl -X POST http://localhost:8080/completion \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello", "n_predict": 128, "temperature": 0.7}'
```

## Integration with Our Stack

### GodModeCoder (Code Review)
```python
# Use llama-server for fast code review
import requests

def gemma4_review(code, focus="security"):
    response = requests.post("http://localhost:8080/completion", json={
        "prompt": f"Review this code for {focus} issues:\n```python\n{code}\n```\nIssues:",
        "n_predict": 512,
        "temperature": 0.3,
        "stop": ["```"]
    })
    return response.json()["content"]
```

### Radio ArmsgeddonFM (DJ Commentary)
```python
# Fast voice generation via llama-server
def generate_dj_intro(song_title, artist):
    prompt = f"Short enthusiastic DJ intro for '{song_title}' by {artist}:"
    response = requests.post("http://localhost:8080/completion", json={
        "prompt": prompt,
        "n_predict": 64,
        "temperature": 0.8
    })
    return response.json()["content"]
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Vulkan not detected** | `mesa-vulkan-drivers`, `VK_ICD_FILENAMES` |
| **OOM on 780M** | `-np 1`, `-c 2048`, Q3_K_M quant |
| **Slow generation** | Check `-np 1`, `--reasoning-budget 0` |
| **Model won't load** | Use ggml-org GGUF, not Ollama blob |
| **Reasoning loops** | `--reasoning-budget 0` or `--reasoning off` |

## Performance Tuning Checklist

- [ ] Build llama.cpp with `-DGGML_VULKAN=ON`
- [ ] Use ggml-org GGUF (Q4_K_M)
- [ ] Run with `-ngl 99 -np 1`
- [ ] Disable reasoning: `--reasoning-budget 0`
- [ ] Limit context: `-c 4096` (or 2048)
- [ ] Set CPU threads: `-t 8`
- [ ] Enable Flash Attention if available: `-fa`
- [ ] Lock memory: `--mlock`

## References
- **llama.cpp Vulkan**: https://github.com/ggml-org/llama.cpp/discussions/24222
- **Gemma 4 GGUF**: https://huggingface.co/ggml-org/gemma-4-26B-A4B-it-GGUF
- **SWA Cache Optimization**: `-np 1` flag documentation
- **Vulkan on AMD**: https://github.com/ggml-org/llama.cpp/blob/master/docs/vulkan.md
- **llama-server**: https://github.com/ggml-org/llama.cpp/tree/master/examples/server