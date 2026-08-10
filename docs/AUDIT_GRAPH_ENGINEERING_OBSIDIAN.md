# АУДИТ: Graph Engineering + Obsidian Integration
**Дата:** 2026-08-06  
**Версия:** 1.0  
**Контекст:** Анализ текущего эволюционного графа Гримуара v3.0, экспорта в Obsidian, текущей конфигурации `.obsidian/` и лучших практик из экосистемы (claude-obsidian, obsidian-skills-pack, graphthulhu, vault-ld, engraph, swarmvault).

---

## 📊 EXECUTIVE SUMMARY

| Компонент | Текущее состояние | Оценка | Приоритет |
|---|---|---|---|
| **Экспортёр (`export_graph_to_obsidian.py`)** | Работает, создаёт 13 заметок + INDEX.md | ✅ Хорошо | — |
| **Graph View Obsidian** | Базовые настройки, нет цветовых групп | ⚠️ Требует настройки | **HIGH** |
| **`.obsidian/graph.json`** | Только force-directed, нет фильтров/групп | ⚠️ Минимально | **HIGH** |
| **`.obsidian/workspace.json`** | Только layout | ⚠️ Не используется | MEDIUM |
| **Dataview** | Не установлен | ❌ Отсутствует | **HIGH** |
| **Heatmap Calendar** | Не установлен | ❌ Отсутствует | MEDIUM |
| **Extended Graph** | Не установлен | ❌ Отсутствует | MEDIUM |
| **Graph Presets** | Не установлен | ❌ Отсутствует | LOW |
| **Pulse integration** | Авто-экспорт каждые 6ч (крон) | ✅ Работает | — |
| **Vault structure** | Только `Evolution/` + дневники | ⚠️ Ограниченная | MEDIUM |

---

## 🔍 АУДИТ ТЕКУЩЕГО СОСТОЯНИЯ

### 1. Экспортёр графов (`export_graph_to_obsidian.py`)

**Сильные стороны:**
- ✅ Читает `graph.yaml` + `pulse.py --quiet` для статусов ЖИВ/БОЛЕН/МЁРТВ
- ✅ Создаёт заметки с frontmatter (type, status, color, role, genome, state, links)
- ✅ Использует `[[wiki-ссылки]]` для рёбер — Graph View строит связи автоматически
- ✅ Эмодзи по типам узлов (HUMAN🧑‍🔬, AGENT🤖, SKILL📜, PIPELINE⚙️, MEMORY🗄️, WATCHDOG🩺)
- ✅ Эмодзи по типам рёбер (FEEDS🍽️, CALLS🤝, CONTROLS🧠, EVALUATES⚖️, MUTATES🧬, BACKUPS🛡️, VISION👁️, APPROVAL✅)
- ✅ Цвета по типам для Dataview/CSS
- ✅ INDEX.md с таблицей узлов, рёбер, fitness-критериями
- ✅ Крон каждые 6ч + fs-watch Obsidian = live updates

**Проблемы / возможности улучшения:**
| Проблема | Влияние | Решение |
|---|---|---|
| Парсинг `pulse.py` хрупкий (regex без якоря `^` для quiet-режима) | Может пропустить мёртвые узлы | Исправить regex (уже документировано в skill) |
| `genome` без `http://`/`:порт`/`.py`/`skill:` трактуется как файл | Ложные статусы для директорий | Добавить `state:` явное или улучшить pulse |
| Нет поддержки `MUTATES`/`BACKUPS` рёбер в текущем graph.yaml | Не показывает эволюционные связи | Добавить рёбра при мутациях |
| `chronicle` и `archive` имеют `state` как путь к файлу | Не парсятся pulse | Добавить `genome: file:...` или отдельный тип проверки |
| Нет версионирования экспорта (git history в Vault) | Потеря истории изменений графа | Добавить git commit в крон-обёртку |

### 2. Конфигурация Obsidian (`.obsidian/`)

**Текущее (`graph.json`):**
```json
{
  "collapse-filter": true,
  "search": "",
  "showTags": false,
  "showAttachments": false,
  "hideUnresolved": false,
  "showOrphans": true,
  "collapse-color-groups": true,
  "colorGroups": [],           // ← ПУСТО!
  "collapse-display": true,
  "showArrow": false,
  "textFadeMultiplier": 0,     // ← Метки НЕ видны!
  "nodeSizeMultiplier": 1,
  "lineSizeMultiplier": 1,
  "collapse-forces": true,
  "centerStrength": 0.5187,
  "repelStrength": 10,         // ← Мало для 13+ узлов
  "linkStrength": 1,
  "linkDistance": 250,
  "scale": 0.713,
  "close": true
}
```

