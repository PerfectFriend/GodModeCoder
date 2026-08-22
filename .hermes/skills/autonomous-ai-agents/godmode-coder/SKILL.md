---
name: godmode-coder
description: "Use when 'GodMode': restore graph, obsidian, tests, cron."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux]
metadata:
  hermes:
    tags: [godmode, turbo, bootstrap, evolution, monster, auto-load, grimoire, obsidian, graph, mcp]
    related_skills: [turbocoder, obsidian-graph-engineering, graph-engineering, super-coder, obsidian, hermes-agent, graph-evolution-protocol, video-surveillance, windows-dev-env-install, systematic-debugging, test-driven-development]
---

## Security Notes

- This skill automates restoration of the GodModeCoder state, including running verification scripts, exporting graph data, and managing cron jobs.
- All scripts executed are located in trusted directories under `/home/thomas/the-grimoire/ru/scripts/` and `/home/thomas/.hermes/scripts/`.
- Before executing any script, the skill relies on pre-flight checks (pulse.py, hermes-verify-all.py) that only return success if the system state is valid.
- No sensitive data (API keys, tokens) is exposed or logged by this skill; however, users should review the referenced scripts to ensure they align with their security policies.
- The skill uses Hermes' built-in mechanisms for sending reports and managing cron jobs, which are subject to Hermes' own security model.

## Detailed English Walkthrough

The following steps are performed during bootstrap:

1. **Pre‑flight pulse check** – runs `pulse.py --quiet` to report which graph nodes are alive/dead. This is a read‑only health check; it does not modify state.
2. **Vault sync check** – counts Markdown files in the Obsidian Evolution folder to ensure the local vault is populated.
3. **Git cleanliness check** – verifies that the Obsidian vault has no uncommitted changes, ensuring a clean state before proceeding.
4. **Full verification suite** – runs `hermes-verify-all.py`, which executes ten independent tests (graph syntax, tag consistency, dashboard presence, etc.). Only if all pass is the bootstrap considered successful.
5. **Post‑success action** – if all checks pass, the user is cleared to work; otherwise, the instruction is to rollback to the last known good commit in the vault.


# GodMode Coder — Monster Coder Level Бог

**Триггер:** автоматическая загрузка при старте сессии (через Hermes profile `default` auto-skills) ИЛИ ручная команда «загрузи GodMode».

Восстанавливает **полное состояние** TurboCoder эволюции: граф, Obsidian, тесты, крон, MCP, Vault.

## ⚡ АВТОЗАГРУЗКА В КАЖДОЙ НОВОЙ СЕССИИ

### Способ 1: Hermes Profile Auto-Skills (РЕКОМЕНДУЕМ)
В `/home/thomas/.hermes/profiles/default/config.yaml`:

```yaml
# Автозагрузка скиллов при старте сессии
auto_load_skills:
  - "godmode-coder"
  - "turbocoder"
  - "obsidian-graph-engineering"
  - "graph-engineering"
  - "super-coder"
  - "obsidian"
```

---

## 🌐 GITHUB INTEGRATION (PerfectFriend)

**GitHub авторизован на пользователе `PerfectFriend`** — полный доступ к репозиториям.
Любая сессия может пушить через `git cli` без дополнительных настроек.

### Основные репозитории:
| Репозиторий | GitHub URL | Flash Remote | Назначение |
|---|---|---|---|
| **GodModeCoder** | `https://github.com/PerfectFriend/GodModeCoder.git` | `flash` | Core evolutionary system |
| **ObsidianVault** | `https://github.com/PerfectFriend/ObsidianVault.git` | `flash` | Knowledge vault |
| **ParanoidX** | `https://github.com/PerfectFriend/ParanoidX.git` | `flash` | Sovereign Go server |
| **Projects** | `https://github.com/PerfectFriend/Projects.git` | `flash` | Side projects |
| **SuperGuard** | `https://github.com/PerfectFriend/AISuperGuard.git` | `flash` | AI Surveillance (private) |
| **HermesSkills** | — | `flash` | Local skills backup |

