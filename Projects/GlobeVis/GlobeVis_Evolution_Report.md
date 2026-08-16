# GlobeVis (VISITORS GLOBE) — Стратегический отчёт: От плагина за $12 к SaaS-лидеру визуальной аналитики

---

**Версия:** 1.0  
**Дата:** 2026-08-07  
**Автор:** Master Inquisitor / Hermes Agent  
**Проект:** GlobeVis / VISITORS GLOBE — Real-time 3D Visitors Globe для WordPress & HTML/PHP  
**Статус:** Конфиденциально. Для внутреннего использования команды (Charles Schreiber + Marketing Partner 50/50).

---

## 📋 ОГЛАВЛЕНИЕ

1. [Исполнительное резюме](#1-исполнительное-резюме)
2. [Текущее состояние и асессмент](#2-текущее-состояние-и-асессмент)
3. [Эволюция проекта: 4 фазы от lifetime-лицензии к Category King](#3-эволюция-проекта-4-фазы-от-lifetime-лицензии-к-category-king)
4. [План маркетинга: Полный захват ниши Visual Real-time Analytics](#4-план-маркетинга-полный-захват-ниши-visual-real-time-analytics)
5. [Таймлайн эволюции и маркетинга](#5-таймлайн-эволюции-и-маркетинга)
6. [Финансовые проекции: 3 сценария](#6-финансовые-проекции-3-сценария)
7. [Риски и митигация](#7-риски-и-митигация)
8. [Decision Framework & Gates](#8-decision-framework--gates)
9. [Immediate Next Steps](#9-immediate-next-steps)

---

## 1. ИСПОЛНИТЕЛЬНОЕ РЕЗЮМЕ

### Суть продукта
**VISITORS GLOBE** — визуальный счётчик посетителей в виде 3D-глобуса с мигающими точками в реальном времени. «Аналитика, которая выглядит как шоу».

**Текущее состояние:**
- Free WP плагин: ~1,000 активных установок (WP.org показывает 60+, но dev говорит ~1000)
- Lifetime лицензия: $12 разово
- Конверсия free→paid: ~1% (1 платящий на 100 фри-инсталлов)
- HTML/PHP версия для любого сайта
- Нужны: логирование, 2 продукта, Stripe оплата

### Стратегический пивот
**Перестать продавать плагин за $12 lifetime. Начать продавать SaaS за $19–149/мес.**

Free плагин = лидогенератор (топ-of-funnel). Продукт = Cloud Dashboard + API + Alerts + White-label + Team seats.

### Рынок
- **TAM:** ~$1B (Visual Real-time Analytics niche)
- **SAM:** ~$1.1B (WP site owners, agencies, e-com, media — англоязычные + EU + LatAm)
- **SOM Target (Year 3):** $3M ARR (Realistic) до $3.9M ARR (Aggressive)

### Партнёрство
**Charles Schreiber (Dev) + Marketing Partner = 50/50 split.**  
Charles даёт продукт, доступы, код. Маркетинг-партнёр даёт GTM, контент, партнёрки, продажи.

---

## 2. ТЕКУЩЕЕ СОСТОЯНИЕ И АСЕССМЕНТ

### SWOT-анализ

| Strengths | Weaknesses |
|-----------|------------|
| ✅ Уникальный визуал: 3D глобус = viral по дизайну | ❌ Lifetime $12 = мёртвая монетизация, нет LTV |
| ✅ Zero-setup интеграция (1 строка кода / WP плагин) | ❌ Нет дашборда, нет логов, нет алертов — продукт «слепой» |
| ✅ WP.org органика: ~1000 инсталлов бесплатно | ❌ Конверсия 1% — критически низкая |
| ✅ Privacy-by-design: только координаты + timestamp | ❌ Нет multi-site, нет API, нет white-label |
| ✅ GDPR-friendly, лёгкий скрипт | ❌ Зависимость от JSON файлов, нет БД, нет масштабируемости |
| ✅ Два продукта готовы (WP + HTML/PHP) | ❌ Нет командной разработки, bus factor = 1 |

| Opportunities | Threats |
|---------------|---------|
| 🟢 Ниша «visual analytics» практически пуста (Hotjar/GA4 — таблицы) | 🔴 Hotjar/Contentsquare могут скопировать визуал за месяц |
| 🟢 E-com платит за «social proof» — глобус на лендинге = конверсия | 🔴 WP.org может запретить «phone home» к внешним серверам |
| 🟢 Агентства покупают за клиентов (multi-seat, white-label) | 🔴 Dev burnout (соло, нет команды) |
| 🟢 Shopify / Wix / Webflow = новые каналы дистрибуции | 🔴 Churn выше ожидаемого без проактивного retention |
| 🟢 Affiliate flywheel: хостинги, WP-агентства, ютуберы | 🔴 AppSumo LTD пользователи = высокий саппорт, низкий LTV |

### Baseline Metrics (August 2026)

| Метрика | Текущее | Цель Q4 2026 (Realistic) | Цель Q4 2026 (Aggressive) |
|---------|---------|--------------------------|---------------------------|
| Free WP Installs | ~1,000 | 5,000 | 15,000 |
| Daily Active Sites | ~200 | 1,000 | 3,000 |
| Pro Subscribers | ~10 | 150 | 500 |
| MRR | ~$0 | $5,500 | $66,000 |
| Chains/Platforms | WP, HTML/PHP | + Shopify | + Wix, Webflow |
| API Calls/day | 0 | 100K | 1M |

---

## 3. ЭВОЛЮЦИЯ ПРОЕКТА: 4 ФАЗЫ ОТ LIFETIME-ЛИЦЕНЗИИ К CATEGORY KING

### ФАЗА 0: FOUNDATION — «Сделать продаваемым» (Недели 1–4)

**Цель:** Рабочий SaaS MVP, готовый к приёму первых платящих пользователей.

| Неделя | Dev (Charles) | Marketing Partner | Deliverable |
|--------|---------------|-------------------|-------------|
| 1 | Stripe Billing: Products, Prices, Checkout, Portal, Webhooks | Positioning doc, pricing copy, FAQ | Stripe test mode working |
| 2 | Multi-tenant DB (sites, events, alerts), API keys | Dashboard wireframes, onboarding emails | Dashboard MVP |
| 3 | WP Plugin v2: «Connect to Cloud» OAuth/API key, batch sync | Landing page: Hero, Demo, Pricing, Signup | Cloud-connected plugin |
| 4 | Free→Trial banner in plugin, UTM tracking | Launch checklist (analytics, heatmaps, errors) | **Soft launch to 50 beta users** |

**Тех долг к закрытию:** JSON → PostgreSQL/SQLite, multi-tenant schema, background sync (WP Cron), logging 100%.

---

### ФАЗА 1: PRODUCT-MARKET FIT — «Люди платят» (Месяцы 1–3)

**Цель:** 100 платящих клиентов, $3–5K MRR, валидированный CAC < $80.

#### Продуктовые доработки:
- Multi-site под один аккаунт
- API ключи + документация
- Alerts: Telegram/Slack/Email (webhook)
- Campaign tracking (UTM → цвет точки)
- Historical replay (слайдер времени)
- Цены: Starter $19, Pro $49, Agency $149/мес

#### GTM Каналы (приоритет):
1. **WP.org Organic Funnel** (Highest ROI) — баннер в плагине, онбординг тур, email sequence, «Powered by» badge
2. **Affiliate Program** — Rewardful/FirstPromoter, 30% recurring, 10 founding partners (WP agencies, hosts)
3. **Content & SEO** — 5 статей/мес, target keywords: "visitor map wordpress", "live traffic website"
4. **Launch Spikes** — AppSumo LTD (Month 2), Product Hunt (Month 3), WP Tavern PR

**KPIs Month 3:**
- 100+ paying customers
- $3,500+ MRR
- CAC < $80 blended
- Churn < 4%
- 20+ affiliates recruited

---

### ФАЗА 2: GROWTH ENGINE — «Масштабируем» (Месяцы 4–12)

**Цель:** $50K MRR, 1,000+ платящих, команда 3–5 человек, Series A optionality.

#### Продукт:
- White-label (убрать брендинг, custom domain) — Agency tier
- Team seats + RBAC (Owner/Admin/Viewer)
- Affiliate dashboard (30% recurring)
- Marketplace тем/скинов глобуса ($5–15 за тему)
- Public share links (viral loop: «посмотри, 500 посетителей прямо сейчас»)
- Интеграции: GA4, Matomo, Plausible, HubSpot
- Shopify App Store launch (Month 6)
- Wix / Webflow apps (Month 9)

#### Маркетинг:
- Paid ads scale (Google + Meta, ROAS > 3)
- YouTube sponsorships (3/мес)
- Agency partner program: co-branded dashboards, volume pricing
- Referral program: 1 месяц бесплатно за реферала
- Webinar series: «Live Analytics for Agencies»
- Internationalization (ES, PT, DE, FR)

#### Найм (к Month 12):
- Support Engineer (full-time, Month 4)
- Content Writer / SEO (part-time → full-time, Month 5)
- Growth Marketer (Month 8, если Aggressive path)

**KPIs Month 12 (Realistic):**
- 600+ paying customers
- $21K MRR
- 25% revenue от affiliates
- 20K organic visits/mo
- Shopify app live, 10+ integrations

**KPIs Month 12 (Aggressive):**
- 1,900+ paying customers
- $66K MRR
- 500M API calls/mo
- Team 8–10 people
- Series A ready ($5–10M на $50–80M valuation)

---

### ФАЗА 3: CATEGORY LEADERSHIP — «Экосистема» (Year 2–3)

**Цель:** $300K+ MRR (Realistic) / $3.9M ARR (Aggressive), Category King, Exit options.

- AI Insights: «Traffic anomaly detected», «Campaign performance summary»
- Marketplace: 3rd-party extensions, custom globe skins
- Enterprise sales: Outbound к 500 target accounts, dedicated AE
- Strategic partnerships: Hosting bundles (Kinsta, Cloudways, WP Engine), ThemeForest
- Acqui-hire / tuck-in: Heatmaps, session replay micro-SaaS
- Universal Reputation Layer concept: переносимая репутация сайта/бренда

**Exit Scenarios:**
- Strategic acquisition: Hotjar, Contentsquare, SimilarWeb, Cloudflare, Datadog — $40M–60M (Aggressive) / $1.5M–5M (Realistic)
- PE roll-up
- Profitable lifestyle business (Realistic path) — $250K ARR, $72K/year each founder

---

## 4. ПЛАН МАРКЕТИНГА: ПОЛНЫЙ ЗАХВАТ НИШИ VISUAL REAL-TIME ANALYTICS

### Стратегия: Product-Led Growth + Affiliate Flywheel + Viral Badge

```
┌─────────────────────────────────────────────────────────────────┐
│                    MARKETING FLYWHEEL                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   🎯 WP.ORG FREE PLUGIN          👥 AFFILIATE ARMY             │
│        │                              │                        │
│        ▼                              ▼                        │
│   ┌─────────┐                     ┌─────────┐                 │
│   │ Banner  │                     │ 30% Rec │                 │
│   │ Upgrade │                     │ Commission              │
│   │ Trial   │                     │ Dashboard               │
│   └────┬────┘                     └────┬────┘                 │
│        │                               │                       │
│        └──────────────┬────────────────┘                       │
│                       ▼                                         │
│            ┌─────────────────────┐                             │
│            │  CLOUD DASHBOARD    │                             │
│            │  (Value Delivery)   │                             │
│            └──────────┬──────────┘                             │
│                       │                                         │
│                       ▼                                         │
│            ┌─────────────────────┐                             │
│            │  VIRAL BADGE        │                             │
│            │  "Powered by"       │                             │
│            │  + Public Share     │                             │
│            └─────────────────────┘                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Канал 1: WP.org Organic Funnel (Primary — 60% trials)
| Action | Owner | Timeline | KPI |
|--------|-------|----------|-----|
| «Upgrade to Cloud Dashboard» banner в free plugin admin | Dev | W1 | 3% CTR |
| In-plugin onboarding tour (3 steps) → «Start 14-day trial» | Dev | W2 | 5% trial start |
| Email sequence: D0 welcome, D2 «see globe», D5 case study, D10 upgrade | Mktg | W2 | 18% trial→paid |
| «Powered by GlobeVis» badge на free глобусе (кликабельно) | Dev | W3 | K-factor 0.3 |
| Ответы на все WP.org support threads → convert to trial | Mktg | Ongoing | 10 trials/mo |

### Канал 2: Affiliate Program (Scale Lever — 25% revenue target)
| Action | Owner | Timeline | KPI |
|--------|-------|----------|-----|
| Rewardful/FirstPromoter setup (30% recurring, 90-day cookie) | Mktg | W1 | Live |
| Recruit 10 founding affiliates (WP agencies, hosts, YouTubers) | Mktg | M1 | 10 partners |
| Affiliate kit: banners, email swipe, demo video, comparison table | Mktg | W2 | Assets ready |
| Monthly newsletter + leaderboard | Mktg | Ongoing | 20% active rate |
| Target: 50 partners M6, 200 partners M12 | Mktg | M6/M12 | 25%/35% rev share |

### Канал 3: Content & SEO (Compound Interest)
| Content Piece | Keyword | Difficulty | Format |
|---------------|---------|------------|--------|
| Best Real-Time Visitor Maps for WordPress 2025 | visitor map wordpress | 28 | Blog + video |
| How to Show Live Traffic on Your Website (No Code) | live traffic website | 35 | Tutorial |
| GlobeVis vs Hotjar vs GA4: Visual Analytics Compared | globevis alternative | 15 | Comparison |
| 10 Ways Agencies Use Live Visitor Globes for Client Reports | agency analytics dashboard | 22 | Listicle |
| Case Study: [E-com Store] Increased Conversions 12% with Live Globe | social proof conversion | 18 | PDF + page |

**Goal:** 50K organic visits/mo by M12 → 1,500 trials/mo

### Канал 4: Launch Events (Spikes)
| Event | Timing | Prep | Expected |
|-------|--------|------|----------|
| AppSumo Select / LTD | Month 2 | 500 codes @ $49, demo video, docs | $25K cash, 500 users, reviews |
| Product Hunt Launch | Month 3 | Hunter booked, 50 upvotes committed | 500 visits, 50 trials |
| WP Tavern / Post Status Feature | Month 3 | Pitch: «First 3D Globe Analytics for WP» | 2,000 visits, credibility |

### Бюджет маркетинга (Realistic Path)
| Категория | M1–M3 | M4–M6 | M7–M12 | Итого Year 1 |
|-----------|-------|-------|--------|--------------|
| Team (contractors) | $0 | $4.5K | $18K | $22.5K |
| Content/SEO | $2K | $3K | $9K | $14K |
| DevRel/Events | $1K | $4K | $12K | $17K |
| Paid Ads | $0 | $2K | $15K | $17K |
| Tools/Infra | $0.5K | $1K | $3K | $4.5K |
| **ИТОГО** | **$3.5K** | **$14.5K** | **$57K** | **~$75K** |

*Reinvest 40% net profit из Month 4. Target: Marketing spend < 30% ARR.*

---

## 5. ТАЙМЛАЙН ЭВОЛЮЦИИ И МАРКЕТИНГА

```
═══════════════════════════════════════════════════════════════════════════════
                        TIMELINE: GLOBEVIS EVOLUTION (0-36 МЕСЯЦЕВ)
═══════════════════════════════════════════════════════════════════════════════

НЕДЕЛИ 1-4 (FOUNDATION)                                    ████████████
├── Stripe Billing: Products, Prices, Checkout, Portal, Webhooks
├── Multi-tenant DB: organizations, sites, events, api_keys, alerts, team_members
├── Dashboard API: orgs → sites → globe + top100 + sparkline
├── WP Plugin v2: "Connect to Cloud" OAuth/API key + WP Cron sync
├── Landing: Hero, Demo Globe, Pricing, FAQ, Comparison, Signup→Checkout
├── Affiliate setup (Rewardful), beta onboarding emails
└── Soft launch: 50 beta users

МЕСЯЦЫ 1-3 (PMF)                                           ████████████████
├── Multi-site, API keys, Alerts (TG/Slack/Email), UTM tracking, Replay
├── WP.org funnel: banner, tour, emails, badge
├── Affiliate: 10 founding partners, kit, newsletter
├── Content: 5 posts/mo, SEO keywords
├── AppSumo LTD (M2), Product Hunt (M3), WP Tavern PR (M3)
├── Target: 100 paying, $3.5K MRR, CAC <$80, Churn <4%

МЕСЯЦЫ 4-6 (EARLY GROWTH)                                  ████████████████████
├── White-label MVP, Team seats RBAC, Affiliate dashboard
├── Theme marketplace, Public share links
├── GA4/Matomo/Plausible integrations
├── Shopify App Store launch
├── Paid ads test (Google + Meta), YouTube sponsorships start
├── Hire: Support (full-time), Content (part-time)
├── Target: 300 paying, $10K MRR, 20% affiliate rev

МЕСЯЦЫ 7-12 (SCALE)                                        ████████████████████████
├── Wix/Webflow apps, Enterprise landing + demo booking
├── Referral program, Webinar series "Live Analytics for Agencies"
├── Internationalization (ES, PT, DE, FR)
├── Agency partner program: co-branded, volume pricing
├── Hire: Growth Marketer (if Aggressive)
├── Target Realistic: 600 paying, $21K MRR, 25% affiliate
├── Target Aggressive: 1,900 paying, $66K MRR, Series A ready

ГОД 2 (CATEGORY LEADERSHIP)                                ████████████████████████████
├── AI Insights: anomaly detection, campaign summaries
├── Marketplace: 3rd-party extensions, custom skins
├── Enterprise sales: 500 target accounts, dedicated AE
├── Hosting bundles (Kinsta, Cloudways, WP Engine), ThemeForest
├── Acqui-hire: heatmaps, session replay
├── Target Realistic: $250K ARR, profitable, $72K/yr each
├── Target Aggressive: $3.9M ARR, $40-60M valuation, exit ready

ГОД 3 (EXIT / SCALE)                                       ████████████████████████████████
├── Realistic: Lifestyle business or $5-10M strategic sale
├── Aggressive: $10M+ ARR, IPO track or $100M+ strategic sale
├── Universal Reputation Layer: portable site/brand reputation

═══════════════════════════════════════════════════════════════════════════════
```

### Key Milestones (Gates)

| Milestone | Deadline | Criteria | Owner |
|-----------|----------|----------|-------|
| **G1: SaaS MVP Live** | Week 4 | Stripe working, Dashboard MVP, WP Plugin v2 connected, 50 beta | Charles |
| **G2: PMF Validated** | Month 3 | 100 paying, $3.5K MRR, CAC <$80, Churn <4%, 20 affiliates | Both |
| **G3: Growth Engine** | Month 6 | 300 paying, $10K MRR, Shopify live, White-label, Support hired | Both |
| **G4: Scale Ready** | Month 12 | Realistic: 600 paying, $21K MRR / Aggressive: 1,900 paying, $66K MRR | Both |
| **G5: Category Leader** | Month 24 | Realistic: $250K ARR profitable / Aggressive: $3.9M ARR, exit ready | Both |

---

## 6. ФИНАНСОВЫЕ ПРОЕКЦИИ: 3 СЦЕНАРИЯ

### Юнит-экономика (Steady State)
| Метрика | Значение |
|---------|----------|
| Blended ARPU | $42/mo ($504/yr) |
| Gross Margin | 89% |
| Monthly Churn | 4% (Realistic) / 2.5% (Aggressive) |
| LTV | $945 (Realistic) / $1,500 (Aggressive) |
| CAC Target | <$315 (LTV/CAC > 3) |
| Blended CAC (actual) | $65 (PLG + Affiliate flywheel) |
| Payback Period | 7 months |

### Сценарий А: ПЕССИМИСТИЧНЫЙ — «Bootstrap Survival»
*Только органика, никакого реинвеста, part-time, нет affine/ads*
- **Year 3:** $2,800 MRR, $34K ARR, 81 customers
- **Founder income:** $12.5K/year each
- **Valuation:** ~$170K
- **Verdict:** Хобби, не бизнес. Не рекомендуется.

### Сценарий Б: РЕАЛИСТИЧНЫЙ — «Profitable Growth» ⭐ РЕКОМЕНДУЕМЫЙ СТАРТ
*$500–7K/mo marketing, 40% profit reinvest, affiliate flywheel, contractors*
- **Year 3:** $21,300 MRR, $256K ARR, 609 customers
- **Founder income:** $72K/year each
- **Cumulative 3-yr cash:** $400K
- **Valuation:** ~$1.5M (6× ARR)
- **Verdict:** Solid lifestyle business. Downside protection, upside optionality.

### Сценарий В: АГРЕССИВНЫЙ — «Category Winner / Market Capture»
*100% revenue reinvest до $50K MRR, затем 80%, затем 60%. Full-time hires, paid ads, $150K burn/mo к Year 2. Нужен $150–300K external capital.*
- **Year 3:** $323,000 MRR, $3.9M ARR, 9,237 customers, team 8–10
- **Founder take-home:** $400K+/year each (post-salaries)
- **Cumulative cash:** $3.5M
- **Valuation:** $40M–60M (10× ARR + growth premium)
- **Verdict:** Category leader. Acquisition target. High execution/cash risk.

### Сравнение

| Метрика | Pessimistic (A) | Realistic (B) | Aggressive (C) |
|---------|-----------------|---------------|----------------|
| Year 3 MRR | $2,800 | $21,300 | $323,000 |
| Year 3 ARR | $34K | $256K | $3.9M |
| Founder Income Y3 | $12.5K | $72K | $400K+ |
| 3-Yr Cash | $75K | $400K | $3.5M |
| Valuation | $170K | $1.5M | $40M–60M |
| Max Burn | $500 | $7K/mo | $150K/mo |
| External Capital | $0 | $0 | $150–300K |
| Time to Profit | Month 5 | Month 4 | Month 18–22 |

---

## 7. РИСКИ И МИТИГАЦИЯ

| Риск | Likelihood | Impact | Митигация |
|------|------------|--------|-----------|
| **WP.org policy change** (ban external connections) | Medium | High | Free plugin fully functional offline; cloud = optional enhancement |
| **Competitor copies visuals + raises $10M** | Medium | High | Moat: white-label, agency workflow, data history, integrations, brand |
| **Stripe/Payment issues** (high-risk countries) | Low | Medium | Stripe Atlas entity, fallback Paddle/LemonSqueezy |
| **Dev burnout** (solo founder) | High | High | Hire contractor by M3, co-founder equity for CTO if needed |
| **Churn higher than expected** | Medium | High | Cohort analysis, cancel flow survey, win-back emails, usage alerts |
| **SEO algorithm update** | Medium | Medium | Diversify: affiliate, paid, email, referral — не SEO-dependent |
| **AppSumo users = high support, low LTV** | High | Medium | Limit LTD seats, separate support tier, upsell to subscription |
| **Charles unavailable / delays** | Medium | High | Clear spec docs, contractor backup, pair programming sessions |

---

## 8. DECISION FRAMEWORK & GATES

### Monthly «Continue / Pivot / Kill» Review (First Friday)

| Gate | Metric | Continue | Pivot | Kill |
|------|--------|----------|-------|------|
| **Month 3** | Paying Customers | >30 | 10–30 | <10 |
| | MRR | >$1,000 | $300–1,000 | <$300 |
| | CAC | <$100 | $100–200 | >$200 |
| **Month 6** | Paying Customers | >100 | 50–100 | <50 |
| | MRR | >$5,000 | $2,000–5,000 | <$2,000 |
| | Churn | <4% | 4–6% | >6% |
| **Month 12** | MRR | >$20,000 | $10,000–20,000 | <$10,000 |
| | Team | 2+ contractors | 1 contractor | 0 |
| | Profitability | Break-even | -$2K/mo | -$5K/mo |

> **Agreement:** Если Kill threshold — graceful wind down, split assets/IP 50/50, no hard feelings.

### Scenario Switch Gates (Realistic → Aggressive)
- **Gate A (Month 3):** $5K MRR + CAC <$80 + LTV >$800 + Churn <4% → Open Aggressive tap
- **Gate B (Month 6):** $15K MRR + Shopify live + 20 affiliates + Paid ads ROAS >3 → Scale to Aggressive budget
- **Gate C (Month 12):** $65K MRR → Series A decision ($1–2M at $10M+ valuation)

---

## 9. IMMEDIATE NEXT STEPS (This Week)

### Charles (Dev) — Technical Foundation
- [ ] **Day 1–2:** Stripe test mode: Products (Starter/Pro/Agency), Prices (mo/yr), Checkout Session API, Customer Portal, Webhooks (`checkout.session.completed`, `customer.subscription.updated`, `invoice.payment_failed`)
- [ ] **Day 3–4:** DB schema: `organizations`, `sites`, `events` (partitioned), `api_keys`, `alerts`, `team_members`, `subscriptions`
- [ ] **Day 5:** `/dashboard` API: Org list → Site detail → Globe iframe + Top 100 + Sparkline
- [ ] **Day 6–7:** WP Plugin v2: Settings «Connect to GlobeVis Cloud» → OAuth/API key → WP Cron sync → success/failure logging

### Marketing Partner — Launch Assets
- [ ] **Day 1:** Positioning canvas: Persona, JTBD, Differentiation, Proof points
- [ ] **Day 2:** Pricing page copy (Notion → Webflow/Framer), FAQ, Comparison vs Hotjar/GA4/Plausible
- [ ] **Day 3:** Onboarding email sequence (5 emails) in Resend/Postmark
- [ ] **Day 4:** Affiliate setup (Rewardful), affiliate kit (banners, swipe, demo video script)
- [ ] **Day 5:** Beta recruitment: 50 WP site owners (Reddit, WP forums, Twitter, cold email)
- [ ] **Day 6:** Launch checklist: Plausible, Hotjar, Sentry, Better Uptime
- [ ] **Day 7:** **Soft launch** to beta → feedback → iterate

### Required Accesses from Charles
| Access | Used For |
|--------|----------|
| Stripe test keys (secret, publishable, webhook secret) | Stripe Billing module |
| Database URL (Postgres: Neon/Supabase/Docker) | Multi-tenant schema |
| WP.org SVN credentials | Plugin v2 deploy |
| Vercel/Netlify access | Landing page deploy |
| Rewardful/FirstPromoter API key | Affiliate program |
| Resend/Postmark API key + verified domain | Email onboarding |
| Sentry / Plausible / Better Uptime DSN | Observability |

---

---

*Document Version: 1.0 | Date: 2026-08-07 | For: Charles Schreiber + Marketing Partner | Confidential*