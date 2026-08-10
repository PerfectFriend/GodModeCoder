---
name: windows-chrome-cdp
description: "Автоматизация Chrome через CDP: порт, профиль, WebSocket."
trigger: "Нужно автоматизировать браузер (X.com, сайты с логином) через CDP на Windows — открыть debug-порт, скопировать профиль, подключиться по WebSocket."
---

# Windows Chrome CDP Automation

Проверенный рабочий путь автоматизации Chrome на Windows (git-bash/MSYS) через Chrome DevTools Protocol, включая работу с залогиненными сессиями (X.com и т.п.).

## Ключевые грабли (обязательно к прочтению)

1. **Google OAuth блокирует вход из automation-браузера** («Не удалось войти в аккаунт», «может быть небезопасно»). Это защита Google, обхода нет. X.com (и большинство сайтов) пускают нормально — входи через email/пароль, не через Google.
2. **Chrome отказывает в remote debugging со стандартным профилем**: `DevTools remote debugging requires a non-default data directory. Specify this using --user-data-dir.` → нужна **копия** профиля в отдельной папке.
3. **Chrome 151+ требует `--remote-allow-origins=*`** — иначе WebSocket-подключение отклоняется: `Rejected an incoming WebSocket connection from the http://127.0.0.1:9222 origin`.
4. **agent-browser (CLI Hermes)**: бинарник в `~/AppData/Local/hermes/hermes-agent/node_modules/.bin/` (добавить в PATH). Флаги `--headed/--profile/--executable-path` **игнорируются**, если демон уже запущен — сначала `agent-browser close --all`.
5. Пока Chrome запущен, профиль заблокирован — второй процесс не возьмёт его. Убивать: `powershell.exe -NoProfile -Command "Get-Process chrome -ErrorAction SilentlyContinue | Stop-Process -Force"`.

## Рабочий рецепт (X.com с залогиненной сессией)

### 1. Скопировать профиль (куки переносятся)
```bash
SRC="/c/Users/tomas/AppData/Local/Google/Chrome/User Data/Default"
DST="/c/Users/tomas/.agent-browser/profiles/chrome-x"
# Стоп Chrome, потом:
rm -rf "$DST"/* && cp -r "$SRC"/* "$DST/"
```
Куки в новых Chrome: `$SRC/Network/Cookies` (SQLite). Полная копия профиля (~385MB) переносит и auth_token X.com.

### 2. Запустить Chrome с debug-портом
```bash
"/c/Program Files/Google/Chrome/Application/chrome.exe" \
  --remote-debugging-port=9222 --remote-allow-origins=* \
  --user-data-dir="C:\Users\tomas\.agent-browser\profiles\chrome-x" \
  "https://x.com/home"   # в фоне (background=true)
```

### 3. Проверить порт
```bash
curl -s http://127.0.0.1:9222/json/version   # работает → JSON с Browser
curl -s http://127.0.0.1:9222/json           # список вкладок
```

### 4. Подключиться через WebSocket (python websocket-client)
```python
import json, urllib.request, websocket
tabs = json.load(urllib.request.urlopen('http://127.0.0.1:9222/json'))
ws_url = next(t['webSocketDebuggerUrl'] for t in tabs if 'x.com' in t.get('url','') and 'blob' not in t['url'] and 'accounts.google' not in t['url'])
w = websocket.create_connection(ws_url, timeout=15)
w.send(json.dumps({'id':1,'method':'Runtime.evaluate','params':{'expression':'document.body.innerText.slice(0,500)','returnByValue':True}}))
print(json.loads(w.recv())['result']['result']['value'])
```
Установка: `uv pip install websocket-client` (уже стоит в venv Hermes).

### 5. Логин в X (если сессия не подхватилась)
- Если копия профиля не залогинила — X покажет форму входа (это НЕ automation-браузер, клавиатура работает).
- Вводить логин/пароль можно через CDP: найти поле `Runtime.evaluate` → `document.querySelector(...).value=...` + dispatchEvent, или просто попросить юзера ввести в окне.
- НЕ через Google-кнопку (п.1 граблей).

### 6. Проверка залогиненности X
```js
!!document.querySelector('[data-testid="loginButton"]') // false = залогинен
!!document.querySelector('[data-testid="sidebarColumn"]')
```

## Альтернатива: agent-browser CLI (для обычных сайтов без Google)
```bash
export PATH="$HOME/AppData/Local/hermes/hermes-agent/node_modules/.bin:$PATH"
agent-browser close --all          # обязательно, иначе флаги игнорируются
agent-browser --headed --profile Default open https://example.com
agent-browser snapshot -i
agent-browser fill @e1 "text"
```
`--cdp 9222` — подключиться к уже запущенному Chrome.

## Полезное
- Поиск через curl: Google/Bing/DDG/Yandex/Searx — все капча/блок. Работает: **Brave search** (`search.brave.com/search?q=...`) и Mojeek; API GitHub/Reddit/HN (Algolia) без ключа, но Reddit блокирует с Windows-IP.
- X.com куки в копии профиля проверяются: `sqlite3 .../Network/Cookies "SELECT host_key,name FROM cookies WHERE host_key LIKE '%x.com%'"`.

## GitHub Automation через CDP (НОВОЕ — из сессии 2026-08-06)

### Особенности GitHub (Turbo SPA)
GitHub использует **Turbo** (Hotwire) — SPA фреймворк, который перехватывает навигацию и отправку форм. Это ломает стандартные подходы:

1. **Формы не сразу доступны после навигации** — Turbo загружает контент асинхронно. Нужно ждать `Turbo.ready` или долгое ожидание.
2. **`form.submit()` может не сработать** — Turbo перехватывает submit. Работает: `form.requestSubmit(submitter)` или клик по кнопке.
3. **`data-turbo="false"` на форме** — отключает Turbo для конкретной формы.
4. **Форма set_visibility** — находится на `/settings`, action=`/settings/set_visibility`, требует `authenticity_token` + `visibility=private`.

### Рабочий рецепт: Сделать репозиторий приватным

```python
# 1. Навигируй на страницу настроек
ws.send(json.dumps({'id': 1, 'method': 'Page.navigate', 'params': {'url': 'https://github.com/ORG/REPO/settings'}}))
time.sleep(8)  # Жди полной загрузки + Turbo

# 2. Жди Turbo ready
while True:
    result = ws.send_eval('Turbo && Turbo.session && Turbo.session.drive ? "ready" : "not ready"')
    if 'ready' in result: break
    time.sleep(1)

# 3. Найди форму set_visibility и сабмить с visibility=private
ws.send_eval('''
const forms = document.querySelectorAll("form");
for(const form of forms) {
    if(form.action && form.action.includes("set_visibility")) {
        const fd = new FormData(form);
        fd.append("visibility", "private");
        form.requestSubmit ? form.requestSubmit(form.querySelector("button[type=submit]")) : form.submit();
        return "submitted";
    }
}
return "not found";
''')

# 4. Жди завершения (Turbo навигация)
time.sleep(5)

# 5. Проверь на странице репо
ws.send(json.dumps({'id': 2, 'method': 'Page.navigate', 'params': {'url': 'https://github.com/ORG/REPO'}}))
time.sleep(3)
# Проверь что "Public" сменилось на "Private"
```

### Паттерны для форм на GitHub
- **Всегда жди Turbo ready** после навигации
- **Используй `form.requestSubmit(submitter)`** вместо `form.submit()`
- **Добавляй скрытые поля через `FormData` + `form.append()`** перед сабмитом
- **Кнопка сабмита нужна для `requestSubmit`** — передай `form.querySelector("button[type=submit]")`
- **`data-turbo="false"` на форме** — если хочешь полностью отключить Turbo для этой формы

### Диалоги (Danger Zone → Change visibility)
Если форма не сабмитится (Turbo перехватывает), работай через UI:
1. Кликни "Change visibility" (кнопка `Button--danger`)
2. В модалке кликни "Change to private" (класс `ActionListContent`)
3. Кликни "I want to make this repository private" (класс `js-repo-visibility-proceed-button`)

### Извлечение куков для API
```python
# Получить все куки через CDP
ws.send(json.dumps({'id': 1, 'method': 'Network.getAllCookies', 'params': {}}))
# Отфильтровать github.com
# Использовать в requests.Session() для API
```

### Типичные ошибки и фиксы
| Ошибка | Причина | Фикс |
|---|---|---|
| "form not found" | Turbo ещё не загрузил форму | Увеличь wait, жди Turbo.ready |
| "submitted but still public" | Turbo перехватил, навигация не завершилась | Жди дольше после сабмита, проверяй репо-страницу |
| "401 на API" | Куки не подходят для REST API | Используй browser automation, не API |
| "dialog not found" | Диалог не открылся | Кликни кнопку открытия, жди 2-3 сек |
