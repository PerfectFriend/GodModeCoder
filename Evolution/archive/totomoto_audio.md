---
extinct: true
extinction_date: 2026-08-15T17:03:08.372974+00:00
extinction_reason: Dead for 6 consecutive days
original_node: totomoto_audio
---

---
type: PIPELINE
status: "МЁРТВ"
color: "#2ecc71"
role: "totomoto Audio Node — полный цикл звука: генерация рекламы для радио (ACE-Step + MusicGen), голосовое общение с Мастером (STT+TTS+LLM), клонирование голоса, микширование, мастерринг; модели локальные на totomoto"
genome: "tailscale://totomoto/audio-pipeline --models ace-step,musicgen,xtts-v2,whisper-large-v3,llm-voice"
state: "active"
links: 7
tags:
  - "#type/pipeline"
  - "#status/dead"
  - "#evolution/graph"
  - "#role/totomoto-audio-node-полный-цикл-звука-генерация-рекламы-для-радио-ace-step-musicgen-голосовое-общение-с-мастером-sttttsllm-клонирование-голоса-микширование-мастерринг-модели-локалные-на-totomoto"
---

# ⚙️ TOTOMOTO_AUDIO

> [!info] **PIPELINE** · Пульс: **МЁРТВ**

**Роль:** totomoto Audio Node — полный цикл звука: генерация рекламы для радио (ACE-Step + MusicGen), голосовое общение с Мастером (STT+TTS+LLM), клонирование голоса, микширование, мастерринг; модели локальные на totomoto

**Геном:** `tailscale://totomoto/audio-pipeline --models ace-step,musicgen,xtts-v2,whisper-large-v3,llm-voice`

**Состояние:** `active`


## Питает (исходящие рёбра)
- 🤝 **CALLS** → [[banner_deploy]]
- 🍽️ **FEEDS** → [[encrypted_comm]]
- 🍽️ **FEEDS** → [[chronicle]]
- 🍽️ **FEEDS** → [[holy_code_apps]]
- 🤝 **CALLS** → [[model_registry]]
- 🍽️ **FEEDS** → [[dj_sound_studio]]

## Кормит (входящие рёбра)
- 🍽️ **FEEDS** ← [[tailscale_mesh]]

---
*Экспорт из `graph.yaml` · 2026-08-15 16:55*

