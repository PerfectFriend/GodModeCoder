---
type: index
---

# 🧬 Эволюционный Граф — Индекс

> [!abstract] Живой граф проектов Гримуара
> Узлов: **21** · Рёбер: **20** · 🟢 ЖИВ: **11** · 🟡 БОЛЕН: **0** · 🔴 МЁРТВ: **10** · ⚪ неизвестно: **0**

## Карта узлов

| Узел | Тип | Пульс | Роль |
|---|---|---|---|
| 🟢 [[oracle]] | 🧑‍🔬 HUMAN | ЖИВ | Мастер Инквизитор — видение, критерии fitness, одо |
| 🔴 [[gardener]] | 🤖 AGENT | МЁРТВ | Hermes Agent — пульс, отбор, мутации, экстинкции |
| 🔴 [[dj]] | 🤖 AGENT | МЁРТВ | Ротация музыки, стрим :8090 |
| 🟢 [[song_protocol]] | 📜 SKILL | ЖИВ | Контент → структура песни → лирики → ACE-Step → кэ |
| 🔴 [[music_pipeline]] | ⚙️ PIPELINE | МЁРТВ | Генерация музыки через ACE-Step (CPU) |
| 🔴 [[voice]] | ⚙️ PIPELINE | МЁРТВ | Голос: Qwen3-TTS GPU / Voicebox — новости, джинглы |
| 🔴 [[radio_cache]] | 🗄️ MEMORY | МЁРТВ | Библиотека: cache/music/<style>/, новости, реклама |
| 🟢 [[watchdog]] | 🩺 WATCHDOG | ЖИВ | Пульс графа: health-чек узлов, статусы ЖИВ/БОЛЕН/М |
| 🟢 [[chronicle]] | 🗄️ MEMORY | ЖИВ | Летопись: рождения, мутации, экстинкции, открытия |
| 🟢 [[archive]] | 🗄️ MEMORY | ЖИВ | Могильник: полные геномы вымерших узлов + причина |
| 🟢 [[paranoidx]] | ⚙️ PIPELINE | ЖИВ | ФЛАГМАН: ParanoidX + IsleProject — Sovereign Go-се |
| 🔴 [[isle_client]] | 🤖 AGENT | МЁРТВ | Клиенты The-Isle / Royal-Isle: Flutter-приложения  |
| 🟢 [[superguard]] | ⚙️ PIPELINE | ЖИВ | КОММЕРЧЕСКИЙ: AISuperGuard — AI-охрана периметра/к |
| 🔴 [[professor]] | 🤖 AGENT | МЁРТВ | Профессор 24/7 — изучает топ-ресурсы (X.com, HN, G |
| 🔴 [[filter_overlord]] | 📜 SKILL | МЁРТВ | Строгий протокол: FROZEN (≥95% coverage, 0 uncommi |
| 🔴 [[autonomous_ai_agents]] | 📜 SKILL | МЁРТВ | Autonomous AI Agents: Spawning and orchestrating a |
| 🟢 [[evolution_elemental_life]] | 📦 PROJECT | ЖИВ | Elemental Life — Cellular automata life simulation |
| 🔴 [[evolution_superguard]] | 📦 PROJECT | МЁРТВ | Elemental Guard — AI-powered video surveillance (Y |
| 🟢 [[evolution_cybertarot]] | 📦 PROJECT | ЖИВ | Elemental Tarot — 78-card elemental tarot with Mag |
| 🟢 [[textbook]] | 🗄️ MEMORY | ЖИВ | Учебник GodModeCoder: накопленные инсайты, паттерн |
| 🟢 [[ai_eng_daily]] | 📜 SKILL | ЖИВ | Ежедневный research AI Engineering: vLLM/SGLang, s |

## Рёбра

| От | Тип | К |
|---|---|---|
| [[oracle]] | 👁️ VISION | [[gardener]] |
| [[oracle]] | 👁️ VISION | [[paranoidx]] |
| [[oracle]] | 👁️ VISION | [[superguard]] |
| [[oracle]] | 👁️ VISION | [[professor]] |
| [[gardener]] | 🧠 CONTROLS | [[watchdog]] |
| [[gardener]] | 🧠 CONTROLS | [[filter_overlord]] |
| [[gardener]] | 🧠 CONTROLS | [[autonomous_ai_agents]] |
| [[gardener]] | 🧠 CONTROLS | [[superguard]] |
| [[gardener]] | 🧠 CONTROLS | [[paranoidx]] |
| [[watchdog]] | 🍽️ FEEDS | [[superguard]] |
| [[watchdog]] | 🍽️ FEEDS | [[paranoidx]] |
| [[filter_overlord]] | ⚖️ EVALUATES | [[evolution_elemental_life]] |
| [[filter_overlord]] | ⚖️ EVALUATES | [[evolution_superguard]] |
| [[filter_overlord]] | ⚖️ EVALUATES | [[evolution_cybertarot]] |
| [[autonomous_ai_agents]] | 🤝 CALLS | [[evolution_elemental_life]] |
| [[autonomous_ai_agents]] | 🤝 CALLS | [[evolution_superguard]] |
| [[autonomous_ai_agents]] | 🤝 CALLS | [[evolution_cybertarot]] |
| [[paranoidx]] | 🍽️ FEEDS | [[isle_client]] |
| [[professor]] | 🍽️ FEEDS | [[textbook]] |
| [[professor]] | 🍽️ FEEDS | [[ai_eng_daily]] |

## Критерии fitness

- **watchdog:** `pulse.py exit 0`
- **gardener:** `pulse.py exit 0`
- **paranoidx:** `api health 200 + docker ps healthy`
- **superguard:** `main.py process alive + telegram bot responds`
- **professor:** `at least 1 insight saved per 24h`
- **autonomous_ai_agents:** `coder agents producing commits`
- **filter_overlord:** `passes ≥ 80% coverage on evolution projects`

*Обновлено: 2026-08-17 09:37*
