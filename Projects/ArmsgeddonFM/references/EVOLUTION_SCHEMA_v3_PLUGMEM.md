Warning: Permanently added '100.124.152.97' (ED25519) to the list of known hosts.
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
# Radio ArmsgeddonFM — Evolution Schema v3.0 (with PlugMem Integration)

> **Single Source of Truth** | **Version Badges: A00→A01→A02...** | **Backups: D:\backups (USB only)**
> **PlugMem**: Long-term memory backbone for cross-cycle knowledge retention

---

## 🧠 ARCHITECTURE: PlugMem-Powered Evolution Loop

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RADIO ARMSGEDDONFM EVOLUTION ENGINE                       │
│                         (PlugMem-Enhanced)                                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   CYCLE N    │───▶│  EXECUTION   │───▶│  EVALUATION  │───▶│  PLUGMEM     │
│  GENERATION  │    │  (Radio Run) │    │  (Metrics)   │    │  CONSOLIDATION│
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
       ▲                                                        │
       │                                                        ▼
       │              ┌──────────────────────────────────────────────┐
       │              │           PLUGMEM MEMORY GRAPH                │
       │              │  ┌─────────┐ ┌──────────┐ ┌─────────────┐   │
       └──────────────│  │Semantic │ │Procedural│ │ Episodic    │   │
                      │  │Prompts  │ │ Pipelines│ │ Cycle Runs  │   │
                      │  │Presets  │ │ Configs  │ │ Metrics     │   │
                      │  └─────────┘ └──────────┘ └────�
C:\Vault\Projects\ArmsgeddonFM\references\EVOLUTION_SCHEMA_v3_PLUGMEM.md


�────────┘   │
                      └──────────────────────────────────────────────┘
```

---

## 📋 PLUGMEM INTEGRATION SPEC

### Memory Graph Schema for Radio

```python
# Radio-specific memory types
RADIO_MEMORY_TYPES = {
    "semantic": {
        "prompt_presets": "Best prompts per time slot (morning/day/evening/night)",
        "music_params": "MusicGen/Riffusion params that produced quality audio",
        "tts_voices": "Voicebox/Qwen-TTS profiles per segment type",
        "news_categories": "RSS feed quality scores per category",
    },
    "procedural": {
        "pipeline_configs": "Working DJ/mixer/streamer configurations",
        "generation_recipes": "Step-by-step music+voice mixing procedures",
        "debug_fixes": "Root-cause fixes for known failure modes",
    },
    "episodic": {
        "cycle_runs": "Full cycle execution traces with metrics",
        "quality_scores": "Human/auto quality ratings per generated hour",
        "failure_cases": "What broke and how it was fixed",
        "listener_feedback": "Telegram reactions, retention, complaints",
    }
}
```

### 6-Line Integration (per PlugMem docs)

```python
from plugmem import MemoryGraph, Memory

# 1. Init memory graph (persists to SQLite/JSON)
mg = MemoryGraph(storage_path="D:/backups/radio_armsgeddonfm/plugmem/")

# 2. Create memory sequence for this cycle
mem = Memory(
    cycle_id="A07",
    task_type="radio_generation",
    context={"preset": "morning", "duration": 3600}
)

# 3. Append observations during execution
mem.append({"event": "music_generated", "model": "musicgen-small", "quality": 0.87})
mem.append({"event": "tts_synthesized", "voice": "qwen_custom_voice", "latency": 2.3})
mem.append({"event": "mix_complete", "ducking_db": -18, "duration": 3598})

# 4. Close & insert into graph
mem.close()
mg.insert(mem)

# 5. Retrieve relevant knowledge for next cycle
relevant = mg.retrieve_and_reason(
    query="best music params for morning energetic electronic",
    k=5
)

