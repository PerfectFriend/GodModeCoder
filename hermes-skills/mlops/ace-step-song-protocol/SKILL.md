---
name: ace-step-song-protocol
description: Use when building content-to-song pipeline with ACE-Step.
---

# ACE-Step Song Generation Protocol

Полный пайплайн: **контент -> структура песни -> рифмованные лирики -> ACE-Step промпт/конфиг -> генерация -> ревью -> кэш радио**.

## Архитектура этапов

```
Content Ingestion -> Story to Song Structure -> Lyrics Generation -> ACE-Step Config/Gen -> Review & Cache
    (RSS, TG,         (verses, chorus,          (rhymed, rhythmic,       (TOML + checkpoint,       (Telegram
     manual)           bridge, mood)             style-matched)           voice pack)               buttons -> approve/reject)
```

---

## 1. Content Ingestion (`content_ingest.py`)

**Источники:**
- RSS/Atom блоги (tech, news, science) -- `blogwatcher` skill
- Telegram каналы (через gateway) -- ссылки на посты
- Ручные ссылки (JSON в `cache/content_queue/`)

**Формат элемента очереди:**
```json
{
  "id": "uuid",
  "source": "rss|telegram|manual",
  "url": "https://...",
  "title": "Заголовок",
  "summary": "Краткое содержание (до 2000 слов)",
  "tags": ["tech", "ai", "science"],
  "lang": "ru",
  "priority": 1-10,
  "created_at": "ISO8601",
  "status": "pending|processing|done|rejected"
}
```

---

## 2. Story to Song Structure (`structure_song.py`)

**LLM промпт (использует пул ключей Hermes):**
```
Ты -- продюсер песен для AI-радио "Мастер-ФМ".
На входе: заметка/статья. На выходе: JSON структура песни.

Требования:
- 2-3 куплета (verse), 1-2 припевов (chorus), опционально бридж (bridge), интро/аутро
- Каждый элемент: описание темы, настроение, ключевые образы (для промпта ACE-Step)
- Стиль: подбирай под тему (rock/jazz/electronic/ambient/chiptune/classical)
- Целевая аудитория: определяет голос (Master/Shurgen/Kids/News)
- Длительность: 180-300 сек
- Язык: ru/en

Вход: {title, summary, tags, lang}
Выход: JSON SongStructure
```

**Схема SongStructure:**
```json
{
  "meta": {
    "title": "Название трека",
    "style": "rock",
    "duration_sec": 240,
    "language": "ru",
    "voice_pack": "master",
    "target_audience": "adult_tech"
  },
  "structure": [
    {"type": "intro", "bars": 4, "desc": "Атмосферный синт, нарастающий бит", "mood": "anticipation"},
    {"type": "verse", "bars": 16, "desc": "История про новый AI-чип, технические детали", "mood": "narrative", "key_images": ["кремний", "нейросети", "энергия"]},
    {"type": "chorus", "bars": 8, "desc": "Гимн прогрессу, хук: будущее уже здесь", "mood": "anthemic", "hook": "будущее уже здесь"},
    {"type": "verse", "bars": 16, "desc": "Применение в быту, примеры", "mood": "practical"},
    {"type": "chorus", "bars": 8, "desc": "Повтор припева с вариацией", "mood": "anthemic"},
    {"type": "bridge", "bars": 8, "desc": "Музыкальная пауза, рефлексия", "mood": "reflective"},
    {"type": "chorus", "bars": 8, "desc": "Финальный мощный припев", "mood": "triumphant"},
    {"type": "outro", "bars": 4, "desc": "Затухание, лого радио", "mood": "calm"}
  ]
}
```

---

## 3. Lyrics Generation (`generate_lyrics.py`)

**Промпт для LLM:**
```
Ты -- лирический поэт для AI-радио.
На входе: SongStructure. На выходе: полные рифмованные лирики.

Правила:
- Строгий ритм (под BPM стиля), рифмы AABB/ABAB
- Куплеты: повествовательные, конкретные образы
- Припевы: запоминающиеся, с хуком, повторяющиеся
- Бридж: контраст, эмоциональный пик
- Язык: естественный, без пафоса, под голос (Master = мужской, уверенный; Kids = простой, весёлый)
- Длина: под duration_sec (примерно 130-150 слов в минуту)
```

**Выход:** `lyrics.txt` + `lyrics_structured.json` (по секциям для промпта).

---

## 4. ACE-Step Prompt Engineering (`build_prompt.py`)

**Стратегия промпта для ACE-Step:**
- **Caption** = компактное описание всего трека (стиль, настроение, инструменты, вокальный стиль)
- **Instrumental** = false (есть вокал)
- **Duration** = из структуры
- **LM** (Language Model) = включён для вокала
- **Voice pack** = маппинг: `master|shurgen|kids|news|female_soft|male_gritty`

**Пример caption для rock-tech:**
> "Энергичный рок 120 BPM, электрогитары, жёсткие ударные, мужской вокал (confident tech narrator), тема: AI чипы будущего, гимнический припев, технический куплет, бридж с атмосферным спадом, качественная продюкция"

---

## 5. Voice Packs (Голосовые пакеты)

