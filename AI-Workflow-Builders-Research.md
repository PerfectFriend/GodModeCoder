# AI Workflow Builders — Research Notes (2026-08-10)

**Источники:** X.com треды + JointJS landing page
**Метод извлечения:** CDP Chrome automation с профилем пользователя (xcom)

---

## 1. MCP + Obsidian Vault — "The Missing Piece" (@chesny)

**Твит:** https://x.com/chesny/status/2077344214493319484

### Ключевые идеи:

**Что уже работает БЕЗ MCP:**
- Claude Code → прямой доступ к vault (файловая система)
- Читает структуру папок, grep/glob поиск, пишет/редактирует markdown
- Реальный кейс: vault вырос с 78 источников → 180 wiki-страниц (83 концепта + инструменты/люди/сравнения)
- Автоматические cross-references при добавлении нового контента
- Никаких плагинов/БД/API — только plain text + агент

**Потолок прямого доступа к файлам:**
- Агент должен заранее знать организацию vault'а (папки, frontmatter conventions, где концепты/инструменты)
- Каждый новый vault = новая интеграция, переобъяснять с нуля в system prompt
- Агент НЕ может спросить "что ты умеешь?" у vault'а
- Нет способа экспортировать derived operations (backlinks graph, Dataview query, orphan pages) без ручной реализации логики каждый раз

**Что решает MCP (Model Context Protocol):**
- Открытый стандарт Anthropic (ноябрь 2024) для интеграции ИИ с внешними системами
- До MCP: N ассистентов × M инструментов = N×M кастомных интеграций
- MCP = универсальный слой: ассистент ↔ MCP-сервер ↔ инструмент/данные
- Позволяет vault'у **экспортировать capabilities** (operations, resources, prompts)
- Агент может **обнаружить** возможности vault'а динамически

---

## 2. Free Polymarket Weather Trading Bots (@recogard)

**Твит 1:** https://x.com/recogard/status/2085805316294209877  
**Твит 2:** https://x.com/recogard/status/2073498090988769526

### 5 бесплатных ботов для погодного трейдинга (от простых к ML):

| # | Бот | Стратегия | Особенности | GitHub |
|---|-----|-----------|-------------|--------|
| 1 | **Hermes weather bot** (beginner, 5 мин) | Gaussian Bucket — прогноз 69F → диапазон 68-70F, сравнение с Polymarket prices | Автономный, сбор погоды из множества источников, самоподобучение, сигналы в Telegram | `github.com/nicolastinkl/h...` |
| 2 | **NWS forecast + Kelly** | NWS temperature data vs Polymarket odds, Kelly sizing для размера ставки | Авто-исполнение сделок | `github.com/MoonsatProtoco...` |
| 3 | **GFS-based bot** | 31 сценарий Global Forecast System → most likely temperature | Веб-дашборд: trades, forecasts, PnL, win rate | `github.com/suislanchez/po...` |
| 4 | **Real-time weather analysis** | Аэропорты (METAR/SPECI) + aviation observations | Детальные отчёты за день/неделю/месяц для любого города | `github.com/yangyuan-zhen/...` |
| 5 | **ML weather model** (Boston Univ thesis) | Учится на исторических ошибках прогнозов (например, NWS завышает на 5F в Чикаго) | Корректирует новые прогнозы на основе learned bias | `github.com/AruneshDev/Aut...` |

**Общее:** у всех есть simulation mode (тест на реальных рынках без риска).

### 20 Free Polymarket Trading Tools (категории):

**Analytics Tools:**
- `SII-WANGZJ/Polymarket_data` — 107GB, 1.1B сделок, 5 проф. Шанхайского ун-та
- `evan-kolberg/prediction-market-backtesting` — backtesting симулятор на реальных данных
- `ent0n29/polybot` — анализ поведения любого трейдера, поиск паттернов/стратегий
- `pmxt-dev/pmxt` — поиск по историческим рынкам/ценам/трейдерам в одном дашборде
- `txbabaxyz/collectmarkets2` — полная история кошелька → CSV + статистика/чарты

**Trading Bots:**
- `alsk1992/CloddsBot` — 118+ стратегий (latency, momentum, penny clipper, smart routing, DCA, expiry fade) — Cambridge CS student, hackathon winner
- `lihanyu81/polymarket_lp_tool` — авто-управление лимитными ордерами для ликвидности
- `MrFadiAi/Polymarket-bot` — Smart Money copy trading (топ трейдеры по PnL/win rate/stability)
- `HarrierOnChain/Prediction-Markets-Trading-Bot-Toolkits` — copy trading, арбитраж, whale alerts, market making, spread farming, sports trading
- ...и другие арбитражные боты

---

## 3. JointJS — AI Workflow Builder Platform

**Страница:** https://www.jointjs.com/ai-workflow-builders?utm_source=x&utm_medium=cpc

### Позиционирование:
> "Most node-graph libraries stop scaling before your product ships. JointJS is built for production from day one."

