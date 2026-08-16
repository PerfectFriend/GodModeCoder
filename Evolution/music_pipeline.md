Warning: Permanently added '100.124.152.97' (ED25519) to the list of known hosts.
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
---
type: PIPELINE
status: "МЁРТВ"
color: "#2ecc71"
role: "Генерация музыки через ACE-Step (CPU)"
genome: "ai-radio/scripts/gen_music.py"
state: "active"
links: 3
tags:
  - "#type/pipeline"
  - "#status/dead"
  - "#evolution/graph"
  - "#role/генерация-музыки-через-ace-step-cpu"
---

# ⚙️ MUSIC_PIPELINE

> [!info] **PIPELINE** · Пульс: **МЁРТВ**

**Роль:** Генерация музыки через ACE-Step (CPU)

**Геном:** `ai-radio/scripts/gen_music.py`

**Состояние:** `active`


## Питает (исходящие рёбра)
- 🍽️ **FEEDS** → [[radio_cache]]

## Кормит (входящие рёбра)
- 🤝 **CALLS** ← [[song_protocol]]
- 🧠 **CONTROLS** ← [[watchdog]]

---
*Экспорт из `graph.yaml` · 2026-08-08 07:17*