# 6. Apply retrieved knowledge to next generation
next_params = relevant.best_params()
```

---

## 🔄 EVOLUTION CYCLE WITH PLUGMEM

### Phase 1: KNOWLEDGE RETRIEVAL (Pre-Generation)
```bash
# Before each cycle, query PlugMem for:
# - Best prompts for current time slot
# - Working pipeline configs
# - Known failure patterns to avoid
python -m radio.plugmem_query --slot morning --cycle A07
```

### Phase 2: GENERATION (Radio Production)
```bash
# Generate 1-hour radio block using retrieved knowledge
python -m radio.dj --cycle A07 --slot morning --duration 3600
```

### Phase 3: EVALUATION (Quality Gates)
```bash
# Auto-evaluation + human feedback collection
python -m radio.evaluate --cycle A07 --auto --human-feedback
```

### Phase 4: CONSOLIDATION (PlugMem Write)
```bash
# Store everything: configs, params, metrics, fixes
python -m radio.plugmem_consolidate --cycle A07 --badge A07
```

### Phase 5: BACKUP & VERSION BADGE
```bash
# USB backup + version tag
./scripts/backup_usb.sh A07
git tag -a A07 -m "Radio ArmsgeddonFM A07: PlugMem integration, morning slot optimized"
```

---

## 🗂️ DIRECTORY STRUCTURE (Updated)

```
C:\Users\tomas\ai-radio\
├── radio/
│   ├── __init__.py
│   ├── dj.py                 # Main orchestrator
│   ├── musicgen_directml.py  # MusicGen on DirectML
│   ├── riffusion_directml.py # Riffusion on DirectML
│   ├── tts_voicebox.py       # Voicebox/Qwen-TTS client
│   ├── news_scraper.py       # 287 RSS feeds → TTS-ready
│   ├── mixer.py              # Audio ducking/mixing
│   ├── streamer.py           # Icecast/RTMP (deferred)
│   ├── plugmem_client.py     # ← NEW: PlugMem integration
│   ├── plugmem_query.py      # ← NEW: Pre-generation retrieval
│   ├── plugmem_consolidate.py# ← NEW: Post-cycle storage
│   ├── evaluate.py           # Quality gates
│   └── presets.py            # Time-slot presets
├── scripts/
│   ├── backup_usb.sh
│   ├── evolve_cycle.sh       # Full cycle runner
│   └── register_plugmem.py   # Memory graph init
├── output/
│   ├── music/                # Generated music blocks
│   ├── voice/                # TTS segments
│   ├── mixed/                # Final mixed hours
│   └── logs/                 # Cycle execution logs
├── D:\backups\radio_armsgeddonfm\
│   ├── plugmem/              # ← NEW: PlugMem SQLite/JSON
│   │   ├── memory_graph.db
│   │   ├── semantic_nodes.json
│   │   ├── procedural_nodes.json
│   │   └── episodic_nodes.json
│   ├── radio_A00_cycle01_...
│   ├── radio_A01_cycle01_...
│   └── ...
├── .env                      # API keys, tokens
├── config.yaml               # Radio config
├── pyproject.toml            # Dependencies
└── README.md
```

---

## 🎯 PLUGMEM NODE TYPES FOR RADIO

### Semantic Nodes (Reusable Knowledge)
| Node Type | Key | Value Example |
|-----------|-----|---------------|
| `prompt_preset` | `morning_energetic` | `"upbeat electronic, 110 bpm, energetic, synthesizers, optimistic"` |
| `music_params` | `musicgen_morning` | `{"model": "facebook/musicgen-small", "duration": 30, "temp": 1.0, "cfg": 3.0}` |
| `tts_profile` | `shurgen_morning` | `{"voice": "qwen_custom_voice", "preset": "Ryan", "speed": 1.05}` |
| `feed_quality` | `ixbt_habr` | `{"reliability": 0.95, "relevance": 0.88, "tts_readiness": 0.92}` |

### Procedural Nodes (Executable Recipes)
| Node Type | Key | Value Example |
|-----------|-----|---------------|
| `pipeline_config` | `dj_v2_morning` | `{"music_first": true, "crossfade": 2.0, "ducking_db": -18, "normalize": -14 LUFS}` |
| `generation_recipe` | `hour_block` | `[{"step": "scrape_news", "slot": "morning"}, {"step": "gen_music", "duration": 1800}, {"step": "gen_tts", "news_items": 10}, {"step": "mix", "ducking": -18}, {"step": "validate", "lufs": -14}]` |
| `debug_fix` | `voicebox_hang` | `{"symptom": "generation stuck", "root_cause": "model not fully loaded", "fix": "warmup_call_before_generation"}` |

### Episodic Nodes (Cycle History)
| Node Type | Key | Value Example |
|-----------|-----|---------------|
| `cycle_run` | `A07_morning` | `{"cycle": "A07", "slot": "morning", "duration": 3600, "quality_auto": 0.87, "quality_human": 0.9, "issues": []}` |
| `quality_score` | `A07_morning_music` | `{"component": "music", "score": 0.87, "criteria": ["coherence", "loop_quality", "genre_match"]}` |
| `listener_feedback` | `A07_tg_reactions` | `{"cycle": "A07", "reactions": 23, "complaints": 0, "retention_min": 47}` |

---

## 📊 QUALITY GATES (PlugMem-Enhanced)

```python
QUALITY_GATES = {
    "music": {
        "coherence": 0.8,        # Spectral continuity
        "loop_quality": 0.75,    # Seamless loop detection
        "genre_match": 0.8,      # CLAP/CLIP similarity to prompt
        "min_duration": 1750,    # Seconds (allow -50s buffer)
    },
    "tts": {
        "naturalness": 0.8,      # MOS estimate
        "pronunciation": 0.85,   # Phoneme accuracy
        "latency_ms": 3000,      # Max generation time
        "voice_consistency": 0.9,# Speaker embedding similarity
    },
    "mix": {
        "lufs": -14,             # Target loudness (±1 LU)
        "ducking_db": -18,       # Music under voice
        "peak_db": -1,           # True peak limit
        "dynamic_range": 6,      # DR minimum
    },
    "pipeline": {
        "total_time": 300,       # Max 5 min for 1-hour block
        "memory_mb": 4096,       # Max VRAM+RAM
        "zero_crashes": True,    # Hard gate
    }
}
```

---

## 🚀 EVOLUTION COMMANDS

```bash
# Initialize PlugMem for Radio
python -m radio.register_plugmem