**Проблемы:**
- ❌ **Нет цветовых групп** — все узлы одного цвета, типы не различимы визуально
- ❌ **`textFadeMultiplier: 0`** — названия узлов не видны никогда
- ❌ **`repelStrength: 10`** — слабая отталкивающая сила, узлы слипаются
- ❌ **`showArrow: false`** — направление рёбер (FEEDS→, CONTROLS←) не видно
- ❌ **Нет фильтров** — показываются все узлы, включая МЁРТВЫЕ
- ❌ **Local graph не настроен** — при клике на узел открывается пустой локальный граф

**Отсутствующие плагины:**
- ❌ **Dataview** — нужен для запросов по frontmatter (type, status, color, links)
- ❌ **Heatmap Calendar** — для визуализации пульса/активности узлов во времени
- ❌ **Extended Graph** — для per-tag colors, edge weights, multiple views
- ❌ **Graph Presets** — для переключения "Full Graph" / "Alive Only" / "By Type"
- ❌ **Tasks** — для трекинга мутаций/экстинкций как задач

---

## 🎯 РЕКОМЕНДАЦИИ ИЗ АНАЛИЗА GITHUB (TOP REPOS)

### Из `AgriciDaniel/claude-obsidian` (10.5k ⭐) — Self-organizing AI second brain
- **Паттерн:** Автоматическое связывание заметок через LLM (Claude Code)
- **Применительно:** Можно добавить авто-связывание новых узлов графа с существующими через LLM при экспорте
- **Взять:** Идея "drop any source → Claude reads, links, files into connected knowledge graph"

### Из `lexbritvin/obsidian-skills-pack` — Agent Skills для Obsidian
- **`obsidian-graph`** — Полная схема `graph.json`, 4 стратегии раскраски, палитры, рецепты
- **`obsidian-graph-audit`** — Диагностика шума: mega-категории, render-only edges, false categories
- **`obsidian-dataview`** — DQL + DataviewJS для дашбордов графа
- **`obsidian-heatmap`** — GitHub-style heatmaps для активности узлов
- **Применительно:** Прямое применение к нашему графу эволюции

### Из `skridlevsky/graphthulhu` (170 ⭐) — MCP server для Obsidian/Logseq
- **39 инструментов:** navigation, search, analysis, writing, decisions, journals, flashcards, whiteboards
- **Применительно:** Можно поднять как MCP-сервер для Hermes Agent → прямой доступ к графу

### Из `The-Knowledge-Graph-Guys/vault-ld` (189 ⭐) — Vault-LD spec
- **YAML-LD frontmatter + shared @context = RDF knowledge graph**
- **Применительно:** Добавить `@context` в frontmatter узлов для семантической совместимости

### Из `devwhodevs/engraph` (164 ⭐) — Local KG для AI agents (Rust + MCP)
- **Hybrid search + MCP server для Obsidian vaults**
- **Применительно:** Альтернатива graphthulhu, на Rust, быстрее

### Из `forloopcodes/contextplus` (1.9k ⭐) — Context+ MCP server
- **RAG + Tree-sitter AST + Spectral Clustering + Obsidian-style linking**
- **Применительно:** Для кодовой базы Grimoire/ParanoidX/SuperGuard — превратить код в feature graph

---

## 🛠 КОНКРЕТНЫЕ ДЕЙСТВИЯ (ПЛАН ВНЕДРЕНИЯ)

### PHASE 1: Базовая конфигурация Graph View (СЕЙЧАС — 30 мин)

#### 1.1 Обновить `.obsidian/graph.json`
```json
{
  "collapse-filter": false,
  "search": "-tag:#dead",
  "showTags": false,
  "showAttachments": false,
  "hideUnresolved": true,
  "showOrphans": false,
  "collapse-color-groups": false,
  "colorGroups": [
    {"query": "tag:#type/human", "color": {"a": 1, "rgb": 15177922}},    // #E67E22
    {"query": "tag:#type/agent", "color": {"a": 1, "rgb": 3447003}},     // #3498DB
    {"query": "tag:#type/skill", "color": {"a": 1, "rgb": 10185699}},    // #9B59B6
    {"query": "tag:#type/pipeline", "color": {"a": 1, "rgb": 3033169}},  // #2ECC71
    {"query": "tag:#type/memory", "color": {"a": 1, "rgb": 9801126}},    // #95A5A6
    {"query": "tag:#type/watchdog", "color": {"a": 1, "rgb": 15158332}}, // #E74C3C
    {"query": "tag:#status/alive", "color": {"a": 1, "rgb": 3033169}},   // Green
    {"query": "tag:#status/dead", "color": {"a": 1, "rgb": 15158332}},   // Red
    {"query": "tag:#status/sick", "color": {"a": 1, "rgb": 15781984}}    // Gold
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

#### 1.2 Добавить теги в экспортёр (`export_graph_to_obsidian.py`)
В `render_node()` добавить в frontmatter:
```yaml
tags:
  - "#type/agent"        # по node.type
  - "#status/alive"      # по pulse статусу
  - "#role/dj"           # по node.role (slugified)
  - "#evolution/graph"   # общий тег графа
