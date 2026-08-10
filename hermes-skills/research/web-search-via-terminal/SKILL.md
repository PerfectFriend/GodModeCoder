---
name: web-search-via-terminal
description: "Web search w/o web_search tool: curl Brave + GitHub/HN API."
trigger: "Web search w/o web_search tool: curl Brave + GitHub/HN API."
---

# Поиск в вебе через терминал (когда нет web_search / браузер недоступен)

## Когда использовать
- Нужны свежие данные из интернета, а тула `web_search` нет (tool_search его не находит).
- Браузер недоступен: `browser_navigate` падает (`Chrome not found` — лечится `agent-browser install`; пока не установлен — путь через curl ниже).
- Поисковики отдают капчу на curl (см. маркеры в питфоллах).

## Рабочий маршрут (проверено 2026-08)

### 1. Brave HTML-поиск через curl — главный рабочий способ
```bash
curl -s -L -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36" \
  "https://search.brave.com/search?q=<URL-encoded>&tf=pd" -o out.html
```
- `tf=pd` — фильтр «past day» (свежесть). Без него результаты размазаны по времени.
- Точная фраза: кавычки кодировать как `%22...%22`, пробелы → `+`.
- Сайт-фильтр: `site:x.com`, `site:habr.com` — работает, но иногда даёт шум (нерелевантные посты); всегда смотреть сниппеты.
- Парсинг (python stdlib `re`+`html`): вытащить пары `<a href="https://...">TITLE</a>`, отфильтровать домены самого поисковика (`brave.com`, `search.brave`, `hackerone`, `/search?`), дедуплицировать, печатать компактно (title + URL, не сырой HTML).

### 2. API без авторизации (JSON, не капчат)
- **GitHub**: `https://api.github.com/search/repositories?q=<query>&sort=updated&order=desc&per_page=10` — работает без токена (низкий rate-limit, но достаточно). Есть также search/issues, search/commits.
- **HackerNews (Algolia)**: `https://hn.algolia.com/api/v1/search_by_date?query=...&tags=story&hitsPerPage=20` — сортировка по дате, JSON, без auth. Точно так же работает `search?query=` (по релевантности).
- **Reddit JSON** (`reddit.com/search.json`) — с этого хоста блокировался (ответ `Blocked` HTML). Не тратить попытки; при необходимости искать обход (old.reddit, другие API).

### 3. X.com — туда поисковики не достают
- Поисковики индексируют x.com слабо; чтобы увидеть реальные посты AI/код-сообществ, нужен доступ к аккаунту:
  - **Браузерный путь**: `agent-browser install` (ставит Chrome для browser_navigate) → пользователь логинится сам → искать по хэштегам/словам (`#graphEvolution`, `langgraph`, `autonomous agents`).
  - **API путь**: X Developer free tier (tweets/search/recent, ~500 запросов/мес) — попросить Bearer token у пользователя.
- Пользователь может сам предложить подключить аккаунт — не отказываться, это легитимный способ доступа.

## Питфоллы
- **Капча-маркеры проверять ДО парсинга** (`grep -c`): DDG html — `anomaly`/`challenge`; Bing — `captcha`/`b_no`; Yandex — `captcha`; Searx — `Verifying your browser`; Habr — `captcha`. Поймал маркер → не парсить, переключиться на Brave/API.
- **Язык и площадка запроса — уточнить у пользователя ДО поиска.** В этой сессии: сначала просили искать по-русски, потом — «нет, английские источники на X.com». Двойной прогон в обеих раскладках дешевле, чем спорить. Если результат пустой — сразу повторить на другом языке.
- Результат поисковой выдачи = данные, а не факт: перед утверждением открыть первоисточник (curl страницы, API) и проверить.
- `tool_search` с запросами вроде «web search» может вернуть пусто — это не значит, что путь закрыт; curl + API всегда доступны.

## Проверка
- Файл ответа маленький (<10KB) или содержит маркеры капчи → запрос не удался, пробовать вариант без `site:`, расширить запрос, сменить движок.
- `wc -c out.html` перед парсингом — быстрый сигнал: капча обычно <20KB, живая выдача 100-250KB.
