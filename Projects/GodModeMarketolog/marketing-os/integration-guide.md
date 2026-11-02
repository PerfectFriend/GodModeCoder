# Marketing OS — Unified Knowledge Base

> **Объединённый источник:** marketingos.ru (теория) + itsapola/marketing-os GitHub (практика) + кейс Metadata
> **Дата обновления:** 2026-08-19
> **Готов к интеграции в GodModeMarketolog**

---

## 🎯 Объединённое определение

**Marketing OS** — это **операционная система маркетинга**: единый набор смыслов, процессов, инструментов, workflow-ов и AI-агентов, который связывает стратегию, каналы, команду и экономику (P&L) в одну работающую систему.

> **Ключевая метафора:** Как ОС компьютера объединяет железо и программы в управляемое целое, так Marketing OS объединяет исследования, позиционирование, каналы, креативы, экономику, команду и AI в систему, где маркетинг работает предсказуемо.

---

## 📚 ДВА ИСТОЧНИКА — ОДНА СИСТЕМА

| Аспект | marketingos.ru (Александр Петров) | itsapola/marketing-os (GitHub) | Синтез |
|--------|----------------------------------|--------------------------------|--------|
| **Фокус** | Стратегия, смыслы, JTBD, структура отдела | Workflow-и, playbooks, AI-агенты, шаблоны | **Полный цикл: от смысла до исполнения** |
| **Уровень** | Концептуальный / методологический | Операционный / исполняемый | **Теория + Практика** |
| **AI роль** | Исполнитель внутри системы (умножает результат) | AI-агенты, workflow automation, prompt libraries | **AI = Infrastructure, not Strategy** |
| **Артефакты** | Статьи, интенсив, фреймворки | Playbooks, workflows, agents, templates, examples | **Playbooks + Templates + Agents** |
| **Структура** | 5 слоёв (Смыслы → Аудитория → Каналы → Экономика → Команда) | 10 стадий Operating Model + Human-AI Responsibility Model | **Интегрированная 10-стадийная модель** |

---

## 🏗 ИНТЕГРИРОВАННАЯ АРХИТЕКТУРА (10 стадий)

```
Business Objectives
        ↓
Market Understanding          ←── СМЫСЛЫ + АУДИТОРИЯ (JTBD, кастдев)
        ↓
Strategic Choices             ←── ПОЗИЦИОНИРОВАНИЕ, ДИФФЕРЕНЦИАЦИЯ
        ↓
Planning                      ←── КАНАЛЫ, КАМПАНИИ, RACI, БРИФЫ
        ↓
Production                    ←── AI-AGENTS, WORKFLOWS, TEMPLATES
        ↓
Review                        ←── RUBRICS, FACT-CHECKS, BRAND VOICE
        ↓
Distribution                  ←── CHANNEL STRATEGY, SCHEDULING
        ↓
Measurement                   ←── ЭКОНОМИКА (P&L, юнит-экономика, revenue)
        ↓
Learning                      ←── RETROSPECTIVES, UPDATED PLAYBOOKS
        ↓
System Improvement            ←── WORKFLOW EVOLUTION, PROMPT EVALUATION
```

---

## 🤖 HUMAN-AI RESPONSIBILITY MODEL (4 уровня)

| Уровень | Название | Когда применять | Примеры |
|---------|----------|-----------------|---------|
| **1** | **Human-Led** | High judgment, sensitivity, accountability, originality | Positioning, crisis comms, executive messaging, ethics, brand direction |
| **2** | **AI-Assisted** | AI accelerates analysis/production, human review essential | **DEFAULT** — competitive analysis, campaign planning, website audits, messaging, content drafting |
| **3** | **Human-Supervised Automation** | Repeatable process, understood risks | Weekly reports, metadata, formatting, research monitoring, quality checks |
| **4** | **Automated** | Low-risk, rules-based, reversible | File naming, link validation, scheduled data pulls, routing, tagging |

