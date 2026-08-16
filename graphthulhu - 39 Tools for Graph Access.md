Warning: Permanently added '100.124.152.97' (ED25519) to the list of known hosts.
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
---
tags: [textbook, mcp, graphthulhu, knowledge-graph, obsidian, logseq, agent-integration, tools]
source: textbook
status: learned
date: 2026-08-10
priority: 9
---

# graphthulhu — 39 Tools for Graph Access

## Summary
**graphthulhu** is an MCP (Model Context Protocol) server that gives AI agents **full read-write access** to Obsidian or Logseq knowledge graphs. It exposes **39 tools** covering navigation, search, analysis, writing, decision protocols, journals, flashcards, and whiteboards. Written in Go, supports both Obsidian (local vault) and Logseq (HTTP API) backends.

## Architecture

### Backend Interface
```go
// vault/vault.go - Backend interface
type Backend interface {
    // Core graph operations
    GetPage(name string) (*Page, error)
    GetBlock(uuid string) (*Block, error)
    SearchPages(query string) ([]*Page, error)
    SearchBlocks(query string) ([]*Block, error)
    
    // Graph analysis
    GetGraphOverview() (*GraphOverview, error)
    GetConnections(page string) (*Connections, error)
    FindGaps() ([]*Gap, error)
    FindClusters() ([]*Cluster, error)
    
    // Write operations
    CreatePage(name, content string) error
    UpdateBlock(uuid, content string) error
    DeletePage(name string) error
    AddLink(source, target string) error
}
```

### Supported Backends
| Backend | Access Method | Auth | Status |
|---------|---------------|------|--------|
| **Obsidian** | Local vault filesystem | None | ✅ Full |
| **Logseq** | HTTP API (port 12315) | Token | ✅ Full |
| **Read-only** | `--read-only` flag | N/A | ✅ Safe |

## MCP Server Setup

### Obsidian Configuration (Claude Code / Desktop)
```json
{
  "mcpServers": {
    "graphthulhu": {
      "command": "graphthulhu",
      "args": ["--backend", "obsidian", "--vault", "C:\\Vault"],
      "env": {}
    }
  }
}
```

### Logseq Configuration
```json
{
  "mcpServers": {
    "graphthulhu": {
      "command": "graphthulhu",
      "env": {
        "LOGSEQ_API_URL": "http://127.0.0.1:12315",
        "LOGSEQ_API_TOKEN": "your-token"
      }
    }
  }
}
```

### Read-Only Mode (Safe for Production)
```json
{
  "mcpServers": {
    "graphthulhu": {
      "command": "graphthulhu",
      "args": ["--read-only", "--backend", "obsidian", "--vault", "C:\\Vault"],
      "env": {}
    }
  }
}
```

## 39 Tools Catalog

### Navigation (4 tools)
| Tool | Description |
|------|-------------|
| `navigate_page` | Get page content by name |
| `navigate_block` | Get block by UUID |
| `navigate_links` | Get outgoing/incoming links for page |
| `navigate_references` | Get block references (transclusions) |

### Search (5 tools)
| Tool | Description |
|------|-------------|
| `search_pages` | Full-text page search |
| `search_blocks` | Full-text block search |
| `search_properties` | Dataview-style property queries |
| `search_tags` | Tag-based search |
| `search_datascript` | Logseq DataScript queries |

### Analysis (6 tools)
| Tool | Description |
|------|-------------|
| `analyze_overview` | Graph stats: nodes, edges, density, components |
| `analyze_connections` | Page connections (in/out, depth) |
| `analyze_gaps` | Structural holes, missing links |
| `analyze_clusters` | Community detection, modularity |
| `analyze_bfs` | Breadth-first traversal from node |
| `analyze_centrality` | PageRank, betweenness, degree centrality |

### Writing (7 tools)
| Tool | Description |
|------|-------------|
| `write_create_page` | Create new page with content |
| `write_update_block` | Update block by UUID |
| `write_delete_page` | Delete page |
| `write_move_page` | Rename/move page |
| `write_add_link` | Add wikilink between pages |
| `write_remove_link` | Remove link |
| `write_transclude` | Add block reference/transclusion |

### Decision Protocol (4 tools) — *Unique to graphthulhu*
| Tool | Description |
|------|-------------|
| `decision_check` | Verify if decision exists for topic |
| `decision_create` | Create decision record with options |
| `decision_resolve` | Resolve decision with chosen option |
| `decision_defer` | Defer decision with reason |

### Journals (4 tools)
| Tool | Description |
|------|-------------|
| `journal_list` | List journal pages in date range |
| `journal_search` | Search within journals |
| `journal_today` | Get/create today's journal |
| `journal_flashcards` | SRS flashcard overview |

### Flashcards (3 tools)
| Tool | Description |
|------|-------------|
| `flashcard_overview` | Due cards, stats |
| `flashcard_due` | Cards due for review |
| `flashcard_create` | Create new flashcard |

### Whiteboards (3 tools)
| Tool | Description |
|------|-------------|
| `whiteboard_list` | List all whiteboards |
| `whiteboard_inspect` | Get whiteboard elements |
| `whiteboard_search` | Search whiteboard content |

### Helpers (3 tools)
| Tool | Description |
|------|-------------|
| `helpers_format_results` | Format tool output for LLM |
| `helpers_paginate` | Paginate large result sets |
| `helpers_summarize` | Auto-summarize page/block |

