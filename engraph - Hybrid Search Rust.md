Warning: Permanently added '100.124.152.97' (ED25519) to the list of known hosts.
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
---
tags: [textbook, mcp, engraph, hybrid-search, obsidian, vector-search, bm25,
C:\Vault\engraph - Hybrid Search Rust.md


 rrf, agent-integration]
source: textbook
status: learned
date: 2026-08-10
priority: 9
---

# engraph — Hybrid Search Rust (Obsidian Hybrid Search)

## Summary
**engraph** (marketed as **Obsidian Hybrid Search** by flowing-abyss) is a **local-first MCP server** written in Rust that provides **hybrid search** (BM25 full-text + fuzzy title + vector embeddings) over Obsidian vaults. It combines lexical and semantic search via **Reciprocal Rank Fusion (RRF)**, runs entirely offline (no API key required with local embeddings), and exposes search as an MCP tool call.

## Core Architecture

### Hybrid Search Pipeline
```
Query → [BM25] ──┐
                ├──→ RRF (Reciprocal Rank Fusion) → Ranked Results
Query → [Fuzzy Title] ┤
                ├──→ 
Query → [Vector] ───┘
```

### Three Retrieval Methods
| Method | Strength | Weight (RRF) |
|--------|----------|--------------|
| **BM25** | Exact keyword matches, acronyms, codes | k=60 |
| **Fuzzy Title** | Typo tolerance, partial titles | k=60 |
| **Vector (Embeddings)** | Semantic similarity, concepts | k=60 |

**RRF Formula**: `score = Σ 1 / (k + rank_i)` across all three retrievers.

## MCP Server Setup

### Minimal Config (Local Embeddings, No API Key)
```json
{
  "mcpServers": {
    "obsidian-hybrid-search": {
      "command": "npx",
      "args": ["-y", "-p", "obsidian-hybrid-search@latest", "obsidian-hybrid-search-mcp"],
      "env": {
        "OBSIDIAN_VAULT_PATH": "C:\\Vault"
      }
    }
  }
}
```

### Full Config (OpenRouter / OpenAI Embeddings)
```json
{
  "mcpServers": {
    "obsidian-hybrid-search": {
      "command": "npx",
      "args": ["-y", "-p", "obsidian-hybrid-search@latest", "obsidian-hybrid-search-mcp"],
      "env": {
        "OBSIDIAN_VAULT_PATH": "C:\\Vault",
        "OBSIDIAN_PREFIX": "myvault_",
        "OBSIDIAN_RESPECT_GITIGNORE": "true",
        "OBSIDIAN_IGNORE_PATTERNS": ".obsidian/**,templates/**,*.canvas",
        "OBSIDIAN_INCLUDE_PATTERNS": "private/notes/**",
        "OPENAI_API_KEY": "sk-or-v1-...",
        "OPENAI_BASE_URL": "https://openrouter.ai/api/v1",
        "OPENAI_EMBEDDING_MODEL": "openai/text-embedding-3-small"
      }
    }
  }
}
```

### Shared HTTP Server Mode
```bash
# Start HTTP server
OBSIDIAN_VAULT_PATH="C:\\Vault" obsidian-hybrid-search serve

# MCP config for HTTP
{
  "mcpServers": {
    "obsidian-hybrid-search": {
      "url": "http://127.0.0.1:3939/mcp"
    }
  }
}
```

## Available MCP Tools

### Primary Tool: `obsidian_search`
```json
{
  "name": "obsidian_search",
  "description": "Search the Obsidian vault using hybrid BM25 + vector retrieval",
  "parameters": {
    "query": { "type": "string", "description": "Search query" },
    "limit": { "type": "integer", "default": 5 },
    "max_tokens": { "type": "integer", "default": 2000 },
    "include_content": { "type": "boolean", "default": true }
  }
}
```

**Returns**: Ranked results with snippets, file paths, scores, and metadata.

## CLI Usage (Direct)

### Installation
```bash
npm install -g obsidian-hybrid-search
```

### Reindex Vault
```bash
cd C:\\Vault
obsidian-hybrid-search reindex
```

### Search from CLI
```bash
obsidian-hybrid-search "how to build a consistent daily review"
```

### Server Management
```bash
obsidian-hybrid-search serve status
obsidian-hybrid-search serve stop
obsidian-hybrid-search serve --foreground
obsidian-hybrid-search serve --http --foreground
obsidian-hybrid-search serve --host 0.0.0.0 --allowed-host 192.168.1.20:3939
```

## Integration with Our Systems

### 1. GodModeCoder Evolution Context
```json
{
  "mcpServers": {
    "vault-search": {
      "command": "npx",
      "args": ["-y", "-p", "obsidian-hybrid-search@latest", "obsidian-hybrid-search-mcp"],
      "env": {
        "OBSIDIAN_VAULT_PATH": "C:\\Vault",
        "OBSIDIAN_IGNORE_PATTERNS": ".obsidian/**,templates/**,*.canvas,Inbox/**"
      }
    }
  }
}
```

**Agent workflow**:
1. **SENSE**: `obsidian_search` for "fitness gates extinction protocol" → retrieves relevant evolution docs
2. **THINK**: `obsidian_search` for "DGM Darwin Gödel Machine" → pulls research papers
3. **MUTATE**: Search for existing patterns before generating new code
4. **FITNESS**: Verify implementation matches documented patterns

