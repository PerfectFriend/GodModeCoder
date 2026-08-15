---
name: social-web-research
description: "Тренды в соцсетях: поиск, X.com через agent-browser."
trigger: "Нужно изучить свежие публикации/тренд в соцсетях (X, Reddit, Telegram) или вебе за последние дни/недели."
---

# Исследование трендов в соцсетях и вебе

Как находить свежие публикации по теме в соцсетях и на вебе, когда обычные поисковики капчатся, а X.com требует логина.

## 0. Первый шаг — язык и площадки (спрашивай у юзера!)

- **Уточни язык источников.** Юзер правил: для tech/AI-тем ищется **на английском** (публикации в X.com, AI/код-сообществах), русский — не по умолчанию. Поиск на неверном языке = пустые результаты и потерянное время.
- Уточни, где искать: X.com, Reddit, Telegram, Habr, блоги, arXiv.
- «За последние дни» = фильтры по дате в каждом движке (см. ниже).

## 1. Поиск через curl (когда браузер не нужен)

Матрица доступности (проверено авг 2026):

| Движок | curl | Статус |
|---|---|---|
| **Brave Search** | ✅ работает | `search.brave.com/search?q=...&tf=pd` — единственный живой веб-поиск без капчи |
| **GitHub API** | ✅ | `api.github.com/search/repositories?q=...&sort=updated` |
| **HN Algolia API** | ✅ | `hn.algolia.com/api/v1/search_by_date?query=...&tags=story` |
| DuckDuckGo html | ❌ | капча (anomaly/challenge) |
| Yandex | ❌ | капча |
| Google | ❌ | капча / блок |
| Habr search | ❌ | капча (но сами статьи скачиваются: `habr.com/ru/articles/<id>/`) |
| Reddit JSON | ❌ | HTTP 403 Blocked |
| SearX инстансы | ❌ | капча |

**Brave — рабочий рецепт:**
```bash
curl -s -L -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36" \
  "https://search.brave.com/search?q=%22exact+phrase%22+keyword&tf=pd" -o out.html
```
- `tf=pd` = past day, `tf=w` = past week, `tf=m` = past month.
- Точная фраза в `%22...%22` (кавычки URL-encode).
- Парсить: `re.findall(r'<a[^>]*href="(https?://[^"]+)"[^>]*>(.*?)</a>', html, re.S)` → отфильтровать ссылки на brave.com/search/hackerone.
- Сниппеты: заголовки в `<a ...>` блоках; для site:x.com — фильтровать href по `x.com/` или `twitter`.

## 2. X.com через agent-browser (требуется логин юзера)

X API почти всегда заблокирован (у юзера ключи отозваны) → автоматизация через браузер с профилем юзера.

### 2.1 Бинарник (НЕ в PATH)
```bash
export PATH="$HOME/AppData/Local/hermes/hermes-agent/node_modules/.bin:$PATH"
agent-browser install   # качает Chrome for Testing (~192MB) в ~/.agent-browser/browsers/
```

### 2.2 Запуск с видимым окном и профилем
```bash
# ВАЖНО: --profile требует ПОЛНЫЙ путь к директории, не имя!
mkdir -p ~/.agent-browser/profiles/xcom
agent-browser --headed --profile "$HOME/.agent-browser/profiles/xcom" open "https://x.com/home"
```
- `--headed` = видимое окно (юзер логинится сам; пароли не просим — это его аккаунт).
- `--profile <полный путь>` — изолированный профиль; логин переживает рестарты.
- `--session-name <name>` — автосохранение/восстановление сессии.
- `open` блокирует терминал → запускать с `background=true` + `notify_on_complete`.

### 2.3 Логин юзера
- **Google OAuth блокирует automation-Chrome** («может быть небезопасно») — юзер должен входить **родным логином X** (телефон/почта + пароль + 2FA), а НЕ через Google-кнопку.
- Юзер логинится сам в открытом окне → ждём «готово» → дальше работаем: `agent-browser open "https://x.com/search?q=<query>&f=live"`, `snapshot -i`, клики, скролл.

### 2.4 Поиск по X — запросы БЕЗ кавычек

- **Кавычки в X-поиске ломают выдачу**: `q="graph ai"` → «No results for "..."». Только голые слова: `q=graph ai`.
- **Короткие запросы лучше длинных** (юзер правил: «пиши graph ai и всё этого хватит»): одно-два слова, не фразы.
- `f=live` — свежие (Latest); без него — Top. `f=image` — только посты с картинками (диаграммы/схемы — золото для изучения трендов).
- После `Page.navigate` — sleep 8–10 с (SPA грузится), затем извлекать посты: `article` → `a[href*="/status/"]` → `time[datetime]`.
- Термин юзера может быть новоязом сообщества — искать и его, и вариации (`graph evolution`, `graph engineering`, `self-evolving graphs`).

### 2.5 Если agent-browser не может прицепиться (копия профиля + системный Chrome)

