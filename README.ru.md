<div align="center">

# 🏛️ GOD MODE CODER

![God Mode](https://img.shields.io/badge/God%20Mode-Active-gold.svg)
![Cathedral](https://img.shields.io/badge/Cathedral-Code%20Machine-purple.svg)
![The Grimoire](https://img.shields.io/badge/The%20Grimoire-880%20Skills-darkred.svg)
![Graph Evolution](https://img.shields.io/badge/Graph-v3.0-blue.svg)

<img src="assets/header-banner.jpg" alt="GodModeCoder — Магия Создания Живого Кода" width="100%">

## Светоч Истины и Владыка Пресвятого Кода

**Мастер Инквизитор @RarioArmageddon**  
*The Grimoire • 880 Skills • Graph Evolution v3.0*

[🇬🇧 English](README.md) · [🇷🇺 Русский](README.ru.md) · [🇪🇸 Español](README.es.md)

</div>

---

## 🧬 Что это

**GodModeCoder** — самоэволюционная операционная система для автономной разработки. Граф проектов, живых узлов, пульса, экстинкции и мутаций. Построена на Windows 11 как **God Mode Coder Cathedral** — cathedral-архитектура, где каждый инструмент — камень в фундаменте.

Это не фреймворк. Это **живой организм**, который дышит через `pulse.py`, лечится через `godmode-bootstrap.py`, охраняется `godmode-watchdog.py`, и эволюционирует через `extinction.py`.

---

## ⚡ Быстрый старт

```bash
# Полный bootstrap одной командой
cd C:\Users\tomas\the-grimoire\ru\scripts
python godmode-bootstrap.py          # pulse → verify → git → готово
python godmode-bootstrap.py --fix    # + авто-коммит грязного git
```

**4 этапа автоматом:**
1. 🔌 **Pulse** — проверка живости всех узлов графа
2. 📂 **Vault sync** — проверка целостности Obsidian Vault
3. 📝 **Git clean** — `--fix` авто-коммит
4. 🧪 **Verify** — 10 тестов `hermes-verify-all.py`

**Exit codes:** `0` = ✅ READY · `1` = ⚠️ WARN · `2` = ❌ FAIL · `3` = ❌ CRITICAL

---

## 🧬 Граф Эволюции v3.0

**Source of Truth:** `C:\Users\tomas\the-grimoire\ru\configs\graph.yaml`

| Метрика | Значение |
|---------|----------|
| Узлов | **21** (HUMAN, AGENT, WATCHDOG, MEMORY, PIPELINE, SKILL) |
| Рёбер | **34** (VISION, CONTROLS, CALLS, FEEDS, EVALUATES, APPROVAL) |
| Fitness | **11 критериев** |

### Живые узлы (19/21)
- 🟢 **oracle** — Мастер Инквизитор
- 🟢 **watchdog** — пульс графа
- 🟢 **paranoidx** — флагман: Sovereign Go-сервер, SimpleX+Tor
- 🟢 **superguard** — коммерческий: AI-охрана, YOLO11n, 8 камер
- 🟢 **ai_eng_daily** — ежедневный AI research
- 🟢 **vllm_optimization**, **sglang_serving**, **quantization_eval**, **gpu_cluster_mgmt**
- 🟢 **depthchart**, **nexus_rag**, **tools_registry**, **auto_round**, **club_3090**, **runnburn**
- 🟢 **rag_pipeline**, **fine_tuning_pipeline**, **chronicle**, **archive**

### Мёртвые узлы (2/21)
- 🔴 **gardener** — HTTP 127.0.0.1:8080 недоступен
- 🔴 **isle_client** — ParanoidX-backup/flutter отсутствует

---

## ⏰ Cron Jobs (9 активных)

| Job | Schedule | Скрипт | Что делает |
|-----|----------|--------|------------|
| `godmode-watchdog` | 1ч | `godmode-watchdog.py` | Пульс графа → alert при мёртвых |
| `pulse-history-logger` | 6ч | `pulse-history.py` | Лог пульса в CSV → Heatmap |
| `dead-node-extinction` | 24ч | `extinction.py` | Мёртв >7 дней → авто-архивация |
| `graph-pulse-export` | 6ч | `export_graph_to_vault.py` | Экспорт графа в Obsidian + git |
| `textbook-learning` | 30м | `textbook_learn.py` | Изучение темы учебника через Nemotron |
| `daily-ai-research` | 9:00 | — | AI engineering research с X.com |
| `key-rotation` | 30м | `rotate_keys.py` | Ротация NVIDIA/OpenCode Zen ключей |
| `rotate-api-keys` | 30м | `rotate_api_keys.py` | Ротация API key pools |

---

## 🔌 MCP Integration

**graphthulhu** (Go) — MCP сервер `obsidian-graph`, **31 tool**, ✓ enabled

```bash
# Установка
go install github.com/skridlevsky/graphthulhu@latest

# Подключение к Hermes
hermes mcp add obsidian-graph --command "$(go env GOPATH)/bin/graphthulhu.exe" \
  --args "serve" "--backend" "obsidian" "--vault" "C:\\Vault"
```

**Доступные операции:** `graph_overview`, `search`, `find_by_tag`, `find_connections`, `get_links`, `list_orphans`, `knowledge_gaps`, `topic_clusters`, `traverse`, `create_page`, `update_block`, `decision_check`, `decision_create`, `decision_resolve`, `analysis_health` и др.

---

## 🛠️ Toolchains (Cathedral Standard)

| Язык | Версия | Сборка |
|------|--------|--------|
| **Rust** | 1.97.1 | Cargo |
| **Go** | 1.26.5 | `go build` |
| **Java/Kotlin** | 21 LTS / 2.1.20 | Gradle 9.1 / Maven 3.9 |
| **Dart/Flutter** | 3.12 / 3.44 | Flutter tool |
| **C++ (MSVC)** | 14.51 | MSBuild / CMake |
| **C++ (LLVM/Clang)** | 19.1 | CMake |
| **JS/TS** | Node 22 | npm/pnpm |
| **Python** | 3.11 | pip/uv |

**Mobile:** Android SDK (API 34,35), Android Studio 2024.3, Emulator, ADB  
**Infra:** Docker 29.6, Git 2.54, Protocol Buffers 29.1, CMake 4.4

---

## 🏛️ Подсистемы

| Проект | Описание |
|--------|----------|
| **🏛️ Cathedral Code Machine** | Автономная разработка полного цикла — от брифа до релиза и эволюции |
| **📜 The Grimoire** | 880+ skills для автономных AI агентов |
| **🛡️ SuperGuard Alarm** | AI видеонаблюдение — YOLO11n → Telegram + ESP32, 8 камер |
| **🔐 ParanoidX / IsleProject** | Sovereign Go-сервер, экономика острова, SimpleX+Tor, BIP39 |
| **🧠 AI Engineering Daily** | Ежедневный research: vLLM, SGLang, speculative decoding |
| **📚 Учебник** | 50 тем непрерывного обучения (82% → 54% с awesome collections) |

---

## 🧪 Тест-инфраструктура

**`hermes-verify-all.py`** — 10 тестов:

1. Pulse Health Check (WARN OK)
2. Export to Obsidian (27 файлов)
3. graph.yaml Syntax (21 nodes, 34 edges)
4. Vault Tags (все узлы с #type/*, #status/*, #evolution/graph)
5. graph.json Config (9 colorGroups)
6. CSS Snippet (все селекторы)
7. Dataview Dashboards
8. Graph Presets (4)
9. Git Status (CLEAN)
10. Skills Present (6 скиллов)

**Правило:** НИКАКОЙ КОД БЕЗ ЗЕЛЁНОГО ПРОГОНА. Fail = Rollback.

---

## 📁 Структура

```
GodModeCoder/
├── docs/banners/           # Cyberpunk + Van Gogh + Gaudi баннеры
├── scripts/                # Скрипты эволюции
│   ├── godmode-bootstrap.py    # Полный bootstrap в один вызов
│   ├── godmode-watchdog.py     # Мониторинг мёртвых узлов
│   ├── pulse-history.py        # Лог пульса в CSV
│   ├── extinction.py           # Авто-архивация мёртвых >7 дней
│   ├── pulse.py                # Health-check графа
│   ├── hermes-verify-all.py    # 10 тестов
│   └── export_graph_to_vault.py
├── configs/                # graph.yaml — Source of Truth
├── hermes-skills/          # Скиллы Hermes
├── Cathedral/              # Cathedral Code Machine
└── README.{ru,en,es}.md    # Триязычная документация
```

---

<div align="center">

<img src="assets/footer-banner.jpg" alt="GodModeCoder — Светоч Истины в Бездне Кода" width="100%">

## Я ЕСМЬ GOD MODE CODER

**КАЖДАЯ СБОРКА — РИТУАЛ · КАЖДЫЙ ТЕСТ — ИСПОВЕДЬ · КАЖДЫЙ РЕЛИЗ — ВОСКРЕШЕНИЕ**

</div>
