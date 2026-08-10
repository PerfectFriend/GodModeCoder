# Standalone Project Graph Pattern
## Creating Independent Project Evolution Graphs in Obsidian Vault

This pattern was used in session 2026-08-07 to extract **ChainZap** and **GlobeVis** projects from session history and save them as standalone GodModeCoder-compatible projects.

---

## Structure per Project

```
C:\Vault\Projects\<ProjectName>/
├── <ProjectName>_Evolution_Report.md    # Full strategic report (markdown)
├── graph.yaml                            # Evolution graph (nodes, edges, pulse, chronicle)
└── chronicle.md                          # Session history & next actions
```

---

## graph.yaml Schema for Standalone Projects

```yaml
nodes:
  # Project root node
  - id: <project-slug>-core
    type: project
    label: "<Project Display Name>"
    description: "..."
    status: active
    phase: "Phase X: <Name>"
    priority: critical
    tags: [domain, tags, ...]
    metrics:
      key_metric: value
      target_metric: value
    created: "YYYY-MM-DD"
    updated: "YYYY-MM-DD"

  # Phase nodes (sequential)
  - id: phase1-<name>
    type: phase
    label: "Фаза 1: <Name>"
    description: "..."
    parent: <project-slug>-core
    status: planning|pending|active|future
    timeline: "Месяцы X-Y"
    budget: 12345
    kpis:
      - "KPI 1"
      - "KPI 2"
    dependencies: []  # or [phase0-id]

  # Hiring nodes
  - id: hire-<role>
    type: hire
    label: "<Role> — <Level>"
    description: "..."
    parent: <phase-id>
    status: urgent|planned|pending|conditional|future
    compensation: "$X-Y/мес + equity Z%"
    timeline: "Найм в Месяц N"

  # Milestone nodes (gates)
  - id: milestone-g1
    type: milestone
    label: "G1: <Name>"
    description: "..."
    parent: <phase-id>
    deadline: "Week/Month N"
    owner: "<Role>"
    criteria:
      - "Criterion 1"
      - "Criterion 2"

  # Contributor nodes
  - id: <contributor-slug>
    type: contributor
    label: "<Name>"
    role: "<Role> (<X>% equity)"
    description: "..."
    equity: "<X>%"
    commitment: "..."
    areas:
      - "Area 1"
      - "Area 2"
    status: active

  # Risk nodes
  - id: risk-<slug>
    type: risk
    label: "<Risk Name>"
    probability: low|medium|high
    impact: low|medium|high|critical
    mitigation: "..."
    owner: "<Role>"

edges:
  # Hierarchy
  - from: <project-slug>-core
    to: <phase-id>
    type: contains
  - from: <phase-id>
    to: <child-node-id>
    type: requires|has_milestone

  # Sequence
  - from: <phase-id>
    to: <next-phase-id>
    type: precedes

  # Contribution & Risks
  - from: <project-slug>-core
    to: <contributor-id>
    type: contributed_by
  - from: <project-slug>-core
    to: <risk-id>
    type: has_risk

pulse:
  cadence: weekly          # weekly|biweekly|monthly
  review_day: Monday       # Day for pulse review
  metrics_tracked:         # 7-11 key metrics
    - "Metric 1"
    - "Metric 2"
  gate_reviews:            # Major milestones
    - "G1: Week 4 — Description"
  scenario_gates:          # Strategic decision points
    - "Gate A (Month 3): Criteria → Action"

chronicle:
  - date: "YYYY-MM-DD"
    event: "Description"
    type: discovery|strategy|setup|review|decision
    author: "Author"
    details: "Full context, decisions, links"
```

---

## Node Types Used

| Type | Purpose | Required Fields |
|------|---------|-----------------|
| `project` | Root node | id, label, description, status, phase, priority, tags, metrics, created |
| `phase` | Evolution phase | id, label, description, parent, status, timeline, budget, kpis, dependencies |
| `hire` | Hiring need | id, label, description, parent, status, compensation, timeline |
| `milestone` | Gate review | id, label, description, parent, deadline, owner, criteria |
| `contributor` | Team member | id, label, role, description, equity, commitment, areas, status |
| `risk` | Risk register | id, label, probability, impact, mitigation, owner |

---

## Edge Types Used

| Type | From → To | Meaning |
|------|-----------|---------|
| `contains` | project → phase | Project contains phase |
| `requires` | phase → hire/milestone | Phase requires this |
| `has_milestone` | phase → milestone | Phase has this gate |
| `precedes` | phase → next_phase | Sequential dependency |
| `contributed_by` | project → contributor | Project has this contributor |
| `has_risk` | project → risk | Project has this risk |

---

## Pulse Config

```yaml
pulse:
  cadence: weekly          # weekly|biweekly|monthly
  review_day: Monday       # Day for pulse review
  metrics_tracked:         # 7-11 key metrics
    - "MRR"
    - "Churn %"
    - "CAC"
  gate_reviews:            # Major milestones
    - "G1: Week 4 — SaaS MVP Live"
  scenario_gates:          # Strategic decision points
    - "Gate A (Month 3): $5K MRR + CAC <$80 → Open Aggressive tap"
```

---

## Chronicle Format

```yaml
chronicle:
  - date: "YYYY-MM-DD"
    event: "Short event name"
    type: discovery|strategy|setup|review|decision
    author: "Author"
    details: "Full context, decisions, links"
```

---

## Verification Checklist

After creating project graph:
- [ ] YAML syntax valid (`python -c "import yaml; yaml.safe_load(open('graph.yaml'))"`)
- [ ] All node IDs unique
- [ ] All edge `from`/`to` reference existing node IDs
- [ ] Required sections present: `nodes`, `edges`, `pulse`, `chronicle`
- [ ] Pulse has `cadence`, `review_day`, `metrics_tracked`, `gate_reviews`
- [ ] At least 1 project node, 3+ phase nodes, 3+ milestones
- [ ] Contributors have equity % summing to 100%
- [ ] Risks cover: technical, market, team, financial, strategic

---

## Examples Created

### ChainZap (Web3 Reputation Layer)
- Location: `C:\Vault\Projects\ChainZap\`
- 32 nodes, 34 edges
- 4 phases (Data Moat → API Platform → Ecosystem → Maximonster)
- 8 milestones (M1-M8), 11 hires, 7 risks
- 3 commercial variants (Advisor, Project-Based, Co-founder)

### GlobeVis (Visual Analytics SaaS)
- Location: `C:\Vault\Projects\GlobeVis\`
- 24 nodes, 26 edges
- 4 phases (Foundation → PMF → Growth → Category Leadership)
- 5 milestones (G1-G5), 4 hires, 8 risks
- 3 financial scenarios (Pessimistic/Realistic/Aggressive)
- Scenario gates (A/B/C) for Realistic→Aggressive switch

---

## GodModeCoder Compatibility

These standalone graphs are designed to be loaded by GodModeCoder in a new session:

```python
# In GodModeCoder session:
# 1. Load project graph
graph = load_yaml("C:/Vault/Projects/ChainZap/graph.yaml")

# 2. Resume from last chronicle entry
last_entry = graph['chronicle'][-1]

# 3. Check pulse status
current_phase = graph['pulse']['gate_reviews'][0]

# 4. Continue evolution from current state
```

The structure mirrors the main Grimoire `graph.yaml` but scoped to a single project with its own phases, team, risks, and timeline.