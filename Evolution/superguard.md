---
type: PIPELINE
status: "ЖИВ"
color: "#2ecc71"
role: "КОММЕРЧЕСКИЙ: AISuperGuard — AI-охрана периметра/кабеля (YOLO вор-электрик → Telegram + ESP32 прожектор/сирена), подписки 50€/мес/камера"
genome: "C:/SuperGuard/superguard/main.py"
state: "production (N100+SG1210MP, 8 камер)"
links: 5
tags:
  - "#type/pipeline"
  - "#status/alive"
  - "#evolution/graph"
  - "#role/коммерческий-aisuperguard-ai-охрана-периметра-кабеля-yolo-вор-электрик-telegram-esp32-прожектор-сирена-подписки-50-мес-камера"
---

# ⚙️ SUPERGUARD

> [!info] **PIPELINE** · Пульс: **ЖИВ**

**Роль:** КОММЕРЧЕСКИЙ: AISuperGuard — AI-охрана периметра/кабеля (YOLO вор-электрик → Telegram + ESP32 прожектор/сирена), подписки 50€/мес/камера

**Геном:** `C:/SuperGuard/superguard/main.py`

**Состояние:** `production (N100+SG1210MP, 8 камер)`


## Питает (исходящие рёбра)
- 🍽️ **FEEDS** → [[watchdog]]
- 🍽️ **FEEDS** → [[hyperprobe]]

## Кормит (входящие рёбра)
- 👁️ **VISION** ← [[oracle]]
- 🧠 **CONTROLS** ← [[gardener]]
- 🍽️ **FEEDS** ← [[hyperprobe]]

---
*Экспорт из `graph.yaml` · 2026-08-12 23:21*
