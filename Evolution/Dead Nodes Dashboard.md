---
type: dashboard
tags: ["#evolution/graph", "#dashboard", "#dead-nodes"]
---

# 💀 Dead Nodes — Кандидаты на экстинкцию / реанимацию

> [!warning] Узлы со статусом **МЁРТВ** (последний пульс: 2026-08-06 18:46)
> MEMORY-узлы (chronicle, archive, radio_cache) исключены — они не требуют health-check.

## Таблица мёртвых узлов

```dataview
TABLE WITHOUT ID
  file.link AS "Узел",
  type AS "Тип",
  role AS "Роль",
  genome AS "Геном / Health-check",
  state AS "Состояние",
  links AS "Связей",
  file.mtime AS "Последний экспорт"
FROM "#evolution/graph"
WHERE status = "МЁРТВ" AND type != "MEMORY"
SORT file.mtime ASC
```

## Анализ по типам

### 🤖 AGENT (требуют запуска процесса / фикса health-check)
```dataview
TABLE WITHOUT ID
  file.link AS "Узел",
  genome AS "Health-check endpoint",
  state AS "Ожидаемое состояние"
FROM "#evolution/graph"
WHERE status = "МЁРТВ" AND type = "AGENT"
```

| Узел | Genome (health-check) | Проблема | Действие |
|---|---|---|---|
| `gardener` | `http://127.0.0.1:8080/api/health` | Hermes Agent не запущен на порту 8080 | Запустить Hermes Agent / настроить health endpoint |
| `dj` | `ai-radio/scripts/dj.py` | Скрипт не запущен как процесс | Запустить DJ pipeline / добавить systemd/Windows service |
| `isle_client` | `ParanoidX-backup/flutter` | Flutter-приложения не собраны/не запущены | Собрать Flutter apps / проверить AES encrypt |

### ⚙️ PIPELINE (требуют запуска генерации / сервисов)
```dataview
TABLE WITHOUT ID
  file.link AS "Узел",
  genome AS "Скрипт / сервис",
  state AS "Ожидаемое состояние"
FROM "#evolution/graph"
WHERE status = "МЁРТВ" AND type = "PIPELINE"
```

| Узел | Genome | Проблема | Действие |
|---|---|---|---|
| `music_pipeline` | `ai-radio/scripts/gen_music.py` | ACE-Step не настроен / GPU недоступен | Настроить ACE-Step на Radeon 780M (ROCm/DirectML) |
| `voice` | `ai-radio/scripts/gen_voice_content.py` | Qwen3-TTS не запущен | Настроить Qwen3-TTS на DirectML |

### 🩺 WATCHDOG (критично — без пульса нет health-check всего графа)
```dataview
TABLE WITHOUT ID
  file.link AS "Узел",
  genome AS "Скрипт пульса",
  controls AS "Контролирует"
FROM "#evolution/graph"
WHERE status = "МЁРТВ" AND type = "WATCHDOG"
```

| Узел | Genome | Проблема | Действие |
|---|---|---|---|
| `watchdog` | `scripts/pulse.py` | pulse.py не запускается кроном / падает | Проверить крон `export_graph_to_vault.py`, логи pulse.py |

## План реанимации (по приоритету)

1. **🩺 WATCHDOG** — без пульса слепота. Проверить крон, запустить pulse.py вручную.
2. **🤖 GARDENER** — центральный контроллер. Hermes Agent должен быть запущен с API health endpoint.
3. **⚙️ VOICE** — Qwen3-TTS на DirectML (Radeon 780M). Приоритет для новостей/джинглов.
4. **⚙️ MUSIC_PIPELINE** — ACE-Step на GPU. Требует ROCm/DirectML setup.
5. **🤖 DJ** — Зависит от music_pipeline + radio_cache. После 3-4.
6. **🤖 ISLE_CLIENT** — Flutter builds. Параллельно, не блокирует радио.

## Команды для диагностики

```bash
# 1. Pulse вручную
cd C:\Users\tomas\the-grimoire\ru\scripts
python pulse.py --quiet

# 2. Hermes Agent health
curl http://127.0.0.1:8080/api/health

# 3. ACE-Step / DirectML check
python -c "import torch; print(torch.cuda.is_available(), torch.version.cuda)"

# 4. Qwen3-TTS check
python -c "from transformers import AutoModel; print('OK')"

# 5. Cron status (Windows Task Scheduler / Hermes cron)
hermes cron list
```

## Связи мёртвых узлов (что ломается каскадно)

```dataviewjs
const pages = dv.pages('"Evolution"').where(p => p.status === "МЁРТВ" && p.type !== "MEMORY");
for (const p of pages) {
  dv.paragraph(`**${p.file.link}** (${p.type})`);
  const content = await dv.io.load(p.file.path);
  const outMatch = content.match(/## Питает \(исходящие рёбра\)([\s\S]*?)(?=##|\Z)/);
  if (outMatch) {
    const lines = outMatch[1].match(/^- .*→ \[\[([^\]]+)\]\]/gm) || [];
    for (const l of lines) dv.paragraph(`  → ${l.replace(/^- /, '')}`);
  }
  dv.paragraph('');
}
```

---

*После реанимации узла — обновить `graph.yaml` (state/genome), запустить экспортёр, пульс покажет ЖИВ.*