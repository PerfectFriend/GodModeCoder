Warning: Permanently added '100.124.152.97' (ED25519) to the list of known hosts.
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
---
tags: [textbook, mcp, agent-memory, knowledge-base, long-term-memory, rag, mcp-server, agent-architecture]
source: textbook
status: learned
date: 2026-08-10
priority: 9
---

# MCP Servers as Agent Knowledge Base

## Summary
**MCP (Model Context Protocol) servers can serve as durable, shared knowledge bases for AI agents** — providing long-term memory that persists across runs, is auditable by humans, and enables write-back of synthesized findings. This pattern replaces "memory black boxes" with human-readable, version-controlled notes that both agents and humans can read, write, and trust.

## Core Problem: Agent Memory Gap

### Two Types of Agent Memory
| Type | Description | Use Case |
|------|-------------|----------|
| **Extraction Memory API** | Automatic, high-volume recall from conversations; optimized for software retrieval | High-throughput, low-curation recall |
| **Knowledge Base (MCP)** | Deliberate, human-readable notes organized in folders/tags; durable, auditable, shared | Correct, inspectable, shared context |

### When Knowledge Base Beats Memory API
- ✅ **Must be auditable**: When agent acts on memory, you need to see exactly what it believed
- ✅ **Humans share context**: Teammates/their assistants need same project state
- ✅ **Write-back required**: Agent should write durable results (plans, decisions) back to memory
- ✅ **Correctness matters**: Extracted fragments can hallucinate; curated notes don't

## MCP as Knowledge Base Interface

### Standard MCP Tools for Knowledge Base
```json
{
  "tools": [
    {"name": "kb_search", "description": "Search knowledge base by query"},
    {"name": "kb_read", "description": "Read a specific note by path/ID"},
    {"name": "kb_create", "description": "Create new note with content"},
    {"name": "kb_update", "description": "Update existing note"},
    {"name": "kb_delete", "description": "Delete note (with confirmation)"},
    {"name": "kb_list", "description": "List notes by folder/tag/date"}
  ]
}
```

### Agent Workflow with MCP Knowledge Base
```
1. START RUN
   → kb_search("current project state") 
   → kb_read("architecture-decision-001")
   → Load relevant context into working memory

2. EXECUTE TASK
   → Reason, act, observe using loaded context

3. END RUN
   → kb_create("decision-002", "Chose X over Y because...")
   → kb_update("project-state", "Completed milestone A")
   → kb_search("related patterns") for next run
```

## Architecture Patterns

### Pattern 1: Obsidian Vault as Knowledge Base (Local-First)
```
┌─────────────────┐     MCP STDIO      ┌──────────────────┐
│   AI Agent      │ ◄─────────────────► │  obsidian-hybrid │
│  (Claude/Codex) │     search/read    │  search / graph  │
└─────────────────┘     write/create   │  thulhu          │
                            ▲            └────────┬─────────┘
                            │                     │
                     ┌──────┴──────┐    ┌─────────┴─────────┐
                     │ C:\Vault    │    │ .obsidian/        │
                     │ ├─ Evolution│    │ ├─ graph.json     │
                     │ ├─ Projects │    │ ├─ plugins/       │
                     │ ├─ Inbox    │    │ └─ graph-presets  │
                     │ └─ ...      │    └──────────────────┘
                     └─────────────┘
```
**Tools**: `obsidian-hybrid-search` (BM25+vector), `graphthulhu` (graph navigation/write)

### Pattern 2: Hjarni / Dedicated KB Server (Multi-Agent)
```
┌─────────────┐   ┌─────────────┐
│  Agent A    │   │  Agent B    │
│  (Coding)   │   │  (Review)   │
└──────┬──────┘   └──────┬──────┘
       │ MCP             │ MCP
       ▼                 ▼
┌─────────────────────────────────┐
│   Hjarni KB Server (MCP)        │
│  ├─ Search/Read/Create/Update   │
│  ├─ Version Control (Git)       │
│  ├─ Access Control (per agent)  │
│  └─ REST API (for humans)       │
└─────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│   Knowledge Store               │
│  ├─ /projects/                  │
│  ├─ /decisions/                 │
│  ├─ /patterns/                  │
│  └─ /conventions/               │
└─────────────────────────────────┘
```

