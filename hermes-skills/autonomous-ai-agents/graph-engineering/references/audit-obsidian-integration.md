# Аудит Graph Engineering + Obsidian Integration (2026-08-06)

## Executive Summary
Проанализировано 20+ топовых GitHub репозиториев по graph engineering + Obsidian. Создан полный стек: экспортёр → Graph View → Dataview дашборды → Heatmap → MCP доступ.

## Топ репозитории и ключевые паттерны

| Репозиторий | ⭐ | Ключевой паттерн для нас |
|---|---|---|
| `AgriciDaniel/claude-obsidian` | 10.5k | Auto-linking LLM, second brain pattern |
| `lexbritvin/obsidian-skills-pack` | — | 9 скиллов: graph, dataview, heatmap, audit |
| `skridlevsky/graphthulhu` | 170 | MCP server 39 tools для Obsidian/Logseq |
| `devwhodevs/engraph` | 164 | Rust MCP, hybrid search, быстрее |
| `The-Knowledge-Graph-Guys/vault-ld` | 189 | YAML-LD spec, RDF interop |
| `forloopcodes/contextplus` | 1.9k | Code → Feature Graph (RAG + AST + Clustering) |
| `ElsaTam/obsidian-extended-graph` | — | Multiple views, per-tag colors, edge weights |

## Реализованный стек (Production Ready)

### 1. Экспортёр (`export_graph_to_obsidian.py`)
- Читает `graph.yaml` + `pulse.py --quiet` для статусов
- Создаёт заметки с frontmatter (type, status, color, role, genome, state, links, **tags**)
- **Критично**: теги в кавычках: `tags: [ "#type/agent", "#status/alive", ... ]`

### 2. Graph View конфигурация (`.obsidian/graph.json`)
- 9 цветовых групп по типу (`#type/*`) и статусу (`#status/*`)
- Фильтр мёртвых: `search: "-tag:#status/dead"`
- Стрелки рёбер: `showArrow: true`
- Forces: `repelStrength: 22`, `linkDistance: 220`

### 3. CSS Snippet (`.obsidian/snippets/graph-colors.css`)
- Цвета узлов по типу (HUMAN/AGENT/SKILL/PIPELINE/MEMORY/WATCHDOG/GATEWAY)
- Кольца статуса (alive/sick/dead/unknown)
- Цвета рёбер по типу (CONTROLS/FEEDS/CALLS/VISION/APPROVAL/EVALUATES/MUTATES/BACKUPS)

### 4. Dataview Дашборды
- `Graph Dashboard.md` — интерактивная таблица, статистика, рёбра, fitness
- `Dead Nodes Dashboard.md` — анализ мёртвых, план реанимации, команды диагностики

### 5. Graph Presets (`Evolution/Presets/`)
- Full Graph, Alive Only, Commercial (ParanoidX+SuperGuard), Radio (AI-Radio stack)

### 6. Auto-Test Suite (`hermes-verify-all.py`)
10 тестов, запускаемых ПОСЛЕ КАЖДОЙ мутации:
- Pulse health check (warn, not fail)
- Export to Obsidian (13 nodes + INDEX)
- graph.yaml syntax validation
- Vault tags validation (quoted tags)
- graph.json config validation (9 color groups)
- CSS snippet selectors
- Dataview dashboards existence
- Graph presets existence
- Git status clean
- Skills presence

### 7. Cron Wrapper (`export_graph_to_vault.py`)
- Запускается Hermes cron каждые 6ч (no_agent=true, deliver=local)
- Экспорт → Git commit → Verification suite
- История эволюции = `git log Evolution/`

### 8. MCP Integration (Planned)
- graphthulhu (Go) или engraph (Rust) как MCP server
- Hermes config.yaml → `obsidian-graph` server
- Операции: query_graph, get_node_status, trigger_pulse, record_mutation, record_extinction

## Критические питфоллы (зафиксированы в skill)

1. **YAML frontmatter tags** — **обязательно в кавычках**:
   ```python
   # ПРАВИЛЬНО:
   "tags:",
   ] + [f'  - "{t}"' for t in tags_list] + [
   ```

2. **Python paths on Windows** — MSYS vs Windows paths
3. **Obsidian rewrites graph.json** on Graph View close
4. **Git in Vault** — init for evolution history

## Следующие шаги (Roadmap)
1. Установить Dataview + Heatmap Calendar plugins в Obsidian
2. Поднять graphthulhu/engraph MCP server
3. Интегрировать в Hermes Agent config
4. Vault-LD @context в frontmatter для RDF interop
5. Авто-тегирование новых узлов через LLM