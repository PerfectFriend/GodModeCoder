---
name: radio_music_pipeline
description: "Free 24/7 radio music - local gen, free APIs, scheduling, full broadcast automation with TTS, evolution cycles, strict program schedule."
version: 2.0.0
author: Hermes Agent
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [radio, music, generation, riffusion, musicgen, playlist, scheduling, amd-igpu, tts, automation, evolution]
    schedule: "every 4h"
    category: mlops
---

# Radio Music Pipeline — Free 24/7 Background Music

Полностью бесплатный пайплайн фоновой музыки для Radio ArmsgeddonFM.
Работает на AMD Radeon 780M (16 GB UMA) без облачных затрат.

## Архитектура

```
music_pipeline/
├── sources/
│   ├── local_generation/     # Riffusion, MusicGen, Stable Audio Open, Bark
│   ├── free_apis/            # Mubert Render (free), YouTube Audio Library, FMA, Jamendo
│   └── cc0_libraries/        # Pixabay, Free Music Archive, Openverse, OpenGameArt
├── processing/
│   ├── normalizer.py         # LUFS -14, peak -1 dB, 44.1kHz/48kHz
│   ├── tagger.py             # ID3: genre, mood, bpm, energy, era
│   └── looper.py             # Seamless loop points (crossfade detection)
├── scheduling/
│   ├── scheduler.py          # Cron: every 4h refresh, hour-based presets
│   ├── presets.yaml          # night_ambient, day_chill, morning_energy, late_night
│   └── playlist_builder.py   # Smart shuffle: no repeat < 2h, mood transitions
├── output/
│   ├── /music/background/    # Active rotation (symlinks to current tracks)
│   ├── /music/archive/       # All generated/downloaded tracks
│   └── /music/staging/       # New tracks awaiting QC
└── mixer/
    └── ducking.py            # ffmpeg sidechain: music -18dB under voice
```

## Локальная генерация (на AMD 780M / 16 GB UMA)

| Модель | Качество | Скорость (CPU) | VRAM/RAM | Лицензия | Статус |
|--------|----------|----------------|----------|----------|--------|
| **Riffusion** | ⭐⭐ | ~10 сек/трек | 2-4 GB RAM | MIT | ❌ HF download broken, dependency hell |
| **MusicGen (Meta)** | ⭐⭐⭐ | ~2-3 мин/трек (30 сек) | CPU only | CC-BY-NC | ✅ **РАБОТАЕТ НА CPU** (musicgen-small, загружен локально через hf-mirror.com) |
| **Stable Audio Open** | ⭐⭐⭐⭐ | ~30-60 сек | 6-8 GB RAM | Open | ⏳ Не тестировано |
| **Bark (Suno)** | ⭐⭐ | ~30 сек | 4-6 GB RAM | MIT | ⏳ Не тестировано |
| **AudioLDM2** | ⭐⭐⭐ | ~1 мин | 6-8 GB RAM | MIT | ⏳ Не тестировано |
| **🎯 Процедурная (FM/аддитивный)** | ⭐⭐ | **<1 сек/трек** | **CPU only** | **MIT** | ✅ **РАБОТАЕТ СРАЗУ** |

**Рекомендация для продакшена: Комбо MusicGen (качество) + Процедурная (скорость/фоллбэк)**

### MusicGen CPU Generation — Working (Aug 2026)

Модель `musicgen-small` скачана локально в `C:/Users/tomas/ai-radio/models/musicgen-small/` через hf-mirror.com. Генерация на CPU работает стабильно (30 сек за ~2-3 мин на Ryzen 7 255).

```python
from audiocraft.models import MusicGen
import torch

# Load directly from local directory on CPU
model = MusicGen.get_pretrained('C:/Users/tomas/ai-radio/models/musicgen-small', device='cpu')
model.set_generation_params(duration=30, top_k=250, top_p=0.9, temperature=1.0, cfg_coef=3.0)

with torch.no_grad():
    wav = model.generate(['ambient electronic, 90 bpm, chill, seamless loop'], progress=True)

import torchaudio
torchaudio.save('output.wav', wav[0].cpu(), model.sample_rate)  # 32000 Hz
```

См. `musicgen_directml` skill → `scripts/generate_music.py` для production-ready скрипта генерации часовых блоков (120 сегментов с crossfade).

### Процедурная генерация — production-ready fallback