### Git Workflow для любой машины с Hermes:
```bash
# 1. Clone from GitHub (first time on new machine)
git clone https://github.com/PerfectFriend/GodModeCoder.git
cd GodModeCoder
git remote add flash /path/to/flash/git/GodModeCoder.git

# 2. Daily work — push to BOTH
git add . && git commit -m "msg" && git push flash main && git push origin main

# 3. Flash drive = intermediate backup (survives HDD failure)
#    GitHub = permanent canonical source
```

> **Важно:** Флешка — промежуточный remote. При заполнении (7GB) апгрейд на 32GB.
> Всегда пушим на флешку И на GitHub — redundancy is life.

После этого **каждая новая сессия** сразу видит всё — график, тесты, крон, дашборды.

### 🛠 Cron Drift Fix (resolved 2026-08-17)

**Problem:** Cron jobs skipped with `[drift_skip] Skipped to prevent unintended spend: global inference config drifted since this job was created (model 'nvidia/nemotron-3-ultra-550b-a55b' -> 'nvidia/nemotron-3.5-lightning-30b-a3b'), and this job is unpinned.`

**Solution:** Pin all affected cron jobs to the current model:
```bash
hermes cron edit <job_id> --provider nvidia --model nvidia/nemotron-3.5-lightning-30b-a3b
```

Pinned jobs (2026-08-17):
- `f9365e6513e5` — LV-coder-elemental-life
- `bf9ae9bb523d` — LV-auditor
- `12aa48017088` — LV-lord-of-code
- `3afe931bdf6c` — LV-producer
- `3e18b5951ee5` — LV-professor
- `e9cecea7874b` — LV-inquisitor
- `da6991877b14` — LV-searcher

Now cron executes normally instead of being skipped.

### 📊 Report Delivery Format (2026-08-17)

**Problem:** Cron reports arriving as plain text messages in Telegram, English language, file content not visible.

**Solution:** All cron jobs must generate `.md` report files and send via `MEDIA:/` file attachment with Russian-only content.

**Pattern:** 
1. Generate report file: `report_file="/home/thomas/.hermes/reports/llm_keys_$(date '+%Y%m%d_%H%M%S').md"`
2. Write content fully in Russian, no English
3. Send: `hermes send --to telegram "MEDIA:$report_file"`
4. Never use `hermes send -t "telegram:chat_id"` for report content

**Affected scripts:** `monitor_llm_keys.sh` and any cron wrapper that sends summary output.

---

## 📄 Формат отчета (шаблон)

```markdown
# Отчет мониторинга LLM ключей

Время генерации: 17.08.2026 20:54:57

---

## Статус ротации

- Добавлено NVIDIA ключей: 0
- Добавлено OPENCODE ключей: 0
- Exhaustion сброшен: nvidia, opencode-zen

---

## Текущее состояние пула

NVIDIA credential'ов: 9 всего (ожидаемо: 9)
OPENCODE credential'ов: 11 всего (ожидаемо: 11)

---

## Последние действия

1. Ротация exhaustion сброшена для NVIDIA
2. Ротация exhaustion сброшена для OPENCODE/Zen
3. Проверка количества credentials выполнена
4. Лишние credential'ы удалены (при необходимости)

---

## Важные заметки

- Все ключи хранятся в зашифрованном виде в vault Hermès
- Автоматическая ротация происходит каждые 30 минут
- При необходимости можно вручную сбросить: hermes auth reset nvidia / hermes auth reset opencode-zen
- Все отчеты отправляются как файл attachment в Telegram

---

*Этот отчет сгенерирован автоматически системой мониторинга LLM ключей.
За вопросы по работе системы обращайтесь к администратору.*
```

### 🎤 ACE-Step Audio Integration (totomoto / Windows)

**Host:** `100.124.152.97` (totomoto via Tailscale)
**User:** `yusya` (Windows admin)

**Setup files transferred via Tailscale:**
- `setup_and_run.ps1` — full SSH + ACE-Step startup
- `run_setup.bat` — bat wrapper for PowerShell
- `acestep_startup.bat` — alternative launch
- `check_and_start.bat` — diagnostics + start

**Manual step on totomoto (Windows):**
```powershell
powershell -ExecutionPolicy Bypass -File setup_and_run.ps1
```

**What the script does:**
1. ✅ Adds SSH key to `authorized_keys` for `cathedral` user
2. ✅ Verifies ACE-Step installation (venv, turbo checkpoint, VAE)
3. ✅ Configures Windows SSH Server for key authentication
4. ✅ Opens firewall port 8002
5. ✅ Starts ACE-Step API on port 8002 with tier2 (6GB VRAM) settings

