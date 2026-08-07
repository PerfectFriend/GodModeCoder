---
name: web-research
description: "Нужен веб-поиск/соцсети: Brave-curl, API, agent-browser."
trigger: "Нужен веб-поиск/соцсети: Brave-curl, API, agent-browser."
---

# Web & Social Media Research

Исследование тем/трендов в вебе и соцсетях: свежие публикации за последние дни, поиск по X.com/Telegram/Reddit/HN, сбор ссылок пачкой, когда browser_navigate недоступен или нужен массовый сбор.

## Шаг 0: уточни язык и платформу ДО поиска
- **Спроси/проверь:** на каком языке искать термин и где ожидаются источники (X.com, Telegram, Habr, Reddit, HN...).
- Реальный кейс: пользователь дал русский термин «автономная граф-эволюция», но хотел англоязычные посты на X.com в AI-сообществах. Первый поиск по-английски был отвергнут («ищи на русском»), потом уточнение дало «нет, на английском, X.com». Уточнение в начале экономит 15 минут.
- Модель запроса: «Термин на [языке], источники ищем на [платформы], период [дни]?»

## Матрица поисковиков (curl с desktop UA)

| Сервис | Статус | Как |
|---|---|---|
| **Brave Search** | ✅ работает | `https://search.brave.com/search?q=<urlencoded>&tf=pd` (tf=pd = день, tf=w = неделя) |
| **GitHub API** | ✅ работает | `https://api.github.com/search/repositories?q=<query>&sort=updated` (без ключа, лимит ~10/мин) |
| **HN Algolia API** | ✅ работает | `https://hn.algolia.com/api/v1/search_by_date?query=<q>&tags=story` |
| Google, Bing, DDG html, Yandex, Searx-инстансы, Habr | ❌ капча/блок curl | переключайся на Brave/API |
| Reddit JSON (`/search.json`) | ❌ блок без auth | ищи через Brave `site:reddit.com` |

Правило: если сервис отдал капчу — не повторяй 10 раз, меняй путь (Brave → API → agent-browser).

## Парсинг Brave-результатов
```python
import re, html
c = open('brave.html', encoding='utf-8', errors='ignore').read()
links = re.findall(r'<a[^>]*href="(https?://[^"]+)"[^>]*>(.*?)</a>', c, re.S)
for u, t in links:
    t = html.unescape(re.sub(r'<[^>]+>', '', t)).strip()
    # фильтруй u: отбрось brave.com/search/hackerone, дедуплицируй
```
Файл качай в `~/tmp_search/`, а не `/tmp` (на Windows MSYS `/tmp` часто не существует).

## Стратегия запросов
1. Точная фраза в кавычках → 2. вариации термина → 3. привязка к платформе (`site:x.com`).
4. Проверяй сниппеты, а не только заголовки — site:x.com даёт шум (нерелевантные аккаунты).
5. Для «последних дней» используй tf=pd / сортировку по дате в API.

## agent-browser для авторизованных платформ (X.com и т.п.)
Полный флоу: см. `references/xcom-authenticated-search.md`.
Кратко: бинарник в `~/AppData/Local/hermes/hermes-agent/node_modules/.bin/agent-browser` (export PATH); первый запуск — `agent-browser install` (качает Chrome ~190MB); headed-окно с профилем; **профиль — полный путь, не имя**; логин делает пользователь в видимом окне (никогда не проси пароль).

## Питфоллы
- **browser_navigate + кириллический URL** → `'utf-8' codec can't decode` — percent-encode URL или иди через curl.
- **browser_navigate «Chrome not found»** → фикс: `agent-browser install` (ставит в `~/.agent-browser/browsers/`).
- Не записывай «поисковик X сломан» навсегда — антибот-политики меняются; durable-урок — рабочие пути (Brave/API/agent-browser), а не запреты.
- agent-browser `open` в headed-режиме блокирует терминал — запускай в background, состояние проверяй через `agent-browser get title/url` из другого вызова.
