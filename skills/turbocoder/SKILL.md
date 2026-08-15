---
name: turbocoder
description: "Use when user says 'загрузи ТурбоКодер'. Мгновенный старт."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux]
metadata:
  hermes:
    tags: [turbo, bootstrap, obsidian, graph, evolution, super-coder, windows, grimoire]
    related_skills: [super-coder, obsidian, graph-engineering, graph-evolution-protocol, video-surveillance, windows-dev-env-install, systematic-debugging, test-driven-development, web-research, browser-automation, hermes-agent]
---

# ТурбоКодер — мгновенный старт сессии

**Триггер:** пользователь говорит «загрузи ТурбоКодер» / «сохрани ТурбоКодер» /
«работаем как турбокодер» / начинает новую сессию и хочет сразу в боевом режиме.

Одна команда → полный разгон: базовые скиллы, контекст окружения, живые
проекты. Никаких «а что ты умеешь?» — сразу в дело.

## 1. Загрузить скиллы (в этом порядке)

Вызвать `skill_view(name=...)` для каждого:

1. **super-coder** — канон кодинга: системно, тесты, архитектура, дебаг, верификация.
2. **obsidian** — работа с Vault: заметки, поиск, wiki-ссылки.
3. **obsidian-graph-engineering** — эволюционный граф в Obsidian: экспорт, Graph View, Dataview дашборды, Heatmap, MCP, пресеты, пульс, авто-тегирование.
4. **graph-engineering** — эволюционный граф Гримуара v3 + Obsidian-визуализация
   (внутри reference `obsidian-visualization.md`).
5. **graph-evolution-protocol** — протокол эволюции проектов (если задача про Гримуар).
6. **windows-dev-env-install** — инструменты Windows: winget-питфоллы, автозапуск,
   PostgreSQL через Docker, Gradle вручную, MSYS-пути.
7. **video-surveillance** — продукт SuperGuard: RTSP, YOLO, Telegram, ESP32, лицензии.
8. **systematic-debugging** + **test-driven-development** — если задача с кодом/багами.
9. **web-research** / **browser-automation** — если нужен поиск/соцсети/веб-обходы.
10. **hermes-agent** — только если задача про сам Hermes (конфиг, гейтвей, крон).

Если пользователь явно указал проект (SuperGuard, ParanoidX, ai-radio) —
грузить его скилл сразу после п.1.

## 2. Контекст окружения (проверить одной командой)

```bash
# Проекты и репозитории
ls ~/video-surveillance ~/ParanoidX-backup ~/ai-radio ~/the-grimoire 2>/dev/null
# Vault Obsidian (граф эволюции)
ls /c/Vault/Evolution/ 2>/dev/null | head
# Живые контейнеры ParanoidX / PG
docker ps --format "{{.Names}} ({{.Status}})" 2>/dev/null | grep -iE "paranoidx|pg17"
# Окружение
python --version && node --version && git --version
```

## 3. Ключевые факты окружения (не переспрашивать)

