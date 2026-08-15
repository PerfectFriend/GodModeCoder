---
name: gpu-cluster-management
description: "Manage GPU clusters with GPUStack for vLLM and SGLang."
trigger: "Manage GPU clusters with GPUStack for vLLM and SGLang."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux]
metadata:
  hermes:
    tags: [gpu, cluster, gpustack, vllm, sglang, orchestration]
    related_skills: [vllm-inference-optimization, sglang-serving]
---

# GPU Cluster Management with GPUStack

Guide for managing GPU clusters for LLM inference using GPUStack.

## GPUStack Overview

- **gpustack/gpustack** (5447★, updated 2026-08-07)
- Unified GPU cluster manager for vLLM and SGLang
- On-demand SSH-accessible GPU instances
- Production-ready multi-GPU orchestration

## Installation

```bash
# Quick install
curl -sfL https://get.gpustack.ai | sh

# Or with Docker
docker run -d \
  --name gpustack \
  --privileged \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v gpustack-data:/var/lib/gpustack \
  -p 9090:9090 \
  gpustack/gpustack:latest
```

## Key Features

1. **Unified Backend Support** - vLLM and SGLang on same cluster
2. **Model Registry** - Centralized model management
3. **Auto-scaling** - Scale workers based on demand
4. **SSH Access** - Direct GPU instance access for debugging
5. **Multi-tenancy** - Resource isolation between teams/workloads

## Architecture

```
GPUStack Controller
    │
    ├── Worker Node 1 (GPU 0-3) → vLLM workers
    ├── Worker Node 2 (GPU 4-7) → SGLang workers
    └── Worker Node N → Mixed backends
```

## Model Deployment

```bash
# Deploy model via CLI
gpustack model deploy \
  --name llama-3.1-70b \
  --backend vllm \
  --model-path meta-llama/Llama-3.1-70B-Instruct \
  --replicas 2 \
  --resources "gpu=4"

# Or SGLang
gpustack model deploy \
  --name qwen2.5-7b \
  --backend sglang \
  --model-path Qwen/Qwen2.5-7B-Instruct \
  --replicas 1 \
  --resources "gpu=1"
```

## Integration with GodModeCoder

For the Grimoire graph evolution:
- `gpu_cluster_mgmt` node feeds from `ai_eng_daily` skill
- Manages inference infrastructure for agent loops
- Enables scalable speculative decoding across GPUs

## Monitoring

- GPUStack dashboard at `http://controller:9090`
- Metrics: GPU utilization, memory, throughput, queue depth
- Alerting on worker health, model load failures

## References

- GPUStack GitHub: https://github.com/gpustack/gpustack
- Documentation: https://gpustack.ai/docs