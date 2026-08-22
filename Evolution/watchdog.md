---
type: WATCHDOG
status: "ЖИВ"
color: "#e74c3c"
role: "Пульс графа: health-чек узлов, статусы ЖИВ/БОЛЕН/МЁРТВ"
genome: "scripts/pulse.py"
state: "active"
links: 3
tags:
  - "#type/watchdog"
  - "#status/alive"
  - "#evolution/graph"
  - "#role/пулс-графа-health-чек-узлов-статусы-жив-болен-мeртв"
---

# 🩺 WATCHDOG

> [!info] **WATCHDOG** · Пульс: **ЖИВ**

**Роль:** Пульс графа: health-чек узлов, статусы ЖИВ/БОЛЕН/МЁРТВ

**Геном:** `scripts/pulse.py`

**Состояние:** `active`


## Питает (исходящие рёбра)
- 🍽️ **FEEDS** → [[superguard]]
- 🍽️ **FEEDS** → [[paranoidx]]

## Кормит (входящие рёбра)
- 🧠 **CONTROLS** ← [[gardener]]

---
*Экспорт из `graph.yaml` · 2026-08-17 09:37*
