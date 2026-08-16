Warning: Permanently added '100.124.152.97' (ED25519) to the list of known hosts.
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
---
tags: [textbook, ai-ml, directml, windows, pytorch, amd-gpu, alternative, rocm-fallback]
source: textbook
status: learned
date: 2026-08-10
priority: 10
---

# DirectML Alternative for Windows PyTorch

## Summary
**DirectML** is Microsoft's hardware acceleration layer for ML on Windows, providing GPU acceleration via DirectX 12. It serves as a **fallback when ROCm is unavailable** (driver issues, unsupported GPU, Windows version mismatch). While ROCm 7.2+ offers native HIP performance, DirectML provides broader compatibility with a ~15-25% performance penalty.

## When to Use DirectML

| Scenario | Use DirectML |
|----------|--------------|
| ROCm driver installation fails | ✅ |
| GPU not in ROCm supported list (pre-RDNA 3) | ✅ |
| Windows version incompatible with ROCm 7.2+ | ✅ |
| Quick prototype without driver reinstall | ✅ |
| Need both NVIDIA + AMD in same system | ✅ |
| ROCm works perfectly | ❌ (Use ROCm instead) |

## Installation

### Option 1: torch-directml (Official Microsoft Package)
```bash
# Install DirectML-enabled PyTorch
pip install torch-directml

# Or specific version
pip install torch-directml==2.9.0
```

### Option 2: Manual PyTorch + DirectML Backend
```bash
# Standard PyTorch + DirectML extension
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install torch-directml
```

### Verify Installation
```python
import torch
import torch_directml

# Check DirectML availability
print('DirectML available:', torch_directml.is_available())

# Get device
device = torch_directml.device()
print('Device:', device)

# Test tensor
x = torch.randn(2, 3).to(device)
y = torch.randn(3, 4).to(device)
z = torch.mm(x, y)
print('Matmul result shape:', z.shape)
print('Device:', z.device)
```

## Usage Patterns

### Basic Model Transfer
```python
import torch
import torch_directml

device = torch_directml.device()

model = MyModel()
model.to(device)

# Input data
input_data = torch.randn(1, 3, 224, 224).to(device)

# Forward pass
with torch.no_grad():
    output = model(input_data)

print('Output device:', output.device)
```

### Training Loop
```python
import torch
import torch_directml
import torch.nn as nn
import torch.optim as optim

device = torch_directml.device()

model = MyModel().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

for epoch in range(epochs):
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
        
        if batch_idx % 100 == 0:
            print(f'Epoch {epoch}, Batch {batch_idx}, Loss: {loss.item():.4f}')
```

### Mixed Precision (AMP)
```python
import torch
import torch_directml
from torch.cuda.amp import autocast, GradScaler

device = torch_directml.device()
scaler = GradScaler()

model = model.to(device)
model.train()

for data, target in train_loader:
    data, target = data.to(device), target.to(device)
    
    optimizer.zero_grad()
    
    with autocast(device_type='cuda'):  # DirectML uses CUDA AMP path
        output = model(data)
        loss = criterion(output, target)
    
    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()
```

## 
C:\Vault\DirectML Alternative for Windows PyTorch.md


Performance Comparison (Radeon 780M)

| Workload | ROCm 7.2 | DirectML | CPU Only | Notes |
|----------|----------|----------|----------|-------|
| **ResNet-18 Training (CIFAR-10)** | 3.2 min/epoch | 4.1 min/epoch | 12 min/epoch | 22% slower than ROCm |
| **Llama-3.2-3B Inference (128 tok)** | 28 tok/s | 18 tok/s | 8 tok/s | 36% slower than ROCm |
| **Whisper Large-v3 (10 min)** | 1.1 min | 1.8 min | 4.2 min | 64% slower than ROCm |
| **Stable Diffusion XL (512x512)** | 12 sec | 18 sec | 45 sec | 50% slower than ROCm |
| **ACE-Step (30s music)** | 45 sec | 1.1 min | 2.5 min | 47% slower than ROCm |

## Limitations vs ROCm

| Feature | ROCm 7.2 | DirectML | Impact |
|---------|----------|----------|--------|
| **FlashAttention** | ✅ Native HIP | ❌ Not supported | Slower attention |
| **FlashInfer/vLLM** | ✅ Full support | ❌ Not supported | No optimized LLM serving |
| **HIP Graphs** | ✅ Native | ❌ Not supported | No graph capture |
| **Multi-GPU** | ✅ HIP_VISIBLE_DEVICES | ⚠️ Complex | Limited scaling |
| **Custom Kernels** | ✅ HIP C++ | ❌ Not supported | Less optimization |
| **Driver Dependency** | Adrenalin 26.1.1+ | Windows built-in | Easier setup |

