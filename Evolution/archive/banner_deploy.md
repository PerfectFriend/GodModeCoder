---
extinct: true
extinction_date: 2026-08-15T17:03:08.371086+00:00
extinction_reason: Dead for 6 consecutive days
original_node: banner_deploy
---

---
type: PIPELINE
status: "МЁРТВ"
color: "#2ecc71"
role: "Баннеры/ReadMe/Deploy: рисует баннеры в фирменном стиле, пишет README на 3 языках (RU/EN/CN), пушит в GH (создаёт новые репо под задачи), обновляет план эволюции"
genome: "C:/LivingCode/scripts/banner_deploy.py --style brand --langs ru,en,zh --create-repos"
state: "active"
links: 12
tags:
  - "#type/pipeline"
  - "#status/dead"
  - "#evolution/graph"
  - "#role/баннеры-readme-deploy-рисует-баннеры-в-фирменном-стиле-пишет-readme-на-3-языках-ru-en-cn-пушит-в-gh-создаeт-новые-репо-под-задачи-обновляет-план-эволюции"
---

# ⚙️ BANNER_DEPLOY

> [!info] **PIPELINE** · Пульс: **МЁРТВ**

**Роль:** Баннеры/ReadMe/Deploy: рисует баннеры в фирменном стиле, пишет README на 3 языках (RU/EN/CN), пушит в GH (создаёт новые репо под задачи), обновляет план эволюции

**Геном:** `C:/LivingCode/scripts/banner_deploy.py --style brand --langs ru,en,zh --create-repos`

**Состояние:** `active`


## Питает (исходящие рёбра)
- 🤝 **CALLS** → [[github_private]]
- 🍽️ **FEEDS** → [[chronicle]]
- 🍽️ **FEEDS** → [[holy_code_apps]]
- 🤝 **CALLS** → [[model_registry]]
- 🍽️ **FEEDS** → [[holy_code_games]]

## Кормит (входящие рёбра)
- 🍽️ **FEEDS** ← [[encrypted_comm]]
- 🤝 **CALLS** ← [[encrypted_comm]]
- 🍽️ **FEEDS** ← [[filter_overlord]]
- 🧠 **CONTROLS** ← [[filter_overlord]]
- 🍽️ **FEEDS** ← [[tailscale_mesh]]
- 🤝 **CALLS** ← [[totomoto_audio]]
- 🤝 **CALLS** ← [[dj_sound_studio]]

---
*Экспорт из `graph.yaml` · 2026-08-15 16:55*

