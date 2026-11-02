# Workflow: Competitive Intelligence (Automated)

> **Stage:** 2 (Market Understanding) | **Human-AI Level:** 3 (Human-Supervised Automation)
> **Trigger:** Weekly cron ИЛИ сигнал о новом конкуренте.

## Цель
Держать актуальную карту конкурентов без ручного мониторинга: что они релизят, где растут, чем отличаются.

## Pipeline
```
Source Identification
    → Data Collection (API/scrape)
    → Enrichment (Clay/Apify)
    → Analysis (LLM cluster)
    → Insight Extraction
    → Distribution (Notion + Telegram)
```

## Шаги (n8n-воркфлоу `competitive_intel`)

### 1. Source Identification
Источники по категориям:
- **GitHub:** новые звёзды, релизы, closed issues у конкурентов
- **Product Hunt:** новые лаунчи в категории
- **X/Twitter:** упоминания конкурентов (advanced search)
- **G2/Capterra/TrustRadius:** новые ревью
- **Reddit:** треды «alternative to [competitor]»

### 2. Data Collection
```python
# Псевдокод сбора
sources = {
    "github": "api.github.com/repos/{competitor}/releases",
    "ph": "api.producthunt.com/v2/posts",
    "x": "X API v2 recent-search ?query={competitor}",
    "reddit": "Pushshift/Apify: 'alternative to {competitor}'"
}
for src, endpoint in sources.items():
    raw = fetch(endpoint)  # rate-limited, через n8n HTTP
    store(raw, f"ci_raw_{src}")
```

### 3. Enrichment
- Clay: привязать компанию → размер, funding, tech stack
- Apify: достать метрики трафика (SimilarWeb), headcount

### 4. Analysis (LLM)
Промпт для агента:
```
Сравни {our_product} и {competitor} по:
- Позиционирование (что они говорят)
- Фичи (что реально умеют)
- Цена (тарифы)
- Weaknesses (жалобы в ревью)
- Threat level (1-10 для нашей воронки)
Верни таблицу + 3 actionable insight.
```

### 5. Insight Extraction
Фильтр: только то, что меняет нашу стратегию (не шум).
- Новый фича конкурента, которую просят НАШИ клиенты?
- Падение их рейтинга = окно для comparison-контента?
- Их клиент пишет «too expensive» = наш angle?

### 6. Distribution
- Notion DB `CI Digest` (tabular, versioned)
- Telegram alert агенту-0 при threat level > 7
- Авто-генерация comparison-статьи (AGENT-2) при сигнале

## AI Responsibilities
Мониторинг, суммаризация, паттерн-детект, сравнительные таблицы.

## Human Responsibilities
Кредибилити источника, интерпретация, стратегические импликации, решение «атаковать или игнорить».

## Success Criteria
- Еженедельный дайджест готов без ручного труда
- Конкурентный сдвиг виден за 7 дней
- ≥ 1 actionable insight/неделю попадает в план AGENT-2

## Failure Modes
- API rate-limit → exponential backoff в n8n
- Шум (false positive) → фильтр threat-level < 5 не шлёт человеку
- Устаревшие источники → квартальный аудит списка конкурентов