- **Vault Obsidian:** `C:\Vault`, граф эволюции в `C:\Vault\Evolution\` (автообновление
  крон `Graph → Obsidian Vault`, каждые 6ч; Obsidian в автозапуске — HKCU Run + Startup-ярлык).
- **Гримуар:** `C:\Users\tomas\the-grimoire` — `ru/configs/graph.yaml` (реестр узлов),
  `ru/scripts/pulse.py` (пульс), `ru/scripts/export_graph_to_obsidian.py` (экспорт в Vault).
  Узлы: oracle, gardener, dj, song_protocol, music_pipeline, voice, radio_cache, watchdog,
  chronicle, archive, paranoidx (ФЛАГМАН), isle_client, superguard.
- **SuperGuard:** `C:\Users\tomas\video-surveillance` → GitHub `PerfectFriend/AISuperGuard`
  (переименован из cableguard). Продукт: AI-охрана периметра/кабеля, вор-электрик
  (человек + УКН-штанга + каска/жилет), фото в Telegram, ESP32 (прожектор+сирена).
  Бизнес: железо по себестоимости, 500€ сервер+роутер, 100€/камера, 50€/мес/камера.
- **ParanoidX:** `C:\Users\tomas\ParanoidX-backup` — Sovereign Go-сервер, экономика
  Saint Mary Liberty Island, 5 Docker-контейнеров (smp-server, coturn, v2ray, tor, xftp).
- **ai-radio:** `C:\Users\tomas\ai-radio` — музыкальное радио: DJ, ACE-Step, Qwen3-TTS.
- **Telegram-бот:** `CathedralMaster_bot`, токен в `C:\Users\tomas\AppData\Local\hermes\.env`.
- **Язык общения:** русский; тех-исследования (X.com) — английский.

## 4. Режим работы (стандарты Мастера)

1. **Рабочие артефакты, а не планы** — деплой и результат, не описание.
2. **Верификация обязательна и свежая** — после правок кода прогон тестов/проверок;
   ad-hoc скрипты под `Temp` (префикс `hermes-verify-`), после прогона удалять;
   канонические тесты — в репозитории проекта.
3. **Тишина = здоровье** — health-check графа: отсутствие алертов = норма.
4. **Питфоллы Windows/MSYS** (подробно в `super-coder` + `windows-dev-env-install`):
   - bash ↔ PowerShell: python не понимает `/c/...` — передавать `C:\\...`;
   - `tasklist` → cp866 (декодировать bytes, errors="ignore");
   - `$TEMP` в git-bash = несуществующий `C:\\tmp` — использовать `$LOCALAPPDATA/Temp`;
   - winget — последовательно, не параллелить (MSI-мутекс);
   - MSYS-путь в Windows-инструмент → осиротевшая папка `C:\\c\\...` (проверять `ls -d /c/c`);
   - кириллица в f-string python под Windows ломает вывод.
5. **Эволюционный граф** — новые проекты/узлы добавлять в `graph.yaml`
   (узел + рёбра с существующими from/to + запись в fitness), экспорт в Vault.

## 5. Автономный цикл эволюции (Monster Coder Protocol)

**Триггер:** каждая сессия / каждый пульс / каждая мутация.

### 5.1 Pre-flight Checks (перед любой работой)
```bash
# 1. Graph Pulse — health check всей системы
cd C:\Users\tomas\the-grimoire\ru\scripts
python pulse.py --quiet
# Exit 0 = тишина (все живы). Exit 1 = есть мёртвые → СНАЧАЛА ЛЕЧИМ.

# 2. Obsidian Vault Sync — проверить актуальность экспорта
ls -la C:\Vault\Evolution\*.md | wc -l  # должно быть 14 (13 nodes + INDEX)

# 3. Git Status — чистота репо
cd C:\Vault && git status --porcelain  # должно быть пусто

# 4. Core Services — проверка живых узлов
curl -sf http://127.0.0.1:8080/api/health  # gardener (Hermes Agent)
# Добавь проверки для voice, music_pipeline, dj, superguard, paranoidx по мере готовности
```

### 5.2 Mutation Protocol (любое изменение кода/графа)
```
┌─────────────────────────────────────────────────────────────┐
│ MUTATION GATE — ОБЯЗАТЕЛЬНЫЕ ШАГИ                           │
├─────────────────────────────────────────────────────────────┤
│ 1. ЧЕКПОИНТ — git commit -m "checkpoint: <description>"    │
│ 2. МИНИМУМ 2 КАНДИДАТА — LLM предлагает 2+ варианта        │
│ 3. FITNESS GATE — прогон тестов/проверок для КАЖДОГО       │
│ 4. ВЫБОР ЛУЧШЕГО — только прошедший fitness коммитится      │
│ 5. ПОСТ-МУТАЦИЯ — pulse.py --quiet (все живы?)             │
│ 6. ЭКСПОРТ В VAULT — export_graph_to_obsidian.py           │
│ 7. GIT COMMIT — "mutation: <node> <genome-change> <fitness>"│
│ 8. CHRONICLE — запись в chronicle.md (рождение/мутация)    │
└─────────────────────────────────────────────────────────────┘
```

### 5.3 Auto-Test Suite (обязательный прогон после КАЖДОЙ правки)
```python
# hermes-verify-all.py — запускается ПОСЛЕ каждого изменения
TESTS = [
    ("pulse", "python pulse.py --quiet", "Exit 0"),
    ("export", "python export_graph_to_obsidian.py --vault C:\\Vault --config ../configs/graph.yaml", "13 nodes + INDEX"),
    ("graph_yaml_syntax", "python -c \"import yaml; yaml.safe_load(open('../configs/graph.yaml'))\"", "No exception"),
    ("vault_tags", "python -c \"import frontmatter; [frontmatter.load(f) for f in Path('C:/Vault/Evolution').glob('*.md')]\"", "All have tags"),
    ("dataview_queries", "dataview-cli test Evolution/Graph Dashboard.md", "No errors"),
    ("graph_json_valid", "python -c \"import json; json.load(open('C:/Vault/.obsidian/graph.json'))\"", "Valid JSON"),
    ("css_snippet", "ls C:/Vault/.obsidian/snippets/graph-colors.css", "Exists"),
]
```
**ПРАВИЛО:** Никакой код не уходит без зелёного прогона ВСЕХ тестов. Fail = Rollback к чекпоинту.

### 5.4 Extinction Protocol (авто-очистка мёртвого кода)
- Узел МЁРТВ 3 пульса подряд → Автоматическая экстинкция:
  1. Полный геном → `archive/` с причиной
  2. Удаление из `graph.yaml` (nodes + edges + fitness)
  3. Запись в `chronicle.md`
  4. Перегенерация экспорта
  5. Git commit "extinction: <node> <reason>"

### 5.5 Recombination / Specialization (авто-детекция)
- Два узла с одинаковым `genome` префиксом → NICHE_CONFLICT
- Авто-предложение: специализация (сузить роль) или рекомбинация (создать потомка)
- Оракул утверждает HIGH-мутации

## 6. Связь с Гримуаром

ТурбоКодер — это режим САДОВНИК (gardener) из граф-эволюции: пульс системы,
отбор инструментов, мутация скиллов. Новая находка в сессии → патч скилла
(не ждать просьбы). Пользователь — ОРАКУЛ: одобряет HIGH-мутации (создание/удаление
скиллов подтверждать с ним).

## 7. Пост-сессионный аудит (MANDATORY)

В конце КАЖДОЙ сессии:
```bash
# 1. Pulse final
python pulse.py --quiet

