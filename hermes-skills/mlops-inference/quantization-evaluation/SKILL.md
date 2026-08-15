---
name: quantization-evaluation
description: "Evaluate quantization quality and nonlinear knowledge loss."
trigger: "Evaluate quantization quality and nonlinear knowledge loss."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux]
metadata:
  hermes:
    tags: [quantization, evaluation, 4-bit, auto-round, knowledge-loss]
    related_skills: [vllm-inference-optimization, sglang-serving]
---

# Quantization Evaluation

Guide for evaluating quantization quality and detecting nonlinear knowledge loss.

## Key Findings (from recent research)

### Nonlinear Knowledge Loss
- "My 4-bit quant was 6.2 bits per weight" - quantization hurts knowledge nonlinearly
- Qwen3.6 27B case study shows disproportionate quality degradation
- Per-model evaluation is MANDATORY - no universal "4-bit is fine" rule

### Evaluation Methodology
1. **Perplexity on held-out data** - baseline quality metric
2. **Task-specific benchmarks** - coding, reasoning, math, multilingual
3. **Knowledge retention tests** - factual recall, reasoning chains
4. **Edge case testing** - long context, rare tokens, multilingual

## Tools

### AutoRound (intel/auto-round, 1556★)
- SOTA quantization algorithm for high-accuracy low-bit LLM inference
- Optimized for CPU/XPU/CUDA
- Multi-algorithm support (GPTQ, AWQ, AutoRound)

### LLMEval (jianzhnie/LLMEval, 1★)
- All-in-one eval toolkit supporting vLLM/SGLang backends
- Quantization-aware evaluation

## Best Practices

1. **Never assume quantization quality** - test every model
2. **Compare multiple quantization methods** (GPTQ, AWQ, AutoRound, HQQ)
3. **Test at multiple bit-widths** (2-bit, 3-bit, 4-bit, 8-bit)
4. **Evaluate on YOUR tasks** - generic benchmarks don't capture domain specifics
5. **Monitor for "quantization collapse"** - sudden quality drops at certain bit-widths

## Qwen3.6 27B Case Study (quesma.com)
- Quantization hurts knowledge nonlinearly
- Some 4-bit quants effectively 6+ bits per weight
- Must validate per-model, per-task

## Configuration Example

```python
from auto_round import AutoRound
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-7B")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B")

# AutoRound quantization
autoround = AutoRound(
    model,
    tokenizer,
    bits=4,
    group_size=128,
    sym=False,
    format="auto_gptq",  # or "auto_awq"
)
autoround.quantize_and_save("./qwen2.5-7b-4bit")
```

## References

- Quantization hurts knowledge nonlinearly: https://quesma.com/blog/quantization-hurts-knowledge/
- My 4-bit quant was 6.2 bits: https://koleslaw.ai/blog/the-quantization-that-didnt-fit
- Do Qwen 3.6 27B quantizations break the pelican?: https://quesma.com/blog/qwen-quantization-quality/
- AutoRound: https://github.com/intel/auto-round
- Visual Guide to Quantization: https://newsletter.maartengrootendorst.com/p/a-visual-guide-to-quantization