# Run single evolution cycle (2 hours per user spec)
./scripts/evolve_cycle.sh A07 morning

# Run full day cycle (4 slots × 2 hours = 8 hours)
./scripts/evolve_cycle.sh A07 full_day

# Query PlugMem for best params
python -m radio.plugmem_query --slot evening --top-k 3

# View Memory Inspector (PlugMem UI)
plugmem inspector --port 7860

# Backup to USB
./scripts/backup_usb.sh A07
```

---

## 📈 METRICS TRACKING (Per Cycle)

| Metric | Target | Storage |
|--------|--------|---------|
| Music Quality (auto) | ≥0.8 | PlugMem episodic |
| TTS Quality (auto) | ≥0.8 | PlugMem episodic |
| Mix Quality (LUFS) | -14 ±1 | PlugMem episodic |
| Pipeline Time | ≤5 min/hr | PlugMem episodic |
| Human Rating (Telegram) | ≥0.85 | PlugMem episodic |
| Listener Retention | ≥40 min/hr | PlugMem episodic |
| Zero Crashes | 100% | PlugMem procedural (debug_fix) |

---

## 🔗 PLUGMEM RESOURCES

- **Repo**: https://github.com/TIMAN-group/PlugMem
- **Paper**: https://arxiv.org/abs/2603.03296 (ICML 2026)
- **Install**: `pip install plugmem` (when published) or from source
- **Plugins**: OpenClaw, Claude Code (Memory Inspector UI)

---

## 📝 NEXT STEPS

1. **Install PlugMem** from source (GitHub)
2. **Create `radio/plugmem_client.py`** — wrapper for MemoryGraph
3. **Add pre-generation query** in `dj.py` — retrieve best params
4. **Add post-cycle consolidation** — store everything to graph
5. **Run Cycle A07** with PlugMem integration
6. **Verify Memory Inspector** shows radio memory graph
7. **Backup to USB** with PlugMem DB included

---

**Version**: A07 (PlugMem Integration)  
**Status**: Schema Ready → Implementation Next  
**Author**: Master Inquisitor + Hermes Agent  
**Date**: 2026-08-07