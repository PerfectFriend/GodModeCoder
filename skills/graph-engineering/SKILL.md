---
name: graph-engineering
description: "Граф-эволюция агентов: узлы, рёбра, пульс, отбор, мутации."
trigger: "Проектировать агентную систему как граф (не цикл): loop/graph/harness, самоэволюция, пульс, отбор, мутации, рекомбинация, экстинкция."
---

# Graph Engineering — агентные системы как графы

Проектирование самоэволюционирующих агентных систем как **графа** вместо замкнутого цикла.
Тренд 2026 в AI-сообществах (X, Anthropic): «цикл повторяет, граф растёт». Это канон
протокола эволюции Гримуара v3.0 (см. `references/x-research-digest.md`).

## Три слоя инженерии агентов (2026)

| Слой | Контролирует | Инструменты |
|---|---|---|
| **LOOP engineering** | итерации: retries, бюджеты, evaluators, выходы, выживание при рестартах | Temporal |
| **GRAPH engineering** | структуру: ноды, рёбра, состояние, ветвления, циклы, чекпоинты | LangGraph, NetworkX |
| **HARNESS engineering** | доступ: тулзы, permissions, память, песочницы, эвалы, трейсы | E2B, OpenAI evals, OpenTelemetry |

Ключевые формулы (из дискурса):
- «Промпт живёт внутри лупа, луп — внутри графа, граф — внутри харнесса».
- «You don't need better prompts. You need graph engineering that makes agents remember everything» (Anthropic engineer).
- «85% инженеров Anthropic запускают сотни агентов. Способ — graph engineering» (Head of Claude Code).
- «Prompt testing — старый воркфлоу. Graph evaluation — новый» — тестируют весь граф, а не финальный ответ.

## Протокол граф-эволюции (Гримуар v3.0)

### Узлы
| Тип | Геном | Фенотип |
|---|---|---|
| AGENT | промпт+роль+инструменты | решения/действия |
| SKILL | SKILL.md+скрипты | процедурная память |
| PIPELINE | код+конфиг | данные на выходе |
| GATEWAY | токены+маршруты | сообщения |
| MEMORY | файлы | контекст для узлов |
| WATCHDOG | скрипт+порог | сигналы тревоги |

### Рёбра
FEEDS (пищевая цепь), CALLS (симбиоз), CONTROLS (нервная система),
EVALUATES (естественный отбор), MUTATES (мутаген), BACKUPS (иммунитет).

### Механизмы эволюции (аналоги живой природы)
- **Пульс (гомеостаз)**: периодический health-чек всех узлов → ЖИВ/БОЛЕН/МЁРТВ. Тишина = здоровье.
- **Мутация**: чекпоинт → LLM предлагает **минимум 2 кандидата** → fitness-гейт → коммит лучшего. Одна мутация — один кандидат = перезапись, а не эволюция.
- **Рекомбинация**: два узла с пересекающимися нишами скрещиваются → потомок, родители в архив.
- **Специализация**: дублирующиеся узлы (NICHE_CONFLICT) — один смещается в узкую нишу.
- **Симбиоз**: узлы, кормящие сильных соседей, получают приоритет ресурсов.
- **Экстинкция**: неиспользуемый узел → полный бэкап в archive/ → удаление → запись в Летопись. Экстинкция ≠ уничтожение.
- **Эмерджентность**: новые свойства из связей, а не из узлов — фиксировать как «открытия».

### События вместо шагов (не цикл!)
PULSE_OK (молчание), PULSE_SICK (чекпоинт→ремонт→ре-тест), VISION (Оракул дал задачу → новый узел/мутация),
FITNESS_LOW (конкурс мутаций), NICHE_CONFLICT (специализация/рекомбинация), STARVATION (мутация ниши/экстинкция),
CRISIS (откат чекпоинтов + сигнал Оракулу).

### Роли
ОРАКУЛ (человек: видение, критерии fitness, одобрение HIGH-мутаций) → САДОВНИК (агент: пульс, отбор, мутации)
→ УЗЛЫ (живут по геномам) → ЛЕТОПИСЕЦ (журнал рождений/смертей/открытий).

### Артефакты
- `graph.yaml` — реестр: nodes (id/type/role/genome/feeds/state), edges (from/to/type), fitness-критерии.
- `pulse.py` — пульс: `check_node()` по genome: `http://`→HTTP, `:порт`→TCP, `*.py`→процесс, `skill:имя`→наличие SKILL.md, иначе файл. Exit 0 = все живы (тишина), exit 1 = есть мёртвые. Windows: tasklist читать как cp866; .py-процессы искать через PowerShell WMI CommandLine.
- `chronicle.md` (Летопись) + `archive/` (могильник).

## GitHub PerfectFriend Backup Protocol

### Репозиторий
- **Owner:** PerfectFriend (Chrome logged in)
- **Repo:** `GodModeCoder-backup` (Private)
- **Branches:** `master` (source), `main` (synced)

