# ACE-Step 1.5 Technical Reference for AI Radio

> Condensed from official docs (README, Tutorial, INFERENCE, CLI, INSTALL, GPU_COMPATIBILITY, API, GRADIO_GUIDE, LoRA_Training) + verified on CPU-only Windows (Radeon 780M, Python 3.11, uv venv).

---

## Model Selection for CPU-Only (Our Environment)

| Component | Choice | Reason |
|-----------|--------|--------|
| **DiT** | `acestep-v15-turbo` | 8 steps, distillation, no CFG needed, fastest |
| **LM** | `acestep-5Hz-lm-1.7B` | Balance speed/quality, works on CPU with `pt` backend |
| **Backend** | `pt` (PyTorch) | `vllm` requires CUDA, `mlx` is Apple-only |
| **Device** | `cpu` | No CUDA on 780M |

**Checkpoints layout** (already in `C:\Users\tomas\ace-step\extracted\checkpoints\`):
```
acestep-v15-turbo\           ← Turbo DiT (default, 8 steps)
acestep-5Hz-lm-1.7B\         ← LM 1.7B (our choice)
vae\ + Qwen3-Embedding-0.6B\ ← Shared components
```

---

## Critical .env Settings (CPU)

```bash
# C:\Users\tomas\ace-step\extracted\.env
ACESTEP_CONFIG_PATH=acestep-v15-turbo
ACESTEP_LM_MODEL_PATH=acestep-5Hz-lm-1.7B
ACESTEP_DEVICE=cpu
ACESTEP_LM_BACKEND=pt              # CRITICAL: vllm fails on CPU
ACESTEP_INIT_LLM=true              # Force-enable LM (auto disables on CPU)
ACESTEP_DOWNLOAD_SOURCE=auto
```

---

## Mandatory TOML Parameters for Radio Generation

```toml
# These are NON-NEGOTIABLE for quality on turbo + CPU
task_type = "text2music"
caption = "..."                    # 5+ dimensions: style + mood + instruments + timbre + era
instrumental = true                # Radio beds/jingles = no vocals
duration = 120                     # 10-300s stable; >300 risk repetition
seed = -1                          # -1 = random; fix for reproducibility
inference_steps = 8                # Turbo sweet spot
shift = 3.0                        # MANDATORY for turbo! Default 1.0 = poor structure
infer_method = "ode"               # Deterministic, faster than sde
device = "cpu"
backend = "pt"
config_path = "acestep-v15-turbo"
audio_format = "wav"               # Lossless for radio processing
thinking = true                    # Enable LM for metadata + caption rewrite
lm_temperature = 0.85
use_cot_metas = true               # Auto BPM/key/duration
use_cot_caption = true             # LM improves caption
use_cot_language = true            # Auto vocal language detect
use_constrained_decoding = true
bpm = 120                          # Set explicitly for radio consistency
keyscale = ""                      # Empty = auto
timesignature = "4"                # 4/4 default
vocal_language = "unknown"
guidance_scale = 7.0               # Ignored by turbo (no CFG)
use_adg = false
offload_to_cpu = true
offload_dit_to_cpu = true
```

---

## Shift Parameter Deep Dive

| Shift | Effect | Use Case |
|-------|--------|----------|
| 1.0 (default) | Even step distribution, more detail, weaker semantics | Experiments only |
| **3.0 (REQUIRED)** | Focus early steps → strong structure, clear semantics | **ALL turbo radio generation** |
| 4-5.0 | Very strong structure, may sound "dry", minimal orchestration | Strict genres (march, techno) |

**Rule:** Never use turbo with `shift=1.0` for radio — structure collapses.

---

## Caption Engineering (80% of Quality)

**Dimensions to combine (3-5 minimum):**
- Style/Genre: rock, jazz, electronic, ambient, chiptune, synthwave, lo-fi
- Emotion: melancholic, uplifting, energetic, dreamy, dark, nostalgic, euphoric
- Instruments: electric guitar, piano, synth pads, 808 drums, strings, brass
- Timbre: warm, bright, crisp, airy, punchy, lush, raw, polished, distorted
- Era/Ref: 80s synth-pop, 90s grunge, "in the style of Daft Punk"
- Production: lo-fi, high-fidelity, live recording, studio-polished
- Vocal (if not instrumental): female/male, breathy, powerful, falsetto, raspy
- Rhythm: slow tempo, mid-tempo, fast-paced, groovy, driving, laid-back

**Radio-specific templates:**

```toml
# Jingle (5-15s)
caption = "short radio jingle, upbeat, catchy melody, brass fanfare, energetic, 5 seconds, station ID"
duration = 5; bpm = 140

# Bed / Music under speech (30-60s)
caption = "radio bed, background music for voiceover, subtle, unobtrusive, ambient electronic, minimal melody, steady rhythm, loopable"
duration = 45; bpm = 100

# Full music block (2-4 min)
caption = "full radio track, energetic pop rock, electric guitar riff, driving drums, catchy chorus, structured verse-chorus, professional production, radio edit"
duration = 180; bpm = 130

# Late night ambient
caption = "late night radio, ambient chillout, soft pads, slow tempo, dreamy atmosphere, minimal percussion, intimate, relaxing, smooth transitions"
duration = 240; bpm = 70
```

---

## Lyrics with Structure Tags (Even for Instrumentals)

```text
[Intro - ambient]
[Main Theme - piano]
[Build - rising energy]
[Climax - powerful]
[Breakdown - minimal]
[Outro - fade out]
```

**Rules:**
- Never stack tags: `[Chorus - anthemic]` ✓ | `[Chorus - anthemic - stacked - high - epic]` ✗
- Consistency: caption says "piano" → lyrics tag `[Piano Solo]`, NOT `[Guitar Solo]`
- Syllables/line: 6-10 (RU: 5-8). Uniform = better rhythm
- UPPERCASE = high vocal intensity
- Parenthetical = backing vocals: `We rise (together) into the light (into the light)`

---

## Quality Screening Workflow (Batch → Score → Best)

```python
from acestep.inference import generate_music, GenerationParams, GenerationConfig
from acestep.handler import AceStepHandler
from acestep.llm_inference import LLMHandler

# Init ONCE
dit = AceStepHandler()
dit.initialize_service(project_root=ACE_ROOT, config_path="acestep-v15-turbo", device="cpu")
llm = LLMHandler()
llm.initialize(checkpoint_dir=os.path.join(ACE_ROOT, "checkpoints"), 
               lm_model_path="acestep-5Hz-lm-1.7B", backend="pt", device="cpu")

# Batch generate 4 variants
params = GenerationParams(task_type="text2music", caption=prompt, instrumental=True, duration=120)
config = GenerationConfig(batch_size=4, audio_format="wav")
result = generate_music(dit, llm, params, config, save_dir=out_dir)

if result.success:
    for audio in result.audios:
        score = audio.get('quality_score', 0)
        seed = audio['params']['seed']
        print(f"Seed {seed}: score={score:.3f}, path={audio['path']}")
    
    best = max(result.audios, key=lambda a: a.get('quality_score', 0))
    # LOG: best_seed, best_path, prompt, style, timestamp
```

---

## LoRA Training for Radio Brand Voice

**Dataset prep (min 8-10 tracks):**
```
radio_lora/
├── track1.wav + track1.lyrics.txt + track1.json
├── track2.wav + track2.lyrics.txt + track2.json
└── ...
```

**track.json:**
```json
{"caption": "bright morning radio jingle, brass fanfare, upbeat, energetic, station ID, 5 seconds", "bpm": 140, "keyscale": "C Major", "timesignature": "4", "language": "en"}
```

**Gradio UI steps:**
1. Launch with `INIT_SERVICE=false` (edit start_gradio_ui.bat)
2. LoRA Training → Dataset Builder → Scan folder
3. Custom Activation Tag: `master_fm_style` (unique)
4. Tag Position: Prepend
5. Auto-Label All (uses LM for captions/BPM/key)
6. Preprocess (tiled encode saves VRAM)
7. Train: r=32, alpha=64, lr=1e-4, epochs=500-800, batch=1
8. Export LoRA

**Usage:**
```python
dit.load_lora(r"C:\path\to\master_fm_lora")
dit.use_lora = True
# In caption: "master_fm_style, radio jingle, upbeat..."
```

⚠️ **LoRA + INT8 Quantization = CONFLICT** — disable quantization before loading.

---

## REST API Integration (For dj.py On-Demand Generation)

**Server startup (.env):**
```bash
ACESTEP_API_KEY=your-secret-radio-key
PORT=8001
SERVER_NAME=0.0.0.0
```

**Endpoints:**
| Endpoint | Purpose |
|----------|---------|
| `POST /release_task` | Submit generation |
| `POST /query_result` | Poll status (batch) |
| `GET /v1/audio?path=...` | Download result |
| `POST /format_input` | LM-enhance caption/lyrics |

**dj.py integration pattern:**
```python
def generate_jingle_on_demand(style: str, duration: int = 10) -> str:
    r = requests.post(f"{API_BASE}/release_task",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={"prompt": JINGLE_PROMPTS[style], "lyrics": "[Instrumental]",
              "thinking": True, "audio_duration": duration, "bpm": 140,
              "inference_steps": 8, "shift": 3.0, "batch_size": 1})
    task_id = r.json()["data"]["task_id"]
    
    while True:
        time.sleep(2)
        r = requests.post(f"{API_BASE}/query_result", json={"task_id_list": [task_id]})
        if r.json()["data"][0]["status"] == 1:
            break
    
    audio_url = json.loads(r.json()["data"][0]["result"])[0]["file"]
    # download and return local path
```

---

## Windows/MSYS Pitfalls (Verified)

```python
# subprocess launch from gen_music.py — CRITICAL:
env = dict(os.environ)
env["ACESTEP_DEVICE"] = "cpu"
env.pop("PYTHONPATH", None)      # Prevents Hermes venv torch import
env.pop("VIRTUAL_ENV", None)     # Prevents venv conflict

# Paths for Python MUST be Windows-style:
ACE_PY = r"C:\Users\tomas\ace-step\extracted\.venv-cpu\Scripts\python.exe"
CLI = r"C:\Users\tomas\ace-step\extracted\cli.py"
cfg_path = r"C:\Users\tomas\ai-radio\scripts\gen_rock_123.toml"

subprocess.run([ACE_PY, CLI, "-c", cfg_path], cwd=ACE_ROOT, env=env, 
               capture_output=True, text=True, encoding='utf-8', errors='ignore', timeout=3600)
```

**Common errors & fixes:**
| Error | Fix |
|-------|-----|
| `CUDA out of memory` | Check `device="cpu"`, `backend="pt"` everywhere |
| `ModuleNotFoundError: vllm` | `ACESTEP_LM_BACKEND=pt` in .env |
| LM not loading on CPU | `ACESTEP_INIT_LLM=true` (auto disables on 0 VRAM) |
| Generation hangs 10+ min | Normal for CPU; reduce duration, batch_size=1 |
| `UnicodeDecodeError` | `encoding='utf-8', errors='ignore'` in subprocess |

---

## Quality Checklist (Pre/Post Generation)

**Before batch:**
- [ ] `shift = 3.0` in TOML
- [ ] `thinking = true`
- [ ] `inference_steps = 8` (turbo)
- [ ] `device = "cpu"`, `backend = "pt"`
- [ ] `audio_format = "wav"`
- [ ] Caption: 5+ dimensions
- [ ] Lyrics tags consistent with caption
- [ ] `instrumental = true` for beds/jingles
- [ ] Duration 10-300s

**After generation:**
- [ ] Audio plays clean (no clicks, cuts, silence)
- [ ] Duration ≈ target (±10%)
- [ ] Tempo matches BPM
- [ ] Structure audible (verse/chorus/bridge)
- [ ] No instrument conflicts
- [ ] Mix balanced, no clipping

**Production logging:**
- [ ] Best seed recorded
- [ ] File named: `jingle_morning_v2_seed42.wav`
- [ ] Metadata logged: style, prompt, seed, BPM, key, duration
- [ ] Placed in correct `cache/music/<style>/` or `cache/jingles/<type>/`