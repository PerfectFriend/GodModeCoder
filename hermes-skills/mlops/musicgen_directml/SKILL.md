---
name: musicgen_directml
description: "Local MusicGen on DirectML for Radio - AMD 780M."
version: 1.0.0
author: Hermes Agent
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [musicgen, directml, audiocraft, radio]
    category: mlops
---

# MusicGen DirectML for Radio ArmsgeddonFM

Локальная генерация музыки на AMD Radeon 780M через DirectML с использованием AudioCraft MusicGen.

## Архитектура

- **Модель**: facebook/musicgen-small / medium / large (через AudioCraft)
- **Устройство**: DirectML (privateuseone:0) на AMD Radeon 780M
- **VRAM**: 16GB UMA
- **Длительность генерации**: 30 сек (лимит MusicGen)
- **Sample rate**: 32000 Hz

## Предзагрузка модели

```python
from audiocraft.models import MusicGen
import torch_directml

d = torch_directml.device()
model = MusicGen.get_pretrained('facebook/musicgen-small')
model.to(d)
```

## Предзаготовленные пресеты для радио

```python
RADIO_PRESETS = {
    "morning": "upbeat electronic, 110 bpm, energetic, synthesizers, optimistic",
    "day_chill": "chill lo-fi hip hop, 85 bpm, relaxed, jazz samples, background",
    "day_ambient": "ambient electronic, 90 bpm, atmospheric, soft pads, minimal",
    "evening_synthwave": "synthwave, 100 bpm, nostalgic, retro, analog synthesizers",
    "night_ambient": "dark ambient, 60 bpm, minimal, drone, deep bass, meditative",
    "late_night_drone": "drone ambient, 50 bpm, very slow, sub-bass, hypnotic",
    "transition": "short transition sting, 5 seconds, electronic, smooth, radio jingle",
}
```

## Генерация и склейка в часовые блоки

```python
# Генерация 30-секундного сегмента
wav = model.generate([prompt])

# Склейка 120 сегментов (1 час) с кроссфейдом 500ms
full_block = stitch_with_crossfade(segments, crossfade_ms=500)
```

## Конфигурация генерации

```python
model.set_generation_params(
    duration=30,
    top_k=250,
    top_p=0.9,
    temperature=1.0,
    cfg_coef=3.0,
)
```

## Выходные файлы

- `/music/generated/` — отдельные 30-сек треки
- `/music/background/` — часовые блоки (24 файла в сутки)
- `/music/stems/` — стемы для микширования (будущее)

## Запуск

```bash
cd /c/Users/tomas/ai-radio
/c/Users/tomas/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe musicgen_directml.py
# или для суточного цикла:
/c/Users/tomas/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe musicgen_directml.py day
```

## Требования

- torch-directml (установлен)
- audiocraft (установлен)
- soundfile, julius (зависимости audiocraft)
- torch-directml device: privateuseone:0

## Статус (актуально на авг 2026) — РАБОТАЕТ НА CPU

- ✅ **MusicGen-small загружен и генерирует на CPU** (30 сек за ~2-3 мин на Ryzen 7 255)
- ✅ **Model files скачаны локально** через hf-mirror.com: `C:/Users/tomas/ai-radio/models/musicgen-small/` (config.json, model.safetensors, state_dict.bin, tokenizer, compression_state_dict.bin)
- ⚠️ **DirectML операторы неполные** — `aten::clone`, `aten::erfinv` не поддерживаются, fallback на CPU происходит автоматически
- ✅ **Working workflow**: Load model on `device='cpu'` → generate → save WAV
- ❌ **GPU/DirectML ускорение** — пока нестабильно, но загрузка модели на DML работает

## Working CPU Generation Script

```python
import torch
from audiocraft.models import MusicGen

# Load directly on CPU (bypasses DirectML operator issues)
model = MusicGen.get_pretrained('C:/Users/tomas/ai-radio/models/musicgen-small', device='cpu')
model.set_generation_params(duration=30, top_k=250, top_p=0.9, temperature=1.0, cfg_coef=3.0)

# Generate
with torch.no_grad():
    wav = model.generate([prompt], progress=True)

# Save
import torchaudio
torchaudio.save(output_path, wav[0].cpu(), model.sample_rate)
```

## Предзаготовленные пресеты для радио (проверено — работают)

```python
RADIO_PRESETS = {
    "morning": "upbeat electronic, 110 bpm, energetic, synthesizers, optimistic",
    "day_chill": "chill lo-fi hip hop, 85 bpm, relaxed, jazz samples, background",
    "day_ambient": "ambient electronic, 90 bpm, atmospheric, soft pads, minimal",
    "evening_synthwave": "synthwave, 100 bpm, nostalgic, retro, analog synthesizers",
    "night_ambient": "dark ambient, 60 bpm, minimal, drone, deep bass, meditative",
    "late_night_drone": "drone ambient, 50 bpm, very slow, sub-bass, hypnotic",
    "transition": "short transition sting, 5 seconds, electronic, smooth, radio jingle",
}
```

## Генерация часовых блоков (120 сегментов × 30 сек = 1 час)

```python
def generate_hour_block(preset_name: str, output_path: str, crossfade_ms: int = 500):
    segments = []
    for i in range(120):
        wav = model.generate([RADIO_PRESETS[preset_name]], progress=False)
        segments.append(wav[0].cpu())
    
    # Crossfade stitching
    full = stitch_segments(segments, crossfade_ms, model.sample_rate)
    torchaudio.save(output_path, full, model.sample_rate)
```

```python
# scripts/procedural_music.py
# FM synthesis, additive, noise shaping — чистый Python + numpy + scipy
# Генерирует 30-сек лопы за <1 сек, бесшовные, под любой BPM/ключ/жанр
```

См. `radio_music_pipeline` → `procedural_generation` раздел.

## Ссылки на файлы проекта

- `musicgen_directml.py` — основной клиент
- `/music/generated/` — сгенерированные треки
- `/music/background/` — часовые блоки
- `/music/stems/` — стемы (планируется)