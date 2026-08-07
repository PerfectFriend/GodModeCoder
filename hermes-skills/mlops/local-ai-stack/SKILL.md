---
name: local-ai-stack
description: "Use for local AI models on AMD iGPU shared RAM."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [local-ai, ollama, vulkan, amd, igpu, stt, tts, whisper, voicebox, music-gen, acestep]
    related_skills: [llama-cpp, hermes-agent]
---

# Local AI Stack on Consumer Hardware (AMD iGPU / shared memory)

Run LLM, STT, TTS and music generation fully offline on a workstation with an AMD APU (e.g. Ryzen 7 255 + Radeon 780M, 24 GB LPDDR5 shared). No cloud traffic after models are downloaded. Proven 2026-08 on Windows 11 + git-bash.

## Hardware reality check (do this first)

- UMA (unified memory) like Apple Silicon: CPU + GPU share system RAM, no VRAM copies.
- Windows may report less RAM than physical (GPU reserve eats some).
- `vulkaninfo` shows GPU-accessible heaps: on a 780M expect ~9.09 GiB + ~4.55 GiB (+ 256 MiB) ≈ **~13.6 GiB GPU-accessible**.
- iGPU ≈ 2.9 TFLOPS FP16 — fine for inference, weak for training.
- **No ROCm for AMD iGPUs on Windows** (only discrete RX cards). Paths: Vulkan (llama.cpp/Ollama), DirectML (PyTorch), or CPU.

### NPU reality check — do NOT assume the box has one (proven 2026-08, Beelink SER9)

- This machine (AZW/Beelink SER9, `Win32_ComputerSystem Manufacturer=AZW Model=SER9`) runs **Ryzen 7 255 = Hawk Point (Zen 4)** — Family 25 Model 117 (`AMD64 Family 25 Model 117 Stepping 2`). Notebookcheck confirms: *"NPU for AI acceleration is not installed / activated"*; Guru3D's SER9 review: *"lacks a dedicated NPU"*.
- **The AMD NPU driver IS installed** (`DriverStore/FileRepository/kipudrv.inf_amd64_*/ipustack.sys`, service `IpuMcdmDriver`, waits on `PCI\VEN_1022&DEV_1502` and `DEV_17F0`) — driver presence does NOT mean the NPU exists. Check whether the device actually enumerates: `Get-PnpDevice | ? {$_.InstanceId -match 'VEN_1022&DEV_1(502|7F0)'}` → empty = NPU absent.
- **Beelink ships cut-down chips without NPU to cut price** — same silicon family minus the XDNA block (known pattern: SER8 8745HS = "8845HS without the Ryzen AI NPU"). The same-looking mini-PC in a pricier config (SER9 with Ryzen AI 9 HX 370) HAS a 50-TOPS NPU; the Ryzen 7 255 version does not.
- **Going into the BIOS to "enable NPU" is pointless on this SKU** — no setting can materialize a fused-off block. Don't chase it; the real power is the 780M iGPU.
- Cheap offline checks before assuming: (a) enumerate `VEN_1022&DEV_1502/17F0` in PnP; (b) `vulkaninfo --summary` → deviceName `AMD Radeon 780M`, memoryHeaps ~9.09 + ~4.55 GiB; (c) `Get-CimInstance Win32_VideoController` AdapterRAM (~4 GB default = the **BIOS UMA allocation, not the ceiling**).
- **BIOS UMA/VRAM is the real speed lever — but it's a BALANCE, not "max it out"** (proven 2026-08 on SER9): iGPU VRAM reported by Windows (`AdapterRAM` ≈ 4 GB) is the UMA Frame Buffer the BIOS gives the GPU; Vulkan already sees ~13.6–15 GiB of shared memory regardless. Raising UMA to 16 GB on a 24 GB box **left Windows with only 8 GB RAM (0.8 free)** — the CPU-side TTS (Voicebox, ~8 GB) starved and the system swapped. The GPU already addresses shared RAM, so huge UMA reservations mostly HURT (they take RAM away from the OS/CPU workloads) for marginal LLM gain. **Recommended: 4–8 GB UMA on a 24 GB machine.** Exact BIOS path (AMI Aptio): `Advanced → AMD CBS → NBIO Common Options → GFX Configuration` → `Integrated Graphics Controller = Forces`, `UMA mode = UMA_Specified` (NOT Auto — Auto can black-screen and require CMOS reset), `UMA Frame Buffer Size = <manual value>`. Enter BIOS via `Del` at power-on (or Windows → Recovery → UEFI Firmware Settings). Also confirm AVX-512 (Hawk Point/Zen 4 has it) helps the CPU-side (TTS) work. Full walkthrough + measurement transcript: `references/bios-uma-tuning.md`.
- Full diagnosis transcript: `references/npu-and-hardware-diagnosis.md`.