```python
# scripts/procedural_music.py
import numpy as np
from scipy.io import wavfile

def fm_synth(duration=30, sr=44100, carrier_freq=220, mod_ratio=2.0, mod_index=5.0, 
             env_attack=0.1, env_decay=0.3, env_sustain=0.5, env_release=1.0):
    """FM synthesis — classic bell/pad tones."""
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    modulator = np.sin(2 * np.pi * carrier_freq * mod_ratio * t)
    carrier = np.sin(2 * np.pi * carrier_freq * t + mod_index * modulator)
    
    # ADSR envelope
    env = np.ones_like(t)
    attack_samples = int(env_attack * sr)
    decay_samples = int(env_decay * sr)
    release_samples = int(env_release * sr)
    sustain_start = attack_samples + decay_samples
    sustain_end = len(t) - release_samples
    
    env[:attack_samples] = np.linspace(0, 1, attack_samples)
    env[attack_samples:sustain_start] = np.linspace(1, env_sustain, decay_samples)
    env[sustain_start:sustain_end] = env_sustain
    env[sustain_end:] = np.linspace(env_sustain, 0, release_samples)
    
    return carrier * env

def additive_synth(duration=30, sr=44100, fundamental=110, harmonics=None, 
                   env_attack=0.5, env_release=2.0):
    """Additive synthesis — organ/pad textures."""
    if harmonics is None:
        harmonics = [(1, 1.0), (2, 0.5), (3, 0.33), (4, 0.25), (5, 0.2)]
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    signal = np.zeros_like(t)
    for h, amp in harmonics:
        signal += amp * np.sin(2 * np.pi * fundamental * h * t)
    
    # Slow attack/release envelope
    env = np.ones_like(t)
    attack = int(env_attack * sr)
    release = int(env_release * sr)
    env[:attack] = np.linspace(0, 1, attack)**2
    env[-release:] = np.linspace(1, 0, release)**2
    return signal * env / len(harmonics)

def noise_based(duration=30, sr=44100, noise_type='pink', 
                filter_cutoff=2000, resonance=2.0, env_attack=0.01, env_release=0.5):
    """Filtered noise — percussive, wind, rain textures."""
    from scipy import signal
    n = int(sr * duration)
    if noise_type == 'white':
        noise = np.random.normal(0, 1, n)
    elif noise_type == 'pink':
        # Voss-McCartney pink noise
        rows = 16
        array = np.random.normal(0, 1, (rows, n))
        noise = np.sum(array, axis=0) / rows
    elif noise_type == 'brown':
        noise = np.cumsum(np.random.normal(0, 1, n))
        noise = noise / np.max(np.abs(noise))
    
    # Simple lowpass
    b, a = signal.butter(2, filter_cutoff / (sr/2), btype='low')
    filtered = signal.filtfilt(b, a, noise)
    
    # Envelope
    env = np.ones(n)
    attack = int(env_attack * sr)
    release = int(env_release * sr)
    env[:attack] = np.linspace(0, 1, attack)
    env[-release:] = np.linspace(1, 0, release)
    return filtered * env

# Preset factory
RADIO_PRESETS_PROCEDURAL = {
    "morning": lambda: fm_synth(30, 44100, carrier_freq=220, mod_ratio=2.0, mod_index=3, 
                               env_attack=0.05, env_decay=0.2, env_sustain=0.7, env_release=0.5) 
                       + 0.3 * additive_synth(30, 44100, fundamental=110, harmonics=[(1,1),(2,0.5),(3,0.3),(5,0.15)]),
    "day_chill": lambda: additive_synth(30, 44100, fundamental=146, harmonics=[(1,1),(2,0.4),(3,0.25),(4,0.15),(6,0.1)]) 
                        + 0.2 * noise_based(30, 44100, 'pink', filter_cutoff=3000),
    "evening_synthwave": lambda: fm_synth(30, 44100, carrier_freq=110, mod_ratio=1.5, mod_index=8,
                                env_attack=0.1, env_decay=0.3, env_sustain=0.6, env_release=1.0),
    "night_ambient": lambda: additive_synth(30, 44100, fundamental=55, harmonics=[(1,1),(2,0.6),(3,0.4),(4,0.2),(5,0.15)],
                                env_attack=2.0, env_release=5.0)
                       + 0.15 * noise_based(30, 44100, 'brown', filter_cutoff=800),
    "late_night_drone": lambda: additive_synth(30, 44100, fundamental=41, harmonics=[(1,1),(2,0.7),(3,0.5),(4,0.3)],
                                    env_attack=5.0, env_release=10.0)
                        + 0.1 * noise_based(30, 44100, 'pink', filter_cutoff=400),
}
```

