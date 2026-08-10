# AI-Radio «Мастер-ФМ» — DJ Streaming Implementation

## Overview
Complete local AI radio station with:
- **Night batch (20:00-07:00)**: Full content generation (music, news, ads, jingles, audiobooks)
- **Day mode (07:00-20:00)**: Only breaking news + stream from cache
- **HTTP MP3 stream** at `http://localhost:8090/radio` (128 kbps, 44.1 kHz)

## Architecture

```
cache/
├── music/<style>/<lang>/     # ACE-Step generated tracks
├── news/<category>/          # GPU-TTS generated news
├── ads/                      # GPU-TTS generated ads
├── jingles/<theme>/          # GPU-TTS generated jingles
├── audiobooks/               # Future: long-form content
└── staging/                  # Song review zone (ace-step-song-protocol)
```

## DJ Agent (`scripts/dj.py`)

### Key Components

1. **Playlist Builder** (`build_playlist`)
   - Night mode: all categories, more content
   - Day mode: reduced content, only breaking news
   - Jingles every N tracks (configurable)

2. **RingBuffer** (5 seconds, 44.1 kHz, stereo)
   - Thread-safe circular buffer for live streaming
   - Provides instant tail for new listeners

3. **FFmpeg Pipeline**
   - Single persistent ffmpeg process reading `playlist.txt` (concat, looped)
   - Outputs MP3 128k to stdout
   - Pump thread fills RingBuffer

4. **HTTP Server**
   - Per-connection handler threads
   - Sends RingBuffer tail → live stream
   - No per-client ffmpeg (saves CPU)

### Critical Implementation Details

**MP3 Header Handling**: MP3 decoders self-synchronize on frame sync (0xFFE0). RingBuffer tail may start mid-frame, but decoder recovers within ~1 frame (~26ms at 44.1kHz). No need to pre-buffer ID3 headers.

**Concat Playlist Format**:
```
file 'C:\Users\tomas\ai-radio\cache\music\rock\track1.mp3'
file 'C:\Users\tomas\ai-radio\cache\jingles\funny\jingle1.wav'
...
```
Written by `write_concat_list()` with proper quote escaping.

**FFmpeg Command**:
```bash
ffmpeg -hide_banner -loglevel error -stream_loop -1 \
  -f concat -safe 0 -i playlist.txt \
  -ar 44100 -b:a 128k -f mp3 pipe:1
```

## GPU-TTS Integration (`gen_voice_content.py`)

Replaced CPU Voicebox with GPU-TTS (Qwen3-TTS 1.7B on Radeon 780M via torch-directml).

### CLI Wrapper (`scripts/gpu_tts_cli.py`)
Compatible with `voicebox_tts.py` interface:
```bash
python gpu_tts_cli.py <input_text_file> <output_wav_file>
```

**Key features**:
- Reads UTF-8 text from file → writes to temp file for `gpu_tts_test.py`
- Runs in clean env: `env -u PYTHONPATH -u VIRTUAL_ENV ./tts-dml-env/Scripts/python.exe`
- Timeout 300s (model load + synthesis)
- Copies result from `ai-radio/gpu_tts_test.wav` to target path

### Integration in `gen_voice_content.py`:
```python
def synth(text: str, out_path: str) -> bool:
    tmp_txt = os.path.join(RADIO_ROOT, "scripts", "_voice_input.txt")
    with open(tmp_txt, "w", encoding="utf-8") as f:
        f.write(text)
    r = subprocess.run(
        [sys.executable, GPU_TTS_CLI, tmp_txt, out_path],
        capture_output=True, text=True, timeout=300,
    )
    return r.returncode == 0 and os.path.exists(out_path) and os.path.getsize(out_path) > 1000
```

## Cron Jobs

| Job ID | Schedule | Description |
|--------|----------|-------------|
| `master-fm-night-batch` | `0 20 * * *` | Full generation: music + voice content |
| `master-fm-day-news` | `*/15 7-19 * * *` | Breaking news only |

Both use `workdir: C:\Users\tomas\ai-radio` and load `qwen3-tts-directml` skill.

## Performance & Memory

| Component | VRAM | System RAM (peak) | Notes |
|-----------|------|-------------------|-------|
| Ollama qwen3:8b | ~6 GB | minimal | 100% GPU via Vulkan |
| GPU-TTS (gen) | ~3-4 GB | WS ~2.4 GB / PM ~11.5 GB | Freed after each process |
| ACE-Step (music) | — | CPU only | ~30s per 30s track |
| RingBuffer | — | ~5 MB | Fixed 5s buffer |
| FFmpeg | — | ~50 MB | Single process |

**Total VRAM**: ~10 GB / 20 GB available on 780M
**System RAM**: GPU-TTS processes sequential → peak PM ~11.5 GB, freed after each

## Configuration (`config.yaml`)

Key sections:
- `radio.schedule` — timing blocks
- `radio.modes.night_batch` / `day_mode` — generation flags
- `radio.generation` — cache TTLs
- `radio.sources` — style/category definitions
- `radio.dj` — voice profile, intro lines

## Testing

```bash
# Test DJ stream
cd /c/Users/tomas/ai-radio && python scripts/dj.py
# → HTTP 200 at localhost:8090/radio

# Test GPU-TTS
python scripts/gpu_tts_cli.py input.txt output.wav

# Test music generation
python scripts/gen_music.py --style rock --count 1 --duration 30

# Full night batch
python scripts/night_batch.py
```

## Files

| File | Purpose |
|------|---------|
| `scripts/dj.py` | Main DJ agent |
| `scripts/gen_voice_content.py` | Voice content generator (GPU-TTS) |
| `scripts/gpu_tts_cli.py` | GPU-TTS CLI wrapper |
| `scripts/gen_music.py` | ACE-Step music generator |
| `scripts/night_batch.py` | Night batch orchestrator |
| `scripts/gpu_tts_test.py` | Core GPU-TTS script |
| `config.yaml` | Radio configuration |
| `cache/` | Content cache (gitignored) |

## Related Skills

- `qwen3-tts-directml` — GPU-TTS on AMD iGPU
- `ace-step-song-protocol` — Content-to-song pipeline