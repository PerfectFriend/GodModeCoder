# Поиск в вебе через curl, когда поисковики капчат

Наблюдения (август 2026, Windows, curl с Chrome UA):

## Работают (не капчат)

| Сервис | Команда/URL | Заметки |
|---|---|---|
| **Brave Search** | `curl -sL -A "<Chrome UA>" "https://search.brave.com/search?q=<query>&tf=pd"` | `tf=pd` = последние сутки. HTML: ссылки `href="https://..."` + текст ссылки. Сниппеты в `class="snippet..."` блоках. 225KB страница. |
| **GitHub Search API** | `curl -s "https://api.github.com/search/repositories?q=<query>&sort=updated&order=desc&per_page=10"` | Без ключа работает (rate limit ~10/min). JSON: `total_count`, `items[].full_name/updated_at/description`. Кириллица в query норм. |
| **HN Algolia API** | `curl -s "https://hn.algolia.com/api/v1/search_by_date?query=<q>&tags=story&hitsPerPage=20"` | JSON: `nbHits`, `hits[].title/url/created_at`. Свежее по дате. |
| **Google через браузер (CDP)** | если есть Chrome с портом 9222 | см. основной SKILL.md, вкладку ищем по URL |

## Капчат / блокируют curl (проверено)

| Сервис | Симптом |
|---|---|
| DuckDuckGo html | страница с `anomaly` / `challenge` (~14KB) |
| Bing | CAPTCHA, `b_no`, нет результатов |
| Yandex | `captcha` в HTML |
| searx.be (json) | `Verifying your browser…` |
| Reddit search.json | `Blocked` (HTML) |

## Приёмы

1. **Всегда** ставить Chrome UA: `-A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"`.
2. Проверка на капчу: `grep -o 'captcha\|anomaly\|challenge' file.html | sort | uniq -c`.
3. Кириллица в URL: `curl --data-urlencode` не работает для GET — кодировать вручную через `python -c "import urllib.parse; print(urllib.parse.quote('граф-эволюция'))"` или просто вставлять %XX-строку.
4. Запрос с точной фразой: кавычки в URL = `%22` (напр. `%22autonomous+graph+evolution%22`).
5. Парсить ссылки: `python -c` с `re.findall(r'href="(https?://[^"]+)"', html)` + фильтр по доменам.
6. Поиск по соцсетям (X/Twitter, Telegram) через поисковики даёт мало — посты X не индексируются полноценно; нужен браузер с сессией (см. основной SKILL.md).
