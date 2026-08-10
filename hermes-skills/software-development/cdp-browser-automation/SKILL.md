---
name: cdp-browser-automation
description: "CDP Chrome: вход в X через копию профиля, без блокировок."
trigger: "Вход в X/сайт с логином из терминала: CDP Chrome, копия профиля, обход блокировок Google и automation."
---

# CDP-автоматизация Chrome: логин и ресёрч (X, сайты с аккаунтом)

## Когда использовать
- Нужно зайти в X.com / другой сайт с логином и искать/читать из терминала
- Окно automation-браузера блокирует клавиатуру, Google режет OAuth, сайт требует подтверждение аккаунта
- Нужна своя сессия (куки) без ручного ввода

## Инструменты
- agent-browser CLI: `export PATH="$HOME/AppData/Local/hermes/hermes-agent/node_modules/.bin:$PATH"` (лежит в node_modules hermes-agent, а не в PATH)
- Первая установка Chrome: `agent-browser install` (качает Chrome в `~/.agent-browser/browsers/`)
- CDP-клиент: `uv pip install websocket-client` (Python)

## Проверенный рецепт (порядок важен)

1. **Убить всё старое**: `agent-browser close --all`, затем `powershell.exe -NoProfile -Command "Get-Process chrome -ErrorAction SilentlyContinue | Stop-Process -Force"`.
   Демон agent-browser **кэширует параметры запуска**: если он уже жив, новые `--profile/--headed/--executable-path` молча игнорируются (`⚠ ... ignored: daemon already running`). Всегда `close --all` перед перезапуском с новыми опциями.

2. **Скопировать профиль в НЕстандартную папку** — Chrome отказывается открывать remote-debugging на дефолтной user-data-dir (`DevTools remote debugging requires a non-default data directory`):
   ```
   cp -r "$LOCALAPPDATA/Google/Chrome/User Data/Default" ~/.agent-browser/profiles/chrome-x
   ```
   Полная копия (~385MB) надёжнее частичной. Куки в новых Chrome лежат в `Network/Cookies`, не в корне профиля.

3. **Запустить системный Chrome с debug-портом**:
   ```
   chrome.exe --remote-debugging-port=9222 --remote-allow-origins=* \
     --user-data-dir="C:\Users\tomas\.agent-browser\profiles\chrome-x" <url>
   ```
   `--remote-allow-origins=*` **обязателен** на Chrome ≥111, иначе CDP WebSocket отвечает 403 (`Rejected an incoming WebSocket connection...`). Проверка: `curl http://127.0.0.1:9222/json/version`.

4. **Подключиться по CDP** (Python websocket-client): GET `http://127.0.0.1:9222/json` → выбрать вкладку с сайтом → `webSocketDebuggerUrl` → `Runtime.evaluate` с `returnByValue: True`. Скрипт-помощник: см. `references/xcom-cdp-login.md`.

5. **React-формы заполнять нативно** — простой `el.value = x` React игнорирует:
   ```js
   Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(el, val);
   el.dispatchEvent(new Event('input',{bubbles:true}));
   el.dispatchEvent(new Event('change',{bubbles:true}));
   ```

6. **Если setter-метод вставил артефакты JSON-экранирования** (значение пришло с лишними кавычками/бэкслешами — например GitHub ругается «Key is invalid. You must supply a key in OpenSSH public key format» после вставки SSH-ключа через `%r % json.dumps(key)` в JS-строку) — переключиться на **`Input.insertText`** (реальные клавиши, чистое значение):
   ```python
   send("Runtime.evaluate", {"expression": "document.querySelector('#field').focus()"})
   send("Input.insertText", {"text": value})   # без JSON-экранирования
   ```
   Этот способ надёжнее для значений со спецсимволами (`#`, `@`, пробелы).

6. **Google-кнопки не трогать**: Google блокирует OAuth-вход из автоматизированного Chrome («Не удалось войти в аккаунт»). Всегда нативный логин сайта (email/пароль), не «Войти с Google».

7. **Клавиатура в automation-окне может не работать** — не заставлять пользователя печатать, вводить через CDP.

## Питфоллы
- Скопированная сессия может не подхватиться сразу (сайт детектит «новое устройство») — это нормально: пройти верификацию один раз, дальше куки живут.
- Не чистить куки профиля в отчаянии — это разрушает исходную сессию пользователя.
- Порядок: закрыл Chrome → скопировал профиль → запустил с портом. Если Chrome уже запущен с тем же user-data-dir, флаг порта молча игнорируется.
- **curl к поисковикам почти всегда капчит** (Google, Bing, DDG, Yandex, Searx — все отдают CAPTCHA/аномалию на curl). Brave search (`search.brave.com/search?q=...&tf=pd`) отдаёт парсибельный HTML без капчи — его ссылки можно вытаскивать regex'ом, если нужен быстрый web-ресёрч без браузера.
- **Язык источников**: для ресёрча X-трендов пользователь хочет англоязычные посты из AI/код-сообществ — искать на английском, не переводить запросы (correction из сессии: «ищи источники на английском языке»).
- Уведомления `[IMPORTANT: Background process ... completed]` — это завершившиеся старые фоновые запуски Chrome; не перезапускать всё подряд, сначала проверить текущее состояние через `get url` / `curl /json`.

## GitHub-автоматизация через CDP (проверено в бою)

Тот же CDP-рецепт работает для GitHub: создание репозитория, добавление SSH-ключа, смена приватности — всё через `Runtime.evaluate` + `Input.insertText`. Ключевые детали:

- **Создание репо** (`github.com/new`): поле имени — `#repository-name-input`, описание — `[id="_r_c_"]`. ВАЖНО: `Input.insertText` вставляет в элемент с фокусом — сначала явно `focus()` на нужное поле, иначе значение уедет в соседнее (в сессии описание влетело в поле имени). Кнопка `Create repository` ищется по тексту. Ошибка «You can't perform that action at this time» может быть транзиентной — перезагрузить страницу и заполнить заново.
- **SSH-ключ** (`github.com/settings/ssh/new`): title — `#ssh_key_title`, key — `#ssh_key_key`. Значения со спецсимволами (`#`, пробелы, `+`) вставлять ТОЛЬКО через `Input.insertText`, не через JS-setter с `json.dumps` — иначе GitHub отклоняет («Key is invalid. You must supply a key in OpenSSH public key format»).
- **Смена приватности** (`/settings` → Danger Zone): меню-кнопка `#visibility_menu-button` → пункт `[data-show-dialog-id="visibility-menu-dialog-private"]` → кнопка «I have read and understand these effects» → финальная «Make this repository private». Проверка: в `/settings` текст «This repository is currently private.»
- После добавления ключа: `ssh -T git@github.com` → «Hi <user>! You've successfully authenticated» — и можно пушить.

## Файлы
- `references/xcom-cdp-login.md` — вход в X пошагово + паттерны поиска (без кавычек, f=live/f=image) + скрипт-заготовка
- `references/graph-engineering-x-research.md` — дайджест тренда Graph Engineering (loop vs graph vs harness), найденного через этот рецепт
- `references/github-cdp-automation.md` — GitHub: создание репо, SSH-ключ, смена приватности (полный флоу)
- `scripts/cdp_helper.py` — переиспользуемый CDP-помощник (eval / fill / insert_text / click_button / navigate)