### Model size ceilings (Q4 quantization)
- 7–9B → fully in GPU memory (~5–6 GB) — fast
- 12–14B → **fully in GPU on 780M** (measured 2026-08): gemma4:12b 8.1 GB @ 100% GPU, 8.1 tok/s; qwen3:14b 9.6 GB @ 100% GPU, 6.7 tok/s — the ~13.6 GiB GPU-accessible heap is enough; `ollama ps` confirms `100% GPU`
- 30B+ → CPU-only — slow but works

## LLM via Ollama + Vulkan on AMD iGPU

Ollama ships a Vulkan backend (`lib/ollama/vulkan/ggml-vulkan.dll`) and detects the 780M — **but drops integrated GPUs by default**:

```
server.log: "dropping integrated GPU; to enable, set OLLAMA_IGPU_ENABLE=1" id=0 library=Vulkan ... AMD Radeon 780M
```

Fix (User-scope env, then restart the server):

```powershell
[Environment]::SetEnvironmentVariable('OLLAMA_IGPU_ENABLE','1','User')
[Environment]::SetEnvironmentVariable('OLLAMA_VULKAN','1','User')
[Environment]::SetEnvironmentVariable('OLLAMA_GPU_LAYERS','99','User')   # offload everything
# the "ollama app" GUI restarts its own server WITHOUT your env —
# kill ALL ollama processes, then start: ollama serve  (with env set in that shell)
```

Verify GPU is used: `ollama ps` → PROCESSOR column shows `100% GPU` (vs `100% CPU` before). Speedup on 780M: ~8.5 → ~14+ tok/s on qwen3:8b.

Pitfalls:
- Server config env is logged at startup — confirm `OLLAMA_IGPU_ENABLE:true` appears before debugging.
- Interrupted `ollama pull` → just re-run, it resumes.
- `ollama run <model> "<prompt>"` blocks on think-tokens for reasoning models; use `--verbose` to see eval rates.
- see also `references/bulk-downloads.md` — probing real progress, "all processes died" triage, and not restart-hammering.

## STT (speech → text)

- Hermes venv ships `faster-whisper` (CTranslate2, CPU) — no GPU needed.
- Config: `stt.enabled: true`, `stt.language: ru`, `stt.local.model: small` (base = fast/rough, small = good RU accuracy ~p=1.00).
- Model auto-downloads to `~/.cache/huggingface/hub` on first use.
- Voice messages on Telegram gateway auto-transcribe through this provider.
- Cloud alternative: Groq `whisper-large-v3` (GROQ_API_KEY) — better but needs internet.

## TTS (text → speech)

