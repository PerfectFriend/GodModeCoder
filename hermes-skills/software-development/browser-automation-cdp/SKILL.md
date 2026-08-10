---
name: browser-automation-cdp
description: "Browser automation via CDP: login, fills, pitfalls."
trigger: "Нужно автоматизировать браузер: залогиниться на сайте (в т.ч. реальным Chrome-профилем пользователя), заполнять React-формы, скрейпить за логином, управлять браузером через CDP. Также: когда поисковики капчат curl."
---

# Browser automation via agent-browser + CDP

Проверенные рецепты управления браузером: agent-browser CLI, подключение к реальному Chrome пользователя через CDP, заполнение React-форм, обходы логин-стен.

## Быстрый старт (agent-browser)

- CLI живёт в Hermes: `export PATH="$HOME/AppData/Local/hermes/hermes-agent/node_modules/.bin:$PATH"`
- Первый раз: `agent-browser install` — качает Chrome for Testing (~192MB) в `~/.agent-browser/browsers`
- Открыть с окном и профилем: `agent-browser --headed --profile <abs-path> open <url>`
  - `--profile Default` = профиль реального Chrome юзера; путь = свой изолированный профиль
- `agent-browser snapshot -i` → ref'ы элементов; `fill @ref "text"`, `click @ref`
- Скрипты: `agent-browser eval <js>`, `agent-browser auth save/login`, `--session-name` для автосейва кук

### Питфоллы agent-browser
- **`⚠ --profile, --headed ignored: daemon already running`** — демон игнорирует новые флаги запуска, если сессия уже жива. ВСЕГДА `agent-browser close --all` перед перезапуском с другими параметрами. Это была главная засада сессии — старые фоновые процессы держали демон со старыми флагами.
- **MSYS-пути ломаются**: `--executable-path` ждёт нативный Windows-путь (`C:\Program Files\...`), не `/c/Program Files/...` (os error 3).
- Убить все Chrome: `powershell.exe -NoProfile -Command "Get-Process chrome -ErrorAction SilentlyContinue | Stop-Process -Force"` — без этого профиль заблокирован SingletonLock'ом.

## Рецепт: реальный Chrome + сессия пользователя через CDP

Цель: управлять браузером, где юзер уже залогинен (или логинить через настоящий Chrome), не перепечатывая пароли в automation-окно.

Ключевые факты:
1. **Chrome отказывается открывать remote-debugging на стандартном user-data-dir**: `DevTools remote debugging requires a non-default data directory.` → нужен свой `--user-data-dir`.
2. **Chrome 127+**: куки лежат в `Network/Cookies` (SQLite) внутри профиля, а не в корневом `Cookies`.
3. **Chrome 136+**: WebSocket CDP с origin `http://127.0.0.1:9222` получает 403 `Rejected an incoming WebSocket connection... Use --remote-allow-origins=*` → запускать с флагом.

Рабочая последовательность (проверена):
```
1. Закрыть весь Chrome (см. команду выше) — иначе профиль занят.
2. Скопировать профиль в нестандартную папку:
   cp -r "…/Google/Chrome/User Data/Default" "…/.agent-browser/profiles/chrome-x"
   (полная копия ~385MB надёжнее; минимум: Network/Cookies*, Local Storage,
    Session Storage, Preferences, Login Data*, Web Data*)
3. Запуск:
   chrome.exe --remote-debugging-port=9222 --remote-allow-origins=* \
     --user-data-dir="C:\…\profiles\chrome-x" "https://target.com"
4. Проверка: curl http://127.0.0.1:9222/json/version ; список вкладок — /json
5. Драйв через CDP WebSocket (python websocket-client, Runtime.evaluate).
```
Важно: скопированные куки могут не дать «уже залогинен» (сайт видит новое устройство и просит ре-авторизацию) — это нормально. Смысл рецепта: окно = настоящий Chrome, в который можно и вводить, и который я дёргаю через порт. auth_token из кук X переносится, но X всё равно может показать форму входа.

## Заполнение React-форм через CDP (native setter trick)

React игнорирует простое `el.value = ...` — нужен нативный сеттер + события:
```js
const setVal = (el, val) => {
  Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set.call(el, val);
  el.dispatchEvent(new Event('input', {bubbles: true}));
  el.dispatchEvent(new Event('change', {bubbles: true}));
};
```
Кликать кнопку по ТОЧНОМУ совпадению текста (`innerText.trim() === 'Продолжить'`), а не по regex — иначе поймаешь первую похожую (например «Вход с аккаунтом Google» вместо «Продолжить»).

## Логин-стены
- **Google OAuth в автоматизированном Chrome** → «Не удалось войти в аккаунт» (Google детектит automation; надёжного обхода нет). Использовать родную форму сайта (email/пароль), не кнопку Google.
- **X.com пускает automation** через прямую форму: email → «Продолжить» → пароль → иногда подтверждение аккаунта (запрос юзернейма) → код на email. Код приходит письмом — просить у юзера, вводить через CDP.
- **Если automation-окно глотает ввод с клавиатуры** — не просить юзера печатать, а всё делать через CDP `Runtime.evaluate`.

## Поиск, когда поисковики капчат curl
DDG html / Bing / Yandex / Searx → captcha/challenge для curl. **Brave HTML поиск работает**: `https://search.brave.com/search?q=...` (парсить `<a href>`). Детали: `references/web-search-fallback.md`.

## Уточнение языка/сообщества ДО поиска
Пользователь поправил: сначала искал английский термин, а нужен был русский; затем уточнил — публикации на английском в X.com в AI/код-сообществах. Урок: при запросе «поищи тему» уточнить язык и площадку (X/Reddit/Telegram/Habr) до старта.

## Файлы
- `references/web-search-fallback.md` — капча поисковиков + парсинг Brave HTML + флоу логина X.com (подробно)
