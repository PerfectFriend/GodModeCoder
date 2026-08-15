# MusicGen CPU Implementation — Working Path (Aug 2026)

## Summary

**MusicGen-small works on CPU** with local model files downloaded from hf-mirror.com. No DirectML needed for generation.

## Model Setup

```bash
# Model directory: C:/Users/tomas/ai-radio/models/musicgen-small/
# Downloaded via hf-mirror.com (bypasses HF CDN timeouts)

Files needed:
├── config.json
├── generation_config.json
├── preprocessor_config.json
├── special_tokens_map.json
├── tokenizer.json
├── tokenizer_config.json
├── spiece.model
├── .gitattributes
├── README.md
├── model.safetensors          # 2.2 GB
├── compression_state_dict.bin  # 225 MB
└── state_dict.bin             # 802 MB (converted from .safetensors)
```

## Conversion Script

```python
import torch
from safetensors.torch import load_file

state_dict = load_file('model.safetensors', device='cpu')
torch.save(state_dict, 'state_dict.bin')
```

## Python Usage

```python
from audiocraft.models import MusicGen
import torch

# Load on CPU (DirectML has operator support gaps)
model = MusicGen.get_pretrained('C:/Users/tomas/ai-radio/models/musicgen-small', device='cpu')
model.set_generation_params(duration=30, top_k=250, top_p=0.9, temperature=1.0, cfg_coef=3.0)

with torch.no_grad():
    wav = model.generate(['ambient electronic, 90 bpm, chill, seamless loop'], progress=True)

import torchaudio
torchaudio.save('output.wav', wav[0].cpu(), model.sample_rate)  # 32000 Hz
```

## Performance

| Metric | Value |
|--------|-------|
| Generation time (30s) | ~2-3 minutes on Ryzen 7 255 |
| VRAM | 0 (CPU only) |
| Sample rate | 32 kHz |
| Quality | ⭐⭐⭐ (good for background radio) |

## Production Components Created

| File | Purpose |
|------|---------|
| `musicgen_directml.py` | MusicGen client with time-based presets, batch generation |
| `audio_stitcher.py` | Crossfade stitching, hourly track builder |
| `dj_pipeline.py` | Full DJ pipeline: music + news TTS + ducking |
| `evolution_runner.py` | Autonomous cycles: tests → debug → gen → USB backup |

## Presets (Time-Based)

| Time | Preset | Prompt |
|------|--------|--------|
| 06-10 | morning | upbeat electronic, 110 bpm, energetic, synthesizers, optimistic |
| 10-17 | day | chill lo-fi hip hop, 85 bpm, relaxed, jazz samples, background |
| 17-21 | evening | synthwave, 100 bpm, nostalgic, retro, atmospheric |
| 21-24 | night | dark ambient, 60 bpm, minimal, drone, deep bass, meditative |
| 00-06 | late_night | drone ambient, 50 bpm, very slow, sub-bass, hypnotic |

## Cron Integration

```yaml
# radio_evolution cron job
schedule: "every 2h"
command: python evolution_runner.py --single --cycles 1
deliver: "telegram:-1004431090317"
workdir: "C:/Users/tomas/ai-radio"
```

## USB Backup

Location: `D:/backups/radio_armsgeddonfm/`
Format: `radio_A{XX}_cycle{YY}_YYYYMMDD_HHMMSS/`
Contents: source, models, generated music, news, logs, version badge

## Version Badges

Auto-increment: A00, A01, A02...
Stored in: `version_badge.txt`

## Key Insight

**DirectML path failed** due to operator support gaps (`aten::clone` not implemented for AutocastPrivateUse1). CPU path is stable and fast enough for radio background generation (30s track in 2-3 min, can batch overnight).