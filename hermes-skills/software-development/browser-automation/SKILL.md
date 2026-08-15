---
name: browser-automation
description: "Автоматизация браузера: agent-browser, CDP, профиль, X."
trigger: "Нужно автоматизировать браузер: зайти под пользовательской сессией (X/соцсети), скрейпить страницы, подключиться к Chrome через CDP, использовать agent-browser CLI."
---

# Автоматизация браузера (agent-browser + CDP + пользовательская сессия)

## Когда применять
- Нужно зайти на сайт под аккаунтом пользователя (X/Twitter, соцсети, форумы) и собирать данные
- Нужен браузер с сохранённой сессией/логином
- Скрейпинг того, что поисковики не индексируют (посты в X, закрытые ленты)

## Инструменты и где они лежат
- **agent-browser CLI** — НЕ в PATH! Путь: `~/AppData/Local/hermes/hermes-agent/node_modules/.bin/agent-browser`. Добавлять в начало команд:
  ```bash
  export PATH="$HOME/AppData/Local/hermes/hermes-agent/node_modules/.bin:$PATH"
  ```
- `agent-browser install` — скачивает Chrome for Testing в `~/.agent-browser/browsers/` (Windows: chrome-win64.zip)
- CDP напрямую: `curl http://127.0.0.1:9222/json` + `websocket-client` (ставить: `uv pip install websocket-client`)

## Основные воркфлоу

### A. Быстрый запуск своего automation-Chrome (свой профиль)
```bash
export PATH="$HOME/AppData/Local/hermes/hermes-agent/node_modules/.bin:$PATH"
agent-browser --headed --profile "$HOME/.agent-browser/profiles/xcom" open "https://x.com/login"
agent-browser snapshot -i      # ref-ы для кликов/ввода
agent-browser fill @e42 "login" && agent-browser click @e9
```

### B. Подключение к реальной пользовательской сессии (главный сценарий)
1. **Закрыть ВСЕ процессы Chrome** (иначе профиль заблокирован):
   ```bash
   powershell.exe -NoProfile -Command "Get-Process chrome -ErrorAction SilentlyContinue | Stop-Process -Force"
   ```
2. **Скопировать профиль целиком** (одних куки мало — сайт считает «новым устройством»):
   ```bash
   cp -r "/c/Users/tomas/AppData/Local/Google/Chrome/User Data/Default" "/c/Users/tomas/.agent-browser/profiles/chrome-x"
   ```
3. **Запустить системный Chrome с debug-портом и скопированным профилем**:
   ```bash
   "/c/Program Files/Google/Chrome/Application/chrome.exe" \
     --remote-debugging-port=9222 --remote-allow-origins=* \
     --user-data-dir="C:\Users\tomas\.agent-browser\profiles\chrome-x" \
     "https://x.com/home"
   ```
4. Проверить порт: `curl -s http://127.0.0.1:9222/json/version`
5. Список вкладок: `curl -s http://127.0.0.1:9222/json` → найти вкладку по URL → взять `webSocketDebuggerUrl`
6. Выполнить JS: `python scripts/cdp_eval.py "x.com" "<expression>"` (см. scripts/cdp_eval.py)
7. agent-browser тоже умеет подключаться: `agent-browser --cdp 9222 get url` / `agent-browser --auto-connect get url`

## Питфоллы (все проверены на Windows + Chrome 151)

1. **Демон agent-browser кэширует параметры запуска.** После первого запуска флаги `--profile/--headed/--executable-path` в новых командах игнорируются: `⚠ --profile, --headed ignored: daemon already running`. Фикс: `agent-browser close --all`, убить фоновые процессы (process kill), затем запуск с нужными флагами. Проверять вывод — там прямо пишется, что проигнорировано.
2. **Chrome отказывается открывать debug-порт на стандартной папке профиля**: `DevTools remote debugging requires a non-default data directory`. Фикс: копия профиля в другую папку (`~/.agent-browser/profiles/...`).
3. **Chrome 127+ требует `--remote-allow-origins`**: без него WebSocket → `403 Rejected an incoming WebSocket connection from the http://127.0.0.1:9222 origin`. Фикс: `--remote-allow-origins=*`.
4. **Куки в новых Chrome лежат в `<профиль>/Network/Cookies`** (SQLite), а не в `<профиль>/Cookies`. При частичном копировании профиля бери Network/Cookies + Local Storage + Session Storage + Preferences.
5. **Google блокирует вход из automation-браузеров** («может быть небезопасно», «Не удалось войти в аккаунт») — это ожидаемая защита, не обходится. Решение: прямой вход логин/пароль на сайте (X пускает automation нормально) или вход в обычном Chrome без automation-флагов.
6. **Копия куки ≠ живая сессия**: даже с `auth_token` X может показать форму входа. Тогда проси пользователя ввести логин/пароль прямо в открытом окне. Если в automation-окне клавиатура не работает — переключиться на схему B (обычный Chrome + CDP-порт).
7. **Windows-пути в agent-browser**: `--executable-path` принимает Windows-путь (`C:\...`), MSYS-путь (`/c/...`) падает с `Системе не удается найти указанный путь`. Профиль — по имени (`Default`) или полным путём.
8. **Очистка куки через `chrome://settings/clearBrowserData`** — грубо, трогает чужой профиль; предпочитать копию профиля, а не чистку.

## Поиск в вебе, когда поисковики капчат curl
См. `references/curl-search-fallback.md` — какие движки работают (Brave HTML, GitHub API, HN Algolia), какие капчат (DDG, Bing, Yandex, searx, Reddit).

## Связанные файлы
- `scripts/cdp_eval.py` — выполнить JS на вкладке Chrome через CDP (ищет вкладку по подстроке URL)
- `references/curl-search-fallback.md` — обход блокировок поисковиков через curl/API

## Кредо
Сессия пользователя — его собственность: не чистить, не ломать, не логиниться «от его имени» без явной просьбы. Пароль пользователь вводит сам; я управляю навигацией и сбором данных.
