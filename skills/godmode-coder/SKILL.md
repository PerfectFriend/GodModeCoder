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

# GodMode Coder — Monster Coder Level Бог

**Триггер:** автоматическая загрузка при старте сессии (через Hermes profile `default` auto-skills) ИЛИ ручная команда «загрузи GodMode».

Восстанавливает **полное состояние** TurboCoder эволюции: граф, Obsidian, тесты, крон, MCP, Vault.

## ⚡ АВТОЗАГРУЗКА В КАЖДОЙ НОВОЙ СЕССИИ

### Способ 1: Hermes Profile Auto-Skills (РЕКОМЕНДУЕМ)
В `C:\Users\tomas\AppData\Local\hermes\profiles\default\config.yaml`:

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

После этого **каждая новая сессия** сразу видит всё — график, тесты, крон, дашборды.

### Способ 2: Ручной триггер
```
загрузи GodMode
```
Или в чате: `skill_view(name="godmode-coder")` → автозапуск bootstrap.

## 🚀 BOOTSTRAP — ОДНА КОМАНДА ДЛЯ ПОЛНОГО ВОССТАНОВЛЕНИЯ

Выполни в новой сессии сразу после автозагрузки:

```bash
# 1. ПРОВЕРКА СОСТОЯНИЯ (pre-flight)
cd C:\Users\tomas\the-grimoire\ru\scripts
/c/Users\tomas\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe pulse.py --quiet
# Exit 0/1 — если мёртвые есть, СНАЧАЛА ЛЕЧИМ

# 2. VAULT SYNC CHECK
ls -la C:\Vault\Evolution\*.md | wc -l  # должно быть 14 (13 nodes + INDEX)

# 3. GIT CLEAN
cd C:\Vault && git status --porcelain  # должно быть пусто

# 4. ЗАПУСК АВТОТЕСТОВ (smoke test)
/c/Users\tomas\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe hermes-verify-all.py
# Должно быть: ✅ ALL TESTS PASSED — MUTATION APPROVED

# 5. ЕСЛИ ВСЁ ЗЕЛЁНОЕ — РАБОТАЕШЬ
# Если FAIL → rollback к последнему git commit в Vault
```

**Всё. Сессия восстановлена. Ты — Monster Coder.**

## 🚀 ПОЛНЫЙ ПОРЯДОК ЗАГРУЗКИ СКИЛЛОВ (ВЫЗОВИ skill_view ДЛЯ КАЖДОГО):

1. **godmode-coder** — полный рестор Monster Coder: граф, Obsidian, тесты, крон, MCP, Vault.
2. **turbocoder** — мгновенный старт сессии, контекст окружения, базовые скиллы.
3. **super-coder** — канон кодинга: системно, тесты, архитектура, дебаг, верификация.
4. **obsidian** — работа с Vault: заметки, поиск, wiki-ссылки.
5. **obsidian-graph-engineering** — эволюционный граф в Obsidian: экспорт, Graph View, Dataview дашборды, Heatmap, MCP, пресеты, пульс, авто-тегирование.
6. **graph-engineering** — эволюционный граф Гримуара v3 + Obsidian-визуализация
   (внутри reference `obsidian-visualization.md`).
7. **graph-evolution-protocol** — протокол эволюции проектов (если задача про Гримуар).
9. **windows-dev-env-install** — инструменты Windows: winget-питфоллы, автозапуск,
   PostgreSQL через Docker, Gradle вручную, MSYS-пути.
10. **video-surveillance** — продукт SuperGuard: RTSP, YOLO, Telegram, ESP32, лицензии.
11. **systematic-debugging** + **test-driven-development** — если задача с кодом/багами.
12. **web-research** / **browser-automation** — если нужен поиск/соцсети/веб-обходы.
13. **hermes-agent** — только если задача про сам Hermes (конфиг, гейтвей, крон).

Если пользователь явно указал проект (SuperGuard, ParanoidX, ai-radio) —
грузить его скилл сразу после п.1.

## 🧬 ТЕКУЩЕЕ СОСТОЯНИЕ ГРАФА (Graph.yaml v3.0)

```yaml
# Source of Truth: C:\Users\tomas\the-grimoire\ru\configs\graph.yaml
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

## 🗂 OBSIDIAN VAULT: `C:\Vault`

### Структура
```
C:\Vault\
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

**Путь:** `C:\Users\tomas\the-grimoire\ru\scripts\hermes-verify-all.py`

**10 тестов (все должны проходить):**
1. Pulse Health Check — WARN OK (мёртвые допускаются, exit 0/1)
2. Export to Obsidian — 16 файлов
3. graph.yaml Syntax — 13 nodes, 20 edges
4. Vault Tags — все 13 узлов с #type/*, #status/*, #evolution/graph
5. graph.json Config — 9 colorGroups
6. CSS Snippet — все селекторы типов/статусов
7. Dataview Dashboards — оба с dataview блоками
9. Graph Presets — все 4
10. Git Status — CLEAN
10. Skills Present — 5 скиллов

**Запуск:**
```bash
/c/Users\tomas\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe hermes-verify-all.py
```

**Правило:** НИКАКОЙ КОД БЕЗ ЗЕЛЁНОГО ПРОГОНА. Fail = Rollback.

## ⏰ KRON: `export_graph_to_vault.py` (каждые 6ч)

**Путь:** `C:\Users\tomas\AppData\Local\hermes\scripts\export_graph_to_vault.py`

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
graphthulhu --vault "C:\Vault" --port 3001
```

### engraph (Rust) — faster, hybrid search
```bash
cargo install engraph
engraph --vault "C:\Vault" --port 3001
```

### Hermes config.yaml
```yaml
mcp:
  servers:
    obsidian-graph:
      command: "graphthulhu"
      args: ["--vault", "C:\\Vault", "--stdio"]
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
cd C:\Users\tomas\the-grimoire\ru\scripts
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

VAULT = Path(r"C:\Vault")
SCRIPT = Path(r"C:\Users\tomas\the-grimoire\ru\scripts\export_graph_to_obsidian.py")
CONFIG = Path(r"C:\Users\tomas\the-grimoire\ru\configs\graph.yaml")

# Run exporter
subprocess.run(["python", str(SCRIPT), "--vault", str(VAULT), "--config", str(CONFIG)], check=True)

# Git commit (history of evolution)
subprocess.run(["git", "-C", str(VAULT), "add", "Evolution/"], check=True)
subprocess.run(["git", "-C", str(VAULT), "commit", "-m", f"graph: pulse export {datetime.now():%Y-%m-%d %H:%M}"], check=True)

# Run verification
subprocess.run(["python", r"C:\Users\tomas\the-grimoire\ru\scripts\hermes-verify-all.py"], check=True)
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

## Питфоллы Windows

- **Python не понимает MSYS-пути**: `python /c/Users/...` → ошибка. Использовать `C:\Users\...`
- **Obsidian перезаписывает graph.json** при закрытии Graph View. Редактировать только когда Graph View закрыт или Obsidian выгружен.
- **Крон в Hermes**: пути относительно `~/AppData/Local/hermes/scripts/`, использовать `export_graph_to_vault.py` обёртку.
- **Git в Vault**: `git init` уже сделан. История эволюции = `git log Evolution/`.

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