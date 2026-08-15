---
name: obsidian-graph-engineering
description: "Use for graph.yaml evolution graphs in Obsidian."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux]
metadata:
  hermes:
    tags: [graph, evolution, obsidian, grimoire, visualization, dataview, mcp, pulse]
    related_skills: [graph-engineering, obsidian, turbocoder, super-coder]
---

# Obsidian Graph Engineering — Эволюционный Граф в Obsidian

Полный воркфлоу для работы с эволюционным графом Гримуара v3.0 в Obsidian:
экспорт из `graph.yaml` → визуализация в Graph View → Dataview дашборды → пульс/health-check → MCP доступ для агентов.

## Архитектура

```
graph.yaml (Source of Truth)
       │
       ▼
export_graph_to_obsidian.py (Exporter)
       │
       ▼
C:\Vault\Evolution\*.md (Nodes + INDEX.md + Dashboards)
       │
       ├──► Graph View (визуализация через [[wiki-links]])
       ├──► Dataview (запросы по frontmatter: type, status, tags)
       ├──► Heatmap Calendar (активность пульса во времени)
       └──► MCP Server (graphthulhu/engraph) → Hermes Agent
```

## Быстрый старт

### 1. Экспорт графа (ручной или крон)
```bash
cd C:\Users\tomas\the-grimoire\ru\scripts
python export_graph_to_obsidian.py --vault "C:\Vault" --config ../configs/graph.yaml
```

### 2. Открыть в Obsidian
- Vault: `C:\Vault`
- Граф: `Evolution/` папка
- Graph View: `Ctrl+G` → настроить пресеты из `Evolution/Presets/`
- Дашборды: `Evolution/Graph Dashboard.md`, `Evolution/Dead Nodes Dashboard.md`

### 3. Крон (авто-экспорт каждые 6ч)
```bash
# В Hermes cron (no_agent=true, deliver=local)
hermes cron create \
  --name "graph-pulse-export" \
  --schedule "every 6h" \
  --script "export_graph_to_vault.py" \
  --skills "obsidian-graph-engineering"
```

## Конфигурация Obsidian (.obsidian/)

### graph.json — Основные настройки
```json
{
  "collapse-filter": false,
  "search": "-tag:#status/dead",
  "showTags": false,
  "showAttachments": false,
  "hideUnresolved": true,
  "showOrphans": false,
  "collapse-color-groups": false,
  "colorGroups": [
    {"query": "tag:#type/human", "color": {"a": 1, "rgb": 15177922}},
    {"query": "tag:#type/agent", "color": {"a": 1, "rgb": 3447003}},
    {"query": "tag:#type/skill", "color": {"a": 1, "rgb": 10185699}},
    {"query": "tag:#type/pipeline", "color": {"a": 1, "rgb": 3033169}},
    {"query": "tag:#type/memory", "color": {"a": 1, "rgb": 9801126}},
    {"query": "tag:#type/watchdog", "color": {"a": 1, "rgb": 15158332}},
    {"query": "tag:#status/alive", "color": {"a": 1, "rgb": 3033169}},
    {"query": "tag:#status/sick", "color": {"a": 1, "rgb": 15781984}},
    {"query": "tag:#status/dead", "color": {"a": 1, "rgb": 15158332}}
  ],
  "collapse-display": false,
  "showArrow": true,
  "textFadeMultiplier": 0.5,
  "nodeSizeMultiplier": 1.3,
  "lineSizeMultiplier": 0.8,
  "collapse-forces": false,
  "centerStrength": 0.5,
  "repelStrength": 22,
  "linkStrength": 0.7,
  "linkDistance": 220,
  "scale": 0.7,
  "close": true
}
```

### CSS Snippet (graph-colors.css)
Путь: `C:\Vault\.obsidian\snippets\graph-colors.css`
- Цвета узлов по типу (HUMAN/AGENT/SKILL/PIPELINE/MEMORY/WATCHDOG)
- Кольца статуса (alive/sick/dead)
- Цвета рёбер по типу (CONTROLS/FEEDS/CALLS/VISION/APPROVAL/EVALUATES/MUTATES/BACKUPS)

### Включить snippet
`C:\Vault\.obsidian\appearance.json`:
```json
{"cssSnippets": ["graph-colors"]}
```

## Теги в экспорте (frontmatter)

Каждый узел получает теги:
```yaml
tags:
  - #type/agent          # по node.type (human/agent/skill/pipeline/memory/watchdog/gateway)
  - #status/alive        # по pulse статусу (alive/sick/dead/unknown)
  - #evolution/graph     # общий тег графа
  - #role/hermes-agent   # по node.role (slugified)
```

## Dataview Дашборды

### Graph Dashboard.md
- Интерактивная таблица всех узлов (тип, статус, роль, геном, связи)
- Статистика графа (кол-во узлов, средняя степень, распределение по типам/статусам)
- Рёбра графа (парсинг из wiki-ссылок в заметках)
- Fitness-критерии из graph.yaml

### Dead Nodes Dashboard.md
- Только мёртвые узлы (кроме MEMORY)
- Анализ по типам: AGENT, PIPELINE, WATCHDOG
- План реанимации по приоритету
- Команды диагностики

### Создание своих дашбордов
```dataview
TABLE file.link, type, status, role, genome
FROM "#evolution/graph"
WHERE type = "PIPELINE"
SORT status DESC
```

## Graph Presets (Evolution/Presets/)

| Пресет | Фильтр Search | Назначение |
|---|---|---|
| Full Graph | `tag:#evolution/graph` | Все узлы |
| Alive Only | `tag:#evolution/graph AND -tag:#status/dead` | Только живые |
| Commercial | `tag:#evolution/graph AND (file:paranoidx OR file:superguard OR file:isle_client OR file:oracle OR file:gardener)` | ParanoidX + SuperGuard |
| Radio | `tag:#evolution/graph AND (file:dj OR file:music_pipeline OR file:voice OR file:radio_cache OR file:song_protocol OR file:gardener OR file:watchdog)` | AI-Radio stack |

## MCP Integration (Graph Access for Agents)

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

### Доступные операции через MCP
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

vault = Path(r"C:\Vault")
script = Path(r"C:\Users\tomas\the-grimoire\ru\scripts\export_graph_to_obsidian.py")
config = Path(r"C:\Users\tomas\the-grimoire\ru\configs\graph.yaml")

# Run exporter
subprocess.run(["python", str(script), "--vault", str(vault), "--config", str(config)], check=True)

# Git commit (history of evolution)
subprocess.run(["git", "-C", str(vault), "add", "Evolution/"], check=True)
subprocess.run(["git", "-C", str(vault), "commit", "-m", f"graph: pulse export {datetime.now():%Y-%m-%d %H:%M}"], check=True)
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
- **Git в Vault**: инициализировать `git init` в `C:\Vault` для истории эволюции.

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