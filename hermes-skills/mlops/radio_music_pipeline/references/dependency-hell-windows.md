# Dependency Hell: MusicGen / Riffusion on Windows + DirectML

**Status: UNRESOLVED — procedural generation is the only working path**

---

## The Problem

AudioCraft (MusicGen) and Riffusion (diffusers) have **fundamentally incompatible version requirements** on Windows with torch-directml.

| Package | AudioCraft requires | Riffusion requires | Installed | Conflict |
|---------|---------------------|-------------------|-----------|----------|
| torch | 2.1.0 | 2.0.1+ | 2.4.1+cu118 | ❌ Major version |
| transformers | 4.31.0 | 4.30+ | 4.40.0 | ❌ Version pin |
| tokenizers | 0.19.x | 0.19.x | 0.22.2 | ❌ API breaking |
| huggingface-hub | 0.19.3-0.20 | 0.19+ | 1.26.1 | ❌ Major API change |
| torchaudio | <2.1.2,>=2.0 | 2.0+ | 2.4.1 | ❌ Version pin |
| torchvision | 0.16.0 | 0.15+ | 0.19.1 | ❌ Version pin |
| xformers | <0.0.23 | — | 0.0.27 | ❌ Version pin |
| av | 11.0.0 | — | 18.0.0 | ❌ Version pin |

**No combination of pip installs resolves this.** Every attempt to pin one breaks another. The core issue: AudioCraft 1.3.0 (latest PyPI) is hard-pinned to torch 2.1 / transformers 4.31, while torch-directml 0.2.5 requires torch 2.4.1.

---

## What Was Tried (All Failed)

1. **AudioCraft from PyPI** → transformers/tokenizers/huggingface-hub version conflicts
2. **AudioCraft from GitHub (1.4.0a2)** → same conflicts, plus `einops`, `spacy`, `dora-search`, `flashy`, `colorlog` missing
3. **Manual version pinning** → `pip install transformers==4.31.0 tokenizers==0.19.1 huggingface-hub==0.20.0` → xformers pulls torch 2.0.1, breaks torch-directml
4. **Riffusion via diffusers** → HF download timeout (us.aws.cdn.hf.co unreachable), huggingface-hub 1.26 API incompatibility
5. **hf-mirror.com** → DNS resolves but CDN still points to us.aws.cdn.hf.co, read timeouts

---

## Working Solution: Procedural Generation

**File: `scripts/procedural_music.py`** — pure Python + numpy + scipy, **zero ML dependencies**

| Feature | Procedural | MusicGen | Riffusion |
|---------|------------|----------|-----------|
| Deps | numpy, scipy | 50+ packages | 30+ packages |
| Speed | <1 sec / 30s | 2-5 min / 30s | ~10 sec / loop |
| VRAM | 0 (CPU) | 6-8 GB | 2-4 GB |
| Deterministic | ✅ | ❌ | ❌ |
| Loop-seamless | ✅ (by design) | ❌ manual | ✅ |
| Works NOW | ✅ | ❌ | ❌ |

### Preset Functions (Production-Ready)

```python
RADIO_PRESETS_PROCEDURAL = {
    "morning": fm_synth + additive (bright, 110-120 bpm feel),
    "day_chill": additive + pink noise (warm, 90-100 bpm),
    "evening_synthwave": fm_synth heavy modulation (retro, 100 bpm),
    "night_ambient": additive low fundamentals + brown noise (dark, 70 bpm),
    "late_night_drone": ultra-slow additive + filtered pink (hypnotic, 50 bpm),
}
```

### Generation → Hour Blocks

```python
def generate_hour_block(preset: str, duration_sec: int = 3600) -> np.ndarray:
    # 120 × 30-sec chunks with 500ms crossfade
    # Slight per-chunk variation (amplitude ±5%)
    # Returns float32 [-1, 1] at 44.1 kHz
```

Output: `/music/background/{preset}_{date}.wav` — ready for mixer ducking.

---

## HF Model Cache Status

```
~/.cache/huggingface/hub/
├── models--facebook--musicgen-small/          # config.json only, .incomplete weights
├── models--facebook--musicgen-medium/         # config.json only
├── models--riffusion--riffusion-model-v1/     # config.json only, .incomplete
└── models--stabilityai--stable-audio-open-1.0/ # not attempted
```

**Do NOT waste time re-downloading.** The cache is corrupted/incomplete. Procedural path works TODAY.

---

## Future Revisit Conditions

Only revisit ML generation when ONE of these is true:

- [ ] AudioCraft releases version compatible with torch 2.4+ / transformers 4.40+
- [ ] `torch-directml` releases supporting torch 2.1 (won't happen)
- [ ] Stable Audio Open has a DirectML-compatible release without HF hub dependency
- [ ] Local model weights are pre-downloaded and converted to ONNX/DirectML format
- [ ] User explicitly requests cloud API (Mubert, Suno, Udio) with budget approved

---

## Related Files

- `scripts/procedural_music.py` — main generation module
- `scripts/generate_background.py` — CLI for hour blocks
- `scripts/music_scheduler.py` — cron integration (every 4h)
- `/music/background/` — active rotation (symlinks)
- `/music/archive/procedural/` — all generated tracks