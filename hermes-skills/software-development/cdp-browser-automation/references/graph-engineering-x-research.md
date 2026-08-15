# Graph Engineering / автономная граф-эволюция — дайджест X (30.07–05.08.2026)

Собрано через CDP-поиск по X (см. xcom-cdp-login.md). Термин пользователя «автономная
граф-эволюция» в англоязычных AI-сообществах = **Graph Engineering** — главный хайп
конца июля — начала августа 2026.

## Суть тренда

Эволюция архитектуры агентов (пост @NawinScript, 02.08, статья с диаграммами):
`Prompt Engineering → Context Engineering → Skills → Loop Engineering → GRAPH ENGINEERING`
Каждый этап сменялся, когда предыдущий переставал масштабироваться.

Три слоя (пост @elune0x, 04.08 — самый чёткий разбор):
- **Loop Engineering** — контролирует итерации: retries, budgets, evaluators, exits,
  stalled progress, переживание крашей/рестартов (Temporal).
- **Graph Engineering** — контролирует структуру: nodes, edges, state, branches, cycles,
  checkpoints, joins. Агенты = ноды графа; топология видна без объяснений LLM
  (LangGraph, NetworkX). «Когда агент пошёл не той веткой — сломан граф».
- **Harness Engineering** — контролирует доступ: tools, permissions, memory, sandboxes,
  evals, traces (E2B, OpenAI evals, OpenTelemetry).

Мантра: «prompt lives inside the loop, loop lives inside the graph, graph lives inside
the harness» (@elune0x).

## Ключевые посты (статус на 05.08.2026)

| Автор | Дата | Ссылка / суть |
|---|---|---|
| @elune0x | 04.08 | `x.com/elune0x/status/2084750034638414246` — LOOP vs GRAPH vs HARNESS, полный разбор |
| @NawinScript | 02.08 | `x.com/NawinScript/status/2084015178883162145` — статья «Loop Engineering vs Graph Engineering: What Actually Changed?» с диаграммами |
| @RichardFedorko | 04.08 | `x.com/RichardFedorko/status/2084753989376090570` — plain-language интро для исследователей + шаблоны воркфлоу |
| @LunarResearcher | 04.08 | `x.com/LunarResearcher/status/2084746556918354175` — Anthropic 50-мин воркшоп по Graph Engineering (таймкоды: tools/memory → почему агенты ломаются в проде → датасеты/эвалы → тест графа до деплоя). «Prompt testing — old workflow, Graph evaluation — new» |
| @themarcusbuild | 04.08 | `x.com/themarcusbuild/status/2084760907851104314` — «85% инженеров Anthropic запускают сотни агентов, способ — graph engineering» (Head of Claude Code, 40-мин разбор) |
| @0xClodex | 04.08 | `x.com/0xClodex/status/2084748511141052749` — «You don't need better prompts. You need graph engineering that makes agents remember everything» |
| @ForwardEditor | 03.08 | `x.com/ForwardEditor/status/2084273276642034037` — **self-evolving graph**: граф сам ведёт PRD, фичи, тесты (ближе всего к «автономной граф-эволюции») |
| @DanKornas | 05.08 | `x.com/DanKornas/status/2084770345089913053` — Potpie: «living context graph» кодовой базы для агентов |
| @spotTheGap | 05.08 | `x.com/spotTheGap/status/2084784781506609523` — «Graph engineering is the new skill floor»: routing, memory boundaries, «не давать каждому агенту переписывать план» |
| Tencent Cloud Intl | 30.07 | «Graph Engineering is already blowing up — fresh buzzword or real deal?» |

Также: Neo4j NODES AI 2026 — «Agentic GraphRAG: autonomous knowledge graph construction»
(video, neo4j.com); Sartech Labs — гайд «Graph Engineering: The Next Evolution».

## Связь с проектами пользователя

- The Grimoire: текущий циклический протокол эволюции = Loop Engineering. Трендовый
  следующий шаг — граф: ноды = агенты (сторож, генератор, редактор, DJ), рёбра = потоки
  данных, сам граф мутирует (self-evolving).
- AI-радио Мастер-ФМ: ротация DJ/контента тоже можно перевести с цикла на граф.
