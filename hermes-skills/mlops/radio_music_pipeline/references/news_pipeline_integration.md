# News Scraper → Radio Pipeline Integration

## Cross-References

This document links `news_scraper_production` with other Radio ArmsgeddonFM skills.

### Downstream Consumers

| Skill | Consumes | Purpose |
|-------|----------|---------|
| `master-fm-radio` | `/newsfeed/<category>/*.txt` | TTS voiceovers for hourly news blocks |
| `qwen3-tts-directml` | Individual .txt files | GPU-accelerated TTS (Voicebox/Qwen3-TTS) |
| `radio_music_pipeline` | — | Background music under news voiceovers |

### Data Flow

```
news_scraper_production.py (hourly cron)
    ↓
/newsfeed/<category>/*.txt  (TTS-ready: "Заголовок. Summary.")
    ↓
master-fm-radio / dj.py
    ├── TTS engine (Voicebox/Qwen3-TTS) → voice.wav
    ├── radio_music_pipeline → background.wav
    ├── Ducking mixer (ffmpeg sidechain) → mixed.wav
    └── Icecast/RTMP output (deferred per user)
```

### Category → Preset Mapping

| News Category | Music Preset | Time Window |
|---------------|--------------|-------------|
| tech, ai_ml, science | `day_chill` | 10:00-18:00 |
| politics, war, ru_politics, ru_war | `streaming_chill` (minor) | 18:00-23:00 |
| finance, crypto | `morning_energy` | 06:00-10:00 |
| culture, gaming, hardware, auto | `day_chill` | 10:00-18:00 |
| health, energy, space | `night_ambient` | 23:00-06:00 |

### Cron Coordination

| Job | Schedule | Skill |
|-----|----------|-------|
| News scrape | every 60m | `news_scraper_production` |
| Music refresh | every 4h | `radio_music_pipeline` |
| Full radio cycle | continuous | `master-fm-radio` |

### TTS-Ready Format

Each `.txt` in `/newsfeed/` follows:
```
Заголовок статьи. Краткое содержание на русском языке, 2-3 предложения. Подготовлено для голосового чтения.
```

Max length per item: ~300 chars (≈15 sec speech @ normal rate).

### Voice Profiles (Voicebox)

| Category | Voice Profile | Language |
|----------|---------------|----------|
| tech, science, ai_ml | `qwen_custom_voice` (Ryan preset) | EN |
| ru_*, politics, war | `Мастер-мужской` (e7013ccf...) | RU |
| culture, gaming | `qwen_custom_voice` | EN |
| finance, crypto | `Мастер-мужской` | RU |

---
*Generated during Radio ArmsgeddonFM integration session (Aug 2026)*