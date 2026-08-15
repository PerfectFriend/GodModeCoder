# Model Download from hf-mirror.com (China Mirror)

When Hugging Face is blocked or slow, use hf-mirror.com as a drop-in replacement.

## Download MusicGen-small

```bash
# Set endpoint
export HF_ENDPOINT=https://hf-mirror.com

# Download all files for facebook/musicgen-small
cd /c/Users/tomas/ai-radio/models/musicgen-small

# Small config files
for f in config.json generation_config.json preprocessor_config.json \
         special_tokens_map.json tokenizer.json tokenizer_config.json \
         spiece.model .gitattributes README.md; do
    curl -L -o "$f" "https://hf-mirror.com/facebook/musicgen-small/resolve/main/$f?download=true"
done

# Large model weights (~2.2 GB safetensors)
curl -L -o "model.safetensors" "https://hf-mirror.com/facebook/musicgen-small/resolve/main/model.safetensors?download=true"

# PyTorch state_dict (~800 MB) - required by audiocraft loaders.py
curl -L -o "state_dict.bin" "https://hf-mirror.com/facebook/musicgen-small/resolve/main/state_dict.bin?download=true"

# Compression model (~225 MB)
curl -L -o "compression_state_dict.bin" "https://hf-mirror.com/facebook/musicgen-small/resolve/main/compression_state_dict.bin?download=true"
```

## Convert model.safetensors → state_dict.bin (if only safetensors downloaded)

```python
import torch
from safetensors.torch import load_file

state_dict = load_file('model.safetensors', device='cpu')
torch.save(state_dict, 'state_dict.bin')
```

## Verification

```bash
ls -la /c/Users/tomas/ai-radio/models/musicgen-small/
# Should have:
# config.json, generation_config.json, preprocessor_config.json
# special_tokens_map.json, tokenizer.json, tokenizer_config.json
# spiece.model, .gitattributes, README.md
# model.safetensors (2.2 GB)
# state_dict.bin (800 MB)
# compression_state_dict.bin (225 MB)
```

## Load in Python

```python
from audiocraft.models import MusicGen

# Load directly from local directory
model = MusicGen.get_pretrained('C:/Users/tomas/ai-radio/models/musicgen-small', device='cpu')
# OR
model = MusicGen.get_pretrained('facebook/musicgen-small')  # uses HF cache
```

## Other Models (Riffusion, Stable Audio, etc.)

```bash
# Riffusion v1
export HF_ENDPOINT=https://hf-mirror.com
mkdir -p models/riffusion-model-v1
cd models/riffusion-model-v1
for f in config.json model.safetensors scheduler_config.json; do
    curl -L -o "$f" "https://hf-mirror.com/riffusion/riffusion-model-v1/resolve/main/$f?download=true"
done

# Stable Audio Open
mkdir -p models/stable-audio-open-1.0
cd models/stable-audio-open-1.0
for f in config.json model.safetensors; do
    curl -L -o "$f" "https://hf-mirror.com/stabilityai/stable-audio-open-1.0/resolve/main/$f?download=true"
done
```