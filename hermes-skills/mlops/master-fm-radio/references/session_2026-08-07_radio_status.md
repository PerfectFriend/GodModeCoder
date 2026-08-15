# Session 2026-08-07: Master-FM Radio Operational Status

## Current Running Services

| Service | Port | PID | Status | Started |
|---------|------|-----|--------|---------|
| DJ (Master-FM) | 8090 | 29180 | ✅ ON AIR | 00:22:25 |
| Hermes Gateway | — | 4488 | ✅ Running | 22:00:38 |

## DJ Playlist Status
```
Playlist: [('news', 'breaking_world_20260806_184525.wav'),
           ('news', 'breaking_tech_20260806_193306.wav'),
           ('news', 'breaking_sport_20260806_193737.wav'),
           ('news', 'breaking_local_20260806_185339.wav')]
```
- Only 4 news blocks in current playlist
- **Cache has NO music yet** — need to run `gen_music.py`
- Warning: `silence_header.mp3` was missing, generated via ffmpeg (9239 bytes)

## DJ Stream Details
- **URL**: `http://localhost:8090/radio`
- **Ring buffer**: 5 seconds
- **Mastering chain**: highpass, gate, EQ, loudnorm, compand, limiter
- **Professional mastering**: highpass 30Hz, agate, equalizer, loudnorm (-14 LUFS), alimiter (limit=0.89), brickwall (limit=0.94)
- **Ring buffer**: 5 seconds for late joiners

## Pulse Check Results (Current)
| Node | Status | Reason |
|------|--------|--------|
| **dj** | ✅ ЖИВ | Port 8090 |
| **watchdog** | ✅ ЖИВ | pulse.py works |
| **radio_cache** | ✅ ЖИВ | Files exist |
| **superguard** | ✅ ЖИВ | Files exist |
| **gardener** | ☠ МЁРТВ | No HTTP 8080 |
| **music_pipeline** | ☠ МЁРТВ | gen_music.py not running |
| **voice** | ☠ МЁРТВ | gen_voice_content.py not running |
| **isle_client** | ☠ МЁРТВ | flutter not found |

## DJ Verification
```bash
# Check if DJ is on air
curl -s http://localhost:8090/radio | head -c 100
# Should return MP3 stream header (ID3 + MP3 frames)
```

## Services to Start
1. **Music Pipeline** (gen_music.py) — generate music per presets
2. **Voice Service** (gen_voice_content.py) — TTS for news, ads, jingles
3. **Health Endpoint** (:8080/api/health) — for gardener node
4. **Flutter** for isle_client node

## DJ Process Management
- **Process**: `scripts/dj.py` running on port 8090
- **PID**: 29180 (background, notify_on_complete)
- **Playlist**: Currently only 4 news blocks (cache has NO music yet)
- **Ring buffer**: 5 seconds for late joiners
- **Mastering chain**: highpass, gate, EQ, loudnorm, compand, limiter

## Cache Status
```
cache/
├── music/          # EMPTY - need gen_music.py
├── news/           # 4 breaking news files
├── jingles/        # EMPTY
├── ads/            # EMPTY
├── audiobooks/     # EMPTY
└── ads/            # EMPTY
```

## Next Actions
1. Run `gen_music.py` to populate music cache (per presets)
2. Run `gen_voice_content.py` for voice content
3. Add health endpoint on :8080 for gardener node
4. Install Flutter for isle_client node
5. Verify SuperGuard token from sguard.env