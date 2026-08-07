---
name: browser-cdp-automation
description: "Управляй Chrome по CDP: логины, веб-UI, генерация картинок."
trigger: "Нужно автоматизировать Chrome: залогиниться в веб-сервис (X, GitHub, Google AI, ChatGPT), вытащить данные/картинки из веб-UI, обойти API-квоты бесплатными веб-лимитами."
---

# Browser Automation via CDP (agent-browser + Chrome DevTools Protocol)

Проверенный рецепт (2026-08): логин в X.com, создание репозиториев GitHub, смена приватности, генерация изображений в Gemini/ChatGPT через веб-UI — всё через CDP с профилем пользователя.

## Стек

- **agent-browser CLI** (Windows): `$HOME/AppData/Local/hermes/hermes-agent/node_modules/.bin/agent-browser` — команды: `snapshot -i`, `get url/title`, `close --all`, `install`, `profiles`.
- **Chrome для тестов**: `agent-browser install` → `C:\Users\tomas\.agent-browser\browsers\chrome-<ver>`.
- **CDP из Python**: `uv pip install websocket-client`; вкладки: `http://127.0.0.1:9222/json` → поле `webSocketDebuggerUrl`; дальше `Runtime.evaluate`, `Input.insertText`, `Input.dispatchKeyEvent`, `Page.navigate`.

## Запуск Chrome с профилем пользователя (главный рецепт)

Chrome **отказывается** открывать remote debugging на стандартной папке профиля:
ошибка `DevTools remote debugging requires a non-default data directory`.
Решение — копия профиля в отдельную папку:

```bash
# 1. убить все Chrome
powershell.exe -NoProfile -Command "Get-Process chrome -EA SilentlyContinue | Stop-Process -Force"
# 2. скопировать профиль ЦЕЛИКОМ (только Cookies НЕ хватает — сессия живёт в десятках файлов)
cp -r "$LOCALAPPDATA/Google/Chrome/User Data/Default" "$HOME/.agent-browser/profiles/chrome-x"
# 3. запустить (Windows-пути, не /c/...!)
"/c/Program Files/Google/Chrome/Application/chrome.exe" \
  --remote-debugging-port=9222 --remote-allow-origins=* \
  --user-data-dir="C:\Users\tomas\.agent-browser\profiles\chrome-x" "https://target.site"
```

**Критично:** Chrome 151+ отклоняет WebSocket без `--remote-allow-origins=*`
(403 `Rejected an incoming WebSocket connection... Use --remote-allow-origins`).
Без него curl к `/json` отвечает, но коннект падает.

## agent-browser: один демон, один набор опций

- Повторные запуски с новыми `--profile / --headed / --executable-path` **игнорируются**: `⚠ --profile, --headed ignored: daemon already running`.
- Всегда: `agent-browser close --all` → затем **один** фоновый запуск с нужными опциями.
- `--auto-connect` находит только Chrome, запущенный **с** debug-портом; к обычному Chrome пользователя не подключится.
- `--executable-path` принимает Windows-путь (`C:\Program Files\...`), НЕ MSYS (`/c/Program Files/...` — os error 3).
- Быстрый осмотр вкладок: `curl -s http://127.0.0.1:9222/json` — там `title`, `url`, `webSocketDebuggerUrl`.

## Ввод текста в React/controlled-формы

JS-сеттер (`Object.getOwnPropertyDescriptor(proto,'value').set`) + `input` event **иногда не проходит**
(GitHub отклонил SSH-ключ: «Key is invalid»). Надёжный путь — имитация реального ввода:

```python
send('Runtime.evaluate', {'expression': 'document.querySelector("#field").focus(); true'})
send('Input.insertText', {'text': 'value'})
```

Всегда проверяй `el.value` после ввода, только потом жми кнопку.

## Логины: Google блокирует automation

- Google OAuth из автоматизированного Chrome: «Не удалось войти в аккаунт» / «may be unsafe». Это защита Google, не обходится.
- **Обход:** нативный логин сервиса. X.com пускает automation нормально: email/телефон → пароль → код. GitHub тоже.
- X при входе с нового устройства: сначала запрос **username**, потом **код на email** (поле `Verification code`).
- Кнопку «Продолжить» ищи по **точному тексту** (`=== 'Продолжить'`), не regex — иначе первым матчится «Вход с аккаунтом Google».

## Многошаговые диалоги (GitHub visibility как эталон)

DOM перечитывать **после каждого шага** — кнопки меняются:
`#visibility_menu-button` → `[data-show-dialog-id="visibility-menu-dialog-private"]`
→ «I want to make this repository private» → «I have read and understand these effects»
→ «Make this repository private».

Ошибка `You can't perform that action at this time` при создании репо — **транзиентная**:
заполни форму заново (клик по полю → `Input.insertText`), выбери radio, жми Create — повтор срабатывает.

## Извлечение сгенерированных картинок

- **Gemini (веб)** сам качает файл в `~/Downloads` → `Gemini_Generated_Image_*.png`.
- **ChatGPT**: картинка в `img[src*="estuary"]`, `naturalWidth > 1000` — fetch → base64 → сохранить:
```python
r = send('Runtime.evaluate', {'expression': '''(async () => {
  const i = [...document.querySelectorAll('img')].find(x => x.naturalWidth > 1000 && x.src.includes('estuary'));
  const b = await (await fetch(i.src)).blob(); const buf = await b.arrayBuffer();
  const u = new Uint8Array(buf); let s='';
  for (let k=0;k<u.length;k++) s += String.fromCharCode(u[k]);
  return {b64: btoa(s), mime: b.type, size: u.length}; })()''',
  'awaitPromise': True, 'returnByValue': True})
```
- `navigator.clipboard.readText()` без разрешения браузера → **пусто**; не полагайся на буфер.

## Бесплатная генерация изображений при исчерпанных API

API-ключи часто мертвы (Gemini 429, Pollinations `Insufficient balance`, HF ZeroGPU `0s left`),
но **веб-UI имеет отдельные бесплатные лимиты**: логин в `gemini.google.com` / `chatgpt.com`
через CDP-браузер → промпт в `.ql-editor` (Gemini) или `#prompt-textarea` (ChatGPT) →
Enter → ждать 60–120 с → скачать. Подробности: `references/free-ai-image-generation.md`.

## Поиск трендов в X из залогиненного браузера

URL поиска: `https://x.com/search?q=<query>&src=typed_query&f=live` (`f=live` свежие, `f=image` медиа).
Посты: `document.querySelectorAll('article')` → `innerText`, `time[datetime]`, `a[href*="/status/"]`.
Подробности и найденная терминология: `references/x-search-research.md`.

## Питфоллы

- **git-bash `$TEMP` → `C:\tmp` (не существует!)**: временные py-скрипты пиши через `write_file` с явным путём `C:\Users\tomas\AppData\Local\Temp\hermes-verify-*.py`, а не через heredoc в `$TEMP`.
- Python не открывает MSYS-пути (`/tmp/...`); только `C:\...`.
- Проверяй состояние после каждого шага (get url / snapshot / Runtime.evaluate) — без подтверждений CDP-скрипты слепнут и жмут не те кнопки.
- Долгая генерация: не выходи из цикла по первому таймауту — Gemini ~45–75 с, ChatGPT ~2 мин на картинку.