### Генерация часовых блоков

```python
def generate_hour_block(preset: str, duration_sec: int = 3600) -> np.ndarray:
    """Generate 1-hour seamless block from 30-sec procedural loops."""
    chunk_fn = RADIO_PRESETS_PROCEDURAL[preset]
    chunk_duration = 30
    num_chunks = duration_sec // chunk_duration
    chunks = []
    
    for i in range(num_chunks):
        chunk = chunk_fn()
        # Add slight variation per chunk
        if i > 0:
            chunk = chunk * (0.95 + 0.1 * np.random.random())
        chunks.append(chunk)
    
    # Crossfade between chunks (500ms)
    crossfade = int(0.5 * 44100)
    result = chunks[0]
    for chunk in chunks[1:]:
        result[-crossfade:] *= np.linspace(1, 0, crossfade)
        chunk[:crossfade] *= np.linspace(0, 1, crossfade)
        result = np.concatenate([result[:-crossfade], result[-crossfade:] + chunk[:crossfade], chunk[crossfade:]])
    
    return result[:duration_sec * 44100]
```

### Riffusion — быстрый старт

```bash
# 1. Установка
cd /c/Users/tomas/ai-radio
python -m venv .venv-riffusion
.c\Users\tomas\ai-radio\.venv-riffusion\Scripts\activate
pip install riffusion torch torchaudio --index-url https://download.pytorch.org/whl/cpu

# 2. Генерация лупа (10 сек, ambient)
python -c "
from riffusion import RiffusionPipeline
pipe = RiffusionPipeline.from_pretrained('riffusion/riffusion-model-v1')
prompt = 'ambient electronic, chill, 90 bpm, seamless loop, no drums'
audio = pipe(prompt, num_inference_steps=20, width=512).audio
audio.export('loop_ambient_90bpm.wav', format='wav')
"
```

### MusicGen (Meta) — лучшее качество

```bash
# Установка (DirectML для AMD)
pip install torch-directml transformers audiocraft

# Генерация
python -c "
from audiocraft.models import MusicGen
model = MusicGen.get_pretrained('facebook/musicgen-small')
model.set_generation_params(duration=30)
wav = model.generate(['ambient electronic, 90 bpm, chill, seamless loop'])
torchaudio.save('musicgen_ambient.wav', wav[0].cpu(), 32000)
"
```

## Бесплатные источники (скачивание)

### Скрипт массового скачивания

```python
# scripts/download_free_music.py
# Источники:
# 1. YouTube Audio Library (1500+ треков) - через yt-dlp
# 2. Free Music Archive (FMA) - API + CC0 фильтр
# 3. Pixabay Music - 3000+ треков, CC0
# 4. Jamendo - поиск по жанрам (ambient, chill, synthwave)
# 5. Openverse (Creative Commons) - фильтр по лицензии
# 6. OpenGameArt - игровая музыка, CC0
```

### Структура папок

```
/music/
├── background/           # Активная ротация (симлинки)
│   ├── ambient/
│   ├── chill/
│   ├── energy/
│   └── night/
├── archive/              # Все треки
│   ├── local_gen/        # Riffusion, MusicGen, Stable Audio
│   ├── free_apis/        # Mubert Render, YouTube Audio Library
│   └── cc0/              # FMA, Jamendo, Pixabay, Openverse
└── staging/              # Новые треки на проверке
```

## Расписание (Cron каждые 4 часа)

| Время | Пресет | Настройка |
|-------|--------|-----------|
| 06:00 | morning_energy | bpm 110-120, major, energy 0.7 |
| 10:00 | day_chill | bpm 90-100, neutral, energy 0.4 |
| 14:00 | day_chill | bpm 95-105, slight major |
| 18:00 | streaming_chill | bpm 85-95, minor, energy 0.3 |
| 22:00 | night_ambient | bpm 70-80, minor, energy 0.2 |
| 02:00 | late_night | bpm 60-70, minor, energy 0.1 |

## Плейлист-менеджер (умный шफल)