Когда agent-browser с `--profile Default` упирается в Chrome lock / OAuth-редирект / клавиатура в automation-окне не работает — проверенный обход: **копия профиля в НЕстандартную папку + системный Chrome с CDP-портом**. Chrome отказывается открывать remote-debugging на дефолтной user-data-dir (`DevTools remote debugging requires a non-default data directory`), а Chrome ≥111 требует `--remote-allow-origins=*` (иначе CDP WebSocket → 403). Полный рецепт и скрипт-заготовка: скиллы `cdp-browser-automation` (+ `references/xcom-cdp-login.md`) и `windows-chrome-cdp`.
- CDP-клиент: `uv pip install websocket-client`; подключение через `Runtime.evaluate` c `returnByValue: True`.
- React-поля заполнять нативно (простой `el.value=x` React игнорирует): `Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(el,val)` + `dispatchEvent(new Event('input'/'change',{bubbles:true}))`.
- Если юзер предложил дать логин/пароль и попросил залогиниться самому — можно через CDP, но сначала предложить родной вход (пароль в чате = риск; после входа посоветовать смену пароля).

### 2.6 Критические питфоллы
| Питфолл | Решение |
|---|---|
| `--profile`/`--headed` **игнорируются**, если демон уже запущен | сначала `agent-browser close --all`, потом запуск с новыми опциями |
| Профиль «not found» по имени | передавать полный путь к директории |
| **Chrome lock**: нельзя прицепиться к профилю, пока обычный Chrome юзера запущен с ним | юзер должен **полностью закрыть свой Chrome** (все окна), иначе «profile in use» |
| Страница `about:blank` после open | дать время, повторить `open` той же командой |
| Свежий automation-профиль без истории → Google/сайты подозревают | вход родным логином, не через OAuth |
| **X.com зацикливается на Google-редиректе** (зависший OAuth-флоу из прошлого входа: `x.com/home` упорно кидает на `accounts.google.com`) | открывать `https://x.com/login` напрямую, в обход `x.com/home`; форма входа появляется, email подставляется автозаполнением профиля |

### 2.7 Реальный профиль юзера (повторный логин не нужен)

Если юзер уже залогинен в X в своём обычном Chrome — прицепляемся к его профилю напрямую:

```bash
agent-browser close --all    # демон держит старые опции запуска — сначала закрыть
# юзер ОБЯЗАН полностью закрыть свой Chrome (все окна), иначе «profile in use»
agent-browser --headed \
  --executable-path "C:\Program Files\Google\Chrome\Application\chrome.exe" \
  --profile Default open "https://x.com/login"
```

- `--executable-path` — **Windows-путь** (`C:\...`); MSYS-формат `/c/Program Files/...` падает с `os error 3` («Системе не удается найти указанный путь»).
- `--profile Default` — имя из `agent-browser profiles` (команда показывает доступные профили Chrome юзера).
- Сессия X подхватывается из профиля; если X всё равно редиректит на Google — см. питфолл выше: `/login` напрямую.

### 2.8 Извлечение ПОЛНОГО текста одного твита/треда (CDP-браузер)

Для конкретного твита (`x.com/i/status/<id>`) curl возвращает ТОЛЬКО мета-теги
(og:title / og:description) и картинки — **_full_text_** не в HTML (рендерится JS).
Полный текст достаётся через CDP-браузер с залогиненным или даже гостевым профилем:

1. Проверить ID: валидные ID-твитов **≤19 цифр** (int64-потолок `9223372036854775807`).
   Лишняя цифра → curl HTTP 404. Пользователь часто даёт 20-цифровой ID — это опечатка:
   проверить длину, попросить правильный.
2. `curl` для быстрого превью — мета-описание даёт заголовок + `og:image` (URL карточки
   статьи `pbs.twimg.com/media/...`). Это «тизер», не контент.
3. Запустить Chrome с CDP (если порт 9222 не отвечает):
   ```bash
   "/c/Program Files/Google/Chrome/Application/chrome.exe" \
     --remote-debugging-port=9222 --user-data-dir="C:\Users\tomas\.agent-browser\profiles\chrome-x" \
     --remote-allow-origins=* --no-first-run about:blank
   ```
4. `browser_navigate` на `https://x.com/i/status/<id>` — X сам редиректит на `/<author>/status/<id>`.
5. **Полный текст** — через `browser_snapshot(full=true)`. Если снапшот обрезан
   (полный html-объём), итог сохранён в `C:\Users\tomas\AppData\Local\hermes\cache\web\browser-snapshot-*.txt`
   — дочитать через `read_file`.
6. `document.querySelectorAll('[data-testid="tweetText"]')` может быть **пуст** для
   статьи-карточки — контент лежит в заголовках `<h1>/<h3>` и параграфах снапшота, а не
   в tweetText. Картинки твита — через `[...document.querySelectorAll('article img')]`
   (src pbs.twimg.com/media). Если юзер просит «почитать/отдать» твит — отдать текст из снапшота БЕЗ отсебятины.
7. Гостевой доступ (нет логина) всё равно отдаёт полный текст статьи — вход не обязателен для чтения одиночного твита.

## 3. Проверка результата (обязательно)

- После любого «открылось/нашлось» — `agent-browser get url` / `get title`, реальный снапшот.
- Цитаты/посты для отчёта — только то, что реально извлечено, не по памяти.
- Файлы промежуточных HTML — в рабочую папку (`~/tmp_search/`), чтобы не засорять контекст.

## 4. Питфоллы языка

- Кириллица в URL-запросах ломает некоторые тулы (браузер: `utf-8 codec` ошибки) — для curl кодировать через `--data-urlencode` или Python `urllib.parse.quote`.
- Термины, которые юзер называет «новой темой», могут быть новоязом сообщества — ищи и точную фразу, и вариации (`graph evolution`, `self-evolving agents`, `agentic graph`).
