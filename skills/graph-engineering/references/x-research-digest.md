# Дайджест X-публикаций: Graph Engineering (30 июля — 5 августа 2026)

Собрано через живой поиск X (аккаунт PerfectFriend, CDP-браузер). Точная фраза
«autonomous graph evolution» даёт **0 результатов** — трендовый термин дискурса:
**Graph Engineering** (также «graph ai», «loop engineering», «harness engineering»).

## Ключевые посты

| Автор | Дата | Суть |
|---|---|---|
| @elune0x | 4 авг | **LOOP vs GRAPH vs HARNESS ENGINEERING** — самый чёткий разбор: loop=итерации (Temporal), graph=структура (LangGraph, NetworkX), harness=доступ (E2B, evals, OpenTelemetry). «Промпт в лупе, луп в графе, граф в харнессе». |
| @wandermist | 30 июл | **«The biggest Graph Engineering mistake everyone makes»** (439,9K просмотров, полный текст статьи — самый развёрнутый гайд в дискурсе): дефолт = **луп** (discover→plan→execute→verify), граф — только по 5 сигналам: (1) разные специализации на шагах, (2) параллельный fan-out→join, (3) разные модели/тулзы на шагах, (4) аудируемое ветвление, (5) перегруженный верификатор → выделить reviewer-узел (самый маленький честный граф). «Луп — это граф с одним узлом и ребром к себе». Граф, который не нужен = налог без отдачи: каждый узел — место отказа, каждое ребро — латентность. Тест-ловушка: не можешь указать, какой сигнал породил узел → удали его. |
| @PawelHuryn | 30 июл | Скепсис (цитируется в статье wandermist): «I call BS on graph engineering. Loop engineering was already confusing.» — бэклэш на хайп. |
| Head of Claude Code (через @themarcusbuild, @0xRafy, @0xClodex, @spotTheGap) | 3–4 авг | «85% инженеров Anthropic запускают сотни агентов. Способ — graph engineering». Один инженер = целая команда; агенты-ноды указывают друг на друга; память, которая не сбрасывается. |
| @LunarResearcher | 4 авг | Anthropic выпустили 50-мин воркшоп по Graph Engineering (таймкоды: tools/memory/planning, почему агенты ломаются в проде, датасеты и эвалы, тест всего графа до деплоя). «Prompt testing — старый воркфлоу, Graph evaluation — новый». |
| @NawinScript | 2 авг | Статья с диаграммами: **эволюция AI-инженерии** Prompt → Context → Skills → Loop → Graph. Каждый этап сменялся, когда предыдущий переставал масштабироваться. |
| @RichardFedorko | 4 авг | Plain-language интро «Loop vs Graph Engineering» для исследователей: луп = plan→act→observe→verify, 4 типа остановки по Anthropic; шаблоны воркфлоу. |
| @ForwardEditor | 3 авг | **Self-evolving graphs**: граф, который сам ведёт PRD → приоритет фич → реализацию → тесты → повтор (GPT-5.6 + Luna Max). |
| @yaserabbass | 3 авг | Реакция: «self-evolving graph — идея умная; как он обрабатывает логические циклы?» |
| @DanKornas | 5 авг | Potpie — «living context graph»: код+SDLC → граф-контекст для агентов (Apache 2.0). |
| Tencent Cloud Intl | 30 июл | «Graph Engineering is already blowing up — свежий бзворд или реальность?» |
| @spotTheGap | 4 авг | «Graph engineering is the new skill floor» — маршрутизация, границы памяти, «не давать каждому агенту переписывать план». |
| Neo4j NODES AI 2026 | авг | Agentic GraphRAG: autonomous knowledge graph construction + adaptive retrieval. |
| Sartech Labs / AI Builder Club | авг | Гайды «Graph Engineering: The Next Evolution», «Graph Engineering with Claude Code». |

## Ключевые месседжи дискурса

1. **Loop** контролирует итерации, **Graph** — структуру, **Harness** — доступ. Путать их = недиагностируемые фейлы агентов.
2. Граф делает топологию **видимой**: «inspect the topology without asking another model to explain it».
3. Память графа не сбрасывается между запусками; агенты верифицируют друг друга, работают параллельно.
4. Self-evolving graph — граф, который сам добавляет/мутирует/удаляет ноды по результатам работы.
5. Graph evaluation (тест всей системы) вместо prompt testing (тест ответа).

## Как это применили

Протокол «Графической Эволюции» (Гримуар v3.0) — см. SKILL.md: узлы/рёбра/состояния,
пульс, мутации с ≥2 кандидатами, рекомбинация, специализация, экстинкция, Летопись.
Артефакты: `graph.yaml` (реестр) + `pulse.py` (health-чек). Пилот: Мастер-ФМ / радио
(DJ → ACE-Step протокол → кэш → голос), The Grimoire, ParanoidX.