```

#### 1.3 Установить Dataview (Community Plugins)
- Включить "Enable JavaScript Queries"
- Создать дашборд `Evolution/Graph Dashboard.md`

### PHASE 2: Dataview дашборды (1-2 часа)

#### 2.1 Создать `Evolution/Graph Dashboard.md`
```dataview
TABLE WITHOUT ID
  file.link AS "Узел",
  type AS "Тип",
  status AS "Статус",
  role AS "Роль",
  links AS "Связей",
  genome AS "Геном"
FROM "#evolution/graph"
WHERE type != "index"
SORT status DESC, type ASC
```

#### 2.2 Добавить heatmap активности пульса
```dataviewjs
// Heatmap пульса за последние 30 дней
// Требует: Heatmap Calendar plugin
// Источник: chronicle.md (парсинг дат записей)
```

#### 2.3 Дашборд "Мёртвые узлы → Кандидаты на экстинкцию"
```dataview
TABLE file.link, role, genome, state
FROM "#evolution/graph"
WHERE status = "МЁРТВ" AND type != "MEMORY"
SORT file.mtime ASC
```

### PHASE 3: Расширенная визуализация (2-4 часа)

#### 3.1 Установить Extended Graph plugin (ElsaTam/obsidian-extended-graph)
- Multiple views / presets
- Per-tag colors
- Edge weights (толщина по типу ребра)
- SVG export для отчётов

#### 3.2 Настроить Graph Presets (ycnmhd/obsidian-graph-presets через BRAT)
Пресеты как заметки в `Evolution/Presets/`:
- `Full Graph.md` — все узлы
- `Alive Only.md` — `-tag:#status/dead`
- `By Type.md` — цвет по типу, без статуса
- `Commercial.md` — только `paranoidx`, `superguard`, `isle_client`
- `Radio.md` — только `dj`, `music_pipeline`, `voice`, `radio_cache`, `song_protocol`

#### 3.3 CSS snippet для кастомных цветов (`.obsidian/snippets/graph-colors.css`)
```css
/* Цвета типов узлов */
.graph-view.color-fill[style*="#E67E22"] { background-color: #E67E22 !important; } /* HUMAN */
.graph-view.color-fill[style*="#3498DB"] { background-color: #3498DB !important; } /* AGENT */
.graph-view.color-fill[style*="#9B59B6"] { background-color: #9B59B6 !important; } /* SKILL */
.graph-view.color-fill[style*="#2ECC71"] { background-color: #2ECC71 !important; } /* PIPELINE */
.graph-view.color-fill[style*="#95A5A6"] { background-color: #95A5A6 !important; } /* MEMORY */
.graph-view.color-fill[style*="#E74C3C"] { background-color: #E74C3C !important; } /* WATCHDOG */

/* Толщина рёбер по типу */
.graph-view.color-line[data-edge-type="CONTROLS"] { stroke-width: 2.5 !important; }
.graph-view.color-line[data-edge-type="FEEDS"] { stroke-width: 2 !important; }
.graph-view.color-line[data-edge-type="CALLS"] { stroke-width: 1.5 !important; }
.graph-view.color-line[data-edge-type="VISION"] { stroke-dasharray: 5,5 !important; }
```

### PHASE 4: Интеграция с Hermes Agent / MCP (1-2 дня)

#### 4.1 Поднять graphthulhu или engraph как MCP server
```bash
# graphthulhu (Go)
go install github.com/skridlevsky/graphthulhu@latest
graphthulhu --vault "C:\Vault" --port 3001

# ИЛИ engraph (Rust) — быстрее
cargo install engraph
engraph --vault "C:\Vault" --port 3001
```

