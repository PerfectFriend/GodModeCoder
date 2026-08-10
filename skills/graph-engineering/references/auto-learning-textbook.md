# Auto-Learning System (Textbook)

Автоматическая система непрерывного обучения через крон. Каждые 6 часов изучает случайную неизученную тему из `Учебник.md`.

## Архитектура

```
Учебник.md (Source of Truth — 32 темы в 8 категориях)
       │
       ▼
textbook_learn.py (Cron Job — каждые 6ч)
       │
       ├──► Учебник.md — обновляет статус темы: 🔴 → 🟢
       ├──► Evolution/chronicle.md — добавляет запись об изучении
       └──► Git commit — история обучения
```

## Учебник.md — Структура

```markdown
---
type: textbook
tags: ["#textbook", "#learning", "#knowledge-base"]
---

# 📚 УЧЕБНИК — Knowledge Base

## Категории (8) с приоритетами:
1. Graph Engineering & Evolution (priority: 10)
2. Obsidian Advanced (9)
3. MCP & Agent Integration (9)
4. AI/ML on AMD Radeon 780M (10)
5. Video Surveillance & YOLO (8)
6. ParanoidX / Sovereign Systems (7)
7. Windows/MSYS Mastery (6)
8. Hermes Agent Internals (8)

## Тема формат:
- [ ] [Topic Name](Topic%20Name.md) — 🔴
- [x] [Topic Name](Topic%20Name.md) — 🟢
```

## Cron Job: textbook-learning

```json
{
  "job_id": "textbook-learning",
  "name": "textbook-learning",
  "schedule": "every 6h",
  "script": "textbook_learn.py",
  "skills": ["obsidian-graph-engineering"],
  "no_agent": true,
  "deliver": "local"
}
```

## Algorithm (textbook_learn.py)

```python
def main():
    # 1. Parse Учебник.md → find all 🔴 topics
    # 2. Weighted random choice (by category priority)
    # 3. Mark 🟡 (in progress) in Учебник.md
    # 4. "Study" topic (generate insights from skill knowledge base)
    # 5. Mark 🟢 in Учебник.md
    # 6. Append to Evolution/chronicle.md:
    #    ## YYYY-MM-DD HH:MM — Learned: Topic Name
    #    ### Key Insights
    #    - insight 1
    #    - insight 2
    #    ### Code Patterns
    #    ```python
    #    # practical example
    #    ```
    #    ### Applied To
    #    - godmodecoder skill
    #    - obsidian-graph-engineering skill
    #    ### Next Steps
    #    - [ ] Deep dive: subtopic
    #    - [ ] Integration: where
    # 7. Git commit: "learned: Topic Name (Category)"
```

## Topic Status Flow

```
🔴 Не изучено → 🟡 В процессе → 🟢 Изучено
     │              │              │
   default      cron picks      cron marks
                (weighted)      after study
```

## Chronicle Entry Template

```markdown
## YYYY-MM-DD HH:MM — Learned: Topic Name
**Category:** Category Name
**Source:** Topic%20Name.md

### Key Insights
- insight 1
- insight 2

### Code Patterns
```python
# practical example
```

### Applied To
- godmodecoder skill
- obsidian-graph-engineering skill

### Next Steps
- [ ] Deep dive: subtopic
- [ ] Integration: where

---
```

## Cron Job Setup

```bash
hermes cron create \
  --name "textbook-learning" \
  --schedule "every 6h" \
  --script "textbook_learn.py" \
  --skills "obsidian-graph-engineering" \
  --no_agent true \
  --deliver local
```

## Key Files

| Path | Purpose |
|------|---------|
| `C:\Vault\Учебник.md` | Source of Truth (32 темы) |
| `C:\Vault\Evolution\chronicle.md` | Learning history |
| `C:\Users\tomas\AppData\Local\hermes\scripts\textbook_learn.py` | Cron script |
| `C:\Users\tomas\the-grimoire\ru\scripts\hermes-verify-all.py` | Verifies all tests pass |