### Pattern 3: Hybrid (KB + Extraction Memory)
| Layer | Technology | Purpose |
|-------|------------|---------|
| **Source of Truth** | Knowledge Base (Obsidian/Hjarni) | Durable, auditable, shared |
| **High-Volume Recall** | Extraction Memory (Vector DB) | Automatic conversation mining |
| **Sync** | Periodic job | KB → Memory API for fast retrieval |

## Knowledge Base Schema for Agents

### Folder Structure
```
C:\Vault\
├── BRAIN.md                 # Master index / entry point
├── conventions/             # Team/project conventions
│   ├── coding-style.md
│   ├── git-workflow.md
│   └── review-checklist.md
├── decisions/               # Architecture Decision Records (ADRs)
│   ├── 001-container-orchestration.md
│   └── 002-mcp-vs-rest.md
├── patterns/                # Reusable solution patterns
│   ├── fitness-gates.md
│   ├── loop-graph-harness.md
│   └── extinction-protocol.md
├── projects/                # Project-specific state
│   ├── godmodecoder/
│   │   ├── current-gen.md
│   │   ├── fitness-scores.md
│   │   └── blockers.md
│   └── radio/
├── research/                # External research synthesis
│   ├── dgm-paper-summary.md
│   └── plugmem-integration.md
└── Inbox/                   # Raw capture (processed daily)
```

### Note Template (Frontmatter Standard)
```yaml
---
id: "adr-001-container-orchestration"
type: "decision"          # decision | pattern | convention | research | state
status: "accepted"        # proposed | accepted | deprecated | superseded
tags: [architecture, containers, paranoidx]
created: "2026-08-10"
updated: "2026-08-10"
author: "GodModeCoder"
related:
  - [[patterns/loop-graph-harness]]
  - [[projects/paranoidx]]
supersedes: null
superseded_by: null
---

# Decision: Container Orchestration for Paranoidx

## Context
5-container stack (SMP, Coturn, V2Ray, Tor, XFTP) on single N100.

## Decision
Use Docker Compose with health checks, not Kubernetes.

## Rationale
- Single host, no scaling need
- Team expertise: Compose > K8s
- Resource overhead: Compose ~50MB vs K8s ~500MB

## Consequences
- Simpler debugging
- No auto-scaling (manual)
- Human gate on deploy required
```

## Agent Read/Write Protocols

### Read Protocol (Start of Run)
```python
async def load_context(agent, goal):
    # 1. Search for goal-relevant notes
    results = await agent.mcp.call("kb_search", {
        "query": goal,
        "tags": agent.project_tags,
        "limit": 10
    })
    
    # 2. Load top-k full notes
    context = []
    for r in results[:5]:
        note = await agent.mcp.call("kb_read", {"path": r.path})
        context.append(note)
    
    # 3. Always load conventions
    conventions = await agent.mcp.call("kb_list", {
        "folder": "conventions",
        "limit": 20
    })
    
    return {"goal_context": context, "conventions": conventions}
```

### Write Protocol (End of Run)
```python
async def save_findings(agent, findings):
    for finding in findings:
        if finding.type == "decision":
            path = f"decisions/{finding.id}.md"
            template = DECISION_TEMPLATE
        elif finding.type == "pattern":
            path = f"patterns/{finding.slug}.md"
            template = PATTERN_TEMPLATE
        elif finding.type == "state_update":
            path = f"projects/{agent.project}/current-state.md"
            template = STATE_TEMPLATE
        
        await agent.mcp.call("kb_create", {
            "path": path,
            "content": template.format(**finding),
            "overwrite": finding.type == "state_update"
        })
```

## MCP Server Implementations Comparison

