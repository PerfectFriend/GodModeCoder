# ACE-Step 1.5 — Полное руководство пользователя для AI Radio

> **Версия:** 1.5 | **Дата:** 2026-08-05 | **Проект:** Master-FM / AI Radio
> **Окружение:** Windows, CPU-only (Radeon 780M, нет CUDA), Python 3.11, uv venv
> **GPU Target:** WSL2 Ubuntu 24.04 + ROCm 6.3 для Radeon 780M (16 GB UMA)

---

## 📋 Оглавление

1. [Архитектура и ментальные модели](#1-архитектура-и-ментальные-модели)
2. [Установка и настройка окружения](#2-установка-и-настройка-окружения)
3. [Выбор моделей для вашего железа](#3-выбор-моделей-для-вашего-железа)
4. [CLI и TOML-конфигурация](#4-cli-и-toml-конфигурация)
5. [Полный справочник параметров](#5-полный-справочник-параметров)
6. [Режимы генерации (Task Types)](#6-режимы-генерации-task-types)
7. [Интеграция с AI Radio (gen_music.py)](#7-интеграция-с-ai-radio-gen_musicpy)
8. [Продвинутые техники настройки](#8-продвинутые-техники-настройки)
9. [LoRA обучение для радио-стиля](#9-lora-обучение-для-радио-стиля)
10. [REST API сервер](#10-rest-api-сервер)
11. [Траблшутинг и частые ошибки](#11-траблшутинг-и-частые-ошибки)
12. [Чек-лист качества генерации](#12-чек-лист-качества-генерации)

---

## 1. Архитектура и ментальные модели

### 1.1 Два мозга: LM + DiT

```
Пользовательский ввод → [5Hz LM] → Семантический чертеж → [DiT] → Аудио
                        ↓
               Инференс метаданных
               Оптимизация капшна
               Планирование структуры
```

**5Hz LM (Language Model) — Планировщик (Опционален)**
- Понимает намерения, делает планы через Chain-of-Thought
- Выводит: BPM, тональность, длительность, структуру, семантические коды
- **Не обязателен** — можно отключить (`thinking=false`), тогда планировщиком становитесь вы

**DiT (Diffusion Transformer) — Исполнитель**
- Превращает планы в аудио через диффузию
- Решает: тембр, микширование, детали
- **Всегда нужен** — это сердце генерации

### 1.2 Человеко-ориентированная генерация (не one-click)

ACE-Step создан для **итеративного диалога** человек↔модель, а не для «нажал — получил»:
1. Бросаете зерна вдохновения
2. Получаете варианты
3. Выбираете интересное направление
4. Итерируете: Cover / Repaint / Add Layer / правка промптов

**Принцип:** «Специфичность побеждает неопределённость» — детальные капшны дают лучший контроль.

---

## 2. Установка и настройка окружения

### 2.1 Что у нас уже есть (проверено 2026-08-05)

```
C:\Users\tomas\ace-step\extracted\     ← Основная установка (portable package)
├── .venv-cpu\                          ← uv venv для CPU inference
├── checkpoints\                        ← Скачанные модели
│   ├── acestep-v15-turbo\              ← Turbo DiT (8 шагов, БЕЗ CFG)
│   ├── acestep-5Hz-lm-1.7B\            ← LM 1.7B (используем)
│   └── vae\ + Qwen3-Embedding-0.6B\    ← Общие компоненты
├── cli.py                              ← Главный CLI (wizard + TOML)
├── acestep/                            ← Python пакет
└── docs/en/                            ← Документация
```

### 2.2 Переменные окружения (.env) — КЛЮЧЕВОЙ ФАЙЛ

Создайте/отредактируйте `C:\Users\tomas\ace-step\extracted\.env`:

```bash
# ==================== Model Settings ====================
ACESTEP_CONFIG_PATH=acestep-v15-turbo          # DiT модель (turbo = 8 шагов, быстро)
ACESTEP_LM_MODEL_PATH=acestep-5Hz-lm-1.7B      # LM модель (1.7B = баланс скорость/качество)

# ==================== Device & Backend ====================
ACESTEP_DEVICE=cpu                             # ВАЖНО: cpu (нет CUDA на 780M)
ACESTEP_LM_BACKEND=pt                          # PyTorch backend (vllm требует CUDA)

# ==================== LLM Initialization ====================
ACESTEP_INIT_LLM=true                          # Принудительно ВКЛЮЧАЕМ LM на CPU
# На CPU LM будет медленным, но даст метаданные и капшн-реврайт

# ==================== Download Settings ====================
ACESTEP_DOWNLOAD_SOURCE=auto                   # auto / huggingface / modelscope

# ==================== API Server (если нужен) ====================
# ACESTEP_API_KEY=your-secret-key
# PORT=8001
# SERVER_NAME=0.0.0.0

# ==================== Gradio UI (если запускаете) ====================
# PORT=7860
# SERVER_NAME=127.0.0.1
# LANGUAGE=en
# ACESTEP_BATCH_SIZE=1
```

> ⚠️ **Критично для CPU:** `ACESTEP_LM_BACKEND=pt` — vllm **не работает** на CPU. `ACESTEP_INIT_LLM=true` — принудительно включаем LM, иначе на CPU авто-детект его отключит.

### 2.3 GPU Path: WSL2 Ubuntu 24.04 + ROCm 6.3

Для полной GPU-утилизации Radeon 780M (16 GB UMA):

```bash
# В WSL2 Ubuntu 24.04:
# 1. ROCm 6.3 repo
wget -qO - https://repo.radeon.com/rocm/rocm.gpg.key | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/rocm.gpg
echo 'deb [arch=amd64] https://repo.radeon.com/rocm/apt/6.3/ noble main' | sudo tee /etc/apt/sources.list.d/rocm.list
sudo apt update

# 2. Minimal ROCm runtime
sudo apt install -y hip-runtime-amd hsa-rocr6.3.0 hipblas6.3.0 hipsparse6.3.0 hipfft6.3.0 rccl6.3.0 rocm-smi

# 3. Verify
rocm-smi
# Should show: Radeon 780M, 16384 MB VRAM

# 4. Python 3.12 venv + ROCm PyTorch
python3.12 -m venv .venv-rocm
source .venv-rocm/bin/activate
pip install torch --index-url https://download.pytorch.org/whl/rocm6.0
pip install -r requirements-rocm.txt  # or pip install -e .

# 5. Environment for ACE-Step
export ACESTEP_DEVICE=auto
export ACESTEP_LM_BACKEND=vllm    # vllm works on Linux ROCm!
export ACESTEP_INIT_LLM=true
export ACESTEP_CONFIG_PATH=acestep-v15-turbo
export ACESTEP_LM_MODEL_PATH=acestep-5Hz-lm-1.7B
export HSA_OVERRIDE_GFX_VERSION=11.0.1
export MIOPEN_FIND_MODE=FAST

# 6. Run API server
python -m acestep.api_server --port 8001 --host 0.0.0.0
```

**Преимущества WSL2 ROCm:**
- `vllm` backend работает (LM в 2-3x быстрее)
- Стабильнее, меньше MIOPEN багов
- 16 ГБ UMA полностью доступны
- Единое окружение с Docker/ParanoidX

### 2.4 Проверка работоспособности

```bash
# CPU test
cd C:\Users\tomas\ace-step\extracted
.venv-cpu\Scripts\python.exe -c "
from acestep.handler import AceStepHandler
h = AceStepHandler()
h.initialize_service(
    project_root=r'C:\Users\tomas\ace-step\extracted',
    config_path='acestep-v15-turbo',
    device='cpu'
)
print('✅ DiT загружен успешно')
"

# GPU test (WSL2)
python -c "
import torch
print('ROCm available:', torch.cuda.is_available())
print('Device:', torch.cuda.get_device_name(0))
print('VRAM:', torch.cuda.get_device_properties(0).total_memory / 1e9, 'GB')
"
```

---

## 3. Выбор моделей для вашего железа

### 3.1 Таблица совместимости

| Ваш случай | DiT модель | LM модель | Backend | Шаги | CFG | Примечание |
|------------|-----------|-----------|---------|------|-----|------------|
| **CPU only** | `acestep-v15-turbo` | `acestep-5Hz-lm-1.7B` | `pt` | 8 | ❌ | Turbo не поддерживает CFG |
| **WSL2 ROCm 16GB (Tier 6a)** | `acestep-v15-turbo` | `acestep-5Hz-lm-1.7B` | `vllm` | 8 | ❌ | **РЕКОМЕНДУЕМ** |
| CPU, нужен CFG | `acestep-v15-sft` | `acestep-5Hz-lm-1.7B` | `pt` | 50 | ✅ | В 6-8x медленнее |
| GPU, макс. качество | `acestep-v15-base` | `acestep-5Hz-lm-4B` | `vllm` | 50-100 | ✅ | LoRA training, extract/lego/complete |

### 3.2 Доступные DiT модели в checkpoints/

```
checkpoints/
├── acestep-v15-turbo\           ← DEFAULT: 8 шагов, distillation, нет CFG, быстрый
├── acestep-v15-turbo-shift1\    ← Больше деталей, слабее семантика
├── acestep-v15-turbo-shift3\    ← Чётче тембр, может быть «сухим»
├── acestep-v15-turbo-continuous ← Экспериментальный, shift 1-5
├── acestep-v15-sft\             ← 50 шагов, ЕСТЬ CFG, больше деталей
└── acestep-v15-base\            ← 50 шагов, CFG, задачи extract/lego/complete
```

**Рекомендация для радио:** `acestep-v15-turbo` — идеальный баланс скорости/качества для потокового контента.

### 3.3 LM модели

| Модель | Параметры | VRAM (GPU) | Скорость | Качество планирования | Наш выбор |
|--------|-----------|------------|----------|----------------------|-----------|
| `acestep-5Hz-lm-0.6B` | 0.6B | ~2GB | ⚡⚡⚡ | Базовое | Для слабых GPU |
| **`acestep-5Hz-lm-1.7B`** | **1.7B** | **~4GB** | **⚡⚡** | **Среднее** | **✅ НАШ ВЫБОР** |
| `acestep-5Hz-lm-4B` | 4B | ~8GB | ⚡ | Богатое | Оверкилл для 16GB |

### 3.4 Tier 6a (16-20 GB VRAM) capabilities

| Параметр | Значение |
|----------|----------|
| Max Duration (LM / No LM) | 8 min / 10 min |
| Max Batch (LM / No LM) | 4 / 8 |
| Offload | CPU (VAE+Text Encoder) |
| Quantization | INT8 |
| LoRA Training | ✅ Possible (16GB min, 20GB recommended) |

---

## 4. CLI и TOML-конфигурация

### 4.1 Основные режимы CLI

```bash
cd C:\Users\tomas\ace-step\extracted

# 1. Интерактивный визард (создаёт TOML, потом генерирует)
.venv-cpu\Scripts\python.exe cli.py

# 2. Генерация из готового TOML (НАШ РЕЖИМ для gen_music.py)
.venv-cpu\Scripts\python.exe cli.py -c config.toml

# 3. Только создать/отредактировать TOML без генерации
.venv-cpu\Scripts\python.exe cli.py --configure
.venv-cpu\Scripts\python.exe cli.py --configure -c existing.toml
```

### 4.2 Структура TOML конфига (полная)

```toml
# === Task & Instruction ===
task_type = "text2music"           # text2music | cover | repaint | lego | extract | complete
instruction = "Fill the audio semantic mask based on the given conditions:"

# === Audio Uploads ===
reference_audio = ""                # Путь к референс-аудио (стиль/тембр)
src_audio = ""                      # Путь к исходному аудио (cover/repaint/lego/extract/complete)
audio_codes = ""                    # Семантические коды 5Hz (продвинутое)

# === Text Inputs ===
caption = "upbeat electronic dance music with heavy bass"
lyrics = "[Instrumental]"
instrumental = true

# === Music Metadata ===
vocal_language = "unknown"          # en, zh, ja, ru, unknown (auto)
bpm = 128                           # 30-300, null = auto от LM
keyscale = "C Major"                # C Major, Am, F# minor, "" = auto
timesignature = "4"                 # 2,3,4,6 (2/4, 3/4, 4/4, 6/8), "" = auto
duration = 30.0                     # 10-600 сек, -1 = auto

# === Generation Parameters ===
inference_steps = 8                 # Turbo: 1-20 (8 default), Base: 1-200
guidance_scale = 7.0                # CFG strength (ТОЛЬКО для non-turbo: base/sft)
seed = -1                           # -1 = random, >0 = фиксированный

# === Advanced DiT Parameters ===
use_adg = false                     # Adaptive Dual Guidance (base only)
cfg_interval_start = 0.0            # CFG start ratio (0.0-1.0)
cfg_interval_end = 1.0              # CFG end ratio (0.0-1.0)
shift = 1.0                         # Timestep shift (1.0-5.0). РЕКОМЕНДУЕТСЯ 3.0 ДЛЯ TURBO!
infer_method = "ode"                # "ode" (быстрее, детерминист) | "sde" (стохастический)
timesteps = []                      # Кастомные таймстепы [0.97, 0.76, ...], перекрывает steps+shift

# === Repainting Parameters ===
repainting_start = 0.0              # Начало репейнта (сек)
repainting_end = -1                 # Конец репейнта (сек), -1 = до конца
audio_cover_strength = 1.0          # Сила влияния референса (0.0-1.0)

# === 5Hz Language Model Parameters ===
thinking = true                     # ВКЛЮЧАЕТ LM для CoT и кодов (КЛЮЧЕВОЙ ПАРАМЕТР)
lm_temperature = 0.85               # 0.0-2.0: выше = креативнее
lm_cfg_scale = 2.0                  # LM CFG strength
lm_top_k = 0                        # 0 = отключено, 40-100 типично
lm_top_p = 0.9                      # 0.0-1.0, 1.0 = отключено
lm_negative_prompt = "NO USER INPUT"
use_cot_metas = true                # LM выводит BPM/key/duration
use_cot_caption = true              # LM переписывает капшн
use_cot_language = true             # LM детектит язык вокала
use_constrained_decoding = true     # FSM-constrained decoding для структуры

# === CoT Generated Values (автозаполняются LM) ===
cot_bpm = 0
cot_keyscale = ""
cot_timesignature = ""
cot_duration = 0.0
cot_vocal_language = "unknown"
cot_caption = ""
cot_lyrics = ""

# === GenerationConfig (batch/output) ===
batch_size = 1                      # 1-8 (на CPU ставьте 1)
allow_lm_batch = false              # Batch в LM (требует VRAM)
use_random_seed = true              # true = случайные сиды
seeds = []                          # Список сидов для батча
lm_batch_chunk_size = 8             # Макс chunk для LM batch
constrained_decoding_debug = false
audio_format = "wav"                # mp3 | wav | flac (WAV для радио — без потерь)
```

### 4.3 Пример рабочего TOML для радио (инструменталка 120 сек)

```toml
# gen_rock_1728394756.toml — сохраняется gen_music.py
task_type = "text2music"
caption = "energetic rock with electric guitar, driving drums, powerful bass, catchy riffs, stadium anthem"
instrumental = true
duration = 120
bpm = 140
keyscale = "E Minor"
timesignature = "4"
vocal_language = "unknown"
inference_steps = 8
seed = -1
shift = 3.0                          # ← ВАЖНО для turbo!
infer_method = "ode"
device = "cpu"
backend = "pt"
config_path = "acestep-v15-turbo"
save_dir = "C:\\Users\\tomas\\ai-radio\\cache\\music\\rock"
audio_format = "wav"
thinking = true
lm_temperature = 0.85
use_cot_metas = true
use_cot_caption = true
use_cot_language = true
```

> 💡 **Правило:** `shift = 3.0` **обязателен для turbo-моделей** — это распределяет внимание диффузии на ранние шаги (структура), давая лучшую семантику. В дефолте стоит 1.0 — это хуже.

---

## 5. Полный справочник параметров

### 5.1 Task Type — тип задачи

| task_type | Описание | Обязательные поля | Модель |
|-----------|----------|-------------------|--------|
| `text2music` | Генерация из текста (DEFAULT) | caption ИЛИ lyrics | Любая |
| `cover` | Кавер: сохранить структуру, сменить стиль | src_audio, caption | Turbo/SFT/Base |
| `repaint` | Перегенер. участка [start, end] | src_audio, repainting_start, repainting_end, caption | Turbo/SFT/Base |
| `lego` | Добавить трек к бэкингу | src_audio, instruction, caption, track name | **Только Base** |
| `extract` | Извлечь трек из микса | src_audio, instruction (track name) | **Только Base** |
| `complete` | Дописать аккомпанемент к соло | src_audio, instruction (tracks), caption | **Только Base** |

### 5.2 Caption — самый важный вход

**Принципы хорошего капшнa:**
```
✅ "energetic rock with electric guitar, driving drums, powerful bass, catchy riffs, stadium anthem"
✅ "melancholic indie folk with acoustic guitar, soft female vocal, intimate atmosphere, fingerpicking"
✅ "upbeat electronic dance music with heavy 808 bass, synthesizer leads, four-on-the-floor, festival energy"

❌ "good music"                                    — слишком vaguе
❌ "fast slow music"                                — конфликт
❌ "violin solo, classical" + lyrics: [Guitar Solo] — конфликт caption↔lyrics
```

**Измерения для капшнa (комбинируйте 3-5):**
| Категория | Примеры |
|-----------|---------|
| **Стиль/Жанр** | pop, rock, jazz, electronic, hip-hop, R&B, folk, classical, lo-fi, synthwave, ambient, chiptune |
| **Эмоция/Атмосфера** | melancholic, uplifting, energetic, dreamy, dark, nostalgic, euphoric, intimate, aggressive, peaceful |
| **Инструменты** | acoustic guitar, piano, synth pads, 808 drums, strings, brass, electric bass, drum machine, flute |
| **Тембр/Текстура** | warm, bright, crisp, muddy, airy, punchy, lush, raw, polished, distorted, clean |
| **Эра/Референс** | 80s synth-pop, 90s grunge, 2010s EDM, vintage soul, modern trap, "in the style of Daft Punk" |
| **Продакшн** | lo-fi, high-fidelity, live recording, studio-polished, bedroom pop, analog warmth |
| **Вокал** | female vocal, male vocal, breathy, powerful, falsetto, raspy, choir, spoken word |
| **Ритм/Темп** | slow tempo, mid-tempo, fast-paced, groovy, driving, laid-back, half-time, double-time |
| **Структура** | building intro, catchy chorus, dramatic bridge, fade-out ending, verse-chorus, AABA |

### 5.3 Lyrics — временной сценарий

**Структурные теги (Meta Tags) — главное оружие:**

```text
[Intro - ambient]
[Verse 1]
Walking through the empty streets
City lights fade away

[Pre-Chorus - building energy]
The night is calling me

[Chorus - anthemic]
WE ARE THE STARS TONIGHT
Shining through the endless sky

[Verse 2]
...

[Bridge - whispered]
Close your eyes and feel the sound

[Guitar Solo - expressive]

[Final Chorus - powerful]
THIS IS OUR MOMENT!

[Outro - fade out]
```

**Правила:**
- **Не стопайте теги** — `[Chorus - anthemic]` хорошо, `[Chorus - anthemic - stacked - high - epic]` плохо
- **Согласованность с caption** — если caption: "violin solo", в lyrics: `[Violin Solo]`, НЕ `[Guitar Solo]`
- **Слогов на строку:** 6-10 (для русского 5-8). Равномерность = лучший ритм
- **UPPERCASE** = высокая интенсивность вокала
- **Скобки** = бэк-вокал/гармонии: `We rise (together) into the light (into the light)`

**Инструменталка:**
```text
[Instrumental]
```
ИЛИ с описанием разделов:
```text
[Intro - ambient]
[Main Theme - piano]
[Climax - powerful]
[Outro - fade out]
```

### 5.4 Music Metadata — тонкая настройка

| Параметр | Диапазон | Когда задавать вручную |
|----------|----------|------------------------|
| `bpm` | 30-300 | Чёткое требование темпа, вальс (3/4), мач к другому треку |
| `keyscale` | C Major, Am, F# Minor... | Нужен конкретный лад (например, для смешивания) |
| `timesignature` | 2,3,4,6 | Вальс (3), свинг (6), нестандартные размеры |
| `vocal_language` | en, zh, ja, ru, es... | Принудительно задать язык, если LM ошибается |
| `duration` | 10-600 сек | Нужна точная длина (дзинглы, реклама, жёсткий тайминг) |

> ⚠️ **Модель не исполняет метаданные механически** — это «якоря». `bpm=120` даст ~118-122. Не пишите BPM/ключ в caption — используйте выделенные параметры.

### 5.5 Advanced DiT Parameters — для продвинутых

| Параметр | Значение | Эффект | Когда использовать |
|----------|----------|--------|-------------------|
| `shift` | 1.0-5.0 (def: 1.0) | **Критично для turbo!** 3.0 = лучше структура, 1.0 = больше деталей | **Всегда 3.0 для turbo** |
| `infer_method` | `ode` / `sde` | `ode`=детерминист, быстрее; `sde`=стохастик, вариативнее | `ode` для радио (стабильность) |
| `timesteps` | `[0.97, 0.76, ...]` | Полный контроль траектории диффузии | Эксперименты, кастомные расписания |
| `guidance_scale` | 1.0-15.0 (def: 7.0) | CFG: выше = больше следование промпту | **Только для base/sft! Turbo игнорирует** |
| `use_adg` | true/false | Adaptive Dual Guidance (base only) | Качественная генерация base |
| `cfg_interval_start/end` | 0.0-1.0 | Когда применять CFG в диффузии | Тонкая настройка base |
| `audio_cover_strength` | 0.0-1.0 | Сила влияния src_audio (cover/repaint) | 0.2 = style transfer, 1.0 = строгий кавер |

### 5.6 LM Parameters — управление планировщиком

| Параметр | Дефолт | Рекомендация для радио |
|----------|--------|------------------------|
| `thinking` | true | **true** — включает LM, даёт метаданные + коды |
| `lm_temperature` | 0.85 | 0.7-0.9: ниже = консервативнее, выше = креативнее |
| `lm_cfg_scale` | 2.0 | 1.5-3.0: сила следования промпту в LM |
| `use_cot_metas` | true | **true** — авто-BPM/key/duration |
| `use_cot_caption` | true | **true** — LM улучшает ваш капшн |
| `use_cot_language` | true | **true** — авто-детект языка вокала |
| `use_constrained_decoding` | true | **true** — гарантирует структуру вывода |

---

## 6. Режимы генерации (Task Types) — детально

### 6.1 Text2Music (основной для радио)

```toml
task_type = "text2music"
caption = "your detailed description"
lyrics = "[Instrumental]"  # или полные лирики
instrumental = true
# + metadata опционально
```

**Для радио:** всегда `instrumental = true` (дзинглы, беды, музыкальные блоки без вокала).

### 6.2 Cover — переработка существующего трека

```toml
task_type = "cover"
src_audio = "C:\\path\\to\\original.wav"
caption = "jazz piano version, intimate, slow tempo"
audio_cover_strength = 0.7    # 0.1-0.3 = loose style transfer, 0.7-1.0 = tight cover
lyrics = "[Instrumental]"     # новые лирики (опционально)
```

**Use cases для радио:**
- Взять популярный трек → сделать радиоверсию (instrumental, другой стиль)
- Создать вариации джинглов на одной мелодической основе

### 6.3 Repaint — локальная правка

```toml
task_type = "repaint"
src_audio = "C:\\path\\to\\track.wav"
repainting_start = 30.0      # секунды
repainting_end = 45.0        # -1 = до конца
caption = "smooth piano bridge with emotional build-up"
```

**Use cases:**
- Исправить неудачный переход
- Заменить куплет на другой
- Продлить трек (repaint в конце с `repainting_end = -1`)

### 6.4 Lego / Extract / Complete — только Base модель

Требуют `acestep-v15-base` (50 шагов, медленнее). Для радио вряд ли нужны, но полезно знать:
- **Lego:** добавить гитару к бэкингу
- **Extract:** выделить вокал для ремикса
- **Complete:** к акапелле сгенерировать полный аккомпанемент

---

## 7. Интеграция с AI Radio (gen_music.py)

### 7.1 Как это работает сейчас

Ваш `gen_music.py`:
1. Читает `config.yaml` → стили + промпты
2. Для каждого стиля генерирует TOML через `gen_toml()`
3. Запускает `cli.py -c config.toml` через subprocess в `.venv-cpu`
4. Сохраняет WAV в `cache/music/<style>/`

### 7.2 Улучшенная версия gen_toml() (скопируйте в gen_music.py)

```python
def gen_toml(style: str, prompt: str, duration: int, out_dir: str, seed: int = -1) -> str:
    safe_dir = out_dir.replace("\\", "\\\\\\\\")
    safe_prompt = prompt.replace("\\", "\\\\\\\\").replace('"', '\\\\"')
    
    # Рекомендуемые настройки для радио (CPU, turbo)
    return f"""task_type = "text2music"
caption = "{safe_prompt}"
instrumental = true
duration = {duration}
seed = {seed}
inference_steps = 8
shift = 3.0
infer_method = "ode"
device = "cpu"
backend = "pt"
config_path = "acestep-v15-turbo"
save_dir = "{safe_dir}"
audio_format = "wav"
thinking = true
lm_temperature = 0.85
use_cot_metas = true
use_cot_caption = true
use_cot_language = true
bpm = 120
keyscale = ""
timesignature = "4"
vocal_language = "unknown"
guidance_scale = 7.0
use_adg = false
cfg_interval_start = 0.0
cfg_interval_end = 1.0
repainting_start = 0.0
repainting_end = -1
audio_cover_strength = 1.0
lm_cfg_scale = 2.0
lm_top_k = 0
lm_top_p = 0.9
lm_negative_prompt = "NO USER INPUT"
use_constrained_decoding = true
allow_lm_batch = false
use_random_seed = true
seeds = []
lm_batch_chunk_size = 8
constrained_decoding_debug = false
"""
```

### 7.3 Добавляем вариативность через сиды

```python
def generate_batch(style: str, prompt: str, duration: int, out_dir: str, count: int = 4):
    """Генерирует батч из count вариантов с разными сидами для выбора лучшего"""
    import random
    seeds = [random.randint(1, 2**31-1) for _ in range(count)]
    
    for i, seed in enumerate(seeds):
        tag = f"{int(time.time())}_{i}"
        cfg_path = os.path.join(RADIO_ROOT, "scripts", f"gen_{style}_{tag}.toml")
        with open(cfg_path, "w", encoding="utf-8") as f:
            f.write(gen_toml(style, prompt, duration, out_dir, seed))
        
        # Запуск...
        r = subprocess.run([ACE_PY, CLI, "-c", cfg_path], ...)
        
        # После батча — можно проскорить и оставить лучший
        # (см. раздел Automatic Scoring ниже)
```

### 7.4 Автоматический скрининг (Quality Scoring)

ACE-Step имеет встроенный **DiT Lyrics Alignment Score** (перплексия):
- Высокий скор = лирики точнее попадают в аудио
- Для инструменталок работает метрика качества генерации

```python
# После генерации батча — парсим вывод или используем Python API
from acestep.inference import generate_music, GenerationParams, GenerationConfig
from acestep.handler import AceStepHandler
from acestep.llm_inference import LLMHandler

# Инициализация один раз
dit = AceStepHandler()
dit.initialize_service(project_root=ACE_ROOT, config_path="acestep-v15-turbo", device="cpu")
llm = LLMHandler()
llm.initialize(checkpoint_dir=os.path.join(ACE_ROOT, "checkpoints"), 
               lm_model_path="acestep-5Hz-lm-1.7B", backend="pt", device="cpu")

# Батч с автоматическим скором
params = GenerationParams(task_type="text2music", caption=prompt, instrumental=True, duration=120)
config = GenerationConfig(batch_size=4, audio_format="wav")
result = generate_music(dit, llm, params, config, save_dir=out_dir)

if result.success:
    for audio in result.audios:
        # extra_outputs содержит скоры
        score = audio.get('quality_score', 0)
        print(f"Seed {audio['params']['seed']}: score={score:.3f}, path={audio['path']}")
    
    # Берём лучший
    best = max(result.audios, key=lambda a: a.get('quality_score', 0))
    print(f"✅ BEST: {best['path']} (seed={best['params']['seed']})")
```

### 7.5 API-базированная интеграция (для GPU сервера)

```python
# Вместо subprocess CLI → HTTP API к WSL2 серверу
import requests, json, time

API = "http://localhost:8001"  # WSL2 API сервер

def generate_via_api(style, prompt, duration, out_dir, count=1):
    results = []
    for i in range(count):
        # 1. Release task
        r = requests.post(f"{API}/release_task", json={
            "prompt": prompt,
            "lyrics": "[Instrumental]",
            "thinking": True,
            "audio_duration": duration,
            "bpm": 120,
            "inference_steps": 8,
            "shift": 3.0,
            "batch_size": 1,
            "audio_format": "wav"
        })
        task_id = r.json()["data"]["task_id"]
        
        # 2. Poll
        while True:
            time.sleep(1)
            r = requests.post(f"{API}/query_result", json={"task_id_list": [task_id]})
            data = r.json()["data"][0]
            if data["status"] == 1:
                break
            elif data["status"] == 2:
                raise Exception("Generation failed")
        
        # 3. Download
        result = json.loads(data["result"])[0]
        audio_url = f"{API}{result['file']}"
        local_path = os.path.join(out_dir, f"{style}_{task_id[:8]}.wav")
        with open(local_path, "wb") as f:
            f.write(requests.get(audio_url).content)
        results.append(local_path)
    return results
```

---

## 8. Продвинутые техники настройки

### 8.1 Prompt Engineering для радио-контента

#### Джинглы (5-15 сек)
```toml
caption = "short radio jingle, upbeat, catchy melody, brass fanfare, energetic, 5 seconds, station ID"
duration = 5
bpm = 140
timesignature = "4"
```

#### Беды / Музыка под речь (30-60 сек)
```toml
caption = "radio bed, background music for voiceover, subtle, unobtrusive, ambient electronic, minimal melody, steady rhythm, loopable"
duration = 45
bpm = 100
```

#### Музыкальные блоки (2-4 минуты)
```toml
caption = "full radio track, energetic pop rock, electric guitar riff, driving drums, catchy chorus, structured verse-chorus, professional production, radio edit"
duration = 180
bpm = 130
```

#### Ночной эфир (Ambient/Chill)
```toml
caption = "late night radio, ambient chillout, soft pads, slow tempo, dreamy atmosphere, minimal percussion, intimate, relaxing, smooth transitions"
duration = 240
bpm = 70
```

### 8.2 Контроль случайности (Seed Management)

```python
# Для воспроизводимости — фиксируйте сид
seed = 42  # Всегда один результат

# Для исследования — батч с разными сидами
seeds = [42, 123, 456, 789, 999]  # 5 вариантов

# Для продакшена — random seed, но логируйте использованный
seed = -1  # random
# После генерации: проверьте result.audios[0]['params']['seed'] и запишите в лог
```

### 8.3 Shift Parameter Deep Dive

| Shift | Характер генерации | Когда использовать |
|-------|-------------------|-------------------|
| 1.0 | Равномерное внимание, больше деталей, слабее структура | Эксперименты, текстурные треки |
| 2.0 | Баланс | Переходный |
| **3.0** | **Фокус на ранние шаги = чёткая структура, сильная семантика** | **DEFAULT ДЛЯ TURBO (РЕКОМЕНДУЕТСЯ)** |
| 4.0 | Очень сильная структура, может быть «сухим», минимальный оркестр | Строгие жанры (марш, техно) |
| 5.0 | Максимальная структура | Редко нужно |

> **Наш стандарт:** `shift = 3.0` для всех turbo-генераций.

### 8.4 Custom Timesteps (продвинутый контроль)

Вместо `inference_steps + shift` можно задать точный расписание:

```toml
# 9-шаговый кастомный schedule (пример из docs)
timesteps = [0.97, 0.76, 0.615, 0.5, 0.395, 0.28, 0.18, 0.085, 0]
inference_steps = 0      # игнорируется когда timesteps задан
shift = 1.0              # игнорируется
```

**Когда полезно:** научные эксперименты, репродукция конкретных результатов, бенчмарки.

### 8.5 LM Negative Prompt — что ИСКЛЮЧИТЬ

```toml
lm_negative_prompt = "low quality, muffled, distorted, clipping, noisy, harsh, dissonant, off-key, off-beat, repetitive, boring, generic, amateur, demo quality"
```

Добавляет в LM понимание чего **не** генерировать. Полезно для поднятия качественного порога.

---

## 9. LoRA обучение для радио-стиля

### 9.1 Зачем радио нужен свой LoRA?

- **Единый бренд-звук** — все джинглы/беды в одном стиле
- **Скорость** — LoRA адаптирует модель за секунды под ваш стиль
- **Консистентность** — не нужно каждый раз писать мега-детальные промпты

### 9.2 Подготовка датасета (минимум 8-10 треков)

Структура:
```
radio_lora_dataset/
├── jingle_morning_01.wav
├── jingle_morning_01.lyrics.txt     # [Instrumental] или с тегами
├── jingle_morning_01.json           # {"caption": "...", "bpm": 140, "keyscale": "C Major", "timesignature": "4", "language": "en"}
├── bed_news_01.wav
├── bed_news_01.lyrics.txt
├── bed_news_01.json
└── ...
```

**JSON аннотация (все поля опциональны):**
```json
{
    "caption": "bright morning radio jingle, brass fanfare, upbeat, energetic, station identification, 5 seconds",
    "bpm": 140,
    "keyscale": "C Major",
    "timesignature": "4",
    "language": "en"
}
```

### 9.3 Обучение через Gradio UI (рекомендуемый путь)

1. **Отключите pre-init в лаунчере:**
   ```bat
   REM start_gradio_ui.bat
   if not defined INIT_SERVICE set INIT_SERVICE=--init_service false
   ```

2. **Запустите Gradio:** `start_gradio_ui.bat`

3. **Вкладка LoRA Training → Dataset Builder:**
   - Scan папку с датасетом
   - Uncheck "All Instrumental" (если есть вокальные джинглы)
   - Custom Activation Tag: `master_fm_style` (уникальный тег)
   - Tag Position: Prepend
   - **Auto-Label All** (использует LM для капшн/BPM/key)
   - Review & Save Dataset → JSON

4. **Preprocess:** конвертит в тензоры (VAE latents + embeddings)
   - На CPU это медленно — будьте терпеливы
   - Рекомендуется рестарт Gradio после автолейбла (освободить VRAM/RAM)

5. **Train LoRATab:**
   - Load предобработанные тензоры
   - Параметры (для CPU/мало VRAM):
     ```
     LoRA Rank (r): 32          (меньше = быстрее, меньше память)
     LoRA Alpha: 64             (обычно 2x rank)
     LoRA Dropout: 0.1
     Learning Rate: 1e-4
     Max Epochs: 500-800        (10 треков → 800, 50 треков → 500)
     Batch Size: 1
     Gradient Accumulation: 1
     Save Every N Epochs: 100
     Shift: 3.0
     Seed: 42
     ```
   - Start Training → ждите завершения

6. **Export LoRA** → папка с адаптером

### 9.4 Использование LoRA в генерации

```toml
# В TOML конфиге или через Python API
# LoRA загружается отдельно (не в TOML), через UI или API

# Python API:
from acestep.handler import AceStepHandler
dit = AceStepHandler()
dit.initialize_service(...)
dit.load_lora("C:\\path\\to\\master_fm_lora")  # Загружает адаптер
dit.use_lora = True

# Теперь генерация с вашим стилем:
caption = "master_fm_style, radio jingle, upbeat"  # Тег активирует LoRA
```

> ⚠️ **LoRA + Quantization = КОНФЛИКТ** (PEFT + TorchAO). Отключите INT8 Quantization перед загрузкой LoRA.

---

## 10. REST API сервер

### 10.1 Запуск API сервера

```bash
cd C:\Users\tomas\ace-step\extracted

# В .env добавьте:
ACESTEP_API_KEY=your-secret-radio-key
PORT=8001
SERVER_NAME=0.0.0.0

# Запуск:
.venv-cpu\Scripts\python.exe -m acestep.api_server
# Или через лаунчер:
start_api_server.bat

# WSL2 GPU version:
python -m acestep.api_server --port 8001 --host 0.0.0.0
```

### 10.2 Основные эндпоинты

| Эндпоинт | Метод | Назначение |
|----------|-------|------------|
| `/release_task` | POST | Создать задачу генерации |
| `/query_result` | POST | Проверить статус (батч) |
| `/format_input` | POST | Улучшить caption/lyrics через LM |
| `/create_random_sample` | POST | Получить случайный пример |
| `/v1/models` | GET | Список доступных моделей |
| `/v1/audio?path=...` | GET | Скачать сгенерированный аудио |
| `/health` | GET | Health check |

### 10.3 Пример запроса (curl)

```bash
# 1. Отправка задачи
curl -X POST http://localhost:8001/release_task \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-secret-radio-key" \
  -d '{
    "prompt": "radio jingle, upbeat, brass, energetic, 5 seconds",
    "lyrics": "[Instrumental]",
    "thinking": true,
    "audio_duration": 5,
    "bpm": 140,
    "inference_steps": 8,
    "shift": 3.0,
    "batch_size": 2
  }'

# Ответ: {"data": {"task_id": "uuid", "status": "queued", "queue_position": 1}, "code": 200}

# 2. Опрос результата
curl -X POST http://localhost:8001/query_result \
  -H "Content-Type: application/json" \
  -d '{"task_id_list": ["uuid-from-above"]}'

# Ответ когда status=1:
# "result": "[{\"file\": \"/v1/audio?path=...\", \"metas\": {...}, \"seed_value\": \"12345\", ...}]"

# 3. Скачивание
curl "http://localhost:8001/v1/audio?path=..." -o jingle.wav
```

### 10.4 Интеграция с DJ (dj.py)

```python
# В dj.py можно добавить генерацию на лету через API
import requests
import json

API_BASE = "http://localhost:8001"
API_KEY = "your-secret-radio-key"

def generate_jingle_on_demand(style: str, duration: int = 10) -> str:
    """Генерирует джингль через API, возвращает путь к файлу"""
    prompt = JINGLE_PROMPTS[style]  # из конфига
    
    # 1. Release task
    r = requests.post(f"{API_BASE}/release_task", 
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={"prompt": prompt, "lyrics": "[Instrumental]", "thinking": True,
              "audio_duration": duration, "bpm": 140, "inference_steps": 8, "shift": 3.0, "batch_size": 1})
    task_id = r.json()["data"]["task_id"]
    
    # 2. Poll до готовности
    while True:
        time.sleep(2)
        r = requests.post(f"{API_BASE}/query_result", 
            json={"task_id_list": [task_id]})
        result = r.json()["data"][0]
        if result["status"] == 1:
            break
        elif result["status"] == 2:
            raise Exception("Generation failed")
    
    # 3. Скачиваем
    audio_url = json.loads(result["result"])[0]["file"]
    local_path = f"C:\\Users\\tomas\\ai-radio\\cache\\jingles\\{style}\\{task_id}.wav"
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    r = requests.get(f"{API_BASE}{audio_url}")
    with open(local_path, "wb") as f:
        f.write(r.content)
    
    return local_path
```

---

## 11. Траблшутинг и частые ошибки

### 11.1 CPU-специфичные проблемы

| Ошибка | Причина | Решение |
|--------|---------|---------|
| `RuntimeError: CUDA out of memory` | Код пытается использовать CUDA | Проверьте `device="cpu"`, `backend="pt"`, `ACESTEP_DEVICE=cpu` |
| `ModuleNotFoundError: No module named 'vllm'` | vllm не ставится на CPU | `ACESTEP_LM_BACKEND=pt` в .env |
| `ACESTEP_INIT_LLM=auto` отключает LM на CPU | Авто-детект видит 0 VRAM | `ACESTEP_INIT_LLM=true` принудительно |
| Генерация вечно висит / очень медленно | CPU inference тормозит | Нормально для CPU. Turbo 8 шагов ~2-5 мин на трек. Уменьшите `duration`, `batch_size=1` |
| `UnicodeDecodeError` в subprocess | Кириллица в stdout | В gen_music.py: `text=True, encoding='utf-8', errors='ignore'` |

### 11.2 WSL2 ROCm проблемы

| Ошибка | Причина | Решение |
|--------|---------|---------|
| `rocm-smi` не видит GPU | Драйверы не загружены | `sudo modprobe amdgpu` + ребут WSL (`wsl --shutdown`) |
| `HSA_OVERRIDE_GFX_VERSION` не помогает | Не тот GFX | Для 780M (RDNA3, GFX1102) используйте `11.0.1` |
| MIOPEN ошибки | Конфликт кэшей | `export MIOPEN_FIND_MODE=FAST` + `rm -rf ~/.config/miopen` |
| `torch.cuda.is_available()` = False | PyTorch не ROCm | Переустановите: `pip install torch --index-url https://download.pytorch.org/whl/rocm6.0` |
| vllm OOM на 16GB | KV cache слишком большой | `export VLLM_WORKER_MULTIPROC_METHOD=spawn` + уменьшите `batch_size` |

### 11.3 Проблемы с TOML/CLI

| Ошибка | Решение |
|--------|---------|
| `toml.TomlDecodeError` | Экранируйте обратные слеши: `\\\\` в путях, `\\\"` для кавычек в caption |
| CLI не находит модели | Проверьте `checkpoints/` — модели должны быть распакованы там |
| `config_path` не найден | Используйте имя папки в checkpoints: `acestep-v15-turbo` (не полный путь) |
| `audio_format = "wav"` не работает | Убедитесь, что `save_dir` существует и записываем |

### 11.4 Качество генерации

| Проблема | Диагностика | Фикс |
|----------|-------------|------|
| Музыка «разваливается» посередине | Слишком длинная duration для turbo | Разбивайте на сегменты (repaint) или используйте base model |
| Нет структуры (нет верс/хорус) | `shift=1.0` (дефолт) | **Обязательно `shift=3.0` для turbo** |
| Конфликт caption ↔ lyrics | Caption: "piano ballad", Lyrics: [Guitar Solo] | Согласовывайте инструменты в обоих полях |
| LM галлюцинирует BPM/ключ | `use_cot_metas=true` но caption слабый | Добавьте `bpm`, `keyscale` вручную |
| Слишком «ИИ-звучит» (механично) | Нет вариативности, лирики без души | Используйте структурные теги, варьируйте интенсивность (UPPERCASE), добавляйте parenthetical бэк-вокал |
| Генерация не похожа на промпт | `thinking=false` или слабый caption | Включите `thinking=true`, напишите детальный caption (5+ измерений) |

### 11.5 Windows/MSYS питфоллы (из super-coder)

```python
# В gen_music.py subprocess запуск:
env = dict(os.environ)
env["ACESTEP_DEVICE"] = "cpu"
env.pop("PYTHONPATH", None)      # Критично! Иначе импортируется torch из Hermes venv
env.pop("VIRTUAL_ENV", None)     # Иначе конфликт venv

# Пути для Python всегда Windows-style:
ACE_PY = r"C:\Users\tomas\ace-step\extracted\.venv-cpu\Scripts\python.exe"
CLI = r"C:\Users\tomas\ace-step\extracted\cli.py"
cfg_path = r"C:\Users\tomas\ai-radio\scripts\gen_rock_123.toml"

subprocess.run([ACE_PY, CLI, "-c", cfg_path], cwd=ACE_ROOT, env=env, ...)
```

---

## 12. Чек-лист качества генерации

### Перед генерацией батча:
- [ ] `shift = 3.0` в TOML (критично для turbo!)
- [ ] `thinking = true` (LM включён)
- [ ] `inference_steps = 8` (turbo) или 50+ (base/sft)
- [ ] `device = "cpu"`, `backend = "pt"` в .env (CPU) или `device=auto`, `backend=vllm` (GPU)
- [ ] `audio_format = "wav"` (без потерь для радио)
- [ ] Caption содержит 3-5 измерений (стиль + эмоция + инструменты + тембр + эра)
- [ ] Lyrics согласованы с caption (инструменты, эмоция, структура)
- [ ] `instrumental = true` для джинглов/бедов/музыкальных блоков
- [ ] `duration` реалистична (10-300 сек стабильно, 300-600 — риск повторов)

### После генерации (проверка результата):
- [ ] Аудио играется без артефактов (клики, обрывы, тишина)
- [ ] Длительность ≈ заданной (±10%)
- [ ] Темп соответствует BPM (слухово или через анализ)
- [ ] Структура слышна (верс/хорус/бридж разделены)
- [ ] Нет конфликтов инструментов (caption: скрипка, слышно: гитара)
- [ ] Качество микса: баланс, нет клиппинга, динамика живая

### Для продакшена (радио):
- [ ] Зафиксирован `seed` лучшего варианта (для воспроизводимости)
- [ ] Файл назван понятно: `jingle_morning_v2_seed42.wav`
- [ ] Метаданные записаны в БД/лог: стиль, prompt, seed, BPM, key, duration
- [ ] Файл положен в правильную `cache/music/<style>/` или `cache/jingles/<type>/`

---

## 📎 Приложения

### А. Полезные ссылки

- **GitHub:** https://github.com/ACE-Step/ACE-Step-1.5
- **HuggingFace Models:** https://huggingface.co/ACE-Step/Ace-Step1.5
- **Technical Report (arXiv):** https://arxiv.org/abs/2602.00744
- **Discord:** https://discord.gg/PeWDxrkdj7
- **Suno Prompting Guide (универсальный):** https://www.notion.so/The-Complete-Guide-to-Mastering-Suno-Advanced-Strategies-for-Professional-Music-Generation-2d6ae744ebdf8024be42f6645f884221

### Б. Ключевые файлы проекта AI Radio

```
C:\Users\tomas\ai-radio\
├── config.yaml                    # Стили, промпты, расписание
├── scripts/
│   ├── gen_music.py               # Главный генератор (использует ACE-Step CLI)
│   ├── dj.py                      # DJ-сервер (плейлист + ffmpeg stream)
│   └── gen_voice_content.py       # TTS для новостей/дзинглов
├── cache/
│   ├── music/<style>/             # Сгенерированные треки
│   ├── jingles/<type>/            # Джинглы
│   ├── news/<category>/           # Новости (TTS)
│   └── ads/                       # Реклама
└── docs/
    └── ACE-STEP-USER-GUIDE.md     # Этот файл
```

### В. Быстрый старт для нового участника команды

```bash
# 1. Активируйте окружение
cd C:\Users\tomas\ace-step\extracted
.venv-cpu\Scripts\activate

# 2. Проверьте модели
ls checkpoints/

# 3. Тестовая генерация (5 сек джингл)
python cli.py --configure
# В визарде: text2music → turbo → 1.7B LM → Simple Mode → 
# "radio jingle, upbeat, brass, 5 seconds" → Instrumental → Generate

# 4. Если работает — используйте gen_music.py для батчей
cd C:\Users\tomas\ai-radio
python scripts\gen_music.py --style rock --count 3 --duration 120
```

---

## 🎯 Главные правила для AI Radio

1. **Turbo + Shift 3.0** — стандарт для всех музыкальных блоков
2. **LM включён (thinking=true)** — даёт метаданные и улучшает капшн
3. **Caption — король** — вкладывайте 80% усилий в написание капшнa
4. **Lyrics с тегами** — даже для инструменталок (`[Intro - ambient]` ... `[Outro - fade out]`)
5. **Батч → Скор → Лучший** — генерируйте 3-4 варианта, берите лучший по quality_score
6. **Логируйте сиды** — лучший сид = воспроизводимость хитов
7. **LoRA для бренда** — когда накопите 10+ эталонных треков, обучите свой LoRA

---

*Документ обновляется по мере эволюции проекта. Последнее обновление: 2026-08-05*
*Вопросы/предложения — в чат Master Inquisitor / Telegram CathedralMaster_bot*