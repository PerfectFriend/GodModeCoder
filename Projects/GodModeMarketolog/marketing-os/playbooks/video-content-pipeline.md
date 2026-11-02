# Playbook: Video Content Pipeline (MoneyPrinterTurbo)

> **Назначение:** Автогенерация коротких видео (Shorts/Reels/TikTok) из темы. $0 локально.
> **Источник:** MoneyPrinterTurbo + AI_Marketing_Machine (AGENT-4 Creative).

## Pipeline
```
Topic/Keyword
    → LLM Script (Hook + Value + CTA, JSON)
    → TTS Voiceover (Edge TTS — free, high quality)
    → Stock Footage (Pexels / local) по visual_keywords
    → Subtitles (Whisper/local)
    → Background Music (local, vol 0.1)
    → FFmpeg Composition (1080x1920, 30fps)
    → Output: MP4
```

## Установка (local, zero cost)
```bash
git clone https://github.com/harry0703/MoneyPrinterTurbo
cd MoneyPrinterTurbo && pip install -r requirements.txt
sudo apt install ffmpeg   # или brew/choco
python main.py --web      # или CLI
```

## Python API (интеграция в AGENT-4)
```python
from dataclasses import dataclass
from enum import Enum
import asyncio, edge_tts, ollama

class VideoOrientation(Enum):
    VERTICAL = "vertical"    # 1080x1920 — Shorts/Reels/TikTok
    HORIZONTAL = "horizontal" # 1920x1080 — YouTube/X

@dataclass
class VideoSpec:
    topic: str
    language: str = "en"
    paragraphs: int = 5
    duration: int = 60
    orientation: VideoOrientation = VideoOrientation.VERTICAL
    tts_voice: str = "en-US-AriaNeural"

async def generate(spec: VideoSpec) -> Path:
    # 1. Script (LLM, JSON: title + paragraphs[{text, visual_keywords}])
    # 2. Voiceover (edge_tts.Communicate)
    # 3. Footage (Pexels API by visual_keywords)
    # 4. Compose (ffmpeg scale+pad, libx264, aac)
    ...
```

## Batch Generation (Content Calendar)
```python
CONTENT_CALENDAR = [
    {"topic": "SuperGuard: AI surveillance on edge", "date": "2026-09-01", "series": "Demo"},
    {"topic": "Zero-IME keyboard — privacy first", "date": "2026-09-02", "series": "Value"},
    {"topic": "Built sovereign stack on trash laptop", "date": "2026-09-03", "series": "Story"},
]
# rename to {date}_{series}_{topic[:30]}.mp4 → auto-schedule via Buffer
```

## Cost Analysis
| Метрик | Explee | Manual | MoneyPrinterTurbo |
|--------|--------|--------|-------------------|
| $/video | $30-50 | $500+ | **$0** local / $0.03 |
| Время | 60с setup | 2-10ч | 5-15 мин |
| Качество | Pro | Variable | Consistent HD |
| Scale | Good | Poor | Excellent |

## AGENT-4 Weekly Cycle
```
Пн: тема недели (feature / case / comparison / launch)
Вт: batch 50+ вариаций в ComfyUI (prompts из brandbook)
Ср: топ-10, upscale 4x, color grade
Чт: адаптация под 8 форматов → 80 финальных ассетов
Пт: загрузка в Asset Library, UTM-теги
Сб: видео (AnimateDiff 5 Reels + SVD 2 Shorts + Runway 1 Hero)
Вс: анализ CTR → prompt-тюнинг
```

## A/B Test Ideas
- AI voice vs cloned voice
- Stock footage vs generated (ComfyUI)
- Hook в первые 3 сек vs медленный заход
- CTA в конце vs CTA в середине

## Hard Rules
- Видео = топ-сигнал для X-алгоритма (см. theory/x-algorithm-playbook.md)
- Саблицы обязательны (доступность + удержание)
- Локальный рендер = ноль зависимости от облака (принцип ParanoidX)