## Integration with Our Systems

### 1. GodModeCoder Evolution Graph
```json
{
  "mcpServers": {
    "godmodecoder-graph": {
      "command": "graphthulhu",
      "args": ["--backend", "obsidian", "--vault", "C:\\Vault"],
      "env": {}
    }
  }
}
```

**Agent capabilities via graphthulhu**:
- **SENSE**: `analyze_overview` → graph health, `analyze_gaps` → missing connections
- **THINK**: `search_blocks` for relevant patterns, `analyze_clusters` for module boundaries
- **MUTATE**: `write_create_page` new node specs, `write_add_link` new dependencies
- **FITNESS**: `analyze_centrality` for node importance, `analyze_connections` for coupling

### 2. Radio ArmsgeddonFM Knowledge Base
```json
{
  "mcpServers": {
    "radio-knowledge": {
      "command": "graphthulhu",
      "args": ["--backend", "obsidian", "--vault", "C:\\Vault"],
      "env": {}
    }
  }
}
```

**Use cases**:
- `search_properties` for song metadata (BPM, key, genre)
- `navigate_links` for pipeline traceability
- `journal_today` for daily generation logs
- `flashcard_create` for prompt/recipe distillation

### 3. Paranoidx/Sovereign Systems Documentation
```json
{
  "mcpServers": {
    "paranoidx-docs": {
      "command": "graphthulhu",
      "args": ["--read-only", "--backend", "obsidian", "--vault", "C:\\Vault"],
      "env": {}
    }
  }
}
```

**Read-only mode** ensures agent cannot modify sovereign system docs.

## Advanced Patterns

### 1. Decision Protocol for Architecture Choices
```markdown
<!-- Agent uses decision_create -->
{
  "topic": "Container orchestration: Docker Compose vs Kubernetes",
  "options": [
    {"id": "compose", "description": "Docker Compose - simpler, single host"},
    {"id": "k8s", "description": "Kubernetes - scalable, complex"}
  ],
  "criteria": ["setup_time", "resource_overhead", "scaling_need", "team_expertise"],
  "context": "Paranoidx 5-container stack on single N100"
}
```

### 2. Gap Analysis for Knowledge Completeness
```python
# Agent calls analyze_gaps, then:
# 1. Identifies orphan nodes (no in/out links)
# 2. Finds missing prerequisite links
# 3. Suggests `write_add_link` to connect clusters
# 4. Creates flashcards for isolated concepts
```

### 3. Cluster-Based Module Extraction
```python
# Agent calls analyze_clusters → gets communities
# For each cluster:
#   - Creates module summary page
#   - Adds `has_component` links from module to pages
#   - Updates Graph.yaml with module boundaries
```

### 4. Journal-Driven Evolution Log
```markdown
<!-- Daily evolution cycle creates journal entry -->
# 2026-08-10 Evolution Cycle 47

## SENSE
- Pulse: 8/13 alive
- Gaps: 3 missing links between optimizer and watchdog

## THINK
- Cluster analysis: optimizer isolated from pipeline
- Centrality: oracle has highest betweenness

## MUTATE
- Added link: optimizer → pipeline (via write_add_link)
- Created page: Fitness Gates & Extinction Protocol

## FITNESS
- Verify: 10/10 tests pass
- Centrality improved: optimizer betweenness +15%

## MEMORY
- Decision: Use mass extinction every 50 gens
- Flashcard: DGM fitness vector dimensions
```

## Installation & Build

### From Source (Go 1.21+)
```bash
git clone https://github.com/skridlevsky/graphthulhu
cd graphthulhu
go build -o graphthulhu ./main.go
# Binary: ./graphthulhu
```

### Pre-built Releases
```bash
# Check GitHub releases for platform binaries
# Linux/Windows/macOS available
```

### As Systemd Service (Linux)
```ini
# /etc/systemd/system/graphthulhu.service
[Unit]
Description=graphthulhu MCP Server
After=network.target

[Service]
Type=simple
User=obsidian
WorkingDirectory=/home/obsidian
ExecStart=/usr/local/bin/graphthulhu --backend obsidian --vault /home/obsidian/vault
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

## Security Considerations

| Risk | Mitigation |
|------|------------|
| **Full write access** | Use `--read-only` for untrusted agents |
| **Vault path traversal** | Validate vault path, run as dedicated user |
| **MCP protocol injection** | Standard MCP validation, no raw SQL |
| **Logseq token exposure** | Store token in env var, not config file |
| **Concurrent edits** | Graphthulhu uses file locking for Obsidian |

## Performance Tuning

| Setting | Recommendation |
|---------|----------------|
| **Vault size < 10k files** | Default indexing OK |
| **Vault size > 10k files** | Enable `--index-cache` (if available) |
| **Large queries** | Use `helpers_paginate` tool |
| **Real-time sync** | Run `analyze_overview` periodically, cache results |

## References
- **GitHub**: https://github.com/skridlevsky/graphthulhu
- **Reddit**: r/logseq discussion on MCP servers
- **MCP Spec**: https://modelcontextprotocol.io/
- **Obsidian Vault API**: Local filesystem markdown + frontmatter
- **Logseq HTTP API**: https://github.com/logseq/logseq/blob/master/docs/api.md