### Что дают "out of the box" (AI Workflow Builder demo):
- Custom node types для LLMs и tools
- Configurable property editor
- Drag-and-drop stencil
- Edge routing
- Undo/redo
- Готовый boilerplate для JS/React/Angular/Vue/Svelte

### Use Cases (кто строит на JointJS):
1. **AI pipeline & agent builders** — соединение LLMs, retrievers, memory в running pipeline; arbitrary graph topology, port-level connection rules
2. **Embedded AI automation platforms** — customer-facing workflow builders в SaaS; canvas под design language, экспортирует только нужные primitives
3. **AI execution tracing & observability** — read-only canvases из trace data, live updates, high node density
4. **Internal AI pipeline tooling** — visual debugging multi-step pipelines для команды

### Key Features (JointJS+):
- **Fully custom node UIs** — сложные интерактивные UI внутри ноды: model selectors, prompt editors, sliders, output previews; полный контроль rendering/state/interaction
- **Execution** — (текст обрезался, но суть: execution backend integration)

### Customer Story:
> "Implementing JointJS in our AI onboarding platform has been a game-changer! Saved significant time/resources by leveraging robust diagramming capabilities instead of building from scratch." — Rasmus Stjernström, CEO Silo Team

---

## Synthesis / Patterns

### Общие темы:
1. **Standards over custom integrations** — MCP (Anthropic), JointJS (diagramming standard) → избегают N×M проблемы
2. **Production-ready from day one** — и MCP, и JointJS позиционируются как production-grade, не прототипы
3. **Extensibility via protocol/layer** — MCP exposing capabilities; JointJS custom node UIs + port rules
4. **Open source + commercial support** — оба имеют free tier / open source core + paid features

### Для нашего контекста (Graph Evolution, SuperGuard, ParanoidX):
- **MCP** — идеально подходит для Obsidian Vault integration (graphthulhu/engraph уже идут в этом направлении)
- **JointJS** — можно использовать для визуализации графов эволюции в веб-интерфейсе (dashboard)
- **Polymarket bots** — примеры автономных агентов с обучением/адаптацией (relevant для godmode-coder evolution loops)

---

## Action Items

- [ ] Изучить MCP spec → интегрировать в Obsidian vault (graphthulhu/engraph MCP servers)
- [ ] Попробовать JointJS demo → оценить для визуализации graph.yaml в браузере
- [ ] Проанализировать архитектуру Polymarket ботов (self-improvement loops) → применить к evolution pulse
- [ ] Добавить ссылки в Vault: `C:\Vault\References\AI-Workflow-Builders\`

---

## 4. The Art of Computer Programming (TAOCP) — Donald Knuth

**Классика, которую нужно иметь под рукой.**

### Общая информация:
- **Автор:** Donald E. Knuth (Stanford University)
- **Издательство:** Addison-Wesley Professional
- **Начало публикации:** 1968 (Vol 1), продолжается до сегодня
- **Статус:** 4 тома опубликованы (Vol 4A, 4B, 4C — фасцикулы), Vol 5+ в разработке
- **Язык:** английский (переводы на русский: т.1-3 есть у «Вильямс», т.4 — частично)

### ТОМЫ И СОДЕРЖАНИЕ:

| Том | Год | Темы | Страниц |
|-----|-----|------|---------|
| **Vol 1: Fundamental Algorithms** | 1968 (3rd ed. 1997) | Математические основы, структуры данных (массивы, списки, деревья, графы), динамическое выделение памяти | ~650 |
| **Vol 2: Seminumerical Algorithms** | 1969 (3rd ed. 1998) | Случайные числа, арифметику больших чисел, полиномы, FFT, численные методы | ~750 |
| **Vol 3: Sorting and Searching** | 1973 (2nd ed. 1998) | Сортировка (внутренняя/внешняя), поиск, хеширование, B-деревья, оптимальные алгоритмы | ~800 |
| **Vol 4A: Combinatorial Algorithms, Part 1** | 2011 | Генерация комбинаторных объектов (перестановки, сочетания, деревья), SAT-решатели, BDD | ~880 |
| **Vol 4B: Combinatorial Algorithms, Part 2** | 2022 | Backtracking, dancing links (Algorithm X), exact cover, SAT extensions | ~900+ |
| **Vol 4C: Combinatorial Algorithms, Part 3** | 2025 (pre-fascicles) | Satisfiability, constraint propagation, المزيد | в процессе |
| **Vol 5+** | planned | Контекстно-свободные грамматики, парсинг, оптимизация компиляторов, teoria automатов | — |

### Ключевые концепции, актуальные сегодня:

1. **MMIX / MIX** — идеальная модель машины для анализа алгоритмов (заменила MIX в новых изданиях)
2. **Literate Programming** — WEB/CWEB: код + документация в одном источнике (прообраз Jupyter, но для системного кода)
3. **Анализ алгоритмов** — строгая математическая оценка сложности (O, Ω, Θ), константы, кэш-эффекты
4. **Combinatorial Generation** — алгоритмы перебора без рекурсии, Gray codes, efficient iterators
5. **Dancing Links (DLX)** — Algorithm X для exact cover → база для SAT-решателей, Sudoku, tiling
6. **Binary Decision Diagrams (BDD)** — компактное представление булевых функций, верификация
7. **Сверхдлинная арифметика** — база для криптографии, big integers в языках

### Почему это актуально для нас (Graph Evolution, AI agents):

| Область | Связь с TAOCP |
|---------|---------------|
| **Graph algorithms** (Vol 1, 4) | Обходы, топологическая сортировка, MST, shortest paths — основа graph-engineering |
| **Combinatorial search** (Vol 4) | Evolution pulse = поиск в пространстве геномов; мутации = комбинаторная генерация |
| **SAT/BDD** (Vol 4) | Fitness criteria = SAT проблемы; верификация конфигураций |
| **Literate Programming** | SKILL.md / EVOLUTION/PROJECT_PLAN.md = код + документация в одном месте |
| **Algorithm analysis** | Версионирование A00→A01 = измерение delta производительности/качества |
| **Memory hierarchy** | AMD iGPU shared RAM (local-ai-stack) → кэш-aware алгоритмы |

### Практические советы по чтению:

1. **Не читайте последовательно** — используйте как справочник: нужна сортировка → Vol 3, комбинаторика → Vol 4
2. **Упражнения** — с рейтингом сложности (00–50); решения в конце томов
3. **MMIX simulators** — `mmixal`, `mmix` (GitHub: `knuth/mmix`) для запуска примеров
4. **Pre-fascicles** — новые главы выкладываются на сайте Knuth (https://www-cs-faculty.stanford.edu/~knuth/taocp.html) раньше книг
5. **Russian translations** — т.1-3 у «Вильямс» (качественный перевод), т.4 — только фрагменты

### Где взять (легально):
- **Официальный сайт:** https://www-cs-faculty.stanford.edu/~knuth/taocp.html (pre-fascicles, errata, MMIX)
- **Addison-Wesley:** бумажные/ebook (DRM-free на informit.com)
- **GitHub:** `knuth/taocp` (MMIX, примеры кода)
- **Архивы:** `archive.org` — старые издания (1968-73) для исторического контекста

### Для Vault (C:\Vault\):
- Создать `References/TAOCP/` с краткими конспектами по томам
- Добавить узел в `graph.yaml`: `id: taocp`, `type: REFERENCE`, `role: "Canonical algorithms bible"`, `genome: "https://www-cs-faculty.stanford.edu/~knuth/taocp.html"`
- Связать с `graph-engineering`, `super-coder`, `systematic-debugging`

---

## 5. Context Graph Engineering with K3 — Kimi Agent Swarm (@0xRicker)

**Твит:** https://x.com/0xRicker/status/2087163793558126997

### Ключевая идея:
> **"A pile of 300 answers is not knowledge. Kimi Agent Swarm doesn't just run agents in parallel. It wires what they find into a single connected graph you can actually use."**

### Проблема "кучи" (pile problem):
- 300 агентов = 300 изолированных ответов в 300 коробках
- Это **не база знаний** — это просто список
- Ценность не в отдельных фактах, а в **связях между ними**
- При масштабировании проблема ухудшается: 100 отчётов компаний → вручную ищешь общих поставщиков/регуляции/зависимости

### Решение Kimi Agent Swarm:
1. **Swarm = мышцы** (параллельный запуск агентов)
2. **Context Graph = мозг** (проводит связи в единую структуру)
3. **Результат:** одна базу знаний, где каждый источник = узел, каждая связь = ребро
4. Можно **запрашивать, расширять, доверять** — это не просто набор ответов

### Архитектура:
- **300 агентов как узлы** (nodes)
- **1 связный граф** (connected graph)
- **5 live data feeds** (живые потоки данных)

### Почему это критично для нас (Graph Evolution, SuperGuard, ParanoidX):

| Аспект | Связь с нашим стеком |
|--------|---------------------|
| **Graph Engineering** | Context Graph = именно то, что строим в `graph.yaml` / `Evolution/` |
| **Evolution Pulse** | Swarm agents = parallel workers; graph wiring = fitness evaluation + edge creation |
| **SuperGuard** | Камеры/детекторы = агенты; annotated frames + alerts = context graph edges |
| **ParanoidX** | Deployment badges + version graph = connected knowledge base |
| **MCP + Obsidian** | Vault = context graph; MCP = protocol для wiring (см. раздел 1) |

### Ключевые цитаты для вдохновения:
> "The gathering is the easy part. The connecting is the expensive part, and it is the part that produces insight."

> "Nodes without edges are just a list."

> "Ten [agents] is hard. Three hundred without a graph is impossible."

### Action Items для нас:
- [ ] Изучить Kimi Agent Swarm architecture (поискать GitHub/docs)
- [ ] Сопоставить с `graph-engineering` skill: pulse → swarm, edges → wiring
- [ ] Добавить в `graph.yaml` узел: `id: k3-context-graph`, `type: PATTERN`, `role: "Swarm-to-graph wiring"`
- [ ] Прототипировать: параллельные агенты → автоматическое построение связей в vault

---

*Извлечено через CDP Chrome automation (профиль xcom) 2026-08-10*