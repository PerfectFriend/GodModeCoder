Warning: Permanently added '100.124.152.97' (ED25519) to the list of known hosts.
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
---
tags: [textbook, obsidian, frontmatter, wikilinks, graph-edges, typed-links,
C:\Vault\Frontmatter Wikilinks & Graph Edges.md


 dataview, metadata]
source: textbook
status: learned
date: 2026-08-10
priority: 9
---

# Frontmatter Wikilinks & Graph Edges

## Summary
Obsidian's frontmatter can store **structured wikilinks** that plugins (Dataview, Graph Link Types, Breadcrumbs, Juggl) convert into **typed graph edges**. This enables semantic knowledge graphs beyond simple `[[wikilink]]` connections.

## Core Concepts

### 1. Wikilinks in Frontmatter (YAML)
```yaml
---
tags: [project, ai]
related:
  - [[Project Alpha]]
  - [[Project Beta]]
depends_on:
  - [[Infrastructure Setup]]
  - [[Data Pipeline]]
blocks:
  - [[Deployment]]
author: [[John Doe]]
status: [[Active]]
---
```

**Key syntax**: `[[Page Name]]` inside YAML arrays or scalar values.

### 2. Typed Links (Breadcrumbs / Graph Link Types)
```yaml
---
# Breadcrumbs format (explicit edge types)
outgoing:
  - type: "depends_on"
    target: "[[Data Pipeline]]"
  - type: "references"
    target: "[[Research Paper]]"
incoming:
  - type: "blocks"
    target: "[[Deployment]]"
---
```

### 3. Dataview Inline Fields (Alternative)
```markdown
depends_on:: [[Data Pipeline]], [[Infrastructure Setup]]
blocks:: [[Deployment]]
author:: [[John Doe]]
status:: [[Active]]
```

## Plugin Ecosystem Support

| Plugin | Reads Frontmatter Wikilinks? | Edge Types | Notes |
|--------|------------------------------|------------|-------|
| **Dataview** | ✅ (metadata) | ❌ (flat) | Queries `file.related`, `file.depends_on` as arrays |
| **Graph Link Types** | ✅ | ✅ | Renders typed edges in graph view |
| **Breadcrumbs** | ✅ (own format + Dataview) | ✅ | Hierarchical + typed edges, trail navigation |
| **Juggl** | ✅ | ✅ | Force-directed graph, edge styling |
| **Excalibrain** | ✅ | ✅ | Auto-generates graph from frontmatter/links |
| **Obsidian Graph Analysis** | ✅ | ❌ | Network analysis metrics |

## Graph Edge Patterns

### Pattern 1: Dependency Graph (DAG)
```yaml
---
id: "task-123"
depends_on:
  - [[Task A]]
  - [[Task B]]
blocks:
  - [[Task C]]
---
```
**Query (DataviewJS)**:
```dataviewjs
const tasks = dv.pages("#task").where(p => p.depends_on);
const edges = tasks.flatMap(t => 
  (t.depends_on || []).map(dep => ({from: dep, to: t.file.link, type: "depends_on"}))
);
dv.table(["From", "To", "Type"], edges.map(e => [e.from, e.to, e.type]));
```

### Pattern 2: Semantic Knowledge Graph
```yaml
---
concept: "Transformer Architecture"
subclass_of: [[Neural Network]]
has_component:
  - [[Attention Mechanism]]
  - [[Feed Forward]]
  - [[Layer Norm]]
used_in:
  - [[BERT]]
  - [[GPT]]
  - [[T5]]
related_papers:
  - [[Attention Is All You Need]]
---
```

### Pattern 3: Project Management (Critical Path)
```yaml
---
project: "GodModeCoder"
phase: "Evolution Engine"
tasks:
  - id: "pulse"
    depends_on: []
  - id: "evolution_cycle"
    depends_on: ["pulse"]
  - id: "fitness_gates"
    depends_on: ["evolution_cycle"]
---
```

## Dataview Queries for Graph Edges

### All Outgoing Typed Edges
```dataview
TABLE without id
  file.link as "Source",
  type,
  target
FROM ""
WHERE depends_on OR related OR blocks
FLATTEN depends_on as target
FLATTEN "depends_on" as type
```

### Incoming Edges (Reverse Lookup)
```dataview
TABLE without id
  file.link as "Target",
  source,
  "depends_on" as type
FROM ""
FLATTEN depends_on as dep
WHERE dep = this.file.link
```

### Full Edge List (Graph Export)
```dataviewjs
const edges = [];
dv.pages("").forEach(p => {
  const types = ["depends_on", "related", "blocks", "subclass_of", "has_component", "used_in"];
  types.forEach(type => {
    (p[type] || []).forEach(target => {
      edges.push({source: p.file.link, target, type});
    });
  });
});
dv.table(["Source", "Target", "Type"], edges.map(e => [e.source, e.target, e.type]));
```

## Graph View Styling (CSS Snippets)

```css
/* .obsidian/snippets/typed-edges.css */
/* Color edges by type */
.graph-view.color-fill[edge-type="depends_on"] { stroke: #e74c3c; }
.graph-view.color-fill[edge-type="related"] { stroke: #3498db; }
.graph-view.color-fill[edge-type="blocks"] { stroke: #f39c12; }
.graph-view.color-fill[edge-type="subclass_of"] { stroke: #9b59b6; }
.graph-view.color-fill[edge-type="has_component"] { stroke: #2ecc71; }

/* Arrow markers for directed edges */
.graph-view .edge[edge-type="depends_on"]::after {
  content: "→";
  position: absolute;
  /* ... styling ... */
}
```

## Integration with Our Systems

### 1. GodModeCoder Evolution Graph
**Frontmatter per node** (`Evolution/*.md`):
```yaml
---
id: "gardener"
type: "agent"
status: "alive"
depends_on: ["oracle", "pulse"]
triggers: ["evolution_cycle"]
provides: ["health_check", "pruning"]
fitness_gates: ["correctness", "efficiency", "safety"]
lineage: "gen-4"
---
```

**Graph.yaml sync**: Auto-generate `Graph.yaml` from frontmatter via script.

### 2. Radio ArmsgeddonFM Pipeline
```yaml
---
stage: "consolidation"
depends_on: ["generation", "mixing"]
feeds: ["backup", "evaluation"]
memory_types: ["semantic", "procedural", "episodic"]
plugins: ["PlugMem", "OpenClaw"]
---
```

### 3. Paranoidx Sovereign Stack
```yaml
---
container: "v2ray"
depends_on: ["coturn", "smp"]
exposes: ["onion_service"]
security_level: "high"
license_gate: true
---
```

## Automation: Frontmatter → Graph.yaml Sync

```python
# scripts/sync_frontmatter_to_graph.py
import yaml
from pathlib import Path

VAULT = Path(r"C:\Vault")
GRAPH_YAML = Path(r"C:\Users\yusya\GodModeCoder\configs\graph.yaml")

EDGE_TYPES = ["depends_on", "related", "blocks", "triggers", "provides", "feeds"]

def extract_edges():
    nodes = []
    edges = []
    for md in VAULT.rglob("*.md"):
        if md.name.startswith("."): continue
        try:
            content = md.read_text(encoding="utf-8")
            if content.startswith("---"):
                fm_end = content.find("---", 3)
                if fm_end > 0:
                    fm = yaml.safe_load(content[3:fm_end])
                    node_id = fm.get("id") or md.stem
                    nodes.append({"id": node_id, **{k:v for k,v in fm.items() if k not in EDGE_TYPES}})
                    for etype in EDGE_TYPES:
                        for target in fm.get(etype, []):
                            edges.append({"source": node_id, "target": target, "type": etype})
        except Exception:
            pass
    return nodes, edges

nodes, edges = extract_edges()
graph = {"nodes": nodes, "edges": edges}
GRAPH_YAML.write_text(yaml.dump(graph, allow_unicode=True, sort_keys=False))
```

## Best Practices

| Practice | Why |
|----------|-----|
| Use `id` field (stable) | Filenames change, IDs don't |
| Prefer arrays over scalars | Multiple values = multiple edges |
| Standardize edge types | Consistent vocabulary = queryable graph |
| Document edge type taxonomy | `docs/edge-types.md` for team |
| Validate with Dataview | `TABLE WHERE depends_on` catches typos |
| Sync to Graph.yaml nightly | Single source of truth for evolution engine |

## Edge Type Taxonomy (Proposed Standard)

| Type | Direction | Semantics | Example |
|------|-----------|-----------|---------|
| `depends_on` | A → B | A requires B before start | Task → Prerequisite |
| `blocks` | A → B | A prevents B | Blocker → Blocked |
| `triggers` | A → B | A starts B | Event → Handler |
| `provides` | A → B | A supplies B | Service → Capability |
| `feeds` | A → B | A outputs to B | Pipeline stage |
| `subclass_of` | A → B | A is specialization | Concept hierarchy |
| `has_component` | A → B | A contains B | Composition |
| `used_in` | A → B | A utilized by B | Tool → Project |
| `references` | A → B | A cites B | Paper → Citation |

## References
- Obsidian Forum: [Wikilinks in YAML Front Matter](https://forum.obsidian.md/t/wikilinks-in-yaml-front-matter/10052)
- Breadcrumbs: [Typed Links](https://publish.obsidian.md/breadcrumbs-docs/Explicit+Edge+Builders/Typed+Links)
- Graph Link Types Plugin: Typed edge rendering
- Dataview Metadata: Frontmatter as queryable fields