- **edge-tts** (ships in Hermes venv, free, cloud): RU voices `ru-RU-DmitryNeural` (male), `ru-RU-SvetlanaNeural` (female). Works out of the box for Telegram voice replies.
- **Voicebox** (jamiepine/voicebox, MIT) — full local voice studio: cloning, 7 engines, emotions. Install = NSIS setup → `voicebox-server.exe` → uvicorn on `http://127.0.0.1:8000`. API quirks (learned the hard way):
  - `POST /generate` REQUIRES `profile_id` — create one first via `POST /profiles` (`voice_type:"preset"` + `preset_engine` + `preset_voice_id`, or `"cloned"` + sample uploads). Preset voices list: `GET /profiles/presets/{engine}` (qwen_custom_voice has Ryan/Aiden male-EN, Uncle_Fu/Dylan/Eric male-ZH).
  - `/generate` returns an id with `"status":"generating"`; poll `GET /history/{id}` (plain JSON). **`GET /generate/{id}/status` is SSE and hangs blocking HTTP clients** — never poll it from urllib/requests.
  - First run downloads the engine to HF cache (~3.8 GB for Qwen3-TTS 1.7B); `GET /health` shows `model_loaded:false` until then.
  - Voicebox's OWN in-process downloader is fragile on flaky links — loops on `ChunkedEncodingError`/`IncompleteRead` and never reaches `model_loaded:true`. **Fix: prefetch the model yourself** into `~/.cache/huggingface/hub` (stable resume), then Voicebox picks up the cached files on the next generate attempt.
  - HF CLI had a breaking rename (2026): `huggingface-cli` is DEPRECATED and now just prints "Use `hf` instead". Prefetch with `hf download <repo>` (resume is automatic by default; do NOT pass `--resume-download` — it is not a valid flag; use `--force-download` to override cache). For multi-GB models, install the Rust accelerator first for stable long transfers: `uv pip install hf_transfer` then `HF_HUB_ENABLE_HF_TRANSFER=1 hf download <repo>`. Watch for concurrent-downloader lock conflicts: if BOTH an `hf download` and Voicebox's own loader grab the same repo, they deadlock on `.locks/` — kill one, `rm -rf ~/.cache/huggingface/hub/.locks`, then let a single downloader finish.
  - When HF keeps resetting a ~3.8 GB model, prefer the same model's smaller sibling (Qwen3-TTS ships 0.6B / 1.7B / 1.7B-CustomVoice) — faster to fetch and fine for voice on CPU, instead of fighting the big one.
  - Preset-profile gotcha: a preset profile MUST set `default_engine` equal to its `preset_engine` (e.g. both `qwen_custom_voice`) or `POST /profiles` rejects it ("Preset profiles must use their preset_engine as default_engine"). **Cloned profiles are the mirror image: send NO engine fields at all** — `voice_type:"cloned"` + name + language only; a cloned profile rejects both `preset_engine` (422) and `default_engine: qwen_custom_voice` (400). The engine is chosen per-request in the `/generate` body. **Not every engine accepts cloned profiles**: `qwen_custom_voice` → HTTP 400 "Engine 'qwen_custom_voice' does not support cloned voice profiles"; **`luxtts` DOES accept cloned profiles** (verified 2026-08 — generation completed with a cloned profile_id). Probe engines one at a time with a tiny POST; the 400/422 error message names the engine family pattern if you get it wrong. See `scripts/clone_voice.py`.
  - **Cloning via luxtts requires the Base model too**: luxtts pulls in `qwen-tts-1.7B` (Base, ~3.86 GB) in addition to the CustomVoice weights; a `/generate` on a cloned profile sits in `loading_model` while Voicebox's fragile in-process downloader fetches it. Prefetch BOTH repos (`Qwen/Qwen3-TTS-12Hz-1.7B-Base` AND `Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice`) via `hf download` + hf_transfer before testing clones — see `references/hf-model-prefetch.md`.
  - Engines: qwen (cloning, 10 langs), qwen_custom_voice (9 presets), luxtts (fast CPU), chatterbox(+turbo, `[laugh]` emotion tags), tada, kokoro.
  - Backend defaults to CPU (`"GPU: None (CPU only)"`) — fine for 0.6B, slow for 1.7B. **The bundled `voicebox-server.exe` is CPU-ONLY and cannot be switched to VRAM**: binary analysis shows `torch_cpu.dll` + `c10.dll` present, but NO `torch_cuda.dll`, `torch_vulkan`, `torch_directml`, `DirectML.dll`, `vulkan-1.dll`; onnxruntime has CPU provider only (no Dml/CUDA/Vulkan providers). The `cuda` strings in the exe are `numba.cuda` (JIT lib), not GPU support. So on AMD iGPU boxes Voicebox always runs on CPU and needs ~8 GB system RAM — a huge BIOS UMA reservation directly starves it. See references/voicebox-api.md and references/bios-uma-tuning.md.
  - **GPU escape hatch (proven 2026-08): run Voicebox's own `qwen_tts` Python API standalone on the iGPU via Microsoft's torch-directml.** The package source lives inside the extracted PyInstaller temp dir (`%LOCALAPPDATA%\Temp\_MEI*/qwen_tts/` — copy it out), the CustomVoice weights are already in HF cache, and the Radeon 780M is directly usable: `torch_directml.device()` + matmul verified. Install from the DirectML Azure feed (NOT PyPI) with `--extra-index-url https://pkgs.dev.azure.com/dnceng/public/_packaging/directml/pypi/simple/`; needs `transformers==4.57.3` (4.46.4 from the README does NOT exist), accelerate, librosa, soundfile, einops, torchaudio. Blocked (as of 2026-08) on the `sox` native binding at import — see `references/gpu-tts-directml.md` for the exact install/verify recipe and current blocker.

### Wire Voicebox into Hermes as a command TTS provider (proven 2026-08)

Hermes `tts_tool` supports user-declared command providers under `tts.providers.<name>` (`type: command`) — any CLI that turns text into audio. That's the clean way to make Telegram voice replies come from Voicebox (cloned voice) instead of edge-tts:

```yaml
tts:
  provider: voicebox
  providers:
    voicebox:
      type: command
      command: '"C:\...\venv\Scripts\python.exe" "C:\Users\tomas\voicebox_tts.py" {input_path} {output_path}'
      output_format: wav
      voice_compatible: true   # required for a native Telegram voice bubble
```

- The command provider receives `{input_path}` (temp UTF-8 text file) and `{output_path}` (where audio must land); placeholders are shell-quoted automatically.
- `voice_compatible: true` → Hermes converts WAV→Ogg/Opus via ffmpeg and tags it `[[audio_as_voice]]`, so Telegram renders a real voice bubble, not an attachment.
- Setting nested provider keys via `hermes config set` needs `--force` (e.g. `hermes config set tts.providers.voicebox.timeout 300 --force`) — without it the CLI suggests the top-level `tts.provider` key and silently doesn't write the nested path. Verify the final block in config.yaml afterwards (command string, output_format, timeout, max_text_length).
- The wrapper script must: POST `/generate` {profile_id, engine, text, language, model_size} → poll **`GET /history/{id}`** (plain JSON, `status` field) until `completed` → GET `/history/{id}/export-audio` → write bytes to `{output_path}`. **DO NOT poll `GET /generate/{id}/status` — it is an SSE stream that holds the connection open and hangs `urllib`/`requests` forever on the first `data:` line** (proven 2026-08: script timed out repeatedly, generation actually completed fine). See `scripts/voicebox_tts.py` (ready to use).
- **Model unloads after every generation** (`/health` → `model_loaded:false`), so each request pays a 3.8 GB reload → 30–90 s on CPU. Keep it warm with `POST /models/load?model_size=1.7B` (or 0.6B); verify via `GET /models/status` (`qwen-custom-voice-1.7B → loaded:true`). Command-provider TTS still needs `timeout: 300` and `max_text_length: 1000` in the provider config — 120 s default is too tight for long texts on CPU.
- Voicebox's model registry (`GET /models/status`) lists Base AND CustomVoice variants separately (`qwen-tts-1.7B` = Base, `qwen-custom-voice-1.7B` = the cloning engine). Only the CustomVoice one matters for preset/cloned profiles; if a stray server starts downloading `model.safetensors` for a Base model you don't need, kill it (see process hygiene below).
- Git-bash path gotcha: Windows Python cannot open MSYS paths — call `python.exe "C:/Users/.../voicebox_tts.py"` with forward-slash Windows paths, NOT `/c/Users/...`. And curl `--data-binary @file` needs a Windows-style path too.
- Telegram voice loop: inbound voice → STT (faster-whisper) → reply text + auto-TTS. Global switch: `voice.auto_tts: true` in config; per-chat: `/voice on` (voice-to-voice), `/voice tts` (always voice), `/voice off`. Restart gateway (`hermes gateway run`) after changing `tts.provider` — the gateway loads TTS config at startup.
- **edge-tts is flaky**: direct calls intermittently fail with `NoAudioReceived` (~1 in 3 in one test run) even though the same voice works standalone. For reliable voice replies prefer the local Voicebox provider; keep edge only as a quick fallback.

### Voicebox server process hygiene

- After a machine move/reboot, stale `voicebox-server.exe` instances can linger. **Two competing servers → API returns "Profile not found" / empty `/profiles` even though the profile row exists in `data/voicebox.db`.** Fix: `taskkill /F /PID <all voicebox-server pids>`, start exactly one (`voicebox-server.exe` from `C:\Users\tomas\Voicebox`), wait ~10s, verify `/health` + `/profiles`.
- Profile survives reboots in `data/voicebox.db` (SQLite) even when the API list looks empty — check the DB before recreating: `SELECT * FROM profiles` (columns: id, name, voice_type, preset_engine, preset_voice_id, default_engine, ...).

## Music generation