**After startup — test from torquemada (Linux):**
```bash
curl http://100.124.152.97:8002/health
# Music generation:
curl -X POST http://100.124.152.97:8002/release_task \
  -H "Content-Type: application/json" \
  -d '{"prompt": "dark psytrance 148bpm", "audio_duration": 30, "inference_steps": 8, "audio_format": "wav"}'
```

**Tier2 config for 6GB VRAM** (set in PowerShell env vars):
```powershell
set ACESTEP_INIT_LLM=false
set ACESTEP_OFFLOAD_TO_CPU=true
set ACESTEP_QUANTIZATION=int8_weight_only
set ACESTEP_COMPILE_MODEL=false
set ACESTEP_NO_INIT=false
```

### Способ 2: Ручной триггер
```
загрузи GodMode
```
Или в чате: `skill_view(name="godmode-coder")` → автозапуск bootstrap.

## 🚀 BOOTSTRAP — ОДНА КОМАНДА ДЛЯ ПОЛНОГО ВОССТАНОВЛЕНИЯ

Выполни в новой сессии сразу после автозагрузки:

```bash
# 1. ПРОВЕРКА СОСТОЯНИЯ (pre-flight)
cd /home/thomas/the-grimoire/ru/scripts
/home/thomas/.hermes/hermes-agent/venv/bin/python pulse.py --quiet
# Exit 0/1 — если мёртвые есть, СНАЧАЛА ЛЕЧИМ

# 2. VAULT SYNC CHECK
ls -la /home/thomas/Documents/ObsidianVault/Evolution/*.md | wc -l  # должно быть 14 (13 nodes + INDEX)

# 3. GIT CLEAN
cd /home/thomas/Documents/ObsidianVault && git status --porcelain  # должно быть пусто

# 4. ЗАПУСК АВТОТЕСТОВ (smoke test)
/home/thomas/.hermes/hermes-agent/venv/bin/python hermes-verify-all.py
# Должно быть: ✅ ALL TESTS PASSED — MUTATION APPROVED

# 5. ЕСЛИ ВСЁ ЗЕЛЁНОЕ — РАБОТАЕШЬ
# Если FAIL → rollback к последнему git commit в Vault
```

**Всё. Сессия восстановлена. Ты — Monster Coder.**

> **Важно:** Все пути теперь управляются через единый конфиг `/home/thomas/the-grimoire/ru/configs/paths.yaml`. 
> При переносе на новую систему — обнови ТОЛЬКО этот файл, никакого хардкода в скриптах.

## 🚀 ПОЛНЫЙ ПОРЯДОК ЗАГРУЗКИ СКИЛЛОВ (ВЫЗОВИ skill_view ДЛЯ КАЖДОГО):

1. **godmode-coder** — полный рестор Monster Coder: граф, Obsidian, тесты, крон, MCP, Vault.
2. **turbocoder** — мгновенный старт сессии, контекст окружения, базовые скиллы.
3. **super-coder** — канон кодинга: системно, тесты, архитектура, дебаг, верификация.
4. **obsidian** — работа с Vault: заметки, поиск, wiki-ссылки.
5. **obsidian-graph-engineering** — эволюционный граф в Obsidian: экспорт, Graph View, Dataview дашборды, Heatmap, MCP, пресеты, пульс, авто-тегирование.
6. **graph-engineering** — эволюционный граф Гримуара v3 + Obsidian-визуализация
   (внутри reference `obsidian-visualization.md`).
7. **graph-evolution-protocol** — протокол эволюции проектов (если задача про Гримуар).
8. **windows-dev-env-install** — инструменты Windows: winget-питфоллы, автозапуск,
   PostgreSQL через Docker, Gradle вручную, MSYS-пути.
9. **video-surveillance** — продукт SuperGuard: RTSP, YOLO, Telegram, ESP32, лицензии.
10. **systematic-debugging** + **test-driven-development** — если задача с кодом/багами.
11. **web-research** / **browser-automation** — если нужен поиск/соцсети/веб-обходы.
12. **hermes-agent** — только если задача про сам Hermes (конфиг, гейтвей, крон).