## Advanced Configuration

### Device Selection (Multi-GPU)
```python
import torch_directml

# List available devices
devices = torch_directml.list_devices()
for i, d in enumerate(devices):
    print(f'Device {i}: {d}')

# Select specific GPU
device = torch_directml.device(torch_directml.devices()[1])  # Second GPU
```

### Memory Management
```python
import torch_directml

device = torch_directml.device()

# Check memory
print('Allocated:', torch_directml.memory_allocated(device))
print('Reserved:', torch_directml.memory_reserved(device))

# Clear cache
torch_directml.empty_cache()
```

### Environment Variables
```cmd
# Force specific adapter (0 = first GPU)
set DML_VISIBLE_DEVICES=0

# Enable debug logging
set DML_LOG_LEVEL=info

# Force WARP (software fallback) for debugging
set DML_FORCE_WARP=1
```

## Integration with Our Stack

### Radio ArmsgeddonFM (Voicebox on DirectML)
```python
# voicebox_directml.py
import torch
import torch_directml

device = torch_directml.device()

# Voicebox model
model = Voicebox().to(device)

# Generation
with torch.no_grad():
    audio = model.generate(text, speaker_embedding).to('cpu')

# Performance: ~2x slower than ROCm but works without ROCm driver
```

### GodModeCoder Evolution (PyTorch Models)
```python
# In evolution_cycle.py — fallback device selection
def get_device():
    import torch
    try:
        import torch_directml
        if torch_directml.is_available():
            return torch_directml.device()
    except ImportError:
        pass
    
    if torch.cuda.is_available():
        return torch.device('cuda')
    return torch.device('cpu')

# All models use get_device()
```

### Paranoidx (No GPU Needed — CPU Only)
```python
# Paranoidx doesn't need GPU, but if running ML anomaly detection:
device = torch.device('cpu')  # Simpler, no driver dependencies
```

## Troubleshooting

### Issue: "No DirectML devices found"
```python
import torch_directml
print(torch_directml.list_devices())

# If empty:
# 1. Update Windows (19041+)
# 2. Update GPU drivers (Adrenalin for AMD, Game Ready for NVIDIA)
# 3. Reinstall torch-directml
pip uninstall torch-directml torch && pip install torch-directml
```

### Issue: OOM on iGPU (Shared Memory)
```python
# DirectML uses shared system RAM
# Limit batch size
batch_size = 4  # Instead of 16

# Gradient accumulation
accumulation_steps = 4
for i, (data, target) in enumerate(loader):
    data, target = data.to(device), target.to(device)
    output = model(data)
    loss = criterion(output, target) / accumulation_steps
    loss.backward()
    
    if (i + 1) % accumulation_steps == 0:
        optimizer.step()
        optimizer.zero_grad()
```

### Issue: Slow Performance
```python
# 1. Use channels-last memory format
model = model.to(memory_format=torch.channels_last)
input = input.to(memory_format=torch.channels_last)

# 2. Disable gradient for inference
with torch.no_grad():
    output = model(input)

# 3. Use torch.compile (PyTorch 2.0+)
model = torch.compile(model, backend='directml')  # Experimental
```

## DirectML vs ROCm Decision Matrix

| Factor | Choose ROCm | Choose DirectML |
|--------|-------------|-----------------|
| **Performance Critical** | ✅ | ❌ |
| **Driver Issues** | ❌ | ✅ |
| **Unsupported GPU (pre-RDNA 3)** | ❌ | ✅ |
| **Need FlashAttention/vLLM** | ✅ | ❌ |
| **Quick Setup / No Driver Reinstall** | ❌ | ✅ |
| **Multi-Vendor GPU (AMD+NVIDIA)** | ❌ | ✅ |
| **Production LLM Serving** | ✅ | ❌ |
| **Quick Prototyping** | ❌ | ✅ |

## Future: DirectML 2.0 / WebNN

- **DirectML 2.0** (Windows 11 24H2+): Better operator coverage, improved performance
- **WebNN API**: Web standard for ML, DirectML as backend
- **ONNX Runtime DirectML EP**: Production deployment path

## References
- **torch-directml PyPI**: https://pypi.org/project/torch-directml/
- **Microsoft DirectML Docs**: https://learn.microsoft.com/en-us/windows/ai/directml/
- **PyTorch DirectML Blog**: https://discuss.pytorch.org/t/amd-rdna-2-and-direct-ml/93024
- **GPUOpen Guide**: https://gpuopen.com/learn/pytorch-windows-amd-llm-guide/
- **Voicebox PR #538**: https://github.com/jamiepine/voicebox/pull/538 (ROCm + DirectML dual support)