- **ACE-Step 1.5** (ace-step/ACE-Step-1.5, MIT) — strongest open music model (~Suno v4.5–v5), 50+ languages, lyrics, covers, LoRA.
  - VRAM guide: ≤6GB → 2B turbo INT8 + CPU offload (right pick for 780M-class iGPU); 8–16GB → 2B turbo/sft + 0.6B/1.7B LM; ≥20GB → XL turbo/sft.
  - Windows portable `.7z` (~2.4 GB, pre-baked deps) or `uv sync && uv run acestep` → Gradio :7860, REST :8001.
  - No 7-Zip on Windows? Extract with Python: `uv pip install py7zr`, then `py7zr.SevenZipFile('ACE-Step-1.5.7z','r').extractall(path='extracted')`. 2.4 GB archive → 7.6 GB / ~57k files in ~12 min (verified). Don't hammer `du` on the in-progress extract dir — it hangs on the busy filesystem; let the process finish and report.
  - The `files.acemusic.ai` CDN is flaky — drops mid-file with curl exit 18 (partial) and 56 (recv reset) even on resume. Don't fight it with one shot; run in background with `curl -sL -C - --retry 20 --retry-delay 8 --retry-all-errors` and let it grind. `axel`/`aria2c` are NOT pre-installed. HuggingFace mirrors of the weight repos exist if the CDN never completes.
  - Models auto-download on first run. Don't fight the big download — resume with `curl -C -` or `--retry`.
- Suno clones seen floating around are old and glitchy — prefer ACE-Step.

### GPU Path for ACE-Step on AMD iGPU (Radeon 780M, 16 GB UMA)

**WSL2 Ubuntu 24.04 + ROCm 6.3 is the recommended path** — Windows ROCm 7.2 is experimental and unstable for consumer APUs.

```bash
# 1. WSL2 Ubuntu 24.04 (already installed)
wsl -d Ubuntu-24.04

# 2. ROCm 6.3 repo
wget -qO - https://repo.radeon.com/rocm/rocm.gpg.key | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/rocm.gpg
echo 'deb [arch=amd64] https://repo.radeon.com/rocm/apt/6.3/ noble main' | sudo tee /etc/apt/sources.list.d/rocm.list
sudo apt update

# 3. Minimal ROCm runtime
sudo apt install -y hip-runtime-amd hsa-rocr6.3.0 hipblas6.3.0 hipsparse6.3.0 hipfft6.3.0 rccl6.3.0 rocm-smi

# 4. Verify
rocm-smi
# Should show: Radeon 780M, 16384 MB VRAM

# 5. Python 3.12 venv + ROCm PyTorch
python3.12 -m venv .venv-rocm
source .venv-rocm/bin/activate
pip install torch --index-url https://download.pytorch.org/whl/rocm6.0
pip install -r requirements-rocm.txt  # or pip install -e .

# 6. Environment for ACE-Step (Tier 6a: 16-20 GB VRAM)
export ACESTEP_DEVICE=auto
export ACESTEP_LM_BACKEND=vllm    # vllm works on Linux ROCm!
export ACESTEP_INIT_LLM=true
export ACESTEP_CONFIG_PATH=acestep-v15-turbo
export ACESTEP_LM_MODEL_PATH=acestep-5Hz-lm-1.7B
export HSA_OVERRIDE_GFX_VERSION=11.0.1
export MIOPEN_FIND_MODE=FAST

# 7. Run API server (bind to 0.0.0.0 for Windows access via localhost)
python -m acestep.api_server --port 8001 --host 0.0.0.0
```

**Tier 6a capabilities (16-20 GB VRAM):**
| Parameter | Value |
|-----------|-------|
| Max Duration (LM / No LM) | 8 min / 10 min |
| Max Batch (LM / No LM) | 4 / 8 |
| Offload | CPU (VAE+Text Encoder) |
| Quantization | INT8 |
| DiT Speed (turbo 8 steps) | ~8-15 sec/track |
| LoRA Training | ✅ Possible (16GB min, 20GB recommended) |

**Advantages over Windows ROCm:**
- `vllm` backend works (LM 2-3x faster)
- Stable, fewer MIOPEN bugs
- 16 GB UMA fully accessible
- Unified with Docker/ParanoidX environment

**Windows → WSL2 integration:** Windows `gen_music.py` calls `http://localhost:8001/release_task` (WSL2 port forwarding works automatically) — 20-40x faster than CPU subprocess.

## Files

