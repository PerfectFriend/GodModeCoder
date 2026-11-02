# Playbook: Financial Gates (Go/No-Go by Numbers)

> **Назначение:** Объективные ворота «продолжаем / пивот / убиваем» по цифрам, не по наитию.
> **Источник:** AI_Marketing_Machine_Plan + Marketing OS Stage 8 (Measurement).

## Gate Criteria
| Gate | Дедлайн | Continue | Pivot | Kill |
|------|---------|----------|-------|------|
| **Gate A** (M3) | 100 клиентов | >30 | 10-30 | <10 |
| | MRR | >$1,000 | $300-1,000 | <$300 |
| | CAC | <$100 | $100-200 | >$200 |
| **Gate B** (M6) | 100 клиентов | >100 | 50-100 | <50 |
| | MRR | >$5,000 | $2,000-5,000 | <$2,000 |
| | Churn | <4% | 4-6% | >6% |
| **Gate C** (M12) | MRR | >$20,000 | $10,000-20,000 | <$10,000 |
| | Team | 2+ contractors | 1 | 0 |
| | Profit | break-even | -$2K/mo | -$5K/mo |

## Leading Indicators (еженедельно — автоотчёт AGENT-5)
| Метрика | Phase 1 | Phase 2 | Алерт если |
|---------|---------|---------|------------|
| Website Visits | 500/wk | 5,000/wk | <300/wk |
| Free→Trial | 3% | 5% | <2% |
| Trials Started | 10/wk | 100/wk | <5/wk |
| Trial→Paid | 18% | 20% | <12% |
| New MRR | $200/wk | $2,000/wk | <$100/wk |
| Organic Traffic | 1,000/mo | 20,000/mo | <500/mo |
| Twitter Followers | +50/wk | +200/wk | <+20/wk |
| Affiliate Signups | 2/wk | 10/wk | <1/wk |

## Lagging Indicators (месячно — Gate Review)
| Метрика | Gate A | Gate B | Kill Threshold |
|---------|--------|--------|----------------|
| Paying Customers | 100 | 1,000 | <10 (M3), <50 (M6) |
| MRR | $1,700 | $17,000 | <$300 (M3), <$2,000 (M6) |
| Blended CAC | <$17 | <$30 | >$80 (M3), >$100 (M6) |
| Monthly Churn | <4% | <3% | >6% |
| LTV/CAC | >3 | >4 | <2 |
| Affiliate Rev % | 10% | 25% | <5% |
| NRR | >100% | >110% | <90% |

## Automated Alerts (AGENT-5 → Telegram)
```
🔴 CAC > $50 за 3 дня → Kill underperforming ad sets
🔴 Trial→Paid < 10% за 7 дней → Audit onboarding emails
⚠️ Organic -20% WoW → Check SEO / алгоритм-апдейт
⚠️ Churn > 5% → Trigger win-back sequence
ℹ️ New affiliate > $500 MRR → Bonus notification
ℹ️ Content > 1000 visits → Amplify with paid boost
```

## Budget Rules (Hardcoded в AGENT-0)
```
До Gate A:       0% реинвестиции (свои средства)
Gate A → Gate B: 60% выручки в маркетинг
После Gate B:    40% выручки в маркетинг
AI Tools Budget: всегда 10% маркетингового бюджета
```

## Применение к проектам
- **SuperGuard:** Gate A = 100 B2B-объектов под охраной, $1.7K MRR
- **ParanoidX:** Gate A = 500 нод в сети, инвестор-$2M SAFE
- **Магазин:** Gate A = 1000 установок гостевых APK, $1K MRR
- **MatrixX:** Gate A = 10K MAU, $1K MRR

## Hard Rules
- Ворота — единственный критерий. Никаких «ну почти».
- Человек (AGENT-0) утверждает pivot/kill на основе цифр, не эмоций.
- Каждый цикл (Learning → System Improvement) делает систему способнее.
