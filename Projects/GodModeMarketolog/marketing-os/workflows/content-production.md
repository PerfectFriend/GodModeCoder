# Workflow: Content Production Pipeline (AI-Assisted)

> **Stage:** 5 (Production) | **Human-AI Level:** 2 (AI-Assisted, human review)
> **Trigger:** Cron Mon 09:00 (batch) + ad-hoc по сигналу CI.

## Цель
Регулярный поток SEO-статей, соц-постов, видео — из positioning + keyword research.

## Pipeline
```
Inputs (Keywords, Positioning, Audience, Brand Voice)
    → Research (serp, competitor gaps)
    → Outline (LLM)
    → Draft (LLM, per channel)
    → SEO Opt (headers, internal links, meta)
    → Format Adapt (X thread / LinkedIn / Reddit / Short script)
    → Human Review (rubric)
    → Publish / Schedule
```

## Content Types & Cadence
| Тип | Объём | Канал | AGENT |
|-----|-------|-------|-------|
| SEO-статья | 2000+ слов | Blog + Dev.to | 2 |
| X thread | 8-12 твитов | X | 2+8 |
| LinkedIn post | 3×/нед | LinkedIn | 2+8 |
| Reddit comment | 2-3/день | Reddit (90/10 rule) | 1+8 |
| YouTube Shorts | 3×/нед, 30-60с | YT/Shorts/TikTok | 4+8 |
| Case study | 1×/мес | Blog + PDF lead magnet | 2 |

## Промпт-шаблон (Draft)
```
Role: Senior {icp_role} copywriter for {product}.
Audience: {segment}, top-2 needs: {needs}.
Positioning: {value_prop}.
Write {format} about {topic}. Structure: Hook → Value → CTA.
Tone: {brand_voice}. No fluff. One clear CTA.
Brand banned words: {banned}.
```

## Quality Gate (rubric, pre-publish)
- [ ] Выражает позиционирование, а не просто «существует»
- [ ] Нет banned-слов, есть CTA
- [ ] SEO: title < 60 char, meta < 155, H2/H3 структура
- [ ] Факт-чек: цифры из реальных метрик, не выдумка
- [ ] Brand voice match (сверено с brand-voice.md)

## Human owns
Creative direction, финальный аппрув, оригинальность, эмоциональный call.

## Пример распределения (каждая статья)
```
1 статья → 10 твитов + 3 LinkedIn + 2 Reddit + 1 Short (за 48ч)
AGENT-8 ставит в очередь, реплаит упоминания, мониторит бренд
```