Если пользователь явно указал проект (SuperGuard, ParanoidX, ai-radio) —
грузить его скилл сразу после п.1.

## 🧬 ТЕКУЩЕЕ СОСТОЯНИЕ ГРАФА (Graph.yaml v3.0)

```yaml
# Source of Truth: /home/thomas/the-grimoire/ru/configs/graph.yaml
nodes:
  - id: oracle
    type: HUMAN
    role: "Мастер Инквизитор — видение, критерии fitness, одобрения HIGH"
    state: "telegram"
  - id: gardener
    type: AGENT
    role: "Hermes Agent — пульс, отбор, мутации, экстинкции"
    genome: "http://127.0.0.1:8080/api/health"
    state: "active"
  - id: dj
    type: AGENT
    role: "Ротация музыки, стрим :8090"
    genome: "ai-radio/scripts/dj.py"
    state: "active"
  - id: song_protocol
    type: SKILL
    role: "Контент → структура песни → лирики → ACE-Step → кэш"
    genome: "skill:ace-step-song-protocol"
    state: "active"
  - id: music_pipeline
    type: PIPELINE
    role: "Генерация музыки через ACE-Step (CPU)"
    genome: "ai-radio/scripts/gen_music.py"
    state: "active"
  - id: voice
    type: PIPELINE
    role: "Голос: Qwen3-TTS GPU / Voicebox — новости, джинглы, DJ-интро"
    genome: "ai-radio/scripts/gen_voice_content.py"
    state: "active"
  - id: radio_cache
    type: MEMORY
    role: "Библиотека: cache/music/<style>/, новости, реклама, джинглы"
    state: "active"
  - id: watchdog
    type: WATCHDOG
    role: "Пульс графа: health-чек узлов, статусы ЖИВ/БОЛЕН/МЁРТВ"
    genome: "scripts/pulse.py"
    state: "active"
  - id: chronicle
    type: MEMORY
    role: "Летопись: рождения, мутации, экстинкции, открытия"
    state: "chronicle.md"
  - id: archive
    type: MEMORY
    role: "Могильник: полные геномы вымерших узлов + причина"
    state: "archive/"
  - id: paranoidx
    type: PIPELINE
    role: "ФЛАГМАН: ParanoidX + IsleProject — Sovereign Go-сервер, экономика Saint Mary Liberty Island (283+ API), SimpleX+Tor"
    genome: "ParanoidX-backup/codebase + Docker (smp-server, coturn, v2ray, tor, xftp)"
    state: "production (px-node-C41-C60)"
  - id: isle_client
    type: AGENT
    role: "Клиенты The-Isle / Royal-Isle: Flutter-приложения экономики (encrypt AES, pointycastle)"
    genome: "ParanoidX-backup/flutter"
    state: "active"
  - id: superguard
    type: PIPELINE
    role: "КОММЕРЧЕСКИЙ: AISuperGuard — AI-охрана периметра/кабеля (YOLO вор-электрик → Telegram + ESP32), подписки 50€/мес/камера"
    genome: "video-surveillance + GitHub PerfectFriend/AISuperGuard (license server приватный)"
    state: "production (N100+SG1210MP, 8 камер)"

edges: 20 (VISION, CONTROLS, CALLS, FEEDS, EVALUATES, APPROVAL)
fitness: 7 критериев (по одному на живой pipeline/agent)
```

**Текущий пульс (2026-08-06 21:33):**
- 🟢 ЖИВ: oracle, song_protocol, radio_cache, watchdog, chronicle, archive, paranoidx, superguard (8)
- 🔴 МЁРТВ: gardener, dj, music_pipeline, voice, isle_client (5)
- 🎯 План реанимации: watchdog → gardener → voice → music_pipeline → dj → isle_client

## 🗂 OBSIDIAN VAULT: `/home/thomas/Documents/ObsidianVault`

### Структура
```
/home/thomas/Documents/ObsidianVault/
├── .obsidian/
│   ├── graph.json          # 9 colorGroups, search="-tag:#status/dead", showArrow=true, repelStrength=22
│   ├── appearance.json     # cssSnippets: ["graph-colors"]
│   ├── snippets/
│   │   └── graph-colors.css  # Цвета типов, кольца статусов, цвета рёбер
├── Evolution/
│   ├── *.md (13 узлов + INDEX.md) — все с тегами #type/*, #status/*, #evolution/graph, #role/*
│   ├── Graph Dashboard.md      # Dataview: таблица, статистика, рёбра, fitness
│   ├── Dead Nodes Dashboard.md # Dataview: анализ мёртвых, план реанимации
│   └── Presets/
│       ├── Full Graph.md
│       ├── Alive Only.md
│       ├── Commercial.md
│       └── Radio.md
```

