Warning: Permanently added '100.124.152.97' (ED25519) to the list of known hosts.
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
---
name: radio-plugmem-integration
description: Use for Radio ArmsgeddonFM cycles with PlugMem memory.
version: "1.0.0"
author: Master Inquisitor + Hermes Agent
tags: [radio, plugmem, memory, evolution, armsgeddonfm]
---

# Radio ArmsgeddonFM — PlugMem Integration Skill

> **Trigger**: Use when setting up or running Radio ArmsgeddonFM evolution cycles with PlugMem long-term memory for cross-cycle knowledge retention (prompts, params, configs, fixes, cycle history).

## Overview

This skill provides a complete integration of **PlugMem** (ICML 2026 plug-and-play long-term memory for LLM agents) into the Radio ArmsgeddonFM 24/7 radio generation pipeline. It enables the system to remember and improve across evolution cycles.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    EVOLUTION CYCLE WITH PLUGMEM                  │
├─────────────────────────────────────────────────────────────────┤
│  1. QUERY PLUGMEM      → Retrieve best params for time slot     │
│  2. GENERATE MUSIC     → MusicGen on DirectML (Radeon 780M)     │
│  3. GENERATE TTS       → Voicebox/Qwen-TTS (news + voice)       │
│  4. MIX AUDIO          → Ducking, crossfade, LUFS normalization │
│  5. EVALUATE           → Duration, size, quality gates          │
│  6. CONSOLIDATE        → Store everything in PlugMem graph      │
│  7. BACKUP USB         → D:\backups\radio_armsgeddonfm\         │
└─────────────────────────────────────────────────────────────────┘
```

## Memory Schema (3 Types × 12 Node Types)

### Semantic Nodes (Reusable Knowledge)
| Node Type | Key Format | Example |
|-----------|------------|---------|
| `prompt_preset` | `{slot}_{style}` | `morning_energetic` |
| `music_params` | `{model}_{slot}` | `musicgen-small_morning` |
| `tts_profile` | `{voice}_{slot}` | `qwen_custom_voice_morning` |
| `feed_quality` | `{feed_name}` | `habr_ru` |

### Procedural Nodes (Executable Recipes)
| Node Type | Key Format | Example |
|-----------|------------|---------|
| `pipeline_config` | `dj_v2_{slot}` | `dj_v2_morning` |
| `generation_recipe` | `{name}` | `hour_block_standard` |
| `debug_fix` | `{symptom[:50]}` | `Voicebox TTS generation hangs` |

### Episodic Nodes (Cycle History)
| Node Type | Key Format | Example |
|-----------|------------|---------|
| `cycle_run` | `{cycle}_{slot}` | `A07_morning` |
| `quality_score` | `{cycle}_{slot}_{component}` | `A07_morning_music` |
| `listener_feedback` | `{cycle}_tg_reactions` | `A07_tg_reactions` |

## Installation

```bash
# 1. Clone and install PlugMem
cd /c/Users/tomas/ai-radio
git clone https://github.com/TIMAN-group/PlugMem.git
cd PlugMem
/c/Users/tomas/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -m pip install -e .

# 2. Initialize radio memory (creates default presets)
/c/Users/tomas/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -m radio.plugmem_client
```

## Usage

### Query Best Configurations (Pre-Generation)
```bash
# Best prompt for time slot
python -m radio.plugmem_query --slot morning --type prompt

# Best music params for model+slot
python -m radio.plugmem_query --slot morning --type music --model musicgen-small

# Best TTS profile
python -m radio.plugmem_query --slot evening --type tts --voice qwen_custom_voice

# Pipeline config
python -m radio.plugmem_query --slot day --type pipeline

# Debug fix lookup
python -m radio.plugmem_query --type fix --symptom "Voicebox hangs"
```

### Consolidate Cycle Results (Post-Generation)
```bash
python -m radio.plugmem_consolidate \
  --cycle A07 --slot morning --duration 3600 \
  --music-quality 0.85 --tts-quality 0.88 --mix-quality 0.90 \
  --pipeline-time 180 \
  --music-model musicgen-small \
  --music-prompt "upbeat electronic, 110 bpm, energetic" \
  --music-params '{"duration": 30, "temperature": 1.0}' \
  --tts-voice qwen_custom_voice --tts-preset Ryan \
  --pipeline-config '{"music_first": true, "ducking_db": -18}' \
  --storage "D:/backups/radio_armsgeddonfm/plugmem" --consolidate
```

### Run Full Evolution Cycle (2 Hours)
```bash
# Basic cycle
./scripts/evolve_cycle.sh A07 morning

# With custom paths
./scripts/evolve_cycle.sh A08 evening \
  D:/backups/radio_armsgeddonfm/plugmem \
  C:/Users/tomas/ai-radio/output
