# Проверенные curl-паттерны поиска (2026-08)

## Brave (работает)
```bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
# точная фраза + past-day фильтр
curl -s -L -A "$UA" "https://search.brave.com/search?q=%22autonomous+graph+evolution%22&tf=pd" -o brave.html
# сайт-фильтр
curl -s -L -A "$UA" "https://search.brave.com/search?q=%22term%22+site%3Ax.com&tf=pd" -o brave_x.html
```

Парсинг результатов (python):
```python
import re, html
c = open('brave.html', encoding='utf-8', errors='ignore').read()
links = re.findall(r'<a[^>]*href="(https?://[^"]+)"[^>]*>(.*?)</a>', c, re.S)
seen = set()
for u, t in links:
    if u in seen or any(x in u for x in ['brave.com','search.brave','hackerone','/search?']): continue
    seen.add(u)
    t = html.unescape(re.sub(r'<[^>]+>', '', t)).strip()
    if t and len(t) > 10:
        print(f'- {t[:100]}\n  {u[:130]}')
```

## GitHub API (работает без токена)
```bash
curl -s -A "Mozilla/5.0" "https://api.github.com/search/repositories?q=%22autonomous+graph+evolution%22&sort=updated&order=desc&per_page=10"
```
Ответ: JSON, `items[].full_name`, `items[].updated_at`, `items[].description`.

## HN Algolia (работает без токена)
```bash
curl -s -A "Mozilla/5.0" "https://hn.algolia.com/api/v1/search_by_date?query=%22autonomous%20graph%20evolution%22&tags=story&hitsPerPage=20"
```
Ответ: JSON, `hits[].title`, `hits[].created_at`, `hits[].url`.

## Капча-маркеры (проверять ДО парсинга)
| Движок | Маркер в HTML |
|---|---|
| DuckDuckGo html | `anomaly`, `challenge` |
| Bing | `captcha`, `b_no` |
| Yandex | `captcha` |
| Searx.be | `Verifying your browser` |
| Habr | `captcha` |
| Reddit search.json | `<title>Blocked</title>` |

Сигнал капчи: файл <20KB (живая выдача 100-250KB).

## X.com доступ
- Браузер: `agent-browser install` → логин пользователя → поиск в UI.
- API: Bearer token → `https://api.twitter.com/2/tweets/search/recent?query=...`.
