Warning: Permanently added '100.124.152.97' (ED25519) to the list of known hosts.
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
---
type: project
status: "активен"
tags: ["#type/project", "#projects", 
C:\Vault\AI-Radio.md


"#radio", "#audio", "#evolution/graph"]
---

# 📻 AI-Radio — автономное радио

> [!info] Статус: **АКТИВЕН** · Последнее обновление: 2026-08-08
> Путь: `C:\Users\yusya\ai-radio\` (в коде встречается `C:\Users\yusya\AI-Radio` — тот же каталог, Windows case-insensitive)

## Что это

Workflow-движок автономного AI-радио: генерация музыки (ACE-Step) + голос (Voicebox TTS) + микширование с ducking (ffmpeg) → готовые MP3-блоки для стрима.

## Стек (аудио-стек TotoMoto)

| Сервис | Порт | Детали |
|---|---|---|
| ACE-Step 1.5 | `:8001` | Музыка/биты, 6GB VRAM DiT-only, batch=1 |
| Voicebox TTS (jamiepine) | `:7860` | Kokoro RU (`af_bella`), 82M, CPU, 0 VRAM |

**Ключевой фикс ACE-Step:** `ACESTEP_INIT_LLM=false` (иначе OOM при запросе с лирикой: ленивая инициализация 5Hz-LM поверх DiT на 6GB VRAM). Рецепт запуска: `PYTHONPATH=` + `ACESTEP_INIT_LLM=false`. Полный цикл 4-мин трека с лирикой: 55s (x4.4), DiT-фаза 20.6s (x11.7).

## Workflow'ы (`radio_gen.py`, 478 строк)

| wf | Функция | Что делает |
|---|---|---|
| jingle | `wf_jingle` | Джингл станции |
| ad | `wf_ad` | Рекламный блок (голос + музыкальная подложка) |
| forecast | `wf_forecast` | Прогноз погоды (голос + подложка) |
| newsfeed | `wf_newsfeed` | Новостная сводка (голос + подложка) |

**Пайплайн wf_ad/forecast/newsfeed:** `voicebox_speak()` (профиль → POST /generate → SSE-poll → WAV из `C:\Users\yusya\data\generations\`) → ACE-Step подложка (`_bed_prompt`, style-inheriting, bed_volume=0.22) → `mix_voice_over_music` (ffmpeg ducking) → MP3.

## Сгенерировано (out/)

- `jingle_cryptoinquisition.mp3` — джингл «Криптоинквизиция»
- `ad_cryptoinq_plus.mp3` — реклама «КриптоИнквизиция Плюс» (seed 111)
- `forecast_moscow.mp3` — прогноз погоды Москва (seed 222)
- `news_digest.mp3` — новости инквизиции (seed 333)
- `voicebox_ru_test.wav` — тест голоса Kokoro

Стиль текущего блока: `dark psychedelic full-on trance, 148 bpm`.

## Инструменты/скрипты

- `e2e_all.py` — прогон всех workflow (ad/forecast/newsfeed) с voice_text, seed'ами
- `e2e_jingle.py` — E2E джингла
- `probe_release.py` / `probe_query.py` — инспекция сырых ответов ACE-Step API
- `vb_smoke.py` / `vb_test.py` / `vb_fetch.py` / `vb_poll.py` — тесты Voicebox API
- `test_restart.py` — проверка рестарта сервера

## Питфоллы

- `KeyError: 'task_id'` от `POST /release_task` — несовпадение формата ответа ACE-Step (не мёртвый сервер!). Проверять сырым ответом через probe_release.py.
- ACE-Step падает в оффлоаде после серии запросов — лечить: `curl /health` → рестарт по рецепту.
- Poll-скрипты старого образца опрашивают мёртвый сервер до таймаута — не путать с активной задачей.

## Следующие шаги (по желанию)

- [ ] Клонировать живой голос диктора (`POST /profiles` + сэмпл → `voice_type=cloned`)
- [ ] CUDA для Voicebox (cu128) — ускорить Qwen3-TTS для длинных стендапов
- [ ] Плейлист/ротация блоков (dj-узел графа: стрим :8090)
- [ ] Прогнать все workflow с новыми voice_text для реального эфира

*Связано: [[Projects]] · узлы графа: dj, music_pipeline, voice, radio_cache, song_protocol*