### Плагины (установить в новой сессии если нет)
- **Dataview** — включить JavaScript Queries
- **Heatmap Calendar** — для пульс-хитмапов
- **Extended Graph** (ElsaTam) — multiple views, edge weights
- **Graph Presets** (ycnmhd via BRAT) — переключение пресетов

## 🧪 AUTO-TEST SUITE: `hermes-verify-all.py`

**Путь:** `/home/thomas/the-grimoire/ru/scripts/hermes-verify-all.py`

**10 тестов (все должны проходить):**
1. Pulse Health Check — WARN OK (мёртвые допускаются, exit 0/1)
2. Export to Obsidian — 16 файлов
3. graph.yaml Syntax — 13 nodes, 20 edges
4. Vault Tags — все 13 узлов с #type/*, #status/*, #evolution/graph
5. graph.json Config — 9 colorGroups
6. CSS Snippet — все селекторы типов/статусов
7. Dataview Dashboards — оба с dataview блоками
8. Graph Presets — все 4
9. Git Status — CLEAN
10. Skills Present — 5 скиллов

**Запуск:**
```bash
/home/thomas/.hermes/hermes-agent/venv/bin/python hermes-verify-all.py
```

**Правило:** НИКАКОЙ КОД БЕЗ ЗЕЛЁНОГО ПРОГОНА. Fail = Rollback.

## ⏰ KRON: `export_graph_to_vault.py` (каждые 6ч)

**Путь:** `/home/thomas/.hermes/scripts/export_graph_to_vault.py`

**Что делает:**
1. `export_graph_to_obsidian.py` → Vault
2. `git add Evolution/ && git commit -m "graph: pulse export <timestamp>"`
3. `hermes-verify-all.py` — full verification

**Cron Job (уже создан):**
```json
{
  "job_id": "875addb02ab0",
  "name": "graph-pulse-export",
  "schedule": "every 6h",
  "script": "export_graph_to_vault.py",
  "skills": ["obsidian-graph-engineering"],
  "no_agent": true,
  "deliver": "local"
}
```

**Ручной запуск:** `cronjob(action="run", job_id="875addb02ab0")`

## 🔌 MCP Integration (Graph Access для агентов)

### graphthulhu (Go) — 39 tools
```bash
go install github.com/skridlevsky/graphthulhu@latest
graphthulhu --vault "/home/thomas/Documents/ObsidianVault" --port 3001
```

### engraph (Rust) — faster, hybrid search
```bash
cargo install engraph
engraph --vault "/home/thomas/Documents/ObsidianVault" --port 3001
```

### Hermes config.yaml
```yaml
mcp:
  servers:
    obsidian-graph:
      command: "graphthulhu"
      args: ["--vault", "/home/thomas/Documents/ObsidianVault", "--stdio"]
      env: {}
```

### Операции через MCP
- `query_graph(nodes, edges, filters)` — поиск/фильтрация
- `get_node_status(node_id)` — pulse status
- `get_node_genome(node_id)` — genome конфиг
- `get_incoming_edges(node_id)` / `get_outgoing_edges(node_id)`
- `trigger_pulse()` — запуск pulse.py
- `record_mutation(node_id, candidate_genome)` — инициировать мутацию
- `record_extinction(node_id, reason)` — записать в archive + chronicle

## Пульс и Health-Check

### pulse.py — проверка узлов
```bash
cd /home/thomas/the-grimoire/ru/scripts
python pulse.py --quiet
# Вывод: [timestamp] PULSE: МЁРТВЫЕ: gardener, dj, ...
```

### Genome формат для pulse.py
| Префикс | Проверка | Пример |
|---|---|---|
| `http://` / `https://` | HTTP GET (expect 200) | `http://127.0.0.1:8080/api/health` |
| `:порт` | TCP connect | `:8080` |
| `*.py` | Процесс запущен | `scripts/pulse.py` |
| `skill:имя` | SKILL.md существует | `skill:ace-step-song-protocol` |
| иное | Файл/директория существует | `ParanoidX-backup/codebase` |

