# Playbook: AutoGTM Cold Outreach (Explee-style)

> **Концепт:** 7 AI-агентов находят ICP, пишут персонализированные письма, букают демо.
> **Источник:** Explee AutoGTM + Jane Street persuasion stack.

## Как работает (60-секундный флоу)
```
1. Enter website → AI Researcher анализирует бизнес
2. CMO дизайнит GTM + ICP сегменты
3. GTM Engineer строит инфраструктуру (domains, mailboxes)
4. SDR находит high-intent prospects (105M companies / 536M people)
5. Copywriter пишет персонализированные письма
6. SalesOps ведёт sequences + deliverability
7. Analyst масштабирует топ-кампании
→ Replies → Agent отвечает → Book demos
```

## Cold Outreach Sequence (AGENT-3 + AGENT-7)
```
День 0:  "Видел {trigger} — думаю, {product} может помочь с {pain_point}"
День 2:  "Кейс: как {similar_company} выросли на {metric} с {solution}"
День 5:  "Бесплатно: ставится за 1 мин. Хочешь ссылку?"
День 8:  "Короткое видео (60с) как это работает — {link}"
День 12: "Последний раз: если не актуально — скажи 'нет', не буду беспокоить"
```
Персонализация через Clay: company name, tech stack, recent posts, funding.
A/B: subject lines, CTA placement, social proof type.

## Trial Onboarding (AGENT-7) — 14 дней, 7 писем
```
D0:  Welcome + "твой доступ жив" + ссылка на дашборд
D1:  "3 вещи, которые увидишь за 24 часа"
D3:  "Как читать [результат]" + GIF
D5:  Кейс: "+{metric}% для {peer}" (PDF)
D7:  "Половина пройдена — ещё можно: Alerts, UTM, Team"
D10: "Upgrade сейчас — зафиксируй цену ${price} навсегда" (scarcity)
D14: "Триал заканчивается завтра — сохраняй данные"
```

## Trial→Paid (AGENT-7) — D0/D2/D5/D10
```
D0:  "Триал окончен. Данные сохранены 30 дней. Вернись за ${price}/мес"
D2:  "Коллега из {industry} апгрейднулся — вот его результат"
D5:  "Спец: Pro ${p2} → ${p1}/мес если решишься до пятницы"
D10: "Последний шанс вернуть историю. После — данные удаляются"
```

## Churn Win-Back (AGENT-7) — D1/D7/D30
```
D1:  "Жаль, что уходишь. Что могли бы иначе? (1-клик опрос)"
D7:  "Обновили: {feature}. Стоит взглянуть?"
D30: "Вернись — первый месяц на нас. Промокод: COMEBACK50"
```

## Persuasion-усиление (из theory/persuasion-frameworks.md)
| Touch | Framework | Hook |
|-------|-----------|------|
| 1 | Problem-Agitation-Solution + Certainty | Боль → агитация → решение как логичный путь |
| 2 | Identity + Growth | «Ты тот, кто модернизировал стек» |
| 3 | Dickens Pattern | Будущее без перемен vs с переменой |
| 4 | Risk Reversal + Agreement Frame | «Понимаю, рискованно → 30-дней пилот бесплатно» |

## Метрики (бенчмарк Explee)
| Метрика | Ожидание |
|---------|----------|
| Deliverability | 97% (pre-warmed pools) |
| Open rate | 35-50% |
| Reply rate | 5-15% |
| Demos/1000 emails | 10-30 |
| Cost per demo | ~$1-3 |

## Hard Rules
- Pre-warmed mailboxes — твой домен никогда не в зоне риска
- Risk reversal обязателен (пилот/гарантия) — не «купи сейчас»
- Ссылки в reply, не в основном письме (deliverability)
