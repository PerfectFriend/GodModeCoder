# Mubert API Reference — Radio ArmsgeddonFM

## Overview
Mubert API provides royalty-free AI music generation via REST API.
**Requires paid subscription** ($49+/month). For free alternatives, see local generation.

## Authentication
- Headers: `customer-id`, `access-token`
- Get from: https://mubert.com/api after signup

## Base URL
```
https://music-api.mubert.com/api/v3/public
```

## Endpoints

### Generate Track
```
POST /tracks
Headers: customer-id, access-token, Content-Type: application/json

Payload:
{
  "playlist_index": "1.0.0",
  "duration": 300,
  "bitrate": 128,
  "format": "mp3",
  "intensity": "medium",
  "mode": "track"
}

Response:
{
  "status": 200,
  "data": {
    "track_id": "...",
    "download_url": "https://...",
    "duration": 300,
    "format": "mp3",
    "bitrate": 128
  }
}
```

### Get Streaming Link (Infinite Radio)
```
GET /streaming/get-link
Params: playlist_index, bitrate, intensity, type (http|webrtc)

Response:
{
  "status": 200,
  "data": { "stream_url": "https://..." }
}
```

## Pricing (2026)
| Plan | Price | Generations/mo | Streaming min/mo |
|------|-------|----------------|------------------|
| Trial | $49 | 100 | 100 |
| Startup | $199-249 | 5,000 | 5,000 |
| Startup+ | $499 | 30,000 | 30,000 |
| Custom | Contact | Custom | Custom |

## Radio Presets (from mubert_client.py)
```python
RADIO_PRESETS = {
    "night_ambient": {"playlist_index": "1.0.0", "intensity": "low", "mode": "track"},
    "day_chill": {"playlist_index": "2.0.0", "intensity": "medium", "mode": "track"},
    "morning_energy": {"playlist_index": "3.0.0", "intensity": "high", "mode": "track"},
    "late_night": {"playlist_index": "4.0.0", "intensity": "low", "mode": "track"},
    "streaming_ambient": {"playlist_index": "1.0.0", "intensity": "medium", "mode": "streaming"},
    "streaming_chill": {"playlist_index": "2.0.0", "intensity": "medium", "mode": "streaming"},
}
```

## Usage in Radio Pipeline
```python
client = MubertClient()
manager = RadioMusicManager(client)

# Generate 1-hour background track
track_path = manager.ensure_background_track()

# Or get streaming URL for live radio
stream_url = client.get_streaming_link(playlist_index="1.0.0", bitrate=128)
```

## Free Alternatives (No Cost)
| Source | Type | Access |
|--------|------|--------|
| **Riffusion** | Local gen (CPU) | `pip install riffusion` |
| **MusicGen** | Local gen (DirectML) | `pip install audiocraft torch-directml` |
| **Stable Audio Open** | Local gen | `pip install stable-audio-tools` |
| **YouTube Audio Library** | Download (CC0) | yt-dlp |
| **Free Music Archive** | Download (CC0) | API + filter |
| **Pixabay Music** | Download (CC0) | Direct links |
| **Jamendo** | Download (CC-BY) | Search by genre |
| **Openverse** | Search (CC0) | Filter by license |

## Integration with Radio Pipeline
- **Paid path**: Mubert API → background tracks / streaming
- **Free path**: Local gen (Riffusion/MusicGen) + free downloads → `/music/background/`
- Mixer: ffmpeg sidechain ducking (music -18dB under voice)
- Scheduler: Every 4 hours, hour-based presets