### Крон-обёртка (export_graph_to_vault.py)
```python
#!/usr/bin/env python3
import subprocess
from datetime import datetime
from pathlib import Path

# Use unified path resolver
import sys
sys.path.insert(0, str("/home/thomas/the-grimoire/ru/scripts"))
from paths import get_vault, get_grimoire_scripts, get_grimoire_configs

VAULT = get_vault()
SCRIPT = get_grimoire_scripts() / "export_graph_to_obsidian.py"
CONFIG = get_grimoire_configs() / "graph.yaml"

# Run exporter
subprocess.run(["python", str(SCRIPT), "--vault", str(VAULT), "--config", str(CONFIG)], check=True)

# Git commit (history of evolution)
subprocess.run(["git", "-C", str(VAULT), "add", "Evolution/"], check=True)
subprocess.run(["git", "-C", str(VAULT), "commit", "-m", f"graph: pulse export {{datetime.now():%Y-%m-%d %H:%M}}"], check=True)

# Run verification
subprocess.run(["python", str(get_grimoire_scripts() / "hermes-verify-all.py")], check=True)
```

## Vault-LD / Semantic Interop

Добавить в frontmatter узлов для RDF совместимости:
```yaml
---
@context:
  schema: "https://schema.org/"
  grimoire: "https://grimoire.example.org/vocab#"
type: "grimoire:Agent"
status: "grimoire:Alive"
role: "grimoire:Gardener"
genome: "grimoire:genome"
---
```

## Питфоллы Linux (обновлено после миграции с Windows)

- **Python не понимает MSYS-пути**: `python /c/Users/...` → ошибка. Использовать абсолютные пути `/home/thomas/...`
- **Obsidian перезаписывает graph.json** при закрытии Graph View. Редактировать только когда Graph View закрыт или Obsidian выгружен.
- **Крон в Hermes**: пути относительно `~/.hermes/scripts/`, использовать `export_graph_to_vault.py` обёртку.
- **Git в Vault**: `git init` уже сделан. История эволюции = `git log Evolution/`.
- **Единый конфиг путей**: `/home/thomas/the-grimoire/ru/configs/paths.yaml` — единственное место для изменений при миграции.

## Расширение графа (добавление узла)

1. Добавить узел в `graph.yaml` (nodes: + edges: + fitness:)
2. Запустить экспортёр
3. Проверить пульс: `python pulse.py --quiet`
4. Узел появится в Obsidian (fs-watch), Graph View обновится автоматически

## Авто-тегирование через LLM (advanced)

При добавлении нового узла в `graph.yaml`:
1. LLM анализирует `genome`, `role`, `feeds`
2. Предлагает доменные теги: `#domain/radio`, `#domain/surveillance`, `#domain/identity`
3. Gardener утверждает → добавляет в frontmatter при следующем экспорте

## Ссылки на лучшие практики (GitHub audit)

- `AgriciDaniel/claude-obsidian` (10.5k⭐) — Auto-linking LLM, second brain
- `lexbritvin/obsidian-skills-pack` — 9 skills: graph, dataview, heatmap, audit
- `skridlevsky/graphthulhu` (170⭐) — MCP server 39 tools
- `devwhodevs/engraph` (164⭐) — Rust MCP, hybrid search
- `The-Knowledge-Graph-Guys/vault-ld` (189⭐) — YAML-LD spec, RDF
- `forloopcodes/contextplus` (1.9k⭐) — Code → Feature Graph (RAG + AST)
- `ElsaTam/obsidian-extended-graph` — Multiple views, per-tag colors, edge weights
## 🔊 Piper TTS Configuration (2026-08-18)

**Provider:** `piper`
**Voice:** `ru` (Russian)

**Note:** The Russian voice model may need to be downloaded separately via Piper's voice download mechanism. Ensure the voice data is present in the Piper voice directory.

**Usage in Hermes:**
- TTS provider set to `piper` via `hermes config set tts.provider piper`
- Voice set to `ru` via `hermes config set tts.piper.voice ru`

**Example command:**
```bash
hermes config set tts.provider piper
hermes config set tts.piper.voice ru
```