### 2. Radio ArmsgeddonFM Knowledge Retrieval
```json
{
  "mcpServers": {
    "radio-search": {
      "command": "npx",
      "args": ["-y", "-p", "obsidian-hybrid-search@latest", "obsidian-hybrid-search-mcp"],
      "env": {
        "OBSIDIAN_VAULT_PATH": "C:\\Vault",
        "OBSIDIAN_INCLUDE_PATTERNS": "Projects/ArmsgeddonFM/**,Evolution/radio_*.md"
      }
    }
  }
}
```

**Use cases**:
- Retrieve prompt templates by semantic similarity
- Find similar song structures (BM25 on metadata)
- Cross-reference PlugMem papers with implementation

### 3. Paranoidx/Sovereign Systems (Read-Only)
```json
{
  "mcpServers": {
    "paranoidx-search": {
      "command": "npx",
      "args": ["-y", "-p", "obsidian-hybrid-search@latest", "obsidian-hybrid-search-mcp"],
      "env": {
        "OBSIDIAN_VAULT_PATH": "C:\\Vault",
        "OBSIDIAN_INCLUDE_PATTERNS": "Paranoidx/**,IsleProject/**,Evolution/paranoidx.md"
      }
    }
  }
}
```

## Local Embeddings (No API Key)

### Models Supported
| Model | Size | Quality | Speed | Use Case |
|-------|------|---------|-------|----------|
| `all-MiniLM-L6-v2` | 22MB | Good | Fast | Default local |
| `all-mpnet-base-v2` | 110MB | Better | Slower | Higher quality |
| `bge-small-en-v1.5` | 33MB | Excellent | Fast | Multilingual |

### Configuration for Local
```json
{
  "mcpServers": {
    "obsidian-hybrid-search": {
      "command": "npx",
      "args": ["-y", "-p", "obsidian-hybrid-search@latest", "obsidian-hybrid-search-mcp"],
      "env": {
        "OBSIDIAN_VAULT_PATH": "C:\\Vault",
        "OBSIDIAN_EMBEDDING_MODEL": "local",
        "OBSIDIAN_LOCAL_MODEL": "all-MiniLM-L6-v2"
      }
    }
  }
}
```

## Performance & Indexing

### Index Structure
```
.vault-index/
├── bm25.idx          # Tantivy BM25 index
├── vectors.db        # SQLite + vec0 (vector storage)
├── titles.idx        # Fuzzy title index
├── metadata.json     # File stats, timestamps
└── embeddings/       # Embedding cache (if local)
```

### Reindex Triggers
- **Full reindex**: `obsidian-hybrid-search reindex` (first run, major changes)
- **Incremental**: Automatic on file change (watch mode)
- **Partial**: `obsidian-hybrid-search reindex --path "Projects/"`

### Performance Tuning
| Setting | Recommendation |
|---------|----------------|
| Vault < 5k files | Default settings |
| Vault 5k-20k | Increase `OBSIDIAN_BATCH_SIZE=100` |
| Vault > 20k | Use HTTP server mode, SSD, 16GB+ RAM |
| Local embeddings | CPU: 4+ cores, RAM: 8GB+ |

## Advanced Patterns

### 1. Agent Self-Correction Loop
```python
async def agent_search_correct(agent, goal):
    # 1. Search for relevant patterns
    results = await agent.call_tool("obsidian_search", {
        "query": f"{goal} implementation pattern",
        "limit": 10
    })
    
    # 2. Filter by relevance score > 0.7
    relevant = [r for r in results if r.score > 0.7]
    
    # 3. If no results, broaden query
    if not relevant:
        results = await agent.call_tool("obsidian_search", {
            "query": goal.split()[0],  # First keyword only
            "limit": 20
        })
    
    return results
```

### 2. Cross-Reference Validation
```python
# Before committing code, search for similar patterns
validation = await agent.call_tool("obsidian_search", {
    "query": "fitness gate extinction protocol implementation",
    "limit": 5
})

if not any("extinction" in r.content for r in validation):
    # Warn: pattern not documented
    agent.log("WARNING: New pattern not in knowledge base")
```

### 3. Knowledge Gap Detection
```python
# Search for concepts mentioned but not implemented
gap_query = "DGM Darwin Gödel Machine fitness vector"
results = await agent.call_tool("obsidian_search", {
    "query": gap_query,
    "limit": 10
})

# If results exist but no code references → gap
has_code = any(".py" in r.path for r in results)
if results and not has_code:
    agent.create_task("Implement DGM fitness vector in evolution_cycle.py")
```

## Security & Privacy

| Feature | Implementation |
|---------|----------------|
| **Local-only** | No data leaves machine (with local embeddings) |
| **Gitignore respect** | `OBSIDIAN_RESPECT_GITIGNORE=true` |
| **Path isolation** | `OBSIDIAN_VAULT_PATH` restricts to single vault |
| **No telemetry** | Open source, no analytics |
| **Read-only option** | File system permissions control write access |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Index not found" | Run `obsidian-hybrid-search reindex` |
| Slow queries | Reduce `limit`, use HTTP server mode |
| Out of memory (local embeddings) | Switch to `all-MiniLM-L6-v2`, close other apps |
| MCP connection failed | Check `npx` version, try `--foreground` for logs |
| Results stale | Run incremental reindex, check file watcher |

## References
- **GitHub**: https://github.com/flowing-abyss/obsidian-hybrid-search
- **Forum**: https://forum.obsidian.md/t/hybrid-search-hybrid-search-mcp-server-cli-for-ai-assistants-bm25-semantic-obsidian-native/112491
- **MCP Registry**: https://mcp.so/servers/obsidian-hybrid-search
- **Blake Crosley Guide**: https://blakecrosley.com/guides/obsidian
- **RRF Paper**: "Reciprocal Rank Fusion Outperforms Condorcet" (Cormack et al., 2009)