### Sync Workflow (Local + Browser CDP)
```bash
# 1. Local merge
cd C:\Vault
git checkout main 2>/dev/null || git checkout -b main
git merge master --allow-unrelated-histories -m "merge: master into main"
git push origin main
git push origin master

# 2. Browser verify (Chrome CDP)
# - Repo page: Private ✓
# - Branches: main & master synced ✓
```

### Make Private (Chrome CDP) — Working Pattern
```python
# Navigate to settings, wait for Turbo ready (8-10s)
# Click "Change visibility" → modal → "Change to private" → "I want to make this repository private"
# Verify: repo page shows "Private"
```
**Critical**: GitHub settings forms use Turbo. Form `submit()` fails silently. Use button-click flow.

### Merge Branches (Local Git) — Recommended
Avoid GitHub UI PR flow and Turbo issues. Use local `git merge` + push.

## Пульс и Health-Check

## Практический воркфлоу: Создание графа для SuperGuard (2026-08-06)

### 1. Инициализация graph.yaml
```bash
# Создать graph.yaml в рабочей директории проекта
nodes:
  - id: oracle
    type: HUMAN
    role: MASTER
    genome: "vision, fitness criteria, approval gates"
    state: "ALIVE"
    feeds: []
    controlled_by: []
    evaluates: [gardener, paranoidx, superguard]
    approves: [gardener]

  - id: gardener
    type: AGENT
    role: GARDENER
    genome: "graph-engineering skill, pulse.py, mutation engine, extinction protocol"
    state: "ALIVE"
    feeds: [chronicle, archive]
    controlled_by: [oracle]
    controls: [paranoidx, superguard, dj, voice, music_pipeline]
    evaluates: [isle_client, song_protocol]
    calls: [radio_cache, chronicle, archive]

  - id: paranoidx
    type: PIPELINE
    role: FLAGSHIP
    genome: "Go + Flutter + v2ray/Tor + smp-server + coturn + license server"
    state: "ALIVE"
    feeds: [watchdog]
    controlled_by: [gardener]
    calls: [isle_client]
    vision_from: [oracle]

  - id: superguard
    type: PIPELINE
    role: COMMERCIAL
    genome: "video-surveillance + panic_mode.py + GitHub PerfectFriend/AISuperGuard"
    state: "ALIVE"
    feeds: [watchdog]
    controlled_by: [gardener]
    vision_from: [oracle]

  - id: watchdog
    type: WATCHDOG
    role: HEALTH_CHECK
    genome: "pulse.py + cron 6h + health criteria per node"
    state: "ALIVE"
    controlled_by: [gardener]
    controls: [dj, voice, music_pipeline, paranoidx, superguard]
    feeds_from: [superguard, paranoidx]

  - id: dj
    type: AGENT
    role: DJ
    genome: "music rotation, stream :8090, ffmpeg + cron"
    state: "DEAD"
    feeds: [radio_cache]
    controlled_by: [gardener, watchdog]
    calls: [radio_cache]

  - id: voice
    type: PIPELINE
    role: VOICE
    genome: "Qwen3-TTS GPU / Voicebox — новости, джинглы"
    state: "DEAD"
    feeds: [radio_cache]
    controlled_by: [gardener, watchdog]

  - id: music_pipeline
    type: PIPELINE
    role: MUSIC_GEN
    genome: "ACE-Step GPU → WAV → radio_cache"
    state: "DEAD"
    feeds: [radio_cache]
    controlled_by: [gardener, watchdog]
    calls: [radio_cache]
    evaluates_from: [gardener]

  - id: radio_cache
    type: MEMORY
    role: LIBRARY
    genome: "cache/music/<style>/, news, ads"
    state: "ALIVE"
    feeds_from: [music_pipeline, voice, dj]

  - id: song_protocol
    type: SKILL
    role: CONTENT_TO_SONG
    genome: "ace-step-song-protocol skill"
    state: "ALIVE"
    controlled_by: [gardener]
    calls: [music_pipeline]
    evaluates_from: [gardener]

  - id: isle_client
    type: AGENT
    role: CLIENT
    genome: "Flutter apps: The-Isle / Royal-Isle, AES encrypt"
    state: "DEAD"
    controlled_by: [gardener, paranoidx]
    evaluates_from: [gardener]

  - id: chronicle
    type: MEMORY
    role: CHRONICLE
    genome: "chronicle.md — births, mutations, extinctions, discoveries"
    state: "ALIVE"
    feeds_from: [gardener]

  - id: archive
    type: MEMORY
    role: ARCHIVE
    genome: "archive.md — full genomes of extinct nodes + cause"
    state: "ALIVE"
    feeds_from: [gardener]

edges:
  # Oracle vision
  - from: oracle
    to: paranoidx
    type: VISION
  - from: oracle
    to: superguard
    type: VISION
  - from: oracle
    to: gardener
    type: VISION
  - from: oracle
    to: gardener
    type: APPROVAL

  # Gardener controls
  - from: gardener
    to: paranoidx
    type: CONTROLS
  - from: gardener
    to: superguard
    type: CONTROLS
  - from: gardener
    to: isle_client
    type: EVALUATES
  - from: gardener
    to: dj
    type: CONTROLS
  - from: gardener
    to: voice
    type: CONTROLS
  - from: gardener
    to: music_pipeline
    type: CONTROLS
  - from: gardener
    to: song_protocol
    type: EVALUATES
  - from: gardener
    to: chronicle
    type: FEEDS
  - from: gardener
    to: archive
    type: FEEDS

  # Paranoidx calls
  - from: paranoidx
    to: isle_client
    type: CALLS

  # Superguard feeds watchdog
  - from: superguard
    to: watchdog
    type: FEEDS

  # Song protocol calls music pipeline
  - from: song_protocol
    to: music_pipeline
    type: CALLS

  # Music pipeline feeds radio_cache
  - from: music_pipeline
    to: radio_cache
    type: FEEDS
  - from: voice
    to: radio_cache
    type: FEEDS
  - from: dj
    to: radio_cache
    type: FEEDS

  # Watchdog controls
  - from: watchdog
    to: dj
    type: CONTROLS
  - from: watchdog
    to: voice
    type: CONTROLS
  - from: watchdog
    to: music_pipeline
    type: CONTROLS

  # Gardener feeds chronicle & archive
  - from: gardener
    to: chronicle
    type: FEEDS
  - from: gardener
    to: archive
    type: FEEDS

  # Paranoidx calls isle_client
  - from: paranoidx
    to: isle_client
    type: CALLS

fitness_criteria:
  paranoidx: "5 Docker-контейнеров живы (smp-server, coturn, v2ray, tor, xftp); API 200; TLS не протух"
  isle_client: "Flutter-сборки идут; encrypt AES работает; клиенты подключаются"
  superguard: "камера RTSP жива; детекция вор-электрик срабатывает; Telegram-алерт уходит; подписка активна"
  dj: "стрим 200 на :8090; ошибок ffmpeg нет; ротация не пуста"
  music_pipeline: "треки генерируются; длительность 180-300с; формат wav"
  voice: "аудио генерируется; язык ru; ошибок TTS нет"
  song_protocol: "скилл используется; очередь контента не растёт"
  watchdog: "тишина = здоровье; срабатывания не ложные"
  gardener: "пульс тихий; мутации проходят fitness; экстинкции в архив"
  oracle: "визия четкая; approval gates работают"
```

