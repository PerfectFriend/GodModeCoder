---
name: sglang-serving
description: "Deploy SGLang serving with omni-modal pipelines."
trigger: "Deploy SGLang serving with omni-modal pipelines."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux]
metadata:
  hermes:
    tags: [sglang, serving, inference, omni-modal, multi-stage, gpu]
    related_skills: [vllm-inference-optimization, gpu-cluster-management]
---

# SGLang High-Performance Serving

Guide for deploying SGLang for production LLM/multimodal serving.

## Core SGLang Features

### High-Performance Serving Framework
- SGLang (sgl-project/sglang, 31442★) - High-performance serving for LLMs and multimodal models
- RadixAttention for efficient prefix caching
- Chunked prefill for long contexts
- Tensor parallelism, pipeline parallelism

### SGLang Omni (sgl-project/sglang-omni, 756★)
- Multi-stage pipeline framework for omni models
- High-performance multi-modal inference
- Updated: 2026-08-07

### SGLang Kernel Wheel Index (sgl-project/whl, 24★)
- Pre-built wheels for easy installation

## Deployment Patterns

### Basic Server
```bash
python -m sglang.launch_server \
    --model-path meta-llama/Llama-3.1-70B-Instruct \
    --tp 4 \
    --port 30000
```

### Multi-Modal / Omni Models
```bash
python -m sglang.launch_server \
    --model-path <omni-model-path> \
    --tp 4 \
    --port 30000 \
    --enable-multimodal
```

## GPU Cluster Integration

### GPUStack (gpustack/gpustack, 5447★)
- Unified cluster manager for vLLM + SGLang
- On-demand SSH-accessible GPU instances

### LLMEval (jianzhnie/LLMEval)
- All-in-one eval toolkit supporting vLLM/SGLang backends

## Quantization Support

### AutoRound (intel/auto-round, 1556★)
- SOTA quantization for CPU/XPU/CUDA
- High-accuracy low-bit LLM inference

## Monitoring

- **inferbench** (bmvinesh/inferbench) - OpenAI-compatible gateway + benchmark harness for vLLM/SGLang/llama.cpp comparison

## References

- SGLang GitHub: https://github.com/sgl-project/sglang
- SGLang Omni: https://github.com/sgl-project/sglang-omni
- GPUStack: https://github.com/gpustack/gpustack