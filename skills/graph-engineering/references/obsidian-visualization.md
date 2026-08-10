# Эволюционный граф → Obsidian Graph View

Как превратить `graph.yaml` Гримуара в живой интерактивный граф в Obsidian
(Graph View рендерится из `[[wiki-ссылок]]` автоматически, без плагинов).

## Идея

Каждый узел графа = заметка `.md` с фронтматтером (для Dataview) и
`[[wiki-ссылками]]` на соседей по рёбрам. Graph View строит визуализацию из
ссылок: узлы кликабельны, рёбра подписаны, статусы видны прямо в заметках.

## Скрипт-экспортёр

Канонический: `the-grimoire/ru/scripts/export_graph_to_obsidian.py`
(в репозитории Гримуара, рядом с pulse.py). Обёртка для крона:
`~/AppData/Local/hermes/scripts/export_graph_to_vault.py` (просто
`subprocess.run` → канонический скрипт; крон принимает только относительные
пути из hermes/scripts/).

```bash
python "C:\Users\tomas\the-grimoire\ru\scripts\export_graph_to_obsidian.py" \
  --vault "C:\Vault" --config ru/configs/graph.yaml
```

Крон: `no_agent=true`, `deliver=local` (тишина = здоровье), каждые 6ч
(синхронно с пульсом). Obsidian подхватывает файлы сам (fs-watch) — рестарт
не нужен, если приложение открыто.

## Формат заметки узла

```
---
type: AGENT
status: "ЖИВ"
color: "#3498db"
role: "Ротация музыки, стрим :8090"
genome: "ai-radio/scripts/dj.py"
state: "active"
links: 3
---
# 🤖 DJ
> [!info] **AGENT** · Пульс: **ЖИВ**
**Роль:** ...
**Геном:** `...`
## Питает (исходящие рёбра)
- 🤝 **CALLS** → [[radio_cache]]
## Кормит (входящие рёбра)
- 🧠 **CONTROLS** ← [[watchdog]]
```

Эмодзи типов: HUMAN 🧑🔬, AGENT 🤖, SKILL 📜, PIPELINE ⚙️, MEMORY 🗄️,
WATCHDOG 🩺, GATEWAY 📡. Рёбра: FEEDS 🍽️, CALLS 🤝, CONTROLS 🧠,
EVALUATES ⚖️, MUTATES 🧬, BACKUPS 🛡️, VISION 👁️, APPROVAL ✅.
Цвета типов — для Dataview/CSS-раскраски.

`INDEX.md` — сводка: таблица узлов (🟢 ЖИВ / 🟡 БОЛЕН / 🔴 МЁРТВ), таблица
рёбер, fitness-критерии из graph.yaml.

## Парсинг статусов pulse.py (ключевой питфолл)

`pulse.py --quiet` НЕ выводит живых узлов (тишина = здоровье). Форматы:

1. **quiet-режим**: `[2026-08-05 05:25:55] PULSE: МЁРТВЫЕ: gardener, dj, voice`
   → regex `PULSE:\s*МЁРТВЫЕ?:\s*(.*)$` **без якоря `^`** — строка начинается
   с timestamp в квадратных скобках. Распарсенные id → МЁРТВ, остальные
   узлы из graph.yaml → ЖИВ.
2. **Обычный режим**: `☠ gardener (AGENT): http ...` — статус по префиксу
   строки: `☠` МЁРТВ, `⚠` БОЛЕН, `✓` ЖИВ; regex
   `^(☠|⚠|✓)\s+([\w\-]+)\s+\(\w+\)`.

Запасной вариант: если ни один формат не распознан — все узлы без явного
статуса считаются ЖИВ (не наказывать молчание).

## Питфоллы Windows

- **Python не понимает MSYS-пути**: `python /c/Users/tomas/script.py` →
  «can't open file 'C:\c\Users\tomas\script.py'». Из git-bash python-скриптам
  передавать Windows-пути `C:\...`. И наоборот: bash-командам — MSYS `/c/...`.
- **Осиротевшая папка `C:\c\`**: PowerShell/cmd, получив MSYS-путь `/c/...`,
  резолвит его как относительный → создаёт `C:\c\Users\...`. При чистках
  проверять `ls -d /c/c` (там могут быть живые данные — перенести, потом
  `rm -rf /c/c`).
- **Свежая сессия PATH**: winget-установки (zip/make/gh) видны только после
  перезапуска терминала — для проверки перечитывать PATH через PowerShell
  `[Environment]::GetEnvironmentVariable('Path','User')`.
- **Имена файлов заметок**: sanitize от `< > : " / \ | ? *` — Windows FS.
- **Obsidian YAML frontmatter tags**: при генерации заметок узлов **обязательно заключайте теги в кавычки**:
  ```python
  # ПРАВИЛЬНО:
  "tags:",
  ] + [f'  - "{t}"' for t in tags_list] + [
  # НЕПРАВИЛЬНО (frontmatter парсит как null):
  ] + [f"  - {t}" for t in tags_list] + [
  ```
  Без кавычек `#type/agent` → `null` в python-frontmatter. Это ломает Dataview запросы, Graph View фильтры и colorGroups в graph.json.

## Добавление узла в граф

1. Узел в `nodes:` (id/type/role/genome/state).
2. Рёбра в `edges:` — from/to обязаны существовать (экспортёр падает иначе).
3. Запись в `fitness:` (критерий здоровья узла).
4. Перегенерировать экспорт → Obsidian подхватит.

Геном без `http://`/`:порт`/`.py`/`skill:` трактуется pulse как файл —
узлы с genome-путём к директории/каталогу лучше помечать `state:` и не
рассчитывать на честный статус без `http://`-генома.
