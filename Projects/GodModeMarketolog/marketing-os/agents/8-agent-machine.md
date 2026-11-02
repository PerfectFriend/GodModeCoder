# Agent Swarm: Autonomous AI Marketing Machine (8 Agents)

> **Концепт:** Автономная машина, которая ищет клиентов, пишет, прогревает, закрывает, масштабирует — 24/7.
> **Философия:** «AI делает рутину. Человек принимает решения. Масштаб — автоматом.»
> **Источник:** AI_Marketing_Machine_Plan (GlobeVis) + Explee AutoGTM.

## Архитектура

```
AGENT-1 RESEARCHER ┐
AGENT-2 CONTENT     ├─→ AGENT-0 ORCHESTRATOR (ты: стратегия, бюджет, ворота)
AGENT-3 OUTREACH    ┘         │
AGENT-4 CREATIVE     ┐        │
AGENT-5 ANALYTICS    ├────────┘
AGENT-6 AFFILIATE    ┐
AGENT-7 EMAIL       ─┤
AGENT-8 SOCIAL      ─┘
```

| Agent | Роль | Output/неделю | Инструменты |
|-------|------|---------------|-------------|
| **0 Orchestrator** | Стратегия, бюджет, gates, weekly review | Рапорт понедельник 09:00 | Notion, Stripe, Plausible, Rewardful |
| **1 Researcher** | Охота за лидами 24/7 | 1000+ qualified leads/мес | X API, Reddit, Apollo, Clay |
| **2 Content** | SEO + Social фабрика | 2 статьи, 20 твитов, 5 LinkedIn | Claude/LLM, ComfyUI, Notion |
| **3 Outreach** | Персонализированный DM/Email | >40% open, >15% reply | Instantly.ai, Lemlist, GPT |
| **4 Creative** | Визуальные ассеты | 50+ вариаций, 10 баннеров, 5 Reels | ComfyUI (local GPU), AnimateDiff |
| **5 Analytics** | Единая правда метрик | Авто-отчёт в Notion | n8n, Metabase, PostHog |
| **6 Affiliate** | Партнёрская армия на автопилоте | Auto-recruit, onboard, leaderboard | Rewardful API, n8n |
| **7 Email** | Автопилот воронок | 5 sequences + A/B тесты | Resend, n8n |
| **8 Social** | Дистрибуция везде | 10 твитов/статью + Reddit + Shorts | Buffer/Typefully, X API |

## Инфраструктура (self-hosted, zero cloud lock-in)
```
Orchestration:  n8n (self-hosted Docker) — все workflows, cron, webhooks
LLM:            OpenAI/Anthropic/локальный llama.cpp (через n8n HTTP)
Image Gen:      ComfyUI (local GPU) + Runway API (видео)
Data:           Clay + Apollo + Apify (enrichment/scraping)
Email:          Resend + Instantly.ai (cold)
Affiliate:      Rewardful API
Analytics:      Plausible + Stripe + PostHog
Social:         Buffer/Typefully + X API v2 + Reddit API
DB:             Airtable (leads/assets/calendar) + PostgreSQL (events)
Alerts:         Slack + Telegram Bot
```

## n8n Workflows (ядро — 14+)
| Workflow | Trigger | Actions | Agent |
|----------|---------|---------|-------|
| `daily_lead_hunt` | Cron 06:00 | X Search → Clay Enrich → Score → Airtable | 1 |
| `reddit_monitor` | Webhook (Pushshift) | Keyword → Filter → Slack Alert → Reply Draft | 1 |
| `content_factory` | Cron Mon 09:00 | Keywords → Outline → Write → SEO → Notion | 2 |
| `creative_batch` | Cron Tue 09:00 | Prompts → ComfyUI → Upscale → Format → Airtable | 4 |
| `social_distribution` | Webhook (Published) | Format → Schedule → Buffer → Engage | 8 |
| `cold_outreach` | Cron Daily 10:00 | Leads → Personalize → Sequence → Instantly | 3 |
| `trial_onboarding` | Stripe `checkout.completed` | Tag → Sequence D0..D14 | 7 |
| `trial_conversion` | Trial Ended | Segment → Sequence D0/D2/D5/D10 | 7 |
| `affiliate_recruit` | Cron Weekly | Search → Enrich → Outreach → Onboard | 6 |
| `affiliate_nurture` | Cron Biweekly | Top Partners → Newsletter → Assets | 6 |
| `weekly_report` | Cron Mon 08:00 | Query APIs → KPIs → Notion → Slack | 5 |
| `alert_cac` | Cron Daily | CAC Calc → Threshold → Telegram | 5 |
| `creative_rotation` | Cron Daily | Ad Perf → Pause Losers → Generate New | 4+5 |
| `seo_monitor` | Cron Daily | Rankings → Alert Drops → Content Gap | 2+5 |

## Применение к проектам Торквемады
- **SuperGuard** — AGENT-3 cold email (B2B: склады, стройки, частные дома) + AGENT-2 build-in-public в X + AGENT-4 demo-видео
- **ParanoidX** — AGENT-1 охота dev-аудитории в X/Reddit + AGENT-8 Show HN + AGENT-5 инвестор-воронка
- **MatrixX** — AGENT-8 viral Shorts (privacy-angle) + AGENT-6community в TG + AGENT-2 контент
- **Магазин ParanoidAndroid** — AGENT-3 cold в X (privacy-энтузиасты) + AGENT-7 email + AGENT-4 креативы «zero-IME»

## Hard Rules
- AI никогда не владеет решением. AGENT-0 (ты) утверждает стратегию и бюджет.
- Ворота (Gate A/B/C) — единственный критерий «продолжаем / пивот / убиваем».
- До Gate A: 0% реинвестиции, свои средства. Gate A→B: 60% выручки в маркетинг.
