---
name: vllm-inference-optimization
description: "Optimize vLLM inference with speculative decoding."
trigger: "Optimize vLLM inference with speculative decoding."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux]
metadata:
  hermes:
    tags: [vllm, inference, optimization, speculative-decoding, kv-cache, paged-attention, gpu]
    related_skills: [sglang-serving, gpu-cluster-management, quantization-evaluation]
---

# vLLM Inference Optimization

Comprehensive guide for optimizing vLLM inference in production environments.

## Core vLLM Architecture (from Aleksa Gordić deep-dive)

### Key Components
1. **PagedAttention** - Memory-efficient attention with paged KV cache blocks
2. **Continuous Batching** - Dynamic batch scheduling without fixed batch sizes
3. **Prefix Caching** - Reuse KV cache for common prefixes (system prompts, few-shot)
4. **Speculative Decoding** - Draft model guesses, target model verifies (2-3× speedup)
5. **Multi-GPU/Multi-Node** - Tensor parallelism, pipeline parallelism, data parallelism

## Speculative Decoding Variants

### Standard Speculative Decoding
- Small draft model (e.g., 7B) generates candidate tokens
- Large target model (e.g., 70B) verifies in single forward pass
- Acceptance rate determines speedup (typically 2-3×)

### DFlash / Spec V2 (LMSYS, 2026)
- Next-generation speculative decoding from LMSYS
- Improved draft model specialization
- Better acceptance rates, lower latency variance
- Blog: https://www.lmsys.org/blog/2026-06-15-next-generation-speculative-decoding-dflash-v2/

### Adaptive Speculative Decoding
- Dynamic draft model selection based on workload
- "Adaptive speculative decoding on a $300 GPU" - Fronde project
- GitHub: https://github.com/Gogo27Gallet/Fronde

## KV Cache Compression Strategies

### KeyDiff / KVPress (fax4ever/kvpress-vllm-tests)
- Compare KV cache compression techniques
- KeyDi and similar methods for long-context inference
- Critical for agent memory/context windows

### Quantization-Aware KV Cache
- Compress KV cache to lower precision
- Trade-off: memory vs. accuracy

## Production Deployment Patterns

### vLLM Omni (vllm-project/vllm-omni, 5919★)
- Framework for omni-modality models
- Multi-modal inference support

### vLLM Ascend (vllm-project/vllm-ascend, 2575★)
- Community hardware plugin for Ascend NPUs

### vLLM.cpp (mudler/vllm.cpp)
- C++ port for lower overhead

## GPU Cluster Integration

### GPUStack (gpustack/gpustack, 5447★)
- Unified cluster manager for vLLM + SGLang
- On-demand SSH-accessible GPU instances
- Production-ready multi-GPU orchestration

## Configuration Best Practices

```python
# Example vLLM server with speculative decoding
from vllm import LLM, SamplingParams

llm = LLM(
    model="meta-llama/Llama-3.1-70B-Instruct",
    speculative_model="meta-llama/Llama-3.1-8B-Instruct",  # Draft model
    speculative_draft_tensor_parallel_size=1,
    tensor_parallel_size=4,  # Target model TP
    max_num_seqs=256,
    max_model_len=32768,
    enable_prefix_caching=True,
    kv_cache_dtype="fp8",  # or "auto"
    gpu_memory_utilization=0.9,
)

sampling_params = SamplingParams(
    temperature=0.7,
    top_p=0.9,
    max_tokens=2048,
    # Speculative decoding params
    speculative_max_tokens=5,  # Max draft tokens per step
)
```

## Monitoring & Observability

- **LLMEval** (jianzhnie/LLMEval) - All-in-one eval toolkit supporting vLLM/SGLang backends
- **inferbench** (bmvinesh/inferbench) - OpenAI-compatible gateway + benchmark harness
- Track: throughput (tok/s), latency (TTFT, TPOT), GPU utilization, acceptance rate

## Windows + AMD iGPU (DirectML/ROCm)

For AMD 780M iGPU on Windows:
- DirectML backend via torch-directml
- ROCm 7.2+ for Windows (experimental)
- See: `ace-step-directml`, `qwen3-tts-directml` skills for AMD patterns

## References

- Inside vLLM: https://www.aleksagordic.com/blog/vllm
- Speculative Decoding Visualized: https://www.adaptive-ml.com/post/speculative-decoding-visualized
- DFlash/Spec V2: https://www.lmsys.org/blog/2026-06-15-next-generation-speculative-decoding-dflash-v2/
- KV Cache Compression: https://github.com/fax4ever/kvpress-vllm-tests
- GPUStack: https://github.com/gpustack/gpustack
- vLLM GitHub: https://github.com/vllm-project/vllm