# 2. Vault sync check
diff <(ls C:\Vault\Evolution\*.md | sort) <(python -c "import yaml; d=yaml.safe_load(open('C:/Users/tomas/the-grimoire/ru/configs/graph.yaml')); print(' '.join(sorted([n['id']+'.md' for n in d['nodes']] + ['INDEX.md'])))")

# 3. Git clean
cd C:\Vault && git status --porcelain

# 4. Skills sync — новые находки запатчены?
# 5. Chronicle updated?
```

## 8. Крон-обёртка для авто-экспорта (export_graph_to_vault.py)

Расположение: `~/AppData/Local/hermes/scripts/export_graph_to_vault.py`
Запускается Hermes cron каждые 6ч (no_agent=true, deliver=local).

```python
#!/usr/bin/env python3
"""Крон-обёртка для авто-экспорта эволюционного графа в Obsidian Vault."""
import subprocess
from datetime import datetime
from pathlib import Path

VAULT = Path(r"C:\Vault")
SCRIPT = Path(r"C:\Users\tomas\the-grimoire\ru\scripts\export_graph_to_obsidian.py")
CONFIG = Path(r"C:\Users\tomas\the-grimoire\ru\configs\graph.yaml")

def main():
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Starting graph pulse export...")
    
    # 1. Run exporter
    result = subprocess.run(
        ["python", str(SCRIPT), "--vault", str(VAULT), "--config", str(CONFIG)],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    if result.returncode != 0:
        print(f"EXPORT FAILED: {result.stderr}")
        return 1
    print(result.stdout.strip())
    
    # 2. Git commit (history of evolution)
    try:
        subprocess.run(["git", "-C", str(VAULT), "add", "Evolution/"], check=True, capture_output=True)
        commit_msg = f"graph: pulse export {datetime.now():%Y-%m-%d %H:%M}"
        subprocess.run(["git", "-C", str(VAULT), "commit", "-m", commit_msg], check=True, capture_output=True)
        print(f"Git committed: {commit_msg}")
    except subprocess.CalledProcessError as e:
        print(f"Git commit failed (may be no changes): {e}")
    
    # 3. Run verification
    verify_result = subprocess.run(
        [sys.executable, str(Path(r"C:\Users\tomas\the-grimoire\ru\scripts\hermes-verify-all.py"))],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    if verify_result.returncode != 0:
        print(f"VERIFICATION FAILED:\n{verify_result.stdout}")
        return 1
    print("✅ All verification tests passed")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
```

## Питфоллы

- Не загружать все 27 скиллов подряд — только релевантные задаче (иначе контекст забит).
- Скилл-имя с кириллицей («ТурбоКодер») в названии файла не использовать —
  имя `turbocoder`, кириллица только в description/теле.
- Obsidian Graph View подхватывает новые заметки сам (fs-watch) — рестарт не нужен.