#### 4.2 Добавить в Hermes `config.yaml`
```yaml
mcp:
  servers:
    obsidian-graph:
      command: "graphthulhu"
      args: ["--vault", "C:\\Vault", "--stdio"]
      env: {}
```

#### 4.3 Навык (skill) для Hermes: `obsidian-graph-engineering`
- `query_graph(nodes, edges, filters)` — через MCP
- `get_node_status(node_id)` — pulse status
- `trigger_mutation(node_id, candidate_genome)` — инициировать мутацию
- `record_extinction(node_id, reason)` — записать в archive + chronicle

### PHASE 5: Автоматизация и качество (ongoing)

#### 5.1 Git history в Vault
В крон-обёртке (`export_graph_to_vault.py`):
```python
import subprocess
subprocess.run(["git", "-C", vault_path, "add", "Evolution/"], check=True)
subprocess.run(["git", "-C", vault_path, "commit", "-m", f"graph: pulse export {datetime.now():%Y-%m-%d %H:%M}"], check=True)
```

#### 5.2 Vault-LD @context в frontmatter
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

#### 5.3 Авто-тегирование через LLM (как в claude-obsidian)
При добавлении нового узла в `graph.yaml`:
1. LLM анализирует `genome`, `role`, `feeds`
2. Предлагает теги: `#domain/radio`, `#domain/surveillance`, `#domain/identity`
3. Gardener утверждает → добавляет в frontmatter при следующем экспорте

---

## 📁 СТРУКТУРА VAULT (РЕКОМЕНДУЕМАЯ)

```
C:\Vault\
├── .obsidian/
│   ├── graph.json           # ← Обновить (Phase 1)
│   ├── workspace.json
│   ├── core-plugins.json    # ← Добавить dataview, heatmap-calendar
│   ├── community-plugins.json
│   └── snippets/
│       └── graph-colors.css # ← Phase 3
├── Evolution/               # ← Текущий экспорт
│   ├── INDEX.md
│   ├── oracle.md
│   ├── gardener.md
│   ├── paranoidx.md
│   ├── superguard.md
│   ├── dj.md
│   ├── music_pipeline.md
│   ├── voice.md
│   ├── radio_cache.md
│   ├── song_protocol.md
│   ├── watchdog.md
│   ├── chronicle.md
│   ├── archive.md
│   └── isle_client.md
├── Evolution/Presets/       # ← Phase 3
│   ├── Full Graph.md
│   ├── Alive Only.md
│   ├── Commercial.md
│   └── Radio.md
├── Evolution/Dashboards/    # ← Phase 2
│   ├── Graph Dashboard.md
│   ├── Dead Nodes.md
│   ├── Pulse Heatmap.md
│   └── Mutation History.md
├── Graph/                   # ← Новое: исходники графа
│   ├── graph.yaml           # ← Копия из the-grimoire/ru/configs/
│   ├── pulse.py             # ← Копия
│   └── export_graph_to_obsidian.py
├── Projects/                # ← Для связей с проектами
│   ├── ParanoidX/
│   ├── SuperGuard/
│   └── AI-Radio/
├── Templates/               # ← Для Dataview/Templates
│   ├── graph-node.md
│   └── mutation-record.md
└── Daily/                   # ← Дневники (уже есть)
    └── 2026-08-06.md
```

---

## 🔗 СВЯЗИ С ТЕКУЩИМИ ПРОЕКТАМИ

### ParanoidX (`C:\ParanoidX-backup`)
- **Граф-узел:** `paranoidx` (PIPELINE, ЖИВ)
- **Экспорт в Vault:** Добавить заметки ключевых компонентов (smp-server, coturn, v2ray, tor, xftp, license-server)
- **Связи:** `isle_client` (CALLS), `oracle` (VISION), `gardener` (CONTROLS)
- **Dataview запрос:** Все узлы с `genome` содержащим "ParanoidX"

### SuperGuard (`C:\Users\tomas\video-surveillance`)
- **Граф-узел:** `superguard` (PIPELINE, ЖИВ)
- **Экспорт:** Камеры, детекторы, Telegram-бот, ESP32 актуаторы
- **Heatmap:** Активность детекций за 30 дней (требует логов)

### AI-Radio (`C:\Users\tomas\ai-radio`)
- **Узлы:** `dj`, `music_pipeline`, `voice`, `radio_cache`, `song_protocol`
- **Heatmap:** Генерация треков / TTS за день
- **Связи:** `radio_cache` как MEMORY hub

