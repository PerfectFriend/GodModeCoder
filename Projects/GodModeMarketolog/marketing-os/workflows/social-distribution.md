# Workflow: Social Distribution (Amplifier)

> **Stage:** 7 (Distribution) | **Human-AI Level:** 3-4
> **Trigger:** Webhook при публикации контента + daily cron для реплаев.

## Каналы и правила

### Twitter/X (ГЛАВНЫЙ)
Профиль-шаблон:
```
Bio: "{one-liner value}. Building in public: $0→$X MRR. DM for beta 🔥"
Pinned: Demo GIF + "See it live → {link in reply}"
```
Ежедневно (авто + ручное 15 мин):
- 5-10 реплаев под твитами про нишу (expert help, no pitch)
- 2-3 quote-tweet кейсов конкурентов + insight
- 1 tweet «build in public» (метрики, wins, blockers)
- 10-15 advanced search реплаев лидам

**Advanced Search Queries (AGENT-1 hunter):**
```
("visitor map" OR "live traffic") (wordpress OR shopify) lang:en -filter:links
"looking for" ("analytics" OR "tracking") {our_niche}
"alternative to" {competitor}
"how to" "{our_use_case}" {niche}
```

### Reddit (long-tail)
- 90% экспертных комментов БЕЗ ссылки, 10% релевантных
- Карма > 1000 перед первым упоминанием
- Сабы: зависят от ниши (r/WordPress, r/SaaS, r/privacy, r/androiddev...)

### LinkedIn (B2B)
- 3×/нед case studies, comparison tables, carousel PDF
- AGENT-3: Sales Nav поиск decision makers → value DM

### YouTube Shorts / Reels / TikTok (viral)
Форматы: Demo (30с), Comparison (30с), Case (60с), Value (15с).
AGENT-4 генерит фон+анимацию, AGENT-8 — хештеги + engagement replies.

## Форматирование под алгоритм X (см. theory/x-algorithm-playbook.md)
- Ссылки НЕ в основном твите → класть в reply (пенальти за http)
- Видео > картинка > текст
- Вопросы («?») в посте → больше реплаев
- Bookmarks = сильный сигнал → делать saveable (чек-листы, фреймворки)

## Алерты
- Reach drop > 20% WoW → проверить теневой бан
- Новый упоминание бренда → авто-реплай-драфт агенту-0