| Pack | Описание | Стили | Аудитория | ACE-Step параметры |
|------|----------|-------|-----------|-------------------|
| `master` | Мастер -- уверенный, глубокий, авторитетный | rock, electronic, classical | adult, tech, news | `voice_ref: master_ref.wav`, `gender: male`, `style: confident` |
| `shurgen` | Шурген -- дерзкий, ироничный, уличный | hip-hop, electronic, chiptune | youth, memes | `voice_ref: shurgen_ref.wav`, `gender: male`, `style: gritty` |
| `kids` | Детский -- простой, весёлый, чёткий | chiptune, ambient, classical | children, family | `voice_ref: kids_ref.wav`, `gender: neutral`, `style: cheerful` |
| `news` | Нюзер -- спокойный, чёткий, дикторский | ambient, classical | general, news | `voice_ref: news_ref.wav`, `gender: neutral`, `style: professional` |
| `female_soft` | Женский мягкий -- тёплый, обволакивающий | jazz, ambient, classical | relax, evening | `voice_ref: female_soft_ref.wav`, `gender: female`, `style: warm` |
| `male_gritty` | Мужской грубый -- ровный, с хрипотцой | rock, blues | adult, late night | `voice_ref: male_gritty_ref.wav`, `gender: male`, `style: raw` |

**Reference WAV** для каждого пакета -- в `cache/voice_packs/<pack>/ref.wav` (15-30 сек чистого голоса).

---

## 6. Full ACE-Step Config Generation (`make_config.py`)

**Вход:** SongStructure + Lyrics + VoicePack
**Выход:** TOML файл для `cli.py -c config.toml`

```toml
task_type = "text2music"
caption = "Энергичный рок 120 BPM, электрогитары, мужской вокал (master), тема: AI чипы..."
instrumental = false
duration = 240
seed = -1
inference_steps = 8
device = "cpu"
backend = "pt"
thinking = false
use_adg = false
offload_to_cpu = true
offload_dit_to_cpu = true
save_dir = "C:/Users/tomas/ai-radio/cache/staging/rock/tech_ai_chips_001"
audio_format = "wav"

# Вокальные настройки (если поддерживаются версией ACE-Step)
# voice_pack = "master"
# lyrics = "..."  # если есть встроенная поддержка
```

---

## 7. Generation & Staging (`generate_song.py`)

- Запуск через `env -u PYTHONPATH -u VIRTUAL_ENV .venv-cpu/Scripts/python.exe cli.py -c config.toml`
- Результат кладётся в **staging**: `cache/staging/<style>/<slug>/`
- Метаданные: `meta.json` (SongStructure + lyrics + voice_pack + prompt)

---

## 8. Review Workflow (`review_bot.py`)

**Telegram-бот (через gateway) с кнопками:**
- 🎧 **Прослушать** -- отправляет WAV/MP3
- ✅ **Утвердить** -> перемещает в `cache/music/<style>/<lang>/` + обновляет индекс DJ
- ❌ **Отклонить** -> удаляет из staging, помечает источник как rejected
- 🔄 **Перегенерировать** -> меняет seed/промпт, запускает заново
- ✏️ **Править лирики** -> открывает редактор, регенерит только вокал (если ACE-Step поддерживает)

**Интерфейс:**
```
Новый трек: "Кремниевое будущее" (rock, 4:00)
Голос: Master | Стиль: Tech Rock
Лирики: [показать]
[Прослушать] [Утвердить] [Отклонить] [Перегенерировать]
```

---

## 9. Cache Organization (Final)

```
cache/
├── music/
│   ├── rock/
│   │   ├── ru/           # утверждённые русские рок-треки
│   │   └── en/
│   ├── jazz/
│   │   ├── ru/
│   │   └── en/
│   └── ...
├── staging/              # временная зона ревью
│   ├── rock/
│   │   └── tech_ai_chips_001/
│   │       ├── song.wav
│   │       ├── meta.json
│   │       └── lyrics.txt
│   └── ...
├── voice_packs/
│   ├── master/ref.wav
│   ├── shurgen/ref.wav
│   ├── kids/ref.wav
│   ├── news/ref.wav
│   ├── female_soft/ref.wav
│   └── male_gritty/ref.wav
├── content_queue/        # входящие заметки
└── content_done/         # обработанные
```

---

## Интеграция с ночным батчем

`night_batch.py` добавляет шаг:
```python
# После генерации музыки по стилям:
if night["generate_songs_from_content"]:
    run_script("content_pipeline.py", ["--process-queue", "--max-songs", "20"])
```

`content_pipeline.py`:
1. Берёт топ-N заметок из `content_queue` по приоритету
2. Для каждой: structure -> lyrics -> prompt -> config -> generate -> stage
3. Шлёт в Telegram на ревью (или авто-утверждает если confidence высокий)
4. Утверждённые -> в `cache/music/<style>/<lang>/`

---

## Cron Jobs

| Job | Schedule | Action |
|-----|----------|--------|
| `content_ingest` | `*/30 * * * *` | Собирает RSS/Telegram -> `content_queue` |
| `song_pipeline` | `0 21 * * *` | Обрабатывает очередь -> staging -> review |
| `night_batch` | `0 20 * * *` | Полный цикл (включая песни из контента) |

---

## Quick Start (Manual Test)

```bash
# 1. Положить заметку в очередь
echo '{"id":"test1","source":"manual","title":"AI чип нового поколения","summary":"Компания анонсировала чип для локального AI...","tags":["tech","ai"],"lang":"ru","priority":8}' > cache/content_queue/test1.json

# 2. Запустить пайплайн одной песни
python scripts/content_pipeline.py --single test1 --auto-approve

# 3. Результат в cache/music/rock/ru/
```

---

## Next Steps

1. [ ] Создать `content_ingest.py` (RSS + TG)
2. [ ] Создать `structure_song.py` (LLM промпт)
3. [ ] Создать `generate_lyrics.py` (LLM промпт)
4. [ ] Создать `build_prompt.py` + `make_config.py`
5. [ ] Создать `generate_song.py` (обёртка ACE-Step)
6. [ ] Создать `review_bot.py` (Telegram gateway)
7. [ ] Подготовить voice packs (записать ref.wav для каждого)
8. [ ] Интегрировать в `night_batch.py`
9. [ ] Добавить cron jobs