### The Grimoire (`C:\Users\tomas\the-grimoire`)
- **Источник правды:** `ru/configs/graph.yaml`, `ru/scripts/pulse.py`, `ru/scripts/export_graph_to_obsidian.py`
- **Vault-LD:** Описать онтологию графа в `@context`

---

## 📋 ЧЕКЛИСТ ВНЕДРЕНИЯ

### Немедленно (сегодня)
- [ ] Обновить `.obsidian/graph.json` с цветовыми группами и фильтрами
- [ ] Добавить теги в `export_graph_to_obsidian.py` frontmatter
- [ ] Установить Dataview plugin + включить JS queries
- [ ] Установить Heatmap Calendar plugin
- [ ] Создать `Evolution/Graph Dashboard.md` с базовым DQL

### На этой неделе
- [ ] Настроить Extended Graph plugin (multiple views)
- [ ] Создать Graph Presets (4-5 пресетов)
- [ ] Добавить CSS snippet для цветов типов узлов
- [ ] Настроить Local graph в workspace.json
- [ ] Добавить git commit в крон-обёртку экспорта

### В этом месяце
- [ ] Поднять graphthulhu/engraph MCP server
- [ ] Интегрировать в Hermes Agent config
- [ ] Написать skill `obsidian-graph-engineering`
- [ ] Добавить Vault-LD @context в frontmatter
- [ ] Настроить авто-тегирование новых узлов через LLM

### Архитектурные улучшения (backlog)
- [ ] Экспорт кода проектов в граф (Context+ / Graphify pattern)
- [ ] Bi-directional sync: Obsidian Canvas → graph.yaml
- [ ] Автоматические мутации через LLM + fitness gate
- [ ] Telegram-бот для пульса графа (уже есть CathedralMaster_bot)

---

## 💡 КЛЮЧЕВЫЕ ИНСАЙТЫ ИЗ АУДИТА

1. **Graph View — не просто визуализация, а интерфейс управления.** С цветовыми группами по типу/статусу и стрелками рёбер Садовник (Gardener) увидит здоровье системы за 1 секунду.

2. **Dataview = Query Layer для графа.** DQL запросы по `type`, `status`, `links`, `genome` заменяют ручной просмотр INDEX.md.

3. **Heatmap = Pulse History.** GitHub-style heatmap активности узлов (последний пульс, мутации, экстинкции) показывает тренды, которые невидимы в статическом графе.

4. **MCP Server = Agent Access.** Graphthulhu/Engraph даёт Hermes Agent прямой доступ к графу как knowledge base — не нужен парсинг markdown.

5. **Vault-LD = Semantic Interop.** YAML-LD frontmatter делает граф понятным другим инструментам (RDF, SPARQL, Knowledge Graphs).

6. **Presets = Context Switching.** "Commercial view" / "Radio view" / "Full view" — разные разрезы для разных задач Оракула и Садовника.

7. **Git History = Audit Trail.** Каждый пульс-экспорт = коммит. История эволюции графа = git log Evolution/.

---

## 📎 ПОЛЕЗНЫЕ ССЫЛКИ (ИЗ GITHUB АУДИТА)

| Репозиторий | Звёзд | Ключевая ценность для нас |
|---|---|---|
| `AgriciDaniel/claude-obsidian` | 10.5k | Авто-связывание LLM, second brain pattern |
| `lexbritvin/obsidian-skills-pack` | — | 9 скиллов: graph, dataview, heatmap, tasks, audit |
| `skridlevsky/graphthulhu` | 170 | MCP server 39 tools для Obsidian/Logseq |
| `devwhodevs/engraph` | 164 | Rust MCP server, hybrid search, быстрее |
| `The-Knowledge-Graph-Guys/vault-ld` | 189 | YAML-LD spec, RDF interop |
| `forloopcodes/contextplus` | 1.9k | Code → Feature Graph (RAG + AST + Clustering) |
| `obra/knowledge-graph` | 101 | TypeScript KG query/traversal, path finding |
| `swarmclawai/swarmvault` | 644 | Local-first LLM Wiki, agent memory, Karpathy pattern |
| `green-dalii/obsidian-llm-wiki` | 421 | Karpathy LLM Wiki plugin для Obsidian |
| `ElsaTam/obsidian-extended-graph` | — | Multiple views, per-tag colors, edge weights |

---

*Аудит подготовлен на основе анализа 20+ топовых GitHub репозиториев по graph engineering + Obsidian, текущего кода экспортёра Гримуара v3.0 и конфигурации Vault `C:\Vault`.*