- Никаких повторов < 2 часа
- Плавные переходы настроения (crossfade 5-10 сек)
- Весовые коэффициенты: новизна > популярность > разнообразие жанров
- Жесткие лимиты: не более 2 трека одного артиста в час

## Микшер (Ducking под голос)

```bash
# ffmpeg sidechain: музыка -18dB под голосом
ffmpeg -i voice.wav -i music.wav \
  -filter_complex "[1:a]volume=0.125[bg];[0:a][bg]sidechaincompress=threshold=0.05:ratio=20:attack=5:release=100[out]" \
  -map "[out]" mixed.wav
```

- Порог: -20 dBFS
- Ratio: 20:1
- Attack: 5 ms
- Release: 100 ms
- Makeup gain: 0 dB

## Интеграция с DJ (dj.py)

```python
# scripts/music_manager.py
class MusicManager:
    def get_background_track(self, hour: int) -> Path:
        preset = self.get_preset_for_hour(hour)
        track = self.ensure_fresh_track(preset, max_age_hours=4)
        return track

    def get_preset_for_hour(self, hour: int) -> str:
        if 6 <= hour < 10: return "morning_energy"
        elif 10 <= hour < 18: return "day_chill"
        elif 18 <= hour < 23: return "streaming_chill"
        else: return "night_ambient"
```

## Конфиг (music_pipeline.yaml)

```yaml
generation:
  default_engine: "riffusion"  # riffusion | musicgen | stable_audio
  fallback_order: ["riffusion", "musicgen", "stable_audio"]
  duration_seconds: 300  # 5 min loops
  sample_rate: 44100

sources:
  local:
    riffusion:
      model: "riffusion/riffusion-model-v1"
      steps: 20
    musicgen:
      model: "facebook/musicgen-small"
      duration: 30
  free_apis:
    mubert_render: true
    youtube_audio_library: true
    fma: true
    jamendo: true
    pixabay: true

scheduling:
  interval_hours: 4
  presets:
    morning_energy: {bpm: [110,120], key: "major", energy: 0.7}
    day_chill: {bpm: [90,100], key: "neutral", energy: 0.4}
    streaming_chill: {bpm: [85,95], key: "minor", energy: 0.3}
    night_ambient: {bpm: [70,80], key: "minor", energy: 0.2}
    late_night: {bpm: [60,70], key: "minor", energy: 0.1}

mixer:
  ducking:
    threshold_db: -20
    ratio: 20
    attack_ms: 5
    release_ms: 100
    music_gain_db: -18
```

## Запуск

```bash
# 1. Генерация фонового трека на 1 час (процедурная — мгновенно)
cd /c/Users/tomas/ai-radio
/c/Users/tomas/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe scripts/procedural_music.py --preset night_ambient --duration 3600

# 2. Запуск планировщика (каждые 4 часа)
python scripts/music_scheduler.py --daemon

# 3. Ручная генерация для теста (30 сек)
python -m scripts.procedural_music --preset day_chill --duration 30

# 4. Все пресеты сразу (для заполнения архива)
for p in morning day_chill evening_synthwave night_ambient late_night_drone; do
  python scripts/procedural_music.py --preset $p --duration 300
done
```

## Скрипты в скилле

- `scripts/procedural_music.py` — **production-ready** процедурная генерация (FM, additive, noise, supersaw). Никаких ML зависимостей, работает мгновенно на CPU.
- `scripts/mubert_client.py` — Mubert API клиент (платный fallback).

## Связанные скиллы

- `local-ai-stack` — локальные модели (Riffusion, MusicGen, Stable Audio Open)
- `news_scraper_production` — новости для голосового контента
- `master-fm-radio` — полный радио-пайплайн (DJ, TTS, микшер)
- `qwen3-tts-directml` — TTS для голосового контента

## Критические ссылки

- `references/dependency-hell-windows.md` — **полный разбор почему ML генерация не работает на Windows/DirectML**, что пробовано, рабочий fallback (процедурная генерация)

## Ссылки

- Riffusion: https://github.com/riffusion/riffusion
- MusicGen: https://github.com/facebookresearch/audiocraft
- Stable Audio Open: https://github.com/Stability-AI/stable-audio-tools
- YouTube Audio Library: https://www.youtube.com/audiolibrary/music
- Free Music Archive: https://freemusicarchive.org/
- Jamendo: https://www.jamendo.com/
- Pixabay Music: https://pixabay.com/music/
- Openverse: https://openverse.org/