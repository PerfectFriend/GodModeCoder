---
name: news_scraper_production
description: "Hourly RSS scraper for Radio - 287 feeds, TTS-ready output."
version: 1.0.0
author: Hermes Agent
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [news, rss, scraper, radio, tts]
    schedule: "every 1h"
    category: mlops
---

# News Scraper Production

Продукционный скрапер новостей для Radio ArmsgeddonFM.

## Возможности
- Парсит 287 RSS фидов из 17 категорий
- Сохраняет только НОВЫе статьи за последний час
- Дедипликация через index.json + state file
- Готовые к TTS текстовые файлы в /newsfeed/<category>/
- Поддержка русскоязычных и англоязычных источников

## Категории (17)
- tech (14 feeds): ixbt, habr, vc.ru, tproger, securitylab...
- ai_ml (19 feeds): huggingface, openai, deepmind, anthropic...
- space (15 feeds): nasa, spacex, space.com, nasaspaceflight...
- science (14 feeds): nature, science, quantamagazine...
- politics (16 feeds): reuters, bbc, nytimes, guardian...
- war (15 feeds): reuters_ukraine, isw, kyiv_independent...
- finance (19 feeds): bloomberg, ft, wsj, cnbc, economist...
- crypto (21 feeds): coindesk, theblock, cointelegraph...
- culture (19 feeds): variety, deadline, rolling stone...
- gaming (14 feeds): ign, gamespot, polygon, kotaku...
- hardware (27 feeds): anandtech, tomshardware, android_authority...
- auto (14 feeds): electrek, insideevs, teslarati...
- health (15 feeds): nih, who, nejm, lancet...
- energy (14 feeds): greentech, pv_magazine, carbon_brief...
- ru_tech (20 feeds): ixbt, habr, vc.ru, 3dnews, securitylab...
- ru_politics (15 feeds): tass, ria, lenta, kommersant...
- ru_war (16 feeds): lenta_war, tass_war, meduza, zona...

## Запуск
```bash
cd /c/Users/tomas/ai-radio
/c/Users/tomas/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe news_scraper_production.py
```

## Выходная структура
```
/newsfeed/
├── tech/
│   ├── index.json
│   └── 20260806_101709_Название_статьи.txt
├── ru/
│   ├── politics/
│   │   ├── index.json
│   │   └── 20260806_102421_Название_статьи.txt
│   ├── tech/
│   └── war/
└── .scraper_state.json
```

Каждый .txt файл содержит готовый к TTS текст: "Заголовок. Саммари статьи."

## Cron
Настроен на запуск каждый час через Hermes cron:
- Job ID: 4defbc023fda
- Schedule: every 60m
- Deliver: local