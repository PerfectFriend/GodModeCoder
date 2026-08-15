---
name: web-search-fallbacks
description: "Поисковики капчат curl — обход: Brave, API GitHub/HN, RSS."
trigger: "Поисковики капчат curl — обход: Brave, API GitHub/HN, RSS."
---

# Поиск в вебе, когда поисковики капчат curl

## Симптом
`curl` на Google, DuckDuckGo (html.duckduckgo.com), Bing, Yandex, Searx (searx.be) → CAPTCHA / «Verifying your browser» / anomaly. Это норма: крупные движки режут не-браузерный трафик. Не паниковать — есть рабочие обходы.

## Работающие обходы (проверено)

### 1. Brave Search HTML (главный рабочий)
```bash
curl -s -L -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36" \
  "https://search.brave.com/search?q=%22<фраза>%22&tf=pd" -o out.html
```
- `tf=pd` — фильтр «за последние сутки» (аналог Google `tbs=qdr:w`)
- `site:домен` в запросе работает: `.../search?q=%22фраза%22+site%3Ax.com`
- Парсинг: ссылки и заголовки по regex (см. ниже); сниппеты — в блоках `snippet`
- Мусор исключать: `brave.com`, `search.brave`, `/search?`, `hackerone`

### 2. API без ключей (точные, структурированные)
- **GitHub**: `https://api.github.com/search/repositories?q=<запрос>&sort=updated&order=desc&per_page=10` (лимит ~10 req/min без токена)
- **HackerNews Algolia**: `https://hn.algolia.com/api/v1/search_by_date?query=<q>&tags=story&hitsPerPage=20` — с датами, идеально для «что обсуждали за последние дни»
- **Reddit JSON**: `https://www.reddit.com/search.json?q=...` — часто 403 Blocked из датацентров; не основной путь

### 3. Тематические источники вместо поисковика
- Habr: `https://habr.com/ru/search/?q=...` (тоже капчит — тогда через Brave `site:habr.com`)
- Конференции и блоги вендоров (Neo4j NODES AI, Sartech Labs и т.п.) — через Brave `site:`

## Парсинг результатов Brave (python, проверено)
```python
import re, html
c = open('out.html', encoding='utf-8', errors='ignore').read()
links = re.findall(r'<a[^>]*href="(https?://[^"]+)"[^>]*>(.*?)</a>', c, re.S)
seen = set()
for u, t in links:
    if u in seen or any(x in u for x in ('brave.com', 'search.brave', '/search?', 'hackerone')):
        continue
    seen.add(u)
    t = html.unescape(re.sub(r'<[^>]+>', '', t)).strip()
    if t and len(t) > 10:
        print(f'- {t[:90]}\n  {u[:120]}')
```

## Питфолл: язык запроса (правка пользователя)
Русскоязычный базворд (напр. «автономная граф-эволюция») часто — перевод англоязычного тренда. Ищи **оба варианта**: русский для локального контекста, английский для источников. Свежие обсуждения AI/код-трендов живут на **X.com (англ.)** в AI/code-сообществах — русскоязычная индексация отстаёт. Если пользователь просит «ищи в соцсетях» — целиться в X.com, а не в поисковики.
