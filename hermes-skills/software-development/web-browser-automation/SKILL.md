---
name: web-browser-automation
description: "Браузер-автоматизация: agent-browser/CDP, логины, поиск."
trigger: "Нужно автоматизировать веб: войти в аккаунт, искать в соцсетях, генерировать картинки через веб-UI, управлять GitHub в браузере — когда API недоступен/заблокирован, а веб-интерфейс работает."
---

# Web Browser Automation (agent-browser + CDP)

Драйв любых веб-сайтов через `agent-browser` CLI + CDP websocket: повторное использование
логина пользователя (профили), поиск в соцсетях, генерация изображений через бесплатные
веб-UI (Gemini/ChatGPT), операции с GitHub UI. Применяется, когда API ключи
заблокированы/исчерпаны, а веб-интерфейс имеет отдельные бесплатные лимиты.

## Установка и запуск

```bash
# agent-browser живёт в node_modules Hermes:
export PATH="$HOME/AppData/Local/hermes/hermes-agent/node_modules/.bin:$PATH"
agent-browser install            # ставит Chrome for Testing
# Запуск с профилем пользователя (headed — видимое окно для логина):
agent-browser --headed --executable-path "C:\Program Files\Google\Chrome\Application\chrome.exe" --profile Default open URL
```

**КРИТИЧЕСКИЙ pitfall (демон):** старые фоновые процессы держат демон со старыми
параметрами — новые `--profile/--headed/--executable-path` молча игнорируются
(«ignored: daemon already running»). Лечение:
1. `process kill` для ВСЕХ старых фоновых процессов agent-browser
2. `agent-browser close --all`
3. убить chrome.exe (`powershell Stop-Process chrome -Force`)
4. запустить ОДИН чистый процесс с нужными параметрами

## Повторное использование логина (профили)

- `--profile Default` переиспользует куки Chrome, но требует **полностью закрытый Chrome** (иначе профиль заблокирован).
- Chrome 151 **отказывается** открывать remote debugging со стандартным `--user-data-dir`
  («DevTools remote debugging requires a non-default data directory») → **копируй профиль**:
  `cp -r "AppData/Local/Google/Chrome/User Data/Default" ~/.agent-browser/profiles/chrome-x`
  (в новых Chrome куки лежат в `Default/Network/Cookies`, не на верхнем уровне).
- Для WebSocket-подключений нужен `--remote-allow-origins=*`, иначе 403
  («Rejected an incoming WebSocket connection»).
- Полный цикл: убить chrome → запустить
  `chrome.exe --remote-debugging-port=9222 --remote-allow-origins=* --user-data-dir=<копия> URL`
  → подключиться по CDP.

## CDP-драйв (python websocket-client)

```python
import json, urllib.request, websocket
tabs = json.load(urllib.request.urlopen('http://127.0.0.1:9222/json'))
ws = [t['webSocketDebuggerUrl'] for t in tabs if 'site.com' in t.get('url','')][0]
w = websocket.create_connection(ws, timeout=25)
w.send(json.dumps({'id':1,'method':'Runtime.evaluate',
  'params':{'expression':'document.body.innerText','returnByValue':True}}))
# awaitPromise=True для async-выражений (fetch, clipboard)
```

Паттерны:
- **Навигация:** `Page.navigate {url}` затем `sleep 6-10` (SPA грузятся долго).
- **Надёжный ввод текста:** `Input.insertText` (имитирует реальный ввод) — НЕ полагайся
  только на Runtime-сеттер: React-формы (GitHub) выдавали «Key is invalid» при setter-вводе,
  а insertText срабатывал. Для React-инпутов: setter + `input`/`change` события.
- **Очистка поля:** focus → `Input.dispatchKeyEvent` Ctrl+A (`modifiers: 2`) → Delete.
- **Скачивание сгенерированных картинок:** `fetch(blobUrl)` → arrayBuffer → b64 через CDP;
  либо проверь `~/Downloads` — **Gemini сам скачивает** файл (`Gemini_Generated_Image_*.png`).
- **Скриншот/состояние:** `document.querySelectorAll('article')`, `img.naturalWidth`,
  `document.body.innerText` — быстрые проверки, что контент загрузился.

## Питфоллы

- **Google блокирует OAuth-вход из automation-браузера** («может быть небезопасно»,
  «Не удалось войти в аккаунт»). Обход: используй нативный логин сайта (X: email+пароль),
  а не «Continue with Google».
- **Поиск X:** без кавычек в запросе; `&f=live` для свежих постов; посты —
  `querySelectorAll('article')`, ссылки `a[href*="/status/"]`.
- **GitHub UI:** создание репо — клик по `#repository-name-input` + insertText, кнопка Create
  может требовать повторного клика; переключение приватности — многошаговый диалог
  (см. references/site-recipes.md).
- **Vision-инструмент может быть недоступен** — анализируй картинки по метрикам PIL
  (яркость, контраст, топ-цвета), а не глазами.

## Support files

- `references/free-ai-image-generation.md` — бесплатная генерация изображений через веб-UI (Gemini/ChatGPT), когда API-пути исчерпаны.
- `references/site-recipes.md` — готовые рецепты: поиск X, GitHub UI (репо/SSH-ключ/приватность), копирование профиля для логина.
