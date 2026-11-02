# Marketing Skills Index

> Импортировано из [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) (MIT License, 46.6k⭐)
> Адаптировано под GodModeMarketolog — локальная копия без внешних зависимостей.
> Все скиллы работают автономно — читают `.agents/product-marketing.md` если существует.

---

## 📂 Структура

```
skills/
├── marketing-plan/          # Комплексный GTM-план (13 секций по AARRR)
├── copywriting/             # Маркетинговый копирайтинг
├── cro/                     # Conversion Rate Optimization
├── content-strategy/        # Стратегия контента
├── launch/                  # Продуктовый лаунч
├── marketing-psychology/    # Психология маркетинга
├── pricing/                 # Ценообразование
├── offers/                  # Офферы, бонусы, валуинг
├── seo-audit/               # SEO аудит
├── social/                  # Социальные сети
├── competitor-profiling/    # Профайлинг конкурентов
├── evals/                   # Тесты качества для каждого скилла
└── references/              # Референсные файлы (aarrr-framework, methodology и т.д.)
```

---

## 🎯 Как работает каждый скилл

### Перед выполнением
Каждый скилл ищет `.agents/product-marketing.md` (или `.claude/product-marketing.md`) для контекста. Если нет — задаёт уточняющие вопросы.

### Стек вызовов
```
marketing-plan → копирует идеи из marketing-ideas (139 идей) + cross-reference с current-state-rubric
copywriting → читает product-marketing.md → пишет copy по JTBD
cro → использует persuasion-frameworks из marketing-psychology
pricing → cross-ref с offers + marketing-psychology (perceived value)
```

---

## 📋 Полный список скиллов

| Скилл | Когда использовать | Ключевой файл |
|-------|-------------------|---------------|
| `marketing-plan` | Комплексный GTM-план, 90-дневный план, fCMO план | `skills/marketing-plan/SKILL.md` |
| `copywriting` | Писать/редактить копирайтинг для любой страницы | `skills/copywriting/SKILL.md` |
| `cro` | Оптимизация конверсии лендингов и воронок | `skills/cro/SKILL.md` |
| `content-strategy` | Стратегия контент-маркетинга | `skills/content-strategy/SKILL.md` |
| `launch` | Продуктовый лаунч, go-to-market | `skills/launch/SKILL.md` |
| `marketing-psychology` | Психологические триггеры, persuasions | `skills/marketing-psychology/SKILL.md` |
| `pricing` | Ценообразование, value-based pricing | `skills/pricing/SKILL.md` |
| `offers` | Структура офферов, бонусы, гарантии | `skills/offers/SKILL.md` |
| `seo-audit` | Аудит SEO, технический SEO, keyword strategy | `skills/seo-audit/SKILL.md` |
| `social` | Социальные сети, контент-планы | `skills/social/SKILL.md` |
| `competitor-profiling` | Анализ конкурентов, positioning | `skills/competitor-profiling/SKILL.md` |

---

## 🔗 Интеграция с marketing-os

```
GodModeMarketolog/
├── marketing-os/              # Теория + фреймворки
│   ├── theory/
│   ├── github-framework/
│   ├── playbooks/
│   ├── templates/
│   └── agents/
├── skills/                    # Исполняемые AI-скиллы (этот каталог)
│   └── <skill>/SKILL.md
├── evals/                     # Тесты качества скиллов
├── references/                # Референсы для скиллов
└── globvis-analysis.md        # Текущий анализ проекта
```

### Рекомендуемый порядок применения:
1. **Скилл `competitor-profiling`** → получить позиционирование
2. **Скилл `marketing-plan`** → сгенерировать план на основе позиционирования
3. **Скилл `copywriting`** → написать тексты по плану
4. **Скилл `cro`** → оптимизировать конверсию
5. **Скилл `pricing`** → настроить ценовую модель
6. **Скилл `launch`** →execute лаунч
7. **Скилл `marketing-psychology`** → добавить психологические триггеры

---

## 🧪 Тестирование (evals)

Каждый скилл имеет `evals/evals.json` — набор тест-кейсов для проверки качества вывода.

```bash
# Запуск эвалов для конкретного скилла
cd skills/<skill-name>/evals && python run_evals.py
```

---

## 📝 Лицензия

Исходный репозиторий: MIT License — coreyhaines31/marketingskills (https://github.com/coreyhaines31/marketingskills)

Адаптация под GodModeMarketolog — собственная, все изменения локальны.

---

*Скиллы скопированы 2026-09-05. Все SKILL.md идентичны оригиналу (cmp-проверено).*
