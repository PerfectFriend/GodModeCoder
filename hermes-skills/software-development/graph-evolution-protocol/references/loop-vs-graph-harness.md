# Loop vs Graph vs Harness Engineering — дайджест X-сообществ (авг 2026)

Собрано из X-постов 30.07–05.08.2026 (AI/код-сообщества). Это идейная база
протокола Гримуара v3.0 (graph-evolution-protocol). Ключевые посты и тезисы.

## Основной разбор: @elune0x (04.08.2026)

«your agent is not the loop — the loop is only the smallest layer.
LOOP vs GRAPH vs HARNESS ENGINEERING».

- **Loop Engineering** — контролирует ИТЕРАЦИИ: retries, budgets, evaluators, exits,
  stalled progress. «When the run keeps going forever the loop is broken».
  → Temporal (long-running, survives crashes).
- **Graph Engineering** — контролирует СТРУКТУРУ: nodes, edges, state, branches,
  cycles, joins, checkpoints. «When the agent takes the wrong path the graph is broken».
  → LangGraph, NetworkX. Ключ: «inspect the topology without asking another model
  to explain it».
- **Harness Engineering** — контролирует ДОСТУП: tools, permissions, memory,
  sandboxes, evals, traces, humans. «When the agent touches the wrong system the
  harness is broken». → E2B (sandbox), OpenAI evals, OpenTelemetry.

Итог: «the prompt lives inside the loop, the loop lives inside the graph,
the graph lives inside the harness». Без loop — никогда не остановится;
без graph — не видно пути; без harness — достанет до чего угодно.

## Anthropic / Head of Claude Code (03–04.08.2026)

- «85% of our engineers are running dozens or hundreds of agents. The way you do
  it is graph engineering» — 40-мин разбор: один инженер = работа целой команды,
  агенты-ноды указывают друг на друга, передают работу.
- 50-мин воркшоп по Graph Engineering (таймкоды: tools/memory/planning →
  почему агенты ломаются в проде → датасеты/эвалы → оценка tool-use траекторий →
  тест всего графа до деплоя). Слоган: «Prompt testing — old workflow.
  **Graph evaluation** — new one» (тестировать всю систему Agent→State→Tools→Eval→Correction).
- «You don't need better prompts. You need graph engineering that makes agents
  remember everything» (общая память графа, параллельные агенты, взаимная проверка).

## Эволюция подходов (NawinScript, 02.08)

`Prompt Engineering → Context Engineering → Skills → Loop Engineering → Graph Engineering`
— каждый этап сменялся, когда предыдущий переставал масштабироваться.

## Self-evolving graphs (Forward Future Brian, 03.08)

«I'm using graphs to create self-evolving games»: граф-промпт, который можно
вставить в любой проект — агент поддерживает PRD + приоритеты фич, строит топ-
приоритет, тестирует, возвращается в начало. Приоритеты пользователя — top priority.

## Прочие тезисы

- @spotTheGap: «Graph engineering is the new skill floor. One eng running a team
  of agents is not magic. It is routing, memory boundaries, and refusing to let
  every agent rewrite the plan».
- @DanKornas: Potpie — «living context graph» для агентов (код+SDLC → граф).
- Tencent Cloud Intl: «Graph Engineering is already blowing up».
- @MichaelGannotti: исследователи Zhejiang University — граф-подходы для агентов.
- Дебаты: «loop vs graph» — летний спор 2026; большинство: graph = структура
  поверх loop, а не замена.

## Ссылки на посты (для цитирования)

- https://x.com/elune0x/status/2084750034638414246
- https://x.com/themarcusbuild/status/2084760907851104314
- https://x.com/LunarResearcher/status/2084746556918354175
- https://x.com/0xClodex/status/2084748511141052749
- https://x.com/NawinScript/status/2084015178883162145
- https://x.com/ForwardEditor/status/2084273276642034037
- https://x.com/RichardFedorko/status/2084753989376090570
- https://x.com/spotTheGap/status/2084784781506609523
