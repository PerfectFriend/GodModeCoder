# Voicebox (jamiepine/voicebox) — worked API session

Full local voice studio: clone any voice, TTS in 7 engines, emotions, effects. MIT, ~48k★, actively maintained (2026-07).

## Install (Windows)
- Release asset: `Voicebox_<ver>_x64-setup.exe` (NSIS, ~542 MB) from GitHub releases. The `/download/windows` link on the site is a tiny HTML redirect — use the GitHub release asset URL directly.
- Silent: `start /wait Voicebox_0.5.0_x64-setup.exe /S /D=C:\Users\<u>\Voicebox`
- Binaries: `voicebox.exe` (GUI), `voicebox-server.exe` (headless API server → uvicorn on http://127.0.0.1:8000), `voicebox-mcp.exe`.

## Startup
`voicebox-server.exe` logs: Python 3.12, backend PYTORCH, `GPU: None (CPU only)` by default, model cache `~/.cache/huggingface/hub`. First run of an engine downloads weights (Qwen3-TTS 1.7B ≈ 3.8 GB) — `GET /health` shows `model_loaded:false` until done.

## Generate flow (the part that bites)
1. **`POST /generate` REQUIRES `profile_id`** — 422 "Field required" without it; unknown id → 404 "Profile not found".
2. Create a profile first:
   ```bash
   # preset voice (no audio sample needed)
   curl -X POST http://127.0.0.1:8000/profiles -H "Content-Type: application/json" \
     -d '{"name":"...","description":"...","language":"ru","voice_type":"preset",
          "preset_engine":"qwen_custom_voice","preset_voice_id":"Ryan",
          "default_engine":"qwen_custom_voice"}'
   # → {"id":"<profile_id>", ...}
   ```
   - Rule: `voice_type:"preset"` requires `default_engine == preset_engine` (else "Preset profiles must use their preset_engine as default_engine").
   - Voice id must exist for that engine: `GET /profiles/presets/{engine}` lists them.
3. Generate:
   ```bash
   curl -X POST http://127.0.0.1:8000/generate -H "Content-Type: application/json" \
     --data-binary @request.json   # ← use a FILE for non-ASCII text; inline -d mangles Cyrillic → "error parsing the body"
   # {"id":"...","status":"generating",...}
   ```
4. Poll **`GET /history/{id}`** (plain JSON `{status, audio_path, duration, error}`). `GET /generate/{id}/status` is SSE (`data: {...}` lines) and HANGS urllib/requests (connection held open; proven 2026-08). Status flow: `loading_model → generating → completed`.
5. `GET /history/{id}/export-audio` returns the WAV bytes; files also land in `<Voicebox>/data/generations/<id>.wav`.

## Model warm-up / persistence
- `/health` → `model_loaded:false` after every completed generation — the 3.8 GB model is unloaded between requests.
- `POST /models/load?model_size=1.7B` loads and keeps it resident (verify: `GET /models/status` shows `qwen-custom-voice-1.7B → loaded:true`). Repeat after each server restart.
- `GET /models/status` lists both Base and CustomVoice variants (`qwen-tts-1.7B` vs `qwen-custom-voice-1.7B`). Preset/cloned profiles use the CustomVoice engine only.

## Engines (field `engine`)
| engine | langs | notes |
|---|---|---|
| qwen | 10 | Qwen3-TTS cloning, delivery instructions ("speak slowly", "whisper") |
| qwen_custom_voice | 10 | 9 preset voices (Ryan/Aiden male-EN, Uncle_Fu/Dylan/Eric male-ZH, Vivian/Serena female-ZH) |
| luxtts | EN | ~1GB VRAM, 48kHz, 150x realtime on CPU |
| chatterbox / chatterbox_turbo | 23 / EN | turbo reads `[laugh] [sigh] [gasp] [whisper]` emotion tags |
| tada | 10 | HumeAI, 700s+ coherent audio |
| kokoro | 8 | 82M tiny, fast CPU, 50 preset voices |

`model_size` accepts 0.6B / 1.7B / 1B / 3B (1.7B default).

## Gotchas
- `profile_id` from `GET /channels` is a CHANNEL id, not a profile — POST /profiles returns the real one.
- Backend is CPU-only unless CUDA libs installed (`/backend/cuda-status`); 0.6B is usable, 1.7B is slow on CPU.
- Effects: `GET /effects/available`, presets via `GET /effects/presets`; `effects_chain` accepted in the generate body.
## Voice cloning (proven API shape 2026-08)
1. Create a cloned profile — note it CANNOT carry preset fields AND rejects a preset default_engine:
   ```bash
   curl -X POST http://127.0.0.1:8000/profiles -H "Content-Type: application/json" \
     --data-binary @clone.json
   # clone.json: {"name":"...","language":"ru","voice_type":"cloned"} 
   # → 422 "Cloned profiles cannot set preset_engine or preset_voice_id" if you include them
   # → 400 "Cloned profiles cannot use default engine 'qwen_custom_voice'" if you pass
   #    default_engine=qwen_custom_voice (discovered 2026-08) — send NO engine fields at all
   # → {"id":"<profile_id>", ...}
   ```
   Generation still works with `"engine": "qwen_custom_voice"` in the /generate body — the
   engine is chosen per-request, not baked into the clone profile.
2. Upload 3–10 audio samples (multipart form-data, one request per sample):
   `POST /profiles/{profile_id}/samples` with fields `file` (audio: mp3/wav/ogg) + `reference_text` (exact transcription of what the speaker says in that clip). Schema: `Body_add_profile_sample_profiles__profile_id__samples_post`; response `ProfileSampleResponse {id, audio_path, reference_text}`.
3. Generate with `{"profile_id": <clone>, "engine": "qwen_custom_voice", ...}` — the engine reads the profile's samples. See `GET /openapi.json` paths `/profiles/{profile_id}/samples`, `/profiles/import`, `/profiles/{profile_id}/compose` for related routes.
4. Sample quality guidance for the user: 5–15 s clips, varied intonation, clean audio (no music/noise/echo), diverse phrases covering the target language's sounds; reference_text must match the audio exactly.

## Telegram voice memo → clone pipeline (zero-friction, proven 2026-08)

The Hermes Telegram gateway ALREADY caches every inbound voice message for STT:
`C:\Users\tomas\AppData\Local\hermes\cache\audio\audio_<hash>.ogg` (opus, mono, 48 kHz;
source: `gateway/platforms/base.py` → `get_audio_cache_dir()` = `cache/audio`, files named
`audio_*` — distinguish from outbound `tts_*.wav/.ogg`). So voice cloning needs NO upload step:

1. User sends 5–10 voice memos in Telegram (different intonations, 5–15 s each).
2. Agent harvests them: `find <hermes>/cache/audio -name 'audio_*.ogg'`.
3. Transcribe each with faster-whisper (local, `stt.language: ru`) → that text is the
   `reference_text` — the user never types anything.
4. Upload via `POST /profiles/{id}/samples` multipart (file + reference_text) — the
   `scripts/clone_voice.py` CLI wraps create/add-sample/samples/test.
5. Test with a short phrase; iterate if the clone is off.

Voice memos may be only 3–5 s — still usable as samples, but recommend longer, varied takes
for quality. Do NOT delete `audio_*.ogg` before cloning — the gateway keeps them for STT
but may clean old cache entries (cache TTL), so harvest promptly or copy to
`C:\Users\tomas\ai-radio\cache\voice-samples\`.
