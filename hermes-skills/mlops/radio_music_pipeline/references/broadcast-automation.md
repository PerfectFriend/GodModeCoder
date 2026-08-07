# Broadcast Automation — Radio ArmsgeddonFM

Full programmatic radio automation with strict schedule, TTS pipeline, and evolution cycles.

## Architecture

```
radio_automation/
├── radio_automation.py       # Main automation class (ProgramScheduler + RadioAutomation)
├── musicgen_directml.py      # MusicGen client (CPU/DirectML, time-based presets)
├── audio_stitcher.py         # Crossfade stitching of 30s segments into hourly tracks
├── dj_pipeline.py            # DJ pipeline: music + news TTS mixing with ducking
├── evolution_runner.py       # Autonomous evolution: tests, debug, generation, USB backups
├── models/musicgen-small/    # Local model (2.2GB weights, loaded from hf-mirror.com)
├── music_output/
│   ├── morning/ day/ evening/ night/ late_night/  # Preset segments
│   └── stitched/             # Hourly mixed tracks
├── radio_output/
│   ├── tts_cache/            # Generated TTS files (time signals, news, ads)
│   └── broadcast_*.wav       # Final assembled broadcast hours
├── newsfeed/                 # TTS-ready news (17 categories from news_scraper_production)
└── D:/backups/radio_armsgeddonfm/  # USB backups per evolution cycle
```

## Program Schedule (Strict)

| Time | Segment | Duration | Details |
|------|---------|----------|---------|
| N:00:00 | Time Signal | 5s | "Radio ArmsgeddonFM. N часов 00 минут. Точное время." |
| N:00:05 | News Block | 3 min | Hot news across all 17 categories |
| N:05:00 | Ad Block | 30s | Self-promo: "Radio Armageddon FM — радио последних дней..." |
| N:08:00 | Music Program | 22 min | Current hour's preset style |
| N:30:00 | Ad Block | 30s | Self-promo (half-hour variant) |
| N:30:30 | Music Program | 27.5 min | **Next hour's preset** (style transition) |

**Preset Mapping:**
- 06-10: morning (upbeat electronic, 110 BPM)
- 10-17: day (chill lo-fi, 85 BPM)
- 17-21: evening (synthwave, 100 BPM)
- 21-24: night (dark ambient, 60 BPM)
- 00-06: late_night (drone ambient, 50 BPM)

## TTS Pipeline

**Primary:** Voicebox (qwen_custom_voice, Ryan preset, profile `e7013ccf-70c7-4f22-a277-e6b3e4ddc4ef`)
**Fallback:** Edge TTS (ru-RU-DmitryNeural) — works reliably

```python
def generate_tts(self, text: str, output_name: str) -> Path:
    # 1. Try Voicebox (if server running on localhost:8000)
    # 2. Fallback to Edge TTS (asyncio + edge_tts.Communicate)
    # 3. Raise if both fail
```

## Evolution Runner (Autonomous)

```bash
# Single cycle: tests → debug → music generation → USB backup
python evolution_runner.py --single --cycles 1

# Continuous: 20 cycles, every 2 hours
python evolution_runner.py --cycles 20 --interval 2 --usb D:/backups/radio_armsgeddonfm
```

**Cron:** `radio_evolution` — every 2h, reports to Telegram group `-1004431090317`

**Each cycle:**
1. Tests (MusicGen import, generation, dir structure)
2. Debug checks (disk space, GPU, model files, USB drive)
3. Music generation (current preset, 30s segment)
4. USB backup to `D:/backups/radio_armsgeddonfm/radio_A{XX}_cycle{YY}_...`

**Version Badges:** Auto-increment A00, A01, A02... stored in `version_badge.txt`

## Generated Assets (This Session)

| File | Purpose |
|------|---------|
| `musicgen_directml.py` | MusicGen client with time-based presets |
| `audio_stitcher.py` | Crossfade stitching, hourly track creation |
| `dj_pipeline.py` | DJ pipeline (music + news + ducking) |
| `evolution_runner.py` | Autonomous 20-cycle evolution with USB backups |
| `radio_automation.py` | Full broadcast automation (schedule, TTS, assembly) |

## Test Results

- **MusicGen-small:** ✅ CPU generation, 30s segments, 32kHz
- **Audio Stitching:** ✅ Crossfade 2s, seamless loops
- **TTS:** ✅ Edge TTS fallback (Dmitry voice) — Voicebox server not responding
- **60-min Broadcast:** ✅ Generated `broadcast_test_2300.wav` (460MB)
- **Schedule Logic:** ✅ 144 events/day, strict hourly structure

## Next: Icecast Streaming

```bash
# Docker Icecast
docker run -d -p 8000:8000 \
  -e ICECAST_PASSWORD=*** \
  -e ICECAST_ADMIN_PASSWORD=*** \
  moul/icecast

# Stream to Icecast
ffmpeg -re -i radio_output/broadcast_test_2300.wav \
  -c:a libmp3lame -b:a 128k \
  -f mp3 icecast://source:radio123@localhost:8000/radio.mp3
```

Then get RTMP keys from `@RadioArmsgeddonFM` (start Live Stream in channel).

## Pitfalls & Fixes (This Session)

| Issue | Fix |
|-------|-----|
| Voicebox server port 8000 blocked by Manager.exe | Use port 8001 (`--port 8001`) |
| Voicebox generation stuck on CPU | Use Edge TTS fallback |
| MusicGen DirectML missing `aten::clone` | Run on CPU (`device='cpu'`) |
| HF download timeout | Use hf-mirror.com for model downloads |
| Edge TTS missing module | `pip install edge-tts` |
| voicebox_tts.py expects file input | Create temp text file, pass path to script |

## Key Code Patterns

### Program Scheduler
```python
class ProgramScheduler:
    def generate_daily_schedule(self, date) -> List[ScheduleEvent]:
        # 6 events per hour × 24 = 144 events/day
        for hour in range(24):
            # N:00:00 - Time Signal (5s)
            # N:00:05 - News Block (3 min)
            # N:05:00 - Ad Block (30s)
            # N:08:00 - Music (22 min, current preset)
            # N:30:00 - Ad Block (30s, half-hour variant)
            # N:30:30 - Music (27.5 min, NEXT preset)
```

### TTS with Fallback
```python
def generate_tts(self, text: str, output_name: str) -> Path:
    # 1. Try Voicebox (temp text file → voicebox_tts.py)
    # 2. Fallback: Edge TTS (asyncio + edge_tts.Communicate)
    # 3. Raise if both fail
```

### Music Assembly
```python
# 1. Ensure segments exist for preset (generate if needed)
# 2. Stitch with 2s crossfade to target duration
# 3. Mix TTS blocks at scheduled offsets with ducking (0.15 level, 100ms fade)
```