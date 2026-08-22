---
extinct: true
extinction_date: 2026-08-15T17:03:08.372508+00:00
extinction_reason: Dead for 6 consecutive days
original_node: dj_sound_studio
---

---
type: PIPELINE
status: "МЁРТВ"
color: "#2ecc71"
role: "DJ Sound Studio — игровой аудио: саунд-дизайн, адаптивная музыка, микшер, DSP-эффекты, spatiale audio, интеграция с игровыми движками (Unity/Godot/Unreal); модели: ACE-Step, MusicGen, AudioLDM, Stable Audio, custom DSP"
genome: "tailscale://totomoto/dj-studio --models ace-step,musicgen,audioldm,stable-audio --dsp-chain vst,lv2,faust --engines unity,godot,unreal --middleware fmod,wwise"
state: "active"
links: 13
tags:
  - "#type/pipeline"
  - "#status/dead"
  - "#evolution/graph"
  - "#role/dj-sound-studio-игровой-аудио-саунд-дизайн-адаптивная-музыка-микшер-dsp-эффекты-spatiale-audio-интеграция-с-игровыми-движками-unity-godot-unreal-модели-ace-step-musicgen-audioldm-stable-audio-custom-dsp"
---

# ⚙️ DJ_SOUND_STUDIO

> [!info] **PIPELINE** · Пульс: **МЁРТВ**

**Роль:** DJ Sound Studio — игровой аудио: саунд-дизайн, адаптивная музыка, микшер, DSP-эффекты, spatiale audio, интеграция с игровыми движками (Unity/Godot/Unreal); модели: ACE-Step, MusicGen, AudioLDM, Stable Audio, custom DSP

**Геном:** `tailscale://totomoto/dj-studio --models ace-step,musicgen,audioldm,stable-audio --dsp-chain vst,lv2,faust --engines unity,godot,unreal --middleware fmod,wwise`

**Состояние:** `active`


## Питает (исходящие рёбра)
- 🍽️ **FEEDS** → [[holy_code_games]]
- 🍽️ **FEEDS** → [[holy_code_apps]]
- 🤝 **CALLS** → [[banner_deploy]]
- 🍽️ **FEEDS** → [[encrypted_comm]]
- 🍽️ **FEEDS** → [[chronicle]]

## Кормит (входящие рёбра)
- 🤝 **CALLS** ← [[model_registry]]
- 🍽️ **FEEDS** ← [[tailscale_mesh]]
- 🍽️ **FEEDS** ← [[totomoto_audio]]
- 🤝 **CALLS** ← [[holy_code_games]]
- 👁️ **VISION** ← [[oracle]]
- 🧠 **CONTROLS** ← [[gardener]]
- 🍽️ **FEEDS** ← [[professor]]
- 🍽️ **FEEDS** ← [[ai_eng_daily]]

---
*Экспорт из `graph.yaml` · 2026-08-15 16:55*