### 2. Экспорт в Obsidian Vault
```bash
# Файлы создаются в C:/Vault/Evolution/
# - INDEX.md (таблица узлов + рёбер + fitness)
# - superguard.md (PIPELINE node)
# - chronicle.md (MEMORY node)
# - archive.md (MEMORY node)
# - graph.yaml (источник правды)
```

### 3. Обновление пульса
```bash
# pulse.py проверяет каждый узел по genome:
# http:// → HTTP GET, :порт → TCP, *.py → процесс, skill:имя → SKILL.md, иначе файл
# Exit 0 = тишина (все живы), Exit 1 = список мёртвых
```

### 4. Летопись (chronicle.md)
- Записывать: рождения узлов, мутации, экстинкции, открытия
- Gardener пишет в chronicle.md через FEEDS edge

## Питфоллы
- Точная фраза «autonomous graph evolution» даёт 0 результатов в X-поиске — трендовый термин «graph engineering» / «graph ai» (без кавычек).
- Telegram-одобрения в графе = точки вмешательства Оракула в живую систему, а не «шаг 8» цикла.
- Цикл не отменяется — он становится пульсом (одним из механизмов), а не всем организмом.
- **pulse.py --quiet формат**: строка `[timestamp] PULSE: МЁРТВЫЕ: gardener, dj, ...` — парсить regex БЕЗ якоря `^` (впереди timestamp). В обычном режиме статус — по префиксу строки `☠`/`⚠`/`✓`. Узлы без явного статуса = ЖИВ.
- **Python не понимает MSYS-пути**: `python /c/Users/.../script.py` → «can't open file 'C:\\c\\Users\\...'». Из git-bash python-скриптам всегда передавать Windows-пути `C:\\...`; bash-командам — MSYS `/c/...`. PowerShell/cmd, получив MSYS-путь, создаёт осиротевшую папку `C:\\c\\Users\\...` (проверять `ls -d /c/c` при чистках).
- **Добавление узла в graph.yaml**: узел + рёбра (from/to существуют) + запись в fitness. Геном без `http://`/`:порт`/`.py`/`skill:` трактуется pulse как файл.
- **Obsidian YAML frontmatter tags**: при генерации заметок узлов **обязательно заключайте теги в кавычки**:
  ```python
  # ПРАВИЛЬНО:
  "tags:",
  ] + [f'  - "{t}"' for t in tags_list] + [
  # НЕПРАВИЛЬНО (frontmatter парсит как null):
  ] + [f"  - {t}" for t in tags_list] + [
  ```
  Без кавычек `#type/agent` → `null` в python-frontmatter. Это ломает Dataview запросы, Graph View фильтры и colorGroups в graph.json.

## Поддержка
- `references/obsidian-visualization.md` — рецепт экспорта в Obsidian Graph View
- `references/x-research-digest.md` — дайджест X-публикаций (август 2026)