> **Принцип:** AI never owns a decision. Humans remain accountable for strategy, creativity, final decisions.

---

## 📦 РЕПОЗИТОРИЙ itsapola/marketing-os — СТРУКТУРА

```
marketing-os/
├── docs/
│   ├── operating-model.md      # 10 стадий + Human-AI model + Decision Rights + Workflow Design Standard
│   ├── philosophy.md           # "AI is Infrastructure, Not Strategy", "Context Is Strategic Asset"
│   └── principles.md           # 6 Core Principles (Systems > Tasks, AI Amplifies Judgment, etc.)
├── playbooks/
│   └── website-audit.md        # 12-шаговый playbook с AI/Human responsibilities
├── workflows/
│   └── competitive-intelligence.md  # (пустой, ожидает заполнения)
├── agents/
│   └── brand-strategist.md     # (пустой, ожидает заполнения)
├── templates/
│   ├── marketing-brief.md      # (пустой)
│   └── website-audit-report.md # Полный шаблон отчёта (15 секций)
├── examples/
│   └── website-audit/          # (пустой)
└── prompts/                    # (отсутствует, планируется)
```

---

## 🎯 ГОТОВЫЕ К ИСПОЛЬЗОВАНИЮ АРТЕФАКТЫ

### 1. **Website Audit Playbook** (playbooks/website-audit.md)
- 12 шагов: Business Context → Homepage → Messaging → Audience → Navigation → Content → Trust → Conversion → SEO → Accessibility → Competitive → Prioritized Recs
- Чёткое разделение AI / Human responsibilities на каждом шаге
- Success criteria для передачи другому маркетологу

### 2. **Website Audit Report Template** (templates/website-audit-report.md)
- 15 секций: Executive Summary → Business Context → 10 audit categories → Prioritized Recommendations (Impact/Effort matrix) → 30-Day Action Plan → Risks → Final Recommendation
- Скоринг 1-10 по 10 категориям + Competitive Scorecard
- Methodology reference к playbook

### 3. **Operating Model** (docs/operating-model.md)
- 10 стадий с таблицами: Primary Goal, AI Assists, Humans Own, Inputs, Outputs, Quality Standard
- **Workflow Design Standard** (12 полей: Purpose, Trigger, Owner, Inputs, Steps, Decision Points, AI Role, Human Role, Outputs, Evaluation, Failure Modes, Escalation, Feedback Loop)
- **Decision Rights** таблица (кто владеет какой decision)
- **Core Feedback Loop** для compounding improvement

### 4. **Philosophy** (docs/philosophy.md)
- "Marketing Is Becoming a Systems Discipline"
- "AI Is Infrastructure, Not Strategy"
- "Human Judgment Is the Control Layer"
- "Context Is a Strategic Asset"
- "Workflows Should Improve Decisions"
- "Documentation Creates Organizational Memory"
- "Systems Should Be Designed Before They Are Automated"
- "Good Systems Create Compounding Returns"
- **Principles of AI-Native Marketing Organization** (12 принципов)

### 5. **Principles** (docs/principles.md)
1. Systems > Tasks
2. AI Amplifies Judgment
3. Reusable Beats Repeatable
4. Context Is The Product
5. Strategy Before Execution
6. Documentation Creates Scale

---

## 📊 КЕЙС METADATA — ПРИМЕНЕНИЕ НА ПРАКТИКЕ

| Элемент Marketing OS | Как реализовано в Metadata |
|----------------------|---------------------------|
| **Смыслы (JTBD)** | B2B marketers "hire" tool to automate routine, optimize by revenue not vanity |
| **Аудитория** | Enterprise marketing teams, demand-gen, $48K+/год contracts |
| **Каналы** | 5 нестандартных: G2/TrustRadius guides, LinkedIn Conversational Ads, Close-loss campaigns, B2C socials с B2B таргетингом |
| **Экономика** | $1.25M/мес, $15M ARR, enterprise pricing, revenue-based optimization |
| **Команда/Процессы** | AI/ML для оптимизации кампаний, автоматические таргетинги, один интерфейс для всех платформ |
| **System Improvement** | 10 лет на PMF, выжили кризис 2020 ($500K, <2 мес runway) через cost cuts + equity conversion |

