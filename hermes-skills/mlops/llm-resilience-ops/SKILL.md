---
name: llm-resilience-ops
description: Use when minimizing downtime from provider/model failures.
---

# LLM Resilience Ops — минимизация простоев из-за отказов провайдера/модели

Цель: LLM-сервис (Hermes gateway, радио-генерация, любой агент на OpenAI-совместимых API) должен переживать отказы отдельных ключей, моделей и провайдеров без простоя.

## 1. Архитектура устойчивости (4 слоя)

1. **Пулы ключей с ротацией** — несколько ключей на провайдера (free-tier: nvidia 6, opencode-zen 12, gemini 2, kilocode 1, groq, openai). Один мёртвый/квотированный ключ не останавливает сервис.
2. **Провайдер-фолбэк** — `aliases` в config.yaml: один логический провайдер, за ним цепочка реальных (nvidia → opencode-zen → groq → ...). Падение модели/провайдера = переключение на следующий.
3. **Мониторинг (watchdog)** — регулярный крон-пробинг всех ключей реальными запросами + автосброс устаревших статусов (см. раздел 4).
4. **Диагностика конфига** — base_url/провайдер обязаны совпадать, иначе фантомные 401 (см. раздел 3).

## 2. Правильная проверка ключей (критично!)

- **Только `POST {base_url}/v1/chat/completions`** с `max_tokens=5`. `GET /v1/models` — ловушка: многие провайдеры (opencode, OpenRouter) отдают 200 даже с чужим/пустым ключом.
- **Всегда браузерный User-Agent**: `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36`. Cloudflare режет дефолтный urllib-UA (error 1010) → ложные 403 у всех ключей провайдера.
- **Классификация ответов:**
  - `200` + completion → ключ жив (проверять `cost: 0` у фритайеров).
  - `401/403` → ключ мёртв/не тот провайдер.
  - `429 quota exceeded` / `insufficient_quota` → ключ ВАЛИДЕН, но лимит/баланс исчерпан — НЕ удалять, оставить в ротации.
  - `429 rate_limit` / `503` / таймаут → транзиентная перегрузка (NIM: `Worker local total request limit reached`) — ретрай, не смерть.
- **Ретрай на таймауты**: 1 повтор через тот же эндпоинт, прежде чем считать ключ проблемным.

## 3. Диагностика фантомных 401 (рассинхрон base_url)

Симптом: `hermes auth list` показывает `exhausted (401)` у ключей, которые живой пробой дают 200; пул бессмысленно ротирует.

Причина: `model.base_url` в config.yaml указывает на ДРУГОЙ провайдер, чем пул ключей (реальный случай: `provider: nvidia` + `base_url: https://openrouter.ai/api/v1`). Каждый свежий клиент сначала бьётся об openrouter с nvapi-ключом → 401 → ключ метится exhausted → ротация → второй клиент уже с правильным base_url и работает.

Проверка (gateway.log):
```
grep -E "client created.*base_url|marking .*exhausted|rotating" logs/gateway.log
```
Лечение: `hermes config set model.base_url <реальный эндпоинт пула>` (nvidia NIM: `https://integrate.api.nvidia.com/v1`).

## 4. Watchdog: крон-пробинг + автосброс статусов

Референс-скрипт: `C:\Users\tomas\AppData\Local\hermes\scripts\key_watchdog.py` (клон под свой home при необходимости).

Логика:
- Читает `auth.json` (пулы) + `.env` (отдельные ключи: GROQ, OPENAI, ...).
- Пробивает каждый ключ (раздел 2), параллельно (6 воркеров), с ретраем.
- **Автосброс устаревших статусов:** если проба дала 200, а в auth.json у ключа `last_status: exhausted` → `hermes auth reset <provider>`.
- Детектит дубли (одинаковые суффиксы ключей в пуле) и мёртвые ключи.
- **Тишина = здоровье:** при полном порядке — пустой stdout (no_agent-крон молчит); отчёт только при проблемах.

Крон (no_agent=true, script-only):
```
cronjob action=create name="LLM Key Watchdog" schedule="every 6h" \
  no_agent=true script="key_watchdog.py" deliver=origin
```
Скрипт обязан лежать в `<home>/scripts/`; в крон передаётся только имя файла.

## 5. Питфолл: gateway держит пул в памяти

- Gateway (`hermes gateway run`) кеширует credential pool в памяти и **перезаписывает auth.json** при событиях пула (ротация, маркировка exhausted) — CLI-правки (`hermes auth remove/reset`) затираются.
- **Рестарт gateway изнутри его процесса заблокирован** (SIGTERM дочерним процессам) — только извне:
  - Windows: `schtasks /create /tn HermesGatewayRestart /tr "\"<hermes.exe>\" gateway restart" /sc once /st HH:MM /f` (MSYS_NO_PATHCONV=1 в git-bash), либо отдельный терминал.
  - После рестарта gateway загружает чистое состояние с диска.
- Проверка: `hermes gateway status` → `✓ Gateway process running (PID ...)`.

## 6. Проверка результата

- `hermes auth list` — статусы чистые у ключей, что дают 200 пробой.
- `cronjob action=list` — watchdog `last_status: ok`.
- `logs/gateway.log` — нет строк `marking .* exhausted (status=401)` без причины.
- Реальный сценарий: остановить один ключ → сервис продолжает работать через ротацию.