```

## Python API

```python
from radio.plugmem_client import RadioPlugMemClient, create_radio_plugmem, init_radio_memory

# Quick init with defaults
client = init_radio_memory()

# Or custom path
client = create_radio_plugmem(Path(r"D:\backups\radio_armsgeddonfm\plugmem"))

# Store knowledge
client.store_prompt_preset("morning", "energetic", "upbeat electronic, 110 bpm...")
client.store_music_params("musicgen-small", "morning", {"duration": 30}, 0.85)
client.store_tts_profile("qwen_custom_voice", "morning", {"preset": "Ryan"})
client.store_pipeline_config("dj_v2_morning", {"ducking_db": -18}, 1.0)
client.store_debug_fix("symptom", "root cause", "fix")

# Retrieve best configs
prompt = client.retrieve_best_prompt("morning", "energetic")
params = client.retrieve_best_music_params("morning", "musicgen-small")
profile = client.retrieve_best_tts_profile("morning", "qwen_custom_voice")
config = client.retrieve_pipeline_config("morning")
fix = client.retrieve_debug_fix("Voicebox hangs")

# Log cycle runs
client.log_cycle_run("A07", "morning", 3600, 
    {"music": 0.85, "tts": 0.88, "mix": 0.90},
    issues=["minor click at 00:45"],
    human_rating=0.9,
    listener_feedback={"reactions": 23, "retention_min": 47})

# Consolidate similar nodes (needs LLM)
stats = client.consolidate()

# Stats
print(client.get_stats())
```

## Directory Structure

```
/c/Users/tomas/ai-radio/
├── radio/
│   ├── __init__.py
│   ├── plugmem_client.py      # Main wrapper (RadioPlugMemClient)
│   ├── plugmem_query.py       # CLI: pre-generation queries
│   ├── plugmem_consolidate.py # CLI: post-cycle storage
│   └── dj.py                  # Orchestrator: full pipeline
├── scripts/
│   └── evolve_cycle.sh        # 2-hour cycle runner
├── EVOLUTION_SCHEMA_v3_PLUGMEM.md
└── PLUGMEM_INTEGRATION_SUMMARY.md

D:\backups\radio_armsgeddonfm\plugmem\
└── chroma/                    # ChromaDB persistent storage
    ├── radio_armsgeddonfm_semantic/
    ├── radio_armsgeddonfm_procedural/
    ├── radio_armsgeddonfm_tag/
    ├── radio_armsgeddonfm_subgoal/
    └── radio_armsgeddonfm_episodic/
```

## Quality Gates

```python
QUALITY_GATES = {
    "music": {"coherence": 0.8, "loop_quality": 0.75, "genre_match": 0.8},
    "tts": {"naturalness": 0.8, "pronunciation": 0.85, "latency_ms": 3000},
    "mix": {"lufs": -14, "ducking_db": -18, "peak_db": -1, "dynamic_range": 6},
    "pipeline": {"total_time": 300, "memory_mb": 4096, "zero_crashes": True}
}
```

## Memory Inspector (Visualization)

```bash
# Launch PlugMem Memory Inspector UI
plugmem inspector --port 7860

# Then open http://localhost:7860
# Views: Graph view | Browse view | Recall trace
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: plugmem` | Reinstall: `cd PlugMem && pip install -e .` |
| `Collection does not exist` | Run `init_radio_memory()` to create collections |
| `LLMClient takes no arguments` | Use `DummyLLMClient()` or configure OpenAI-compatible endpoint |
| Consolidation fails | Needs LLM service — configure `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL` in env |
| DirectML OOM on 780M | Reduce batch size, enable CPU offload, clear cache between gens |

## Environment Variables

```bash
# Optional: for semantic consolidation (merge similar nodes)
export LLM_BASE_URL="http://localhost:8000/v1"
export LLM_API_KEY="your-key"
export LLM_MODEL="your-model"

# Optional: for real embeddings (instead of deterministic fallback)
export EMBEDDING_BASE_URL="http://localhost:8001/v1"
export EMBEDDING_MODEL="nvidia/NV-Embed-v2"
```

## Version Badges

Each evolution cycle increments the badge: `A00 → A01 → A02...`
- Badge stored in cycle metadata
- USB backup named: `radio_A07_cycle01_20260807_093628`
- Git tag: `git tag -a A07 -m "Radio ArmsgeddonFM A07: PlugMem integration"`

## References

- **PlugMem Repo**: https://github.com/TIMAN-group/PlugMem
- **PlugMem Paper**: https://arxiv.org/abs/2603.03296 (ICML 2026)
- **Radio Schema**: `EVOLUTION_SCHEMA_v3_PLUGMEM.md`

---

**Skill Version**: 1.0.0  
**Compatible**: Hermes Agent, Windows + DirectML (Radeon 780M)  
**Storage**: USB-only backups at `D:\backups\radio_armsgeddonfm\`