---

## 🔧 ИНТЕГРАЦИЯ В GODMODEMARKETOLOG

### Рекомендуемая структура папки:
```
GodModeMarketolog/
├── marketing-os/
│   ├── theory/                 # marketingos.ru концепты
│   │   ├── 5-layers.md
│   │   ├── vs-strategy-plan.md
│   │   ├── build-order.md
│   │   ├── ai-role.md
│   │   ├── symptoms-checklist.md
│   │   └── coffee-example.md
│   ├── github-framework/       # itsapola/marketing-os
│   │   ├── operating-model.md
│   │   ├── philosophy.md
│   │   ├── principles.md
│   │   ├── human-ai-model.md
│   │   ├── workflow-standard.md
│   │   └── decision-rights.md
│   ├── playbooks/
│   │   └── website-audit.md
│   ├── workflows/
│   │   └── competitive-intelligence.md  (to develop)
│   ├── agents/
│   │   └── brand-strategist.md          (to develop)
│   ├── templates/
│   │   ├── marketing-brief.md
│   │   └── website-audit-report.md
│   ├── cases/
│   │   └── metadata-case.md
│   └── integration-guide.md
```

### Приоритеты для GodModeMarketolog:
1. **Сразу используй:** Website Audit Playbook + Report Template — готовые инструменты
2. **Адаптируй:** Operating Model (10 стадий) под свои проекты
3. **Разработай:** AI-агентов (Brand Strategist, Product Marketer, SEO Analyst, Content Strategist, Executive Advisor)
4. **Наполни:** Workflows (Competitive Intelligence, Content Production, Campaign Planning, SEO Research)
5. **Создай:** Prompt libraries для каждого workflow

---

## 🚀 NEXT ACTIONS

### Для即时 использования:
- [ ] Запустить Website Audit на текущем проекте (playbook + template)
- [ ] Применить Operating Model к следующему кампанийному циклу
- [ ] Использовать Human-AI Responsibility Model для классификации текущих задач

### Для развития GodModeMarketolog:
- [ ] Создать `brand-strategist` agent на основе operating-model.md Stage 3
- [ ] Разработать `competitive-intelligence` workflow (Stage 2)
- [ ] Построить `content-production` pipeline (Stage 5) с AI-assist
- [ ] Настроить feedback loop: Measurement → Learning → System Improvement
- [ ] Документировать Context как shared infrastructure (philosophy.md)

---

## 💡 ОДНО ПРЕДЛОЖЕНИЕ ДЛЯ ЗАПОМИНАНИЯ

> **Marketing OS = 5 слоёв (Петров) × 10 стадий (GitHub) × 4 уровня Human-AI × Playbooks + Templates + Agents**
>
> Это не "ещё один фреймворк". Это **операционная модель**, которая превращает маркетинг из набора активностей в систему, где:
> - Контекст — инфраструктура
> - AI — усилитель, не замена
> - Документация — организационная память
> - Каждый цикл делает организацию способнее

---

## 🔗 ССЫЛКИ

- **Теория:** https://marketingos.ru/blog/chto-takoe-os-v-marketinge
- **GitHub:** https://github.com/itsapola/marketing-os
- **Кейс Metadata:** https://maximsoldatkin.ru/metadata-b2b-marketing-os-1-25m/
- **AI Market OS (продукт):** https://aimarketos.com/
- **KZSalesHub подход:** https://kzsaleshub.com/marketing-os/

---

*Файл готов к копированию в GodModeMarketolog vault. Все артефакты скачаны в `/home/thomas/.hermes/vault/marketing-os-github/`*