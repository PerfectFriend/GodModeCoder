# Web search fallback + X.com login flow (подробности сессии)

## Поисковики vs curl (проверено 2026-08)

| Поисковик | URL | Результат с curl |
|---|---|---|
| DuckDuckGo html | `https://html.duckduckgo.com/html/?q=...` | ❌ CAPTCHA (`anomaly`/`challenge` в HTML) |
| Bing | `https://www.bing.com/search?q=...` | ❌ CAPTCHA (нет `b_algo` результатов) |
| Yandex | `https://yandex.ru/search/?text=...` | ❌ CAPTCHA |
| Searx | `https://searx.be/search?q=...&format=json` | ❌ «Verifying your browser…» |
| Reddit JSON | `https://www.reddit.com/search.json?q=...` | ❌ 403 Blocked (без OAuth) |
| **Brave** | `https://search.brave.com/search?q=...` | ✅ **РАБОТАЕТ** — 100-200KB HTML с результатами |

**Brave — рабочий поисковик для curl.** Парсинг:
```python
import re, html
c = open('brave.html', encoding='utf-8', errors='ignore').read()
links = re.findall(r'<a[^>]*href="(https?://[^"]+)"[^>]*>(.*?)</a>', c, re.S)
# Фильтровать мусор: исключить brave.com, search.brave, /search?, google, bing
# Заголовок-«хлебные крошки»: "X x.com › mark_k › status › ..." + сам URL
```
- Запрос с `&tf=pd` — фильтр «past day», но работает слабо.
- `site:x.com` в запросе даёт ссылки на посты X (заголовок вида `X x.com › user › status › id`).

## GitHub API (без ключа)
- `https://api.github.com/search/repositories?q=...&sort=updated` — работает, rate limit 10/min.
- Русскоязычные термины в репо → 0 результатов, но по-английски искать надо отдельно.
- HN Algolia: `https://hn.algolia.com/api/v1/search_by_date?query=...` — работает, 0 hits если тема нишевая.

## Флоу логина X.com через CDP (проверено)

Прямая форма X (НЕ Google) работает в automation-браузере:

1. `https://x.com/login` → поля `input[name="username_or_email"]` + `input[type="password"]`
2. Заполнить через native setter (см. SKILL.md) → клик кнопки **«Продолжить»** по точному тексту
3. Если запросит подтверждение аккаунта: поле `input[name="challenge_response"]` — ввести **юзернейм без @** → «Продолжить»
4. Дальше: «Проверьте свою электронную почту» — код на email → `Verification code` → «Продолжить»
   - Таймер повтора письма ~19 сек, код живёт дольше
   - Код просить у юзера (он читает почту), вводить через CDP

## Логин через Google OAuth в automation — не пытаться
- Google: «Не удалось войти в аккаунт» / «может быть небезопасно» — детектит автоматизированный браузер.
- Даже с реальным профилем юзера (Chrome for Testing / CDP) — блок.
- Обход только через родную форму сайта.

## Куки Chrome 127+ (важно для переноса сессии)
- Файл кук: `<profile>/Network/Cookies` (SQLite), не `<profile>/Cookies`.
- В X: `auth_token` (103B), `ct0` (223B) в `.x.com` — но X всё равно может потребовать ре-вход на «новом устройстве».

## Ошибка Chrome про data directory
`DevTools remote debugging requires a non-default data directory` — Chrome 136+ отказывает в remote debugging на стандартном `User Data`. Нужен СВОЙ `--user-data-dir` (копия профиля).

## WebSocket CDP 403
`Rejected an incoming WebSocket connection from the http://127.0.0.1:9222 origin. Use --remote-allow-origins=*` — запускать Chrome с `--remote-allow-origins=*`.

## Python CDP-драйв (минимум)
```bash
uv pip install websocket-client
```
```python
import json, urllib.request, websocket
tabs = json.load(urllib.request.urlopen('http://127.0.0.1:9222/json'))
ws = [t['webSocketDebuggerUrl'] for t in tabs if 'x.com' in t.get('url','')][0]
w = websocket.create_connection(ws, timeout=15)
w.send(json.dumps({'id':1,'method':'Runtime.evaluate',
    'params':{'expression':'document.body.innerText','returnByValue':True}}))
# цикл: читать recv() пока msg['id']==1
```