- `references/voicebox-api.md` — worked Voicebox session: profile creation, generate flow, engines, gotchas, **voice-cloning API shape (cloned profile + samples upload)**, model warm-up (`/models/load`).
- `references/acestep-cpu.md` — ACE-Step 1.5 on CPU/AMD iGPU: requirements-cpu.txt trimming, **PYTHONPATH-pollution fix** (`env -u PYTHONPATH`), flat TOML config keys, backslash-escaping gotcha.
- `references/ai-radio.md` — «Мастер-ФМ» local AI radio architecture: cache layout, ffmpeg → ring-buffer → HTTP broadcast chain, voice-content generation.
- `references/acestep-user-guide.md` — **Complete ACE-Step 1.5 user guide for AI Radio**: architecture, CPU/GPU setup (WSL2 ROCm), TOML configs, all parameters, task types, gen_music.py integration, prompt engineering for jingles/beds/news/ads, LoRA training for brand sound, REST API, troubleshooting, quality checklist.
- `references/hf-model-prefetch.md` — reliable HF model prefetch recipe: `hf` CLI rename, hf_transfer install, lock-deadlock fix, flaky-Wi-Fi handling.
- `references/npu-and-hardware-diagnosis.md` — how to tell whether an AMD mini-PC actually has an NPU (PnP enumeration, Family/Model decode, DriverStore kipudrv.inf check) and how to reason about the real speed levers (BIOS UMA/VRAM, AVX-512, Vulkan heaps). Proven on Beelink SER9 / Ryzen 7 255.
- `references/bios-uma-tuning.md` — BIOS UMA Frame Buffer walkthrough (SER9: AMD CBS → NBIO → GFX, UMA_Specified not Auto), measured 16 GB-vs-4–8 GB tradeoff, and the binary string-scan technique for checking whether a compiled AI app supports GPU (Voicebox = CPU-only).
- `references/display-artifacts-tv.md` — white sparkle dots on black backgrounds when the "monitor" is actually an LCD TV on HDMI (22W_LCD_TV): triage order (TV picture mode/DCR/DNR/sharpness first, then HDMI cable, pixel format, Image Sharpening/Enhanced Sync), TDR event 4107 semantics, EDID native-mode check, RAM-starvation link to oversized UMA.
- `references/gpu-tts-directml.md` — GPU path for Voicebox TTS: installing torch-directml from the Microsoft Azure DevOps feed (NOT PyPI), verifying the Radeon 780M computes on it, extracting `qwen_tts` from the PyInstaller `_MEI` temp dir, the real dependency versions (transformers 4.57.3, not 4.46.4), and the current `sox` import blocker. **Proven: install + device + matmul on 780M. Not yet proven: full generation.**
- `references/gemini-vision-via-pool.md` — analyze images via pooled Gemini keys (direct `generateContent` REST + base64 inline_data) when the Hermes vision toolset is unavailable; key lives in `auth.json` → `credential_pool.gemini[].access_token`.
- `scripts/voicebox_tts.py` — ready-to-use Hermes command-TTS wrapper (text file → Voicebox audio; handles SSE status, engine/profile, Cyrillic). See "Wire Voicebox into Hermes" section above.
- `scripts/acestep_api_client.py` — **Python API client for ACE-Step REST server**: replaces subprocess CLI with HTTP calls to WSL2 GPU server (20-40x speedup), preset-based generation for jingles/beds/tracks/ads/news/sweepers, batch generation with seed management, quality selection.
- `scripts/setup-wsl2-rocm.sh` — **One-shot WSL2 ROCm 6.3 setup**: installs ROCm runtime, Python 3.12 venv, PyTorch ROCm, ACE-Step deps, creates activation/startup scripts for API server and Gradio UI.
- `scripts/send_telegram_doc.py` — send any local file (.md/.pdf/image/audio) to a Telegram chat via Bot API `sendDocument`; reads `TELEGRAM_BOT_TOKEN` from Hermes `.env` without leaking it (proven 2026-08: user DM gets the file, `message_id` returned). Usage: `python send_telegram_doc.py "C:\\path\\file.md" [chat_id] ["caption"]` — use when the user asks to deliver a file/инструкцию to Telegram.
- `scripts/clone_voice.py` — voice-cloning CLI: create cloned profile (NO engine fields — clones reject `default_engine`), upload samples (multipart file + reference_text), list, test. See references/voicebox-api.md → "Telegram voice memo → clone pipeline".
- `templates/start-ai-stack.bat` — Windows logon autostart for Ollama + Voicebox (register under Run key). Prevents losing all background services after a reboot or physical machine move.
- `templates/ai-radio-presets.toml` — **Ready-to-use TOML presets** for all AI Radio content types: jingles (morning/night/breaking), beds (news/talk/music/late_night), full tracks (rock/pop/electronic/ambient/jazz/chiptune), ads (energetic/relaxed), news intros (main/sports/weather/tech), sweepers (up/down), cover/repaint templates, LoRA-activated brand presets.
- `templates/acestep-api.service` — **Systemd service unit** for ACE-Step API server on WSL2: auto-start on boot, GPU env vars, restart on failure, resource limits for 16GB VRAM.
