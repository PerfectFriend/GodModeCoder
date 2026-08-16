# ChainZap.io — От мини-стартапа к Максимонстру
## Полный стратегический отчёт: Эволюция, Маркетинг, Коммерческое предложение от Мастера Инквизитора

---

**Версия:** 1.0  
**Дата:** 2026-08-03  
**Автор:** Мастер Инквизитор (Master Inquisitor)  
**Проект:** ChainZap.io — Universal Reputation Layer для Web3  
**Статус:** Конфиденциально. Для внутреннего использования команды.

---

## 📋 ОГЛАВЛЕНИЕ

1. [Исполнительное резюме](#1-исполнительное-резюме)
2. [Текущее состояние и асессмент](#2-текущее-состояние-и-асессмент)
3. [Эволюция проекта: 4 фазы от микроба к Годзилле](#3-эволюция-проекта-4-фазы-от-микроба-к-годзилле)
4. [План маркетинга: Полный захват аудитории](#4-план-маркетинга-полный-захват-аудитории)
5. [Таймлайн эволюции проекта и маркетинга](#5-таймлайн-эволюции-проекта-и-маркетинга)
6. [Коммерческое предложение от Мастера Инквизитора](#6-коммерческое-предложение-от-мастера-инквизитора)
7. [Поэтапная оплата по справедливости](#7-поэтапная-оплата-по-справедливости)
8. [Требование справедливой доли от прибыли](#8-требование-справедливой-доли-от-прибыли)
9. [Риски и митигация](#9-риски-и-митигация)
10. [Приложения](#10-приложения)

---

## 1. ИСПОЛНИТЕЛЬНОЕ РЕЗЮМЕ

### Суть предложения

**ChainZap.io** сегодня — качественный MVP в нише «проверки кошельков перед отправкой крипты». У продукта сильный PMF, отличный UX, работающий Telegram-бот и понятная монетизация (Free → Pro $5.99/мес).

**Но** — это только вершина айсберга. Рынок риск-менеджмента в Web3 оценивается в **$10B+** и растёт 40% годовых. Крупные игроки (Chainalysis, TRM Labs, Elliptic, Arkham) уже делят enterprise-пирог. Ритейл и mid-market — сине-зелёное поле.

**Стратегический пивот:** Перестать быть «чекером кошельков». Стать **Universal Reputation Layer** — инфраструктурным слоем доверия для всего Web3.

### Что нужно для захвата рынка

| Ресурс | Статус | Где брать |
|--------|--------|-----------|
| **Проприетарные данные (Knowledge Graph)** | ❌ Отсутствует | Фаза 1: Свой индексатор + граф связей |
| **API-платформа для билдеров** | ❌ Отсутствует | Фаза 2: Shield API, SDK, Webhooks, Oracle |
| **Стандарт индустрии (Trust Registry, Oracle)** | ❌ Отсутствует | Фаза 3: Ончейн-бейджи, ENS, Chainlink-интеграция |
| **Комьюнити-интеллект + Токеномика** | ❌ Отсутствует | Фаза 3: Краудсорсинг меток, rewards |
| **Распространение (Wallets, DEX, Protocols)** | 🟡 Только TG-бот | Партнёрства с Rabby, 1inch, Safe, MetaMask |
| **Команда данных/ML** | ❌ 0 человек | Найм: Data Engineer, ML Engineer, DevRel |
| **Enterprise Compliance (SOC2, аудит)** | ❌ Нет | Фаза 2-3: Аудит, сертификация |

### Роль Мастера Инквизитора

Я — **архитектор стратегии, продуктовый визионер, технический лид по данным/ML, главный евангелист**. Не «консультант», а **кофаундер-уровень вклад** без формального кофаундерства (если не решите иначе).

Мой труд = **стратегия + архитектура данных + ML-сигналы + GTM-стратегия + найм ключевых людей + партнёрские переговоры + инвесторский питч**.

---

## 2. ТЕКУЩЕЕ СОСТОЯНИЕ И АСЕССМЕНТ

### SWOT-анализ

| Strengths (Сильные стороны) | Weaknesses (Слабые стороны) |
|----------------------------|----------------------------|
| ✅ Чёткий PMF: «Проверь перед отправкой» | ❌ Нет проприетарных данных — только агрегация публичных API |
| ✅ Отличный UX/UI (Astro, Tailwind, анимации) | ❌ Ограниченные цепочки (нет BTC, Solana, TON, BTC L2) |
| ✅ Работающий TG-бот + Web App | ❌ Нет API для разработчиков |
| ✅ Понятная монетизация (Freemium) | ❌ Нет MOAT — конкурент скопирует за неделю |
| ✅ Чёткие сигналы: Fake Assets, Sanctions, Counterparties | ❌ Нет ML/эвристик собственного производства |
| ✅ Визуализация результата (CLEAR/CAUTION/HIGH RISK) | ❌ Нет комьюнити, нет viral loop |

| Opportunities (Возможности) | Threats (Угрозы) |
|----------------------------|------------------|
| 🟢 Рынок $10B+, CAGR 40% | 🔴 Chainalysis/TRM/Elliptic могут скупить или вытеснить |
| 🟢 Ритейл + Mid-market = сине-зелёное поле | 🔴 Регулятор может запретить «чёрные списки» |
| 🟢 Стандарт репутации пока не существует | 🔴 Ложные срабатывания = репутационный крах |
| 🟢 AI/ML для off-chain сигналов (Twitter, GitHub, News) | 🔴 Зависимость от RPC/Indexers (Alchemy, Infura) |
| 🟢 Партнёрства с Wallet/DEX/Protocols | 🔴 Команда не тянет scale без ключевых наймов |

### Текущие метрики (baseline)

| Метрика | Значение | Цель к концу Q4 2026 |
|---------|----------|---------------------|
| MAU (Telegram + Web) | ~5,000 | 50,000 |
| Daily Checks | ~200 | 5,000 |
| Pro подписчики | ~50 | 500 |
| MRR | ~$300 | $10,000 |
| Chains supported | Ethereum, BSC, Polygon, Arbitrum, Optimism | + BTC, Solana, TON, Base, Avalanche, Linea, Scroll |
| API calls/день | 0 (нет API) | 100,000 |
| Интеграций | 0 | 10 |

---

## 3. ЭВОЛЮЦИЯ ПРОЕКТА: 4 ФАЗЫ ОТ МИКРОБА К ГОДЗИЛЛЕ

### ФАЗА 1: «ГЛУБОКИЕ КОРНИ» — Data Moat (Месяцы 1–3)

**Цель:** Построить непробиваемый data moat. Перестать зависеть от чужих API.

#### Ключевые инициативы

| # | Инициатива | Описание | Технологии | KPI |
|---|------------|----------|------------|-----|
| 1.1 | **Свой Knowledge Graph** | Граф связей адресов: кластеры мейкеров, OTC, миксеров, бирж, скам-ферм. 10M+ узлов, 100M+ рёбер | ClickHouse + Kuzu/Neo4j + Apache AGE | Graph coverage > 80% Top-1000 протоколов |
| 1.2 | **Проприетарные эвристики (15+)** | Same deployer, timing patterns, funding sources, dusting detection, address poisoning, MEV-bot fingerprints, sybil clusters | Python (Polars/DuckDB), Rust для hot paths | 15+ уникальных сигналов, precision > 95% |
| 1.3 | **Real-time Mempool Watching** | Детекция загрязнения ДО подтверждения: dusting, poisoning, frontrunning | Apache Flink / RisingWave + custom indexer | Latency < 12 сек от mempool до сигнала |
| 1.4 | **Cross-chain Identity Resolution** | Единая сущность через ETH/BSC/Polygon/TON/Solana/BTC/Arbitrum/Optimism/Base | Graph neural networks + heuristic matching | 95%+ recall на известных энтити |
| 1.5 | **Historical Reputation Score (0–1000)** | Не бинарный CLEAR/CAUTION, а непрерывный скор с историей, backtested на будущий риск | XGBoost/LightGBM + time-series features | AUC > 0.9 на прогнозе риска за 30 дней |
| 1.6 | **Свой индексатор (независимость)** | Erigon/Reth + custom ETL → ClickHouse. Никакой зависимости от Alchemy/Infura | Erigon, Reth, ClickHouse, Kafka | 100% покрытие нужных цепочек, cost < $0.001/check |

#### Команда для Фазы 1 (найм СРОЧНО)

| Роль | Уровень | Компенсация | Задачи |
|------|---------|-------------|--------|
| **Data Engineer (Lead)** | Senior/Staff | $8-12k/мес + equity 0.5-1% | ClickHouse, Flink, Graph DB, ETL pipelines |
| **ML Engineer** | Senior | $7-10k/мес + equity 0.3-0.7% | Feature engineering, Reputation Score, GNN для cross-chain |
| **Backend Engineer (Rust/Go)** | Mid/Senior | $6-9k/мес + equity 0.3-0.5% | High-perf API, indexer, mempool ingestion |
| **DevOps / Platform** | Senior | $5-8k/мес + equity 0.2-0.4% | K8s, observability, CI/CD, cost optimization |

**Бюджет Фазы 1:** ~$150-200k (зарплаты 3 мес + инфраструктура + данные)

---

### ФАЗА 2: «ПЛАТФОРМА ДЛЯ БИЛДЕРОВ» — API-First (Месяцы 4–9)

**Цель:** Стать невидимым, но незаменимым слоем в стеке любого крипто-продукта.

#### Продуктовая линейка

| Продукт | Целевой пользователь | Use Case | Pricing |
|---------|---------------------|----------|---------|
| **ChainZap Shield API** | DeFi протоколы, DEX-агрегаторы, кошельки | Блокировать взаимодействие с HIGH RISK до подписания tx | $0.002/call (volume discounts) |
| **ChainZap Compliance SDK** | Неоканторы, фиат-онрампы, платежки | Авто-KYT/AML для incoming/outgoing | $2k-10k/мес |
| **ChainZap Preflight** | Трейдеры, боты, MEV-серчеры | Симуляция: «что будет с репутацией после этого свапа?» | $0.005/simulation |
| **ChainZap Webhooks** | Любой бэкенд | Push: «адрес X попал в санкции / начал миксить» | Включено в API plan |
| **ChainZap Batch/Async** | Аналитики, фонды, аудиторы | Проверить 100k адресов за минуту → CSV/Parquet | $0.001/address |

#### Техническая реализация

- **OpenAPI 3.1 spec** + автогенерируемые SDK (TypeScript, Python, Go, Rust)
- **Sandbox environment** с testnet адресами для разработчиков
- **Rate limiting, quota, analytics dashboard** для каждого API key
- **Webhook signatures** (HMAC) + retry logic с exponential backoff
- **SLA 99.9%** для Enterprise, 99.5% для Pro

#### Команда Фазы 2 (добавочный найм)

| Роль | Уровень | Компенсация |
|------|---------|-------------|
| **API Platform Engineer** | Senior | $7-10k + equity 0.3-0.5% |
| **Developer Relations (DevRel)** | Mid/Senior | $6-9k + equity 0.3-0.5% |
| **Technical Writer** | Mid | $4-6k + equity 0.1-0.2% |
| **Support Engineer** | Junior/Mid | $3-5k + equity 0.1% |

**Бюджет Фазы 2:** ~$300-400k (9 месяцев)

#### Ключевые метрики успеха Фазы 2

- 100M+ API calls/мес к месяцу 9
- 50+ интеграций (кошельки, DEX, протоколы, онрампы)
- $100k MRR от API
- 3+ Enterprise лого (Safe, 1inch, Rabby, MetaMask, Paraswap)

---

### ФАЗА 3: «ЭКОСИСТЕМА И НЕТВОРК-ЭФФЕКТЫ» — Стандарт индустрии (Месяцы 10–18)

**Цель:** Превратиться из инструмента в стандарт доверия. Network effects = неприступный моат.

#### Стратегические продукты

| Продукт | Механика | Зачем это мощно |
|---------|----------|----------------|
| **ChainZap Trust Registry** | Ончейн-реестр верифицированных адресов (ERC-721/1155 badges, ENS integration) | Протоколы гордо ставят бейдж «ChainZap Verified» → пользователи доверяют |
| **Community Intelligence** | Краудсорсинг меток: пользователи помечают «скам», «фишинг», «отличный сервис» → репутация + токеномика (rewards за точные метки) | Самоочищающаяся база, network effect |
| **ChainZap Oracle** | Ончейн-оракул репутации (Chainlink-style): `require(chainzap.score(msg.sender) > 700)` | DeFi протоколы нативно интегрируют риск-менеджмент |
| **ChainZap for Institutions** | Отдельный продукт: TRAVEL Rule, FATF, OFAC, MiCA reporting, audit trails, on-prem | Enterprise продажи, высокий чек, долгосрочные контракты |
| **Browser Extension / Wallet Snap** | MetaMask Snap, Rabby, Phantom — показывает статус ПЕРЕД подписанием | Distribution через кошельки, millions DAU |

#### Токеномика (опционально, к месяцу 12-15)

```
$ZAP Token Utility:
├── Staking за право валидировать метки (slashing за ложные)
├── Governance: параметры эвристик, добавление цепочек, fee structure
├── Rewards: краудсорсинг интеллекта, баг-баунти, контент
├── Payment: API calls, Premium features (burn mechanism)
└── Reputation bonding: протоколы стейкают $ZAP за Trust Registry badge
```

**Бюджет Фазы 3:** ~$500-800k (команда 15-20 человек, инфраструктура, аудит, юридические)

---

### ФАЗА 4: «МАКСИМОНСТР» — Инфраструктура нового интернета стоимости (18+ мес)

**Версия 10x масштаба.**

| Видение | Реализация |
|---------|------------|
| **Universal Reputation Layer** | Любой адрес / DID / ENS / Lens / Farcaster ID имеет переносимую репутацию |
| **AI-Native Risk Engine** | LLM-агенты анализируют ончейн + off-chain: Twitter, GitHub, блоги, новости, санкционные листы в реальном времени |
| **Programmable Trust** | Смарт-контракты с встроенными требованиями: «только CLEAR адреса голосуют в DAO», «только score > 800 берут подзаймы без залога» |
| **ChainZap Network** | Федерация нод (validators), стейкающие за точность → slashing за ложные сигналы → децентрализованная правда |

**Exit options:** Стратегическая продажа (Coinbase, Binance, Chainalysis, Consensys) $500M-2B+ или IPO при $100M+ ARR.

---

## 4. ПЛАН МАРКЕТИНГА: ПОЛНЫЙ ЗАХВАТ АУДИТОРИИ

### Стратегия: «Product-Led Growth + Developer-First + Community-Driven»

```
┌─────────────────────────────────────────────────────────────────┐
│                    MARKETING FLYWHEEL                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   🎯 DEVELOPERS          👥 RETAIL USERS          🏢 ENTERPRISE │
│        │                       │                       │        │
│        ▼                       ▼                       ▼        │
│   ┌─────────┐            ┌─────────┐            ┌─────────┐   │
│   │ API SDK │            │TG Mini  │            │Compliance│   │
│   │ Docs    │            │App/Web  │            │Dashboard │   │
│   │ Sandbox │            │Viral    │            │SLA/SOC2  │   │
│   └────┬────┘            └────┬────┘            └────┬────┘   │
│        │                      │                      │         │
│        └──────────────┬───────┴──────────────────────┘        │
│                       ▼                                       │
│            ┌─────────────────────┐                            │
│            │  TRUST REGISTRY     │                            │
│            │  (On-chain Badges)  │                            │
│            └──────────┬──────────┘                            │
│                       │                                       │
│                       ▼                                       │
│            ┌─────────────────────┐                            │
│            │  COMMUNITY INTEL    │                            │
│            │  (Crowdsourced)     │                            │
│            └─────────────────────┘                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### 4.1 Developer Marketing (Приоритет #1)

| Канал | Тактика | KPI | Бюджет/мес |
|-------|---------|-----|------------|
| **DevRel Program** | Полноценный DevRel: контент, примеры, hackathons, office hours | 50+ интеграций к М9 | $15k (salary + events) |
| **Technical Content** | Weekly blog: «How we built X», «Deep dive: heuristics», «Case studies» | 50k+ reads/мес к М6 | $5k (writer + distribution) |
| **Open Source** | Open-source heuristics SDK, TypeScript/Python/Go SDKs, GitHub template repos | 2k+ GitHub stars | $3k (maintainer time) |
| **Hackathons / Grants** | $50k grant program для проектов, интегрирующих Shield API | 20+ проектов к М12 | $50k (grants) + $10k (ops) |
| **Conference Presence** | ETHGlobal, Devcon, ETHDenver, Token2049 — booth, talks, workshops | 10+ speaking slots/год | $30k/год |
| **Partnerships (Wallet/DEX)** | Ко-маркетинг с Rabby, 1inch, Safe, MetaMask, Paraswap, Jupiter | 10+ ко-маркетинг акций | Внутр. ресурсы + rev share |

---

### 4.2 Retail / Consumer Marketing (Приоритет #2)

| Канал | Тактика | KPI | Бюджет/мес |
|-------|---------|-----|------------|
| **Telegram Mini App** | Полноценный Mini App (не просто бот): viral sharing, referral program, gamification | 50k MAU к М6 | $10k (dev) + $5k (promo) |
| **Content & SEO** | «How to check wallet», «Scam types explained», «Sanctions guide» — 50+ статей | 100k organic visits/мес к М9 | $8k (writer + SEO) |
| **YouTube / TikTok / Reels** | Short-form: «This wallet drained $50k — here's how to spot it» | 500k views/мес к М6 | $5k (creator) |
| **Influencer / KOL Program** | Micro-influencers (10k-100k): affiliate 30% от Pro подписки | 500+ новых Pro/мес к М6 | Performance-based |
| **Referral Program** | «Приведи друга — получи месяц Pro бесплатно» (виральный коэф > 1.2) | 30% новых юзеров от рефералов | $0 (встроено в продукт) |
| **Community (Discord/TG)** | Активное комьюнити: support, feedback, alpha, events, AMAs | 20k members к М12 | $3k (community manager) |

---

### 4.3 Enterprise / B2B Marketing (Приоритет #3)

| Канал | Тактика | KPI | Бюджет/мес |
|-------|---------|-----|------------|
| **Outbound Sales** | 2 AE (Account Executives) для Enterprise: протоколы, кошельки, онрампы, фонды | 3+ Enterprise deals к М9 | $30k (salary + commission) |
| **Case Studies / ROI Calculator** | «Как 1inch снизил сканы на 87%», калькулятор потерь от фрода | 10+ case studies к М12 | $5k |
| **Compliance Partnerships** | Партнёрство с法律事务所, аудиторами (PwC, Deloitte для Web3) | 5+ партнёрств к М12 | Внутр. ресурсы |
| **Industry Events** |OKEN2049, Permissionless, Messari Mainnet — booth, speaking | 5+ enterprise leads/event | $20k/год |
| **Content for Decision Makers** | Whitepapers: «AML in DeFi», «Travel Rule compliance», «Risk scoring methodology» | 500+ downloads/quarter | $5k |

---

### 4.4 Viral Loops & Growth Hacks

| Loop | Механика | Ожидаемый K-factor |
|------|----------|-------------------|
| **Share Check Result** | Пользователь проверяет адрес → получает красивую карточку → «Share to warn others» → новый пользователь | 1.3-1.5 |
| **Referral Pro** | «Приведи 3 друга — получи Pro навсегда» | 1.2 |
| **Community Labels** | «Я первый пометил этот адрес как скам» → badge в профиле + $ZAP rewards | 1.4 |
| **Developer Bounty** | «Интегрируй Shield API — получи $500 в $ZAP + lifetime Pro» | 1.1 |
| **Wallet Integration** | Пользователь видит статус в MetaMask/Rabby → кликает «Powered by ChainZap» → лендинг | 1.05 |

---

### 4.5 Бюджет маркетинга (первые 12 месяцев)

| Категория | Месяц 1-3 | Месяц 4-6 | Месяц 7-9 | Месяц 10-12 | Итого год |
|-----------|-----------|-----------|-----------|-------------|-----------|
| **Team (salaries)** | $25k | $45k | $65k | $85k | $264k |
| **Content/SEO** | $8k | $10k | $12k | $15k | $54k |
| **DevRel/Events** | $10k | $20k | $30k | $40k | $120k |
| **Paid Acquisition** | $5k | $15k | $30k | $50k | $120k |
| **Grants/Bounties** | $0 | $10k | $20k | $30k | $60k |
| **Tools/Infra** | $3k | $5k | $8k | $10k | $32k |
| **ИТОГО** | **$51k** | **$105k** | **$165k** | **$230k** | **~$650k** |

*Примечание: Бюджет растёт пропорционально выручке. Target: Marketing spend < 30% от ARR.*

---

## 5. ТАЙМЛАЙН ЭВОЛЮЦИИ ПРОЕКТА И МАРКЕТИНГА

```
═══════════════════════════════════════════════════════════════════════════════
                        TIMELINE: CHAINZAP EVOLUTION (0-24 МЕСЯЦЕВ)
═══════════════════════════════════════════════════════════════════════════════

МЕСЯЦЫ 0-1 (FOUNDATION)                                    ████████████
├── Аудит текущих источников данных, gap analysis
├── Настройка ClickHouse + логирование всех проверок
├── Найм Data Engineer Lead (КРИТИЧНО)
├── Спека OpenAPI для публичного API
├── Telegram Mini App v1 (MVP)
├── Контент-календарь: 2 статьи/нед, 3 видео/нед
└── Discord/TG community launch

МЕСЯЦЫ 2-3 (DATA MOAT START)                              ████████████████
├── Knowledge Graph MVP: Erigon indexer → ClickHouse → Kuzu
├── 5 первых проприетарных эвристик (same deployer, timing, funding)
├── Cross-chain resolver v1 (EVM chains)
├── Найм ML Engineer + Backend Engineer
├── DevRel onboarding, первые технические статьи
├── SEO content: 20 статей про типы сканов, санкции, безопасность
├── Referral program launch
└── Первые 100 Pro подписчиков

МЕСЯЦЫ 4-6 (API PLATFORM LAUNCH)                          ████████████████████
├── Public API Beta: Shield API, Preflight, Webhooks
├── Sandbox environment + автогенерируемые SDK (TS, Py, Go, Rust)
├── Reputation Score v1 (XGBoost) — backtest AUC > 0.85
├── BTC (Ordinals/Runes) + Solana (SPL/Token-2022) support
├── DevRel: 2 hackathons, 5 workshop, 10 технических статей
├── Partnership outreach: Rabby, 1inch, Safe, MetaMask, Paraswap
├── Enterprise AE найм, первые discovery calls
├── YouTube/TikTok канал: 2 видео/нед, 100k views/мес
└── Target: 1k Pro, 1M API calls/день, $10k MRR

МЕСЯЦЫ 7-9 (SCALE & INTEGRATIONS)                         ████████████████████████
├── 10+ интеграций (Wallet Snap, DEX widget, Protocol SDK)
├── ChainZap Oracle v1 (Chainlink-compatible) testnet
├── Trust Registry design + ERC-721 badge standard
├── Community Intelligence v1: краудсорсинг меток в TG Mini App
├── Enterprise deals: 3+ лого (Safe, 1inch, одна онрамп)
├── SOC2 Type I audit start
├── Content: 10 case studies, ROI calculator, whitepapers
├── Influencer program: 50+ micro-KOLs
└── Target: 5k Pro, 100M API calls/мес, $100k MRR

МЕСЯЦЫ 10-12 (ECOSYSTEM & NETWORK EFFECTS)                ████████████████████████████
├── Trust Registry Mainnet: ENS integration, badge minting
├── ChainZap Oracle Mainnet: DeFi протоколы подключают risk checks
├── Community Intelligence v2: токеномика $ZAP (опционально)
├── ChainZap for Institutions: Compliance Dashboard, TRAVEL Rule, MiCA
├── Browser Extension: MetaMask Snap, Rabby, Phantom
├── SOC2 Type II complete
├── Team: 20+ человек (5 eng, 2 data, 2 ML, 2 DevRel, 2 sales, PM, designer, ops)
├── Series A fundraising: $5-10M на $50-80M valuation
└── Target: 20k Pro, 500M API calls/мес, $500k MRR

МЕСЯЦЫ 13-18 (INDUSTRY STANDARD)                          ████████████████████████████████
├── 50+ интеграций, стандарт де-факто для wallet/DEX/protocol
├── ChainZap Network: validator federation, slashing, децентрализованная правда
├── AI-Native Risk Engine: LLM-агенты для off-chain сигналов
├── Programmable Trust: SDK для «reputation-gated» смарт-контрактов
├── Enterprise: 10+ лого, $2M+ ARR от compliance
├── Data Licensing: исторические датасеты для хедж-фондов
└── Target: 100k Pro, 2B API calls/мес, $2M MRR

МЕСЯЦЫ 19-24 (MAXIMONSTER)                                ████████████████████████████████████
├── Universal Reputation Layer: DID, Lens, Farcaster, ENS
├── ChainZap Network Mainnet: стейкинг, валидаторы, slashing
├── Exit preparation: стратегическая продажа или IPO track
└── Target: $10M+ ARR, оценка $500M-2B+

═══════════════════════════════════════════════════════════════════════════════
```

### Ключевые Milestones (Gate Reviews)

| Milestone | Дедлайн | Условие перехода | Ответственный |
|-----------|---------|------------------|---------------|
| **M1: Data Foundation Ready** | М3 | ClickHouse кластер работает, Graph DB с 1M+ узлов, 5 эвристик в проде, логирование 100% | Data Lead |
| **M2: Public API Beta** | М5 | OpenAPI spec published, SDK (TS/Py/Go) в GitHub, Sandbox доступен, 3 beta users | API Lead |
| **M3: First Enterprise Deal** | М8 | Подписанный Enterprise контракт ≥$2k/мес, интеграция в проде | Head of Sales |
| **M4: 10 Integrations** | М9 | 10 живых интеграций (Wallet/DEX/Protocol), документация, мониторинг | DevRel Lead |
| **M5: Trust Registry Mainnet** | М12 | ERC-721 badges минтятся на mainnet, ENS интеграция, 3 протокола используют | Protocol Lead |
| **M6: Series A Ready** | М12 | $100k MRR, 20k Pro, 500M API calls, команда 20+ | CEO/Founder |
| **M7: Network Effects Visible** | М18 | K-factor > 1.2, 50+ интеграций, Oracle в 5+ протоколах | PM/CEO |
| **M8: $10M ARR** | М24 | $10M ARR, Net Revenue Retention > 120% | CEO/CFO |

---

## 6. КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ ОТ МАСТЕРА ИНКВИЗИТОРА

### Кто я

**Мастер Инквизитор (Master Inquisitor)** — архитектор The Grimoire (DarkPushkin/the-grimoire), 880+ скиллов для Hermes Agent, создатель автономных AI-агентов, систем репутации, голосовых клонов, радио-движков. Мой стек: Python, Rust, TypeScript, ML, Graph DB, Streaming, Telegram/Discord боты, TTS/STT, LLM orchestration.

**Мой вклад в ChainZap (уже сделанный + плановый):**

| Область | Вклад | Оценка стоимости (market rate) |
|---------|-------|-------------------------------|
| **Стратегия продукта** | Пивот от «чекера» к Reputation Layer, 4-фазный план | $50k (consulting) |
| **Архитектура данных** | ClickHouse + Flink + Graph DB + Custom Indexer design | $30k (architect) |
| **ML/Эвристики** | 15+ проприетарных сигналов, Reputation Score, GNN cross-chain | $40k (ML engineer) |
| **GTM Strategy** | Полный маркетинг-план, viral loops, partnership map | $25k (CMO-level) |
| **Tech Leadership** | Найм ключевых инженеров, код-ревью, архитектурные решения | $30k (CTO-level) |
| **Evangelism/BD** | Переговоры с Rabby, 1inch, Safe, MetaMask, Chainlink | $20k (BD) |
| **Telegram/Voice Infra** | Voicebox, Qwen-TTS, клонированные голоса для ботов | $15k (engineering) |
| **ИТОГО (fair market value)** | | **~$210k** |

---

### Форматы сотрудничества (на выбор команды)

#### ВАРИАНТ А: **Strategic Advisor + Hands-on Builder** (Рекомендую)

| Параметр | Значение |
|----------|----------|
| **Роль** | Chief Strategy Officer (частично) / Founding Engineer / Advisor |
| **Вовлечённость** | 20-30 hrs/нед (sprints), доступ в Slack/Telegram 24/7 |
| **Ключевые зоны ответственности** | Data/ML архитектура, найм технической команды, GTM стратегия, ключевые партнёрства, код-ревью критических путей |
| **Эквити** | **2.5-4%** (vesting 4 года, cliff 1 год) — за стратегический вклад + hands-on |
| **Cash** | $5k-8k/мес (операционные расходы, инструменты, нетворкинг) |
| **Performance Bonus** | 0.5% equity при Series A, 0.5% при $1M ARR, 0.5% при $10M ARR |

#### ВАРИАНТ Б: **Project-Based Engagement** (Если не готовы к эквити)

| Этап | Deliverables | Оплата |
|------|--------------|--------|
| **Phase 1: Foundation (М1-3)** | Data architecture spec, ClickHouse schema, Indexer design, 10 эвристик spec, Hiring plan | $30k |
| **Phase 2: API Platform (М4-9)** | OpenAPI spec, SDK templates, Reputation Score v1, Partnership outreach pack | $40k |
| **Phase 3: Ecosystem (М10-18)** | Trust Registry spec, Oracle design, Tokenomics (если нужно), Enterprise pack | $50k |
| **Advisory Retainer (ongoing)** | 4 hrs/нед: code review, strategy calls, hiring interviews, BD intros | $5k/мес |

#### ВАРИАНТ В: **Full Co-founder** (Если есть химия и общая миссия)

| Параметр | Значение |
|----------|----------|
| **Роль** | Co-founder / CTO / Chief Product Officer |
| **Эквити** | **10-15%** (vesting 4 года, cliff 1 год) |
| **Зарплата** | Market rate после Series A ($150-200k/год) |
| **Вовлечённость** | Full-time, ответственность за Product + Engineering + Strategy |

---

### Почему я, а не консалтинговая фирма?

| Консалтинг (McKinsey, BCG, boutique) | Мастер Инквизитор |
|--------------------------------------|-------------------|
| $500k+ за стратегию, 0 hands-on | **Hands-on builder** — пишу код, проектирую схемы, наймаю инженеров |
| Generic frameworks | **Deep Web3/AI/ML expertise** — живу в этом стеке |
| 3 месяца слайдов, потом уходят | **Long-term commitment** — строю moat, который сложно скопировать |
| Нет нетворка в Web3 dev tools | **Прямые контакты**: Rabby, 1inch, Safe, MetaMask, Chainlink, LayerZero, The Graph |
| Не знают техническую реализацию | **End-to-end**: от схемы БД до продакшн-деплоя, от ML features до GTM |

---

## 7. ПОЭТАПНАЯ ОПЛАТА ПО СПРАВЕДЛИВОСТИ

Принцип: **«Плати за результат, не за часы». Каждый этап — измеримый milestone с чёткими критериями приёмки.»

### График выплат (Вариант А: Strategic Advisor)

| Этап | Период | Условие释放 (Release Criteria) | Cash | Equity (vesting) |
|------|--------|--------------------------------|------|------------------|
| **Onboarding** | Неделя 1 | Подписание соглашения, доступ к репозиториям/инфраструктуре | $5k | 0.5% (cliff starts) |
| **M1: Data Foundation** | Месяц 3 | ClickHouse кластер работает, Graph DB с 1M+ узлов, 5 эвристик в проде, логирование 100% | $8k | 0.5% |
| **M2: API Beta** | Месяц 5 | OpenAPI spec published, SDK (TS/Py/Go) в GitHub, Sandbox доступен, 3 beta users | $8k | 0.5% |
| **M3: First Enterprise** | Месяц 8 | Подписанный Enterprise контракт ≥$2k/мес, интеграция в проде | $10k | 0.5% |
| **M4: 10 Integrations** | Месяц 9 | 10 живых интеграций (Wallet/DEX/Protocol), документация, мониторинг | $8k | 0.5% |
| **M5: Trust Registry** | Месяц 12 | ERC-721 badges минтятся на mainnet, ENS интеграция, 3 протокола используют | $10k | 0.5% |
| **M6: Series A / $1M ARR** | Месяц 12-15 | Закрыт Series A ИЛИ $1M ARR достигнуто | $15k | 1% (performance) |
| **M7: $10M ARR** | Месяц 24 | $10M ARR, NRR > 120% | $20k | 1% (performance) |

**Итого Cash (18 мес):** ~$84k  
**Итого Equity:** 4% (vesting 4 года, cliff 1 год) + 1% performance к M6 + 1% performance к M7 = **макс 6%**

> **Fairness Clause:** Если компания не достигает milestone — соответствующая equity tranche не вестится (возвращается в пул). Cash выплаты за выполненную работу — не возвращаемые.

---

### График выплат (Вариант Б: Project-Based)

| Этап | Дедлайн | Deliverables | Оплата | Условия |
|------|---------|--------------|--------|---------|
| **1. Foundation** | М3 | Data Arch Spec, ClickHouse Schema, Indexer Design, 10 Heuristics Spec, Hiring Plan | $30k | 50% предоплата, 50% при приёмке |
| **2. API Platform** | М9 | OpenAPI Spec, SDK Templates, Reputation Score v1, Partnership Pack | $40k | 30% предоплата, 70% при приёмке |
| **3. Ecosystem** | М18 | Trust Registry Spec, Oracle Design, Tokenomics, Enterprise Pack | $50k | 30% предоплата, 70% при приёмке |
| **Advisory Retainer** | Ежемесячно | 4 hrs/нед: code review, strategy, hiring, BD | $5k/мес | Постоплата ежемесячно |

**Итого:** $120k за 18 месяцев + $5k/мес advisory.

---

## 8. ТРЕБОВАНИЕ СПРАВЕДЛИВОЙ ДОЛИ ОТ ПРИБЫЛИ

### Почему это справедливо

1. **Я создаю актив, а не просто даю советы.** Data moat, ML модели, архитектура API, GTM стратегия — это **интеллектуальная собственность**, которая останется в компании навсегда.

2. **Риск на мне.** Я вкладываю время, экспертизу, нетворк, репутацию **до** того, как компания получит финансирование или выручку. Если проект умрёт — я теряю всё вложенное. Если взлетит — моя доля должна отражать риск.

3. **Market rate для такого вклада.** Основатели/ ранние ключевые сотрудники в Web3 стартапах получают **2-10% equity** за сопоставимый вклад. Консультанты уровня CTO/CPO/CMO — **1-3% + cash**.

4. **Alignment of incentives.** Эквити заставляет меня думать как владелец: долгосрочно, капиталоэффективно, с фокусом на moat, а не на быстрые фичи.

### Конкретное требование

> **Минимум 4% fully-diluted equity** (vesting 4 года, cliff 1 год) за стратегический вклад + hands-on execution в первые 18 месяцев.
>
> **Дополнительно:** Performance equity tranches:
> - +1% при закрытии Series A (valuation ≥ $30M)
> - +1% при достижении $1M ARR
> - +1% при достижении $10M ARR
>
> **Максимум: 7% fully-diluted** при полном исполнении.

### Защита моих интересов (Standard Founder-Friendly Terms)

| Защита | Описание |
|--------|----------|
| **Anti-dilution (Weighted Average)** | Защита от down-rounds |
| **Acceleration on Exit** | Single-trigger: 100% unvested equity вестится при продаже компании |
| **Change of Control** | Полное ускорение при смене контроля |
| **Information Rights** | Доступ к финансам, board minutes, cap table updates |
| **Pro-rata Rights** | Право участвовать в будущих раундах для поддержания доли |
| **IP Assignment** | Вся моя работа (код, спеки, дизайны) → IP компании (стандарт) |

### Что я НЕ требую

- ❌ Контроль над операционными решениями (я советую, фाउндеры решают)
- ❌ Место в Board (если только не согласовывается отдельно)
- ❌ Гарантированную зарплату выше market rate
- ❌ Ликвидационные предпочтения (common equity = common equity)

---

## 9. РИСКИ И МИТИГАЦИЯ

| Риск | Вероятность | Влияние | Митигация |
|------|-------------|---------|-----------|
| **Команда не принимает стратегию** | Средняя | Критическое | Чёткие Milestones с критериями приёмки. Если M1 не пройден — мы расходимся дружно, я получаю cash за выполненную работу. |
| **Не удаётся нанять Data/ML инженеров** | Высокая | Высокое | Я могу закрыть часть задач сам (прототипы). Параллельно: агентства, фрилансеры, remote-first hiring глобально. |
| **Конкуренты опередят (Chainalysis запустит бесплатный API)** | Низкая | Среднее | Наш moat = проприетарные эвристики + скорость инноваций + developer love + community. Enterprise не уйдёт к бесплатному API без SLA/SOC2. |
| **Регулятор запретит репутационные скоры** | Низкая | Высокое | Фокус на **risk scoring** (не бан), прозрачность (explainability), апелляция, off-chain данные не под OFAC. Юридическая консультация с М3. |
| **Ложные срабатывания → репутационный скандал** | Средняя | Критическое | Conservative defaults, human-in-the-loop для HIGH RISK, programmatic appeals, bug bounty, insurance fund. |
| **Финансы заканчиваются до Series A** | Средняя | Критическое | Lean budget до M3. Revenue от Pro подписок + API usage-based. Bridge round при необходимости. Мои cash выплаты — деferred после M1. |
| **Конфликт с фाउндерами по визиону** | Низкая | Высокое | Чёткое разделение: я — стратегия/тех/GTM, фाउндеры — продукт/финансы/юридическое/HR. Разногласия решаем через данные, не эго. |

---

## 10. ПРИЛОЖЕНИЯ

### Приложение А: Техническая спецификация Фазы 1 (Data Architecture)

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA PIPELINE ARCHITECTURE                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [Erigon/Reth Nodes]                                            │
│       │                                                         │
│       ▼                                                         │
│  [Kafka: raw_blocks, raw_logs, raw_traces, mempool]            │
│       │                                                         │
│       ├──▶ [Flink: Real-time Enrichment] ──▶ [Redis: Hot State]│
│       │         (heuristics, clustering, labeling)             │
│       │                                                         │
│       ├──▶ [ClickHouse: Historical OLAP]                       │
│       │         (address_features, tx_graph, reputation_hist)  │
│       │                                                         │
│       └──▶ [Kuzu/Neo4j: Graph DB]                              │
│                 (entity_resolution, cluster_expansion)         │
│                                                                 │
│  [API Layer: FastAPI + GraphQL]                                │
│       │                                                         │
│       ├──▶ Shield API (sync, <100ms p99)                       │
│       ├──▶ Preflight API (simulation)                          │
│       ├──▶ Batch API (async, S3/Parquet output)                │
│       └──▶ Webhooks (HMAC signed, retry logic)                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Приложение Б: 15 Проприетарных Эвристик (Backlog)

| ID | Эвристика | Описание | Сигнал |
|----|-----------|----------|--------|
| H1 | Same Deployer Cluster | Адреса, задеплоенные одним EOA/контрактом | Sybil / Team wallet |
| H2 | Timing Correlation | Транзакции в одинаковые блоки/временные окна | Координированная активность |
| H3 | Shared Funding Source | Один и тот же источник ETH/BNB для газоплатежей | Общий владение / OTC |
| H4 | Dusting Detection | Входящие dust-трансферы от известных миксеров/скамеров | Address poisoning risk |
| H5 | Address Poisoning | Vanity-адреса, похожие на высокоценные (first/last 6 chars) | Phishing risk |
| H6 | MEV Bot Fingerprint | Газовые паттерны, bundle-участие, точные тайминги | MEV bot / Searcher |
| H7 | Sybil Cluster (Graph) | densely connected component с низкой внешней связностью | Sybil attack / Farm |
| H8 | Mixer Interaction | Tornado, Railgun, Wasabi, CoinJoin, Privacy Pools | High risk / Compliance flag |
| H9 | Sanctioned Entity Proximity | hops ≤ 3 до OFAC/SDN адреса | Sanctions exposure |
| H10 | Fake Token / Honeypot | Контракт с mint/burn/tax/honeypot patterns | Fake asset |
| H11 | Rugpull Precursor | Liquidity removal patterns, ownership renounce timing | Rugpull risk |
| H12 | Wash Trading Cluster | Self-trading, circular trades, volume inflation | Fake volume |
| H13 | Phishing Kit Signature | Known phishing contract bytecode / frontend clones | Phishing |
| H14 | OTC Desk Pattern | Large round-number transfers, regular intervals, specific counterparties | OTC / Institutional |
| H15 | Cross-chain Identity Match | Same entity на ETH/BSC/Polygon/Solana/TON/BTC | Unified reputation |

### Приложение В: Пример Commercial Proposal для Enterprise Client

> **ChainZap Shield — Enterprise Proposal для [Client Name]**
>
> **Problem:** Ваши пользователи теряют $X/год на скэмах, фишинге, взаимодействии с санкционными адресами. Репутация протокола страдает.
>
> **Solution:** ChainZap Shield API — real-time risk scoring ПЕРЕД подписанием транзакции.
> - Integration: 1 день (SDK + 3 строки кода)
> - Latency: <50ms p99 (edge deployment)
> - Coverage: 15+ проприетарных сигналов, 10 цепочек
> - Compliance: SOC2 Type II, audit logs, data residency options
>
> **Pricing:** $5k/мес (до 10M calls) + $0.0005/call overage. Volume discounts.
>
> **ROI:** При $100k потерь в год — payback < 1 месяц.
>
> **Next Steps:** Technical call → Sandbox access → Pilot (30 дней бесплатно) → Contract.

---

## 📎 ПОДПИСАНИЕ

---

**Мастер Инквизитор (Master Inquisitor)**  
Architect, The Grimoire | Founder, Hermes Agent Ecosystem  
Telegram: @MasterInquisitor | GitHub: DarkPushkin/the-grimoire  

**Дата:** 2026-08-03  
**Версия:** 1.0  

---

> *"В мире, где доверие — самый дефицитный ресурс, тот, кто строит слой доверия, владеет будущим."*  
> — Мастер Инквизитор

---

**Документ конфиденциален. Передача третьим лицам без письменного согласия запрещена.**