# ChainZap Evolution Chronicle

## Session History

### 2026-08-03 — ChainZap Evolution Report Created
**Author:** Master Inquisitor  
**Session:** `20260803_054928_f4543633` (Telegram, nemotron-3-ultra-free)  
**Event:** Full strategic report generated (50 KB) covering:
- Executive summary with pivot to Universal Reputation Layer
- SWOT analysis and baseline metrics
- 4-phase evolution plan (Data Moat → API Platform → Ecosystem → Maximonster)
- Complete marketing plan (Developer/Retail/Enterprise, viral loops, $650k/yr budget)
- Commercial proposal (3 variants: Strategic Advisor, Project-Based, Co-founder)
- Milestone-based payment schedule with fairness clause
- Equity demand: 4-7% fully-diluted with performance tranches
- Risk register with mitigations
- Technical appendices: Data pipeline architecture, 15 proprietary heuristics, Enterprise proposal template

**Deliverable:** `ChainZap_Evolution_Report.md` sent to Telegram topic

---

### 2026-08-07 — Project Extracted to Obsidian Vault
**Author:** Hermes Agent (this session)  
**Session:** Current (default profile)  
**Event:** ChainZap project extracted from session history and saved as standalone project in Obsidian Vault for GodModeCoder compatibility

**Files Created:**
1. `C:/Vault/Projects/ChainZap/ChainZap_Evolution_Report.md` — Full strategic report (Markdown, 50 KB)
2. `C:/Vault/Projects/ChainZap/graph.yaml` — Graph evolution format with:
   - Project node with metrics and phases
   - 4 phase nodes with KPIs, budgets, timelines
   - 11 hiring nodes (urgent/planned/pending)
   - 8 milestone nodes with criteria and owners
   - Contributor node (Master Inquisitor) with equity terms
   - 3 commercial variant nodes with terms
   - 7 risk nodes with probability/impact/mitigation
   - Edges: contains, requires, has_milestone, precedes, proposes, has_risk
   - Pulse config: weekly cadence, Monday reviews, tracked metrics, gate reviews
   - Chronicle: session history entries

**Purpose:** Enable GodModeCoder to load this project in a new session with full context via `graph.yaml` evolution graph protocol.

---

### 2026-08-09 — BOOTSTRAPPED PIVOT: $0 Budget, Human + AI Team
**Author:** Master Inquisitor + Hermes Agent  
**Session:** Current (default profile)  
**Event:** Radical restructuring — removed all hiring budget, replaced team with **Master Inquisitor (Human) + Hermes Agent (AI)**. Budget = $0. Revenue-first, bootstrap execution.

**Key Changes:**
1. **Budget:** $0 across all phases (was $1.175M total)
2. **Team:** 2 contributors — Human (Strategy/GTM/Hands-on Data) + AI (Full-stack Data/ML/Backend/DevOps/Docs 24/7)
3. **Timeline:** Accelerated via AI force multiplier (M1: Month 3, M2: Month 6, M3: Month 9...)
4. **Milestones:** Adapted for bootstrapped reality (smaller Graph DB targets, self-hosted infra)
5. **New Risks:** Burnout, Technical Debt, Solo Human bottleneck
6. **Equity:** Master Inquisitor = Founder equity (no external dilution yet)

**Philosophy:** "Hermes = 10x force multiplier. We automate everything: codegen, tests, docs, CI/CD, infra. First human hires ONLY after M3 (revenue)."

**Files Updated:**
- `graph.yaml` — Complete rewrite for bootstrapped model
- `chronicle.md` — This entry

---

### 2026-08-09 — LOCAL-FIRST INFRASTRUCTURE: Netbook + Tor Hidden Service
**Author:** Master Inquisitor  
**Decision:** До релиза проекта хостинг не нужен. Локальный тестовый стенд на нетбуке (где крутится нода):
- **40GB SSD** — хватает для ClickHouse + Graph DB + индексов
- **Tor уже поднят** — добавляем ещё один hidden service для API
- **Zero hosting cost** — никаких VPS, облаков, Kubernetes до revenue
- **Release Candidate** — показываем инвестору через `.onion` URL
- **После получения денег** — мигрируем на нормальный хостинг

**Architecture:**
```
Netbook (local)                    Investor/Partner
├── ClickHouse (embedded)          │
├── Kuzu/FalkorDB (embedded)       │   Tor Browser
├── Indexer (Rust)                 │       │
├── API (FastAPI/Go)               │       ▼
└── Tor Hidden Service ─────────────▶ .onion URL
    (private, no public IP)            (demo access)
```

**Benefits:**
- $0 infrastructure cost
- No public attack surface (hidden service only)
- Works behind NAT/firewall/CGNAT
- Perfect for stealth development
- Investor demo: "Here's the .onion URL, try the API"

**Files Updated:**
- `graph.yaml` — Phase 1 description + KPI "Infra cost: $0"
- `chronicle.md` — This entry

---

## Next Actions (Bootstrapped Phase 1 Start)

### Immediate (Week 1-2)
- [ ] **ClickHouse single-node** on cheap VPS ($20/мес) or local — Hermes designs schema, deploys
- [ ] **Graph DB** (Kuzu/FalkorDB — embedded, free) — Hermes sets up, models schema
- [ ] **Indexer v1** (Rust/Go) — mempool ingestion → ClickHouse → Graph DB — Hermes writes
- [ ] **5 Heuristics Spec** — Master Inquisitor defines, Hermes implements
- [ ] **Logging Pipeline** — 100% check logging to ClickHouse — Hermes builds

### Month 1 Targets
- [ ] ClickHouse operational with schema
- [ ] Graph DB > 10k nodes (seed data)
- [ ] Indexer catching mempool + logs
- [ ] 2-3 heuristics in production
- [ ] CI/CD for data jobs (GitHub Actions, free)

### Month 2 Targets
- [ ] Graph DB > 50k nodes
- [ ] 5 heuristics in production, precision > 95%
- [ ] Latency < 12s mempool → signal
- [ ] Cross-chain resolution 95%+ recall

### Month 3 — M1 Gate Review
- [ ] ClickHouse single-node operational
- [ ] Graph DB > 100k nodes
- [ ] 5 heuristics in production
- [ ] 100% check logging
- [ ] CI/CD pipeline for data jobs

---

## Master Inquisitor + Hermes Commitment

| Role | Master Inquisitor (Human) | Hermes Agent (AI) |
|------|---------------------------|-------------------|
| **Focus** | Strategy, GTM, Partnerships, Sales, High-level Architecture | Execution: Code, Infra, ML, Docs, Tests, CI/CD, Ops |
| **Availability** | Full-time, 6 days/week | 24/7 parallel |
| **Cost** | $0 (founder equity) | $0 (local Ollama) |
| **Key Deliverables** | Partnerships (Rabby, 1inch, Safe, MetaMask, Chainlink), Enterprise sales, GTM strategy, Architecture decisions | ClickHouse/Flink/Graph DB, Indexer, ML pipelines, API/SDKs, Docs, Infra, Code review |

---

## Gate Reviews Scheduled (Bootstrapped)

| Milestone | Deadline | Criteria |
|-----------|----------|----------|
| M1: Data Foundation | Month 3 | ClickHouse + Graph DB (100k+ nodes), 5 heuristics, 100% logging |
| M2: Public API Beta | Month 6 | OpenAPI spec, SDKs (TS/Py/Go), Sandbox, 3 beta users |
| M3: First Enterprise | Month 9 | Signed contract ≥$2k/mo, production integration |
| M4: 10 Integrations | Month 10 | 10 live Wallet/DEX/Protocol integrations |
| M5: Trust Registry | Month 14 | ERC-721 badges on mainnet, ENS, 3 protocols using |
| M6: $1M ARR / Series A | Month 18 | $1M ARR OR Series A term sheet, team 5-10+ |
| M7: Network Effects | Month 22 | K-factor >1.2, 50+ integrations, Oracle in 5+ protocols |
| M8: $10M ARR | Month 30 | $10M ARR, NRR >120% |

---

## Key Metrics Baseline (August 2026)
- **MAU:** ~5,000 (Telegram + Web)
- **Daily Checks:** ~200
- **Pro Subscribers:** ~50
- **MRR:** ~$300
- **Chains:** Ethereum, BSC, Polygon, Arbitrum, Optimism
- **API Calls/day:** 0 (no API yet)
- **Integrations:** 0
- **Infra Cost:** $0 (local) → $50-100/мес (VPS from Month 1)

## Targets (Month 6 — M2)
- **MAU:** 25,000
- **Daily Checks:** 2,000
- **Pro Subscribers:** 200
- **MRR:** $3,000
- **API Calls/day:** 10,000
- **Integrations:** 3 (beta)

## Strategic Positioning
**Current:** Wallet checker (Free → Pro $5.99/mo)  
**Pivot:** Universal Reputation Layer — infrastructure trust layer for all Web3  
**Moat:** Proprietary Knowledge Graph + 15+ heuristics + Real-time mempool + Cross-chain identity + Reputation Score (ML) — **BUILT BY US**  
**Distribution:** Wallet/DEX/Protocol integrations (Rabby, 1inch, Safe, MetaMask, Paraswap)  
**Exit:** Strategic sale (Coinbase, Binance, Chainalysis, Consensys) $500M-2B+ or IPO at $100M+ ARR

---

## Bootstrapped Principles

1. **Revenue First** — Every feature must drive Pro subs or API usage
2. **AI Force Multiplier** — Hermes writes 80% of code, we review 20%
3. **No External Dependencies** — Own the data, own the infra, own the models
4. **Lean Infra** — VPS <$100/мес until revenue covers it
5. **Hard Deadlines** — M-gates are non-negotiable; miss = pivot or kill
6. **Burnout Prevention** — 1 day off/week, Hermes does the grunt work
7. **Technical Excellence** — Hermes self-reviews (TurboCoder), mandatory tests for critical paths

---

*Chronicle maintained per Graph Evolution Protocol v3.0 — pulse weekly, gates at milestones, chronicle per session. Bootstrapped edition: Human + AI, $0 budget, infinite leverage.*