| Server | Backend | Write Support | Auth | Best For |
|--------|---------|---------------|------|----------|
| **obsidian-hybrid-search** | Obsidian vault | ✅ (via file API) | Local | Local-first, hybrid search |
| **graphthulhu** | Obsidian/Logseq | ✅ Full CRUD | Token/None | Graph navigation + write |
| **Hjarni** | Custom (SQLite/Git) | ✅ Full CRUD | API Key | Multi-agent, shared KB |
| **GitMem** | Git repo | ✅ Git commits | SSH/HTTPS | Code-focused memory |
| **SeaMeet** | Embedded DB | ✅ Local-first | Local | Multi-agent access control |

## Security & Governance

### Access Control
```yaml
# .mcp-permissions.yaml
agents:
  godmodecoder:
    read: ["*"]
    write: ["projects/godmodecoder/**", "patterns/**", "decisions/**"]
    delete: []
  paranoidx-agent:
    read: ["projects/paranoidx/**", "conventions/**"]
    write: ["projects/paranoidx/state.md"]
    delete: []
  radio-agent:
    read: ["projects/radio/**", "research/**"]
    write: ["projects/radio/logs/**"]
```

### Audit Trail
- Every MCP tool call logged with: `agent_id`, `tool`, `params`, `timestamp`, `result_hash`
- Knowledge base backed by Git → full history, blame, revert
- Human review gate for `kb_delete` and high-impact `kb_update`

## Integration with Evolution Loops

### GodModeCoder Nightly Evolution
```python
# In autonomous_evolution.py → MEMORY phase
async def update_knowledge_base(cycle_results):
    # 1. Create decision record if fitness improved
    if cycle_results.fitness_improved:
        await kb_create(f"decisions/gen-{cycle}-fitness-improvement.md", 
            f"Generation {cycle}: Fitness improved from {prev} to {new}")
    
    # 2. Update project state
    await kb_update("projects/godmodecoder/current-gen.md", 
        f"gen={cycle}, fitness={fitness}, alive={alive}/{total}")
    
    # 3. Extract new patterns
    for pattern in cycle_results.new_patterns:
        await kb_create(f"patterns/{pattern.slug}.md", pattern.content)
    
    # 4. Log extinction events
    if cycle_results.extinction_triggered:
        await kb_create(f"research/extinction-gen-{cycle}.md", 
            f"Type: {extinction_type}, Removed: {count}")
```

### Radio ArmsgeddonFM Daily Cycle
```python
# Morning: load prompt templates, song patterns
context = await load_context("radio-generation")

# Evening: save generated songs, evaluations
await kb_create("projects/radio/logs/2026-08-10.md", daily_log)
await kb_update("projects/radio/song-catalog.md", new_entries)
```

## Best Practices

| Practice | Why |
|----------|-----|
| **One KB per project/team** | Isolation, clear ownership |
| **Human-readable markdown** | Debuggable, version-controllable |
| **Standard frontmatter** | Queryable, filterable, linkable |
| **ADR format for decisions** | Audit trail, supersession tracking |
| **Write-back every run** | Compound knowledge, avoid cold starts |
| **Read conventions first** | Consistency across agents |
| **Git-back the vault** | Full history, blame, collaboration |

## Anti-Patterns to Avoid

| Anti-Pattern | Fix |
|--------------|-----|
| Agent-only memory (opaque vectors) | Use KB as source of truth |
| No write-back → cold start every run | Mandate write protocol |
| Single flat folder | Structured: conventions/decisions/patterns/projects |
| No frontmatter schema | Enforce `type`, `status`, `tags`, `related` |
| Deleting instead of superseding | Use `status: superseded`, link to replacement |

## References
- **Hjarni**: https://hjarni.com/blog/knowledge-base-for-ai-agents
- **MCP Spec**: https://modelcontextprotocol.io/
- **Google Cloud MCP Guide**: https://cloud.google.com/discover/what-is-model-context-protocol
- **Anthropic MCP Announcement**: https://www.anthropic.com/news/model-context-protocol
- **GitMem**: https://glama.ai/mcp/servers/gitmem-dev/gitmem
- **Obsidian Hybrid Search**: https://github.com/flowing-abyss/obsidian-hybrid-search
- **graphthulhu**: https://github.com/